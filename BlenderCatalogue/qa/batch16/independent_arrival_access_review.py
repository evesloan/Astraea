"""Independent complete arrival access, physical interfaces and translation review.
Read-only source cache/native GLB inspection. No author generator is imported.
"""
from pathlib import Path
import sys,json,hashlib,itertools,collections
import numpy as np
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';BASE=ROOT/'assets/auditorium_arrival'
for p in ['qa/batch07','qa/batch08','qa/batch12','qa/batch15']:sys.path.insert(0,str(ROOT/p))
from independent_geometry import Native,C
from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles,triangle_uncovered_area,clip_polygon
from independent_void_geometry import triangle_box_mask
from independent_contact_graph import normal_witness
TOL=2e-7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(Path(p).relative_to(ROOT)),'sha256':sha(p)}
json_default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist()

def corners(lo,hi):return np.array(list(itertools.product(*zip(lo,hi))),float)
def key(t):return tuple(sorted(tuple(x)for x in np.round(t,6)))
def descendants(so,name,root):
 while name in so:
  name=so[name]['parent']
  if name==root:return True
 return False

def convex_parts(t):
 """Use actual outward faces to prove convexity; otherwise decompose axial prism caps."""
 v=np.unique(t.reshape(-1,3),axis=0);h=Hull(v)
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 if np.max(np.einsum('vti,ti->vt',v[:,None,:]-t[None,:,0],n))<=TOL:return [h],'actual outward face halfspaces prove convex solid'
 for ax in range(3):
  vals=np.unique(v[:,ax])
  if len(vals)!=2:continue
  caps=t[np.max(np.abs(t[:,:,ax]-vals[0]),axis=1)<TOL]
  if not len(caps):continue
  delta=np.zeros(3);delta[ax]=vals[1]-vals[0]
  hs=[Hull(np.vstack([q,q+delta]))for q in caps]
  vol=abs(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
  if abs(sum(x.hull.volume for x in hs)-vol)>1e-7:continue
  residual=sum(triangle_uncovered_area(q,hs)for q in t)
  if residual<1e-9:return hs,'exact actual cap triangle-prism decomposition; checked source volume and continuous surface union coverage'
 raise ValueError('Unsupported nonconvex semantic part')

def continuous_overlap(a,b,delta):
 """LP maximum common interior radius over the entire closed linear motion interval."""
 A=[];rhs=[]
 for h,moving in [(a,True),(b,False)]:
  for p in h.planes:
   A.append([*p[:3],-float(p[:3]@delta)if moving else 0.,1.]);rhs.append(-p[3])
 r=linprog([0,0,0,0,-1],A_ub=A,b_ub=rhs,bounds=[(None,None)]*3+[(0,1),(None,None)],method='highs')
 if not r.success:raise RuntimeError(r.message)
 return {'maximum_shared_interior_radius_m':float(r.x[4]),'translation_fraction_at_witness':float(r.x[3]),'point_source_m':r.x[:3].tolist(),'material_intrusion':bool(r.x[4]>TOL),'boundary_contact':bool(abs(r.x[4])<=TOL)}

def empty_box(t,labels,lo,hi):
 """Full triangle/AABB SAT and containment. Epsilon only classifies boundary contact."""
 lo=np.asarray(lo,float);hi=np.asarray(hi,float)
 full=triangle_box_mask(t,lo,hi);strict=triangle_box_mask(t,lo+TOL,hi-TOL)
 enclosed=[]
 for name in np.unique(labels):
  q=t[labels==name]
  if ((q.max((0,1))<lo)|(q.min((0,1))>hi)).any():continue
  if inside_mesh([(lo+hi)/2],q)[0] and nearest_distances([(lo+hi)/2],q)[0]>TOL:enclosed.append(str(name))
 return {'intruding_surface_parts':sorted(set(str(x)for x in labels[strict])),'box_midpoint_enclosed_by_parts':enclosed,'boundary_only_parts':sorted(set(str(x)for x in labels[full])-set(str(x)for x in labels[strict])),'pass':not strict.any()and not enclosed}

def nesting_check(tris,profile):
 """Clip every complete actual triangle into each local X slab, then check its wall halfspace."""
 rows=[]
 for section in profile:
  a,b=section['x_interval_m'];slope,intercept=section['inner_y_line'];minimum=float('inf');witness=None;count=0
  for t in tris:
   if t[:,0].max()<a-1e-12 or t[:,0].min()>b+1e-12:continue
   p=clip_polygon(t,np.array([-1.,0,0,a]),tol=0.)
   if len(p)<1:continue
   p=clip_polygon(p,np.array([1.,0,0,-b]),tol=0.)
   if len(p)<1:continue
   d=(p[:,1]-slope*p[:,0]-intercept)/np.sqrt(1+slope*slope);j=int(d.argmin());count+=1
   if d[j]<minimum:minimum=float(d[j]);witness=p[j].tolist()
  if count:rows.append({'shell_part':section['part'],'x_interval_m':[a,b],'clipped_triangle_count':count,'minimum_inward_normal_clearance_m':minimum,'minimum_source_y_clearance_m':minimum*np.sqrt(1+slope*slope),'minimum_witness_source_m':witness,'pass':minimum>=-TOL})
 xmin=min(x['x_interval_m'][0]for x in profile);xmax=max(x['x_interval_m'][1]for x in profile);v=tris.reshape(-1,3);within=bool(v[:,0].min()>=xmin-TOL and v[:,0].max()<=xmax+TOL)
 return {'sections':rows,'all_vertices_inside_tested_profile_width':within,'minimum_inward_normal_clearance_m':min((x['minimum_inward_normal_clearance_m']for x in rows),default=-1e9),'minimum_source_y_clearance_m':min((x['minimum_source_y_clearance_m']for x in rows),default=-1e9),'pass':within and bool(rows)and all(x['pass']for x in rows)}

def main():
 results=[]
 for ident in ['AST-CUL-001','AST-CUL-002']:
  mp=BASE/f'{ident}.manifest.json';m=json.loads(mp.read_text());sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());cache=ROOT/s['geometry_cache'];inputpaths=[('source',sp),('export',gp),('manifest',mp),('generator',BASE/m['generator']),('source_audit',rp),('geometry_cache',cache),('collision',BASE/'collision_proposals.json'),('marker_api',BASE/'marker_api.json')]+[('export_'+v['name'],BASE/v['export'])for v in m.get('state_derivatives',[])];inputbindings={k:bind(p)for k,p in inputpaths};a=np.load(cache);tri=a['triangles'];labels=a['object_names'];so={x['name']:x for x in s['objects']};nat=Native(gp);nt=nat.tris@C;nodes=nat.g.doc['nodes'];ni={x.get('name'):i for i,x in enumerate(nodes)};failures=[]
  current=sha(sp)==s['sha256']==m['source_sha256'] and sha(gp)==m['glb_sha256'] and sha(BASE/m['generator'])==m['generator_sha256']
  if not current:failures.append('Source audit or manifest is stale')
  mapping=collections.defaultdict(list)
  for j,t in enumerate(nt):mapping[key(t)].append(j)
  partnative={};unmatched=[];used=set();sourceparts=sorted(set(str(x)for x in labels));native_ownership=[]
  for name in sourceparts:
   ix=[];errors=[];role=so[name]['materials'][0];owner=so[name]['parent']
   for t in tri[labels==name]:
    choices=[j for j in mapping.get(key(t),[])if j not in used and nat.materials[j]==role and nodes[ni[str(nat.nodes[j])]].get('extras',{}).get('semantic_parts') and name in json.loads(nodes[ni[str(nat.nodes[j])]]['extras']['semantic_parts'])]
    if not choices:unmatched.append(name);continue
    j=choices[0];used.add(j);ix.append(j);errors.append(float(max(np.linalg.norm(t[:,None,:]-nt[j][None,:,:],axis=2).min(0).max(),np.linalg.norm(t[:,None,:]-nt[j][None,:,:],axis=2).min(1).max())))
   partnative[name]=np.array(ix,int)
   actualowners=sorted(set(nodes[nat.parents.get(ni[str(nat.nodes[j])],ni[str(nat.nodes[j])])].get('name')for j in ix))
   native_ownership.append({'part':name,'declared_source_owner':owner,'native_parent_names':actualowners,'matched_triangles':len(ix),'source_triangles':int((labels==name).sum()),'maximum_actual_corner_error_m':max(errors,default=1e9),'pass':len(ix)==int((labels==name).sum())and actualowners==[owner]and max(errors,default=1e9)<TOL})
  if unmatched or len(used)!=len(nt):failures.append('Source/native semantic triangle correspondence incomplete')
  if unmatched:
   r={'catalogue_id':ident,'passed':False,'input_bindings_current':current,'failures':failures,'unmatched_semantic_parts':sorted(set(unmatched)),'native_ownership':native_ownership};results.append(r);print(ident,r['failures'],r['unmatched_semantic_parts'],flush=True);continue
  nlabels=np.empty(len(nt),dtype=object)
  for name,ix in partnative.items():nlabels[ix]=name
  def ntris(name):return nt[partnative[name]]
  markers=[]
  for mr in m['physical_and_proposal_markers']:
   name=mr['name'];p=np.array(mr['source_m']);idx=ni[name];actual=nat.world[idx][:3,3];sourcep=np.array(so[name]['matrix_world'])[:3,3];owner=nodes[nat.parents[idx]].get('name');dnormal=mr.get('direction_source');row={'name':name,'kind':mr['kind'],'source_position_error_m':float(np.linalg.norm(sourcep-p)),'native_position_error_m':float(np.linalg.norm(actual-C@p)),'source_owner':so[name]['parent'],'native_owner':owner,'declared_owner':mr['owner']}
   row['pass']=max(row['source_position_error_m'],row['native_position_error_m'])<TOL and owner==so[name]['parent']==mr['owner']
   if dnormal is not None:
    row['direction_basis_error']=float(np.linalg.norm(np.array(mr['direction_gltf'])-C@np.array(dnormal)));row['native_direction_extras_match']=np.linalg.norm(np.array(nodes[idx]['extras']['direction_gltf'])-C@np.array(dnormal))<TOL;row['source_direction_extras_match']=np.linalg.norm(np.array(so[name]['properties']['direction_source'])-np.array(dnormal))<TOL;row['pass']&=row['direction_basis_error']<TOL and row['native_direction_extras_match']and row['source_direction_extras_match']
   if mr['physical_part']:
    part=mr['physical_part'];st=tri[labels==part];gt=ntris(part);n=np.array(dnormal);row.update(physical_part=part,source_surface_distance_m=float(nearest_distances([p],st)[0]),native_surface_distance_m=float(nearest_distances([p],gt)[0]),source_normal=normal_witness(p,st,n),native_normal=normal_witness(p,gt,n));row['pass']&=max(row['source_surface_distance_m'],row['native_surface_distance_m'])<TOL and row['source_normal']['pass']and row['native_normal']['pass']and so[part]['parent']==mr['owner']
   markers.append(row)
  joins=[]
  for jr in m['joins']:
   p=np.array(jr['probe_source_m']);row={'name':jr['name'],'parts':jr['parts'],'point_source_m':p.tolist(),'basis_error_m':float(np.linalg.norm(C@p-np.array(jr['probe_gltf_m']))),'witnesses':[],'pass':True}
   for name,n in zip(jr['parts'],[jr.get('normal_a_source'),jr.get('normal_b_source')]):
    st=tri[labels==name];gt=ntris(name);sd=float(nearest_distances([p],st)[0]);nd=float(nearest_distances([p],gt)[0]);w={'part':name,'source_distance_m':sd,'native_distance_m':nd}
    if n is None:w.update(kind='explicit buried bearing probe, no opposing surface-normal claim',source_inside=bool(inside_mesh([p],st)[0]),native_inside=bool(inside_mesh([p],gt)[0]));w['pass']=(sd<TOL or w['source_inside'])and(nd<TOL or w['native_inside'])
    else:w.update(kind='physical boundary with outward normal',source_normal=normal_witness(p,st,n),native_normal=normal_witness(p,gt,n));w['pass']=max(sd,nd)<TOL and w['source_normal']['pass']and w['native_normal']['pass']
    row['witnesses'].append(w);row['pass']&=w['pass']
   na=jr.get('normal_a_source');nb=jr.get('normal_b_source')
   if na is not None and nb is not None:row['opposing_normal_dot']=float(np.array(na)@nb);row['pass']&=row['opposing_normal_dot']<-.999
   row['pass']&=row['basis_error_m']<TOL;joins.append(row)
  movements=[];state={};decompositions={}
  for name in sourceparts:
   hs,method=convex_parts(tri[labels==name]);decompositions[name]=hs
  for motion in m['motions']:
   root=motion['root'];delta=np.array(motion['axis_source'])*(motion['access_m']-motion['closed_m']);moving=[x for x in sourceparts if descendants(so,x,root)];mm=np.isin(labels,moving);nm=np.isin(nlabels,moving);owned_markers=[x['name']for x in m['physical_and_proposal_markers']if descendants(so,x['name'],root)];sourceclosed=np.array(so[root]['matrix_world']);nativeclosed=nat.world[ni[root]];checks=[];broad=0
   for an in moving:
    for bn in sourceparts:
     if bn in moving:continue
     for ah in decompositions[an]:
      for bh in decompositions[bn]:
       alo=np.minimum(ah.lo,ah.lo+delta);ahi=np.maximum(ah.hi,ah.hi+delta)
       if ((alo>bh.hi+TOL)|(ahi<bh.lo-TOL)).any():continue
       broad+=1;hit=continuous_overlap(ah,bh,delta)
       if hit['material_intrusion']or hit['boundary_contact']:checks.append({'moving_part':an,'fixed_part':bn,**hit})
   # Positive control placed at0.5mm travel within an actual moving solid, proving the first millimetre is included.
   first=decompositions[moving[0]][0];centre=first.points.mean(0);centre[1]=first.hi[1]+.0005;control=Hull(corners(centre-.0001,centre+.0001));positive=continuous_overlap(first,control,delta);positive['closed_separation_m']=.0004;positive['witness_travel_m']=positive['translation_fraction_at_witness']*np.linalg.norm(delta);positive['detected_within_first_millimetre']=0<positive['witness_travel_m']<.001
   # Native root update applied through the real native basis; every owned mesh and marker follows it.
   posed=tri.copy();posed[mm]+=delta;nposed=nt.copy();nposed[nm]+=C.T@(C@delta);state['access']=(posed,nposed)
   poses=[]
   for travel in [0.,.000001,.0001,.001,float(np.linalg.norm(delta)/2),float(np.linalg.norm(delta))]:
    f=travel/np.linalg.norm(delta);d=delta*f;markers_pose=[]
    for name in owned_markers:
     mr=next(x for x in m['physical_and_proposal_markers']if x['name']==name);p=np.array(mr['source_m'])+d;got=nat.world[ni[name]][:3,3]+C@d;markers_pose.append({'name':name,'position_error_m':float(np.linalg.norm(got-C@p)),'named_surface_distance_m':float(nearest_distances([p],ntris(mr['physical_part'])+d)[0])})
    poses.append({'travel_m':travel,'markers':markers_pose,'pass':all(max(x['position_error_m'],x['named_surface_distance_m'])<TOL for x in markers_pose)})
   verts=tri[mm].reshape(-1,3);envelope=[np.minimum(verts.min(0),(verts+delta).min(0)).tolist(),np.maximum(verts.max(0),(verts+delta).max(0)).tolist()]
   sextra=so[root]['properties'];nextra=nodes[ni[root]]['extras'];rootmetadata=all(np.linalg.norm(np.array(ex['translation_axis_source'])-motion['axis_source'])<TOL and np.linalg.norm(np.array(ex['translation_axis_gltf'])-C@np.array(motion['axis_source']))<TOL and ex['closed_translation_m']==motion['closed_m']and ex['access_translation_m']==motion['access_m']for ex in [sextra,nextra])
   bearings=[]
   for an in [x for x in moving if x.endswith('_drawer_slide')]:
    bn=an.replace('_drawer_slide','_fixed_slide_bearing');ah=decompositions[an][0];bh=decompositions[bn][0];width=min(ah.hi[0],bh.hi[0])-max(ah.lo[0],bh.lo[0]);depths=[min(ah.hi[1]+f*delta[1],bh.hi[1])-max(ah.lo[1]+f*delta[1],bh.lo[1])for f in [0,1]];flatgap=abs(ah.lo[2]-bh.hi[2]);boxes=all(abs(h.hull.volume-np.prod(h.hi-h.lo))<1e-10 for h in [ah,bh]);bearings.append({'moving_runner':an,'fixed_bearing':bn,'actual_box_solids_verified':boxes,'bearing_plane_separation_m':float(flatgap),'minimum_width_overlap_m':float(width),'closed_and_access_length_overlap_m':[float(v)for v in depths],'minimum_area_overlap_m2':float(width*min(depths)),'continuous_basis':'For fixed-axis box runners translated monotonically inY, interval-overlap length is piecewise linear and concave; its minimum on the full closed interval occurs at an endpoint. X overlap andZ bearing faces remain invariant.','pass':boxes and flatgap<TOL and width>TOL and min(depths)>TOL})
   rr={'root':root,'closed_translation_m':motion['closed_m'],'source_and_native_root_motion_metadata_match':rootmetadata,'source_root_closed_world_matrix':sourceclosed.tolist(),'native_root_closed_world_matrix':nativeclosed.tolist(),'moving_parts':moving,'moving_physical_markers':owned_markers,'complete_sweep_envelope_source_m':envelope,'translation_source_m':delta.tolist(),'full_interval':[0.,1.],'pair_count':len(moving)*(len(sourceparts)-len(moving)),'broad_phase_convex_pairs':broad,'contact_or_intrusion_pairs':checks,'continuous_runner_bearings':bearings,'first_millimetre_positive_control':positive,'sampled_native_marker_poses':poses,'pass':rootmetadata and motion['closed_m']==0 and np.linalg.norm(sourceclosed[:3,3])<TOL and np.linalg.norm(nativeclosed[:3,3])<TOL and not any(x['material_intrusion']for x in checks)and positive['material_intrusion']and positive['detected_within_first_millimetre']and all(x['pass']for x in poses+bearings)}
   movements.append(rr)
  derivatives=[]
  for dr in m.get('state_derivatives',[]):
   dn=Native(BASE/dr['export']);dt=dn.tris@C;dnodes=dn.g.doc['nodes'];dni={x.get('name'):i for i,x in enumerate(dnodes)};expected=state[dr['name']][0];dmapping=collections.defaultdict(list)
   for j,t in enumerate(dt):dmapping[key(t)].append(j)
   dused=set();dlabels=np.empty(len(dt),dtype=object);dparts={};derrors=[];dunmatched=[]
   for name in sourceparts:
    ix=[]
    for t in expected[labels==name]:
     choices=[j for j in dmapping.get(key(t),[])if j not in dused and dn.materials[j]==so[name]['materials'][0] and name in json.loads(dnodes[dni[str(dn.nodes[j])]].get('extras',{}).get('semantic_parts','[]'))and dnodes[dn.parents[dni[str(dn.nodes[j])]]].get('name')==so[name]['parent']]
     if not choices:dunmatched.append(name);continue
     j=choices[0];dused.add(j);ix.append(j);dlabels[j]=name;derrors.append(float(max(np.linalg.norm(t[:,None,:]-dt[j][None,:,:],axis=2).min(0).max(),np.linalg.norm(t[:,None,:]-dt[j][None,:,:],axis=2).min(1).max())))
    dparts[name]=np.array(ix,int)
   dmarks=[]
   for mr in m['physical_and_proposal_markers']:
    p=np.array(mr['source_m'],float)
    for mo in m['motions']:
     if descendants(so,mr['name'],mo['root']):p+=np.array(mo['axis_source'])*(mo['access_m']-mo['closed_m'])
    row={'name':mr['name'],'native_position_error_m':float(np.linalg.norm(dn.world[dni[mr['name']]][:3,3]-C@p)),'native_parent':dnodes[dn.parents[dni[mr['name']]]].get('name')};row['pass']=row['native_position_error_m']<TOL and row['native_parent']==mr['owner']
    if mr['physical_part']and len(dparts[mr['physical_part']]):
     q=dt[dparts[mr['physical_part']]];row['named_surface_distance_m']=float(nearest_distances([p],q)[0]);row['surface_normal']=normal_witness(p,q,mr['direction_source']);row['pass']&=row['named_surface_distance_m']<TOL and row['surface_normal']['pass']
    dmarks.append(row)
   drrow={'state':dr['name'],'binding':bind(BASE/dr['export']),'manifest_hash_matches':sha(BASE/dr['export'])==dr['glb_sha256'],'maximum_source_posed_native_corner_error_m':max(derrors,default=1e9),'unmatched_semantic_parts':sorted(set(dunmatched)),'unmatched_native_triangles':len(dt)-len(dused),'markers':dmarks,'pass':not dunmatched and len(dused)==len(dt)and max(derrors,default=1e9)<TOL and all(x['pass']for x in dmarks)and sha(BASE/dr['export'])==dr['glb_sha256']};derivatives.append(drrow)
   if drrow['pass']:state[dr['name']]=(expected,dt);nlabels_access=dlabels
  state['closed']=(tri,nt);voids=[];probes=[];colfile=json.loads((BASE/'collision_proposals.json').read_text())[ident];col=colfile['shapes'];metadata_consistent=colfile['preserve_voids']==m['receiver_voids']and colfile['motion_roots']==m['motions']and json.loads((BASE/'marker_api.json').read_text())[ident]==m['physical_and_proposal_markers']
  scenarios=list(m['receiver_voids'])
  for vr in m['receiver_voids']:
   if vr['name']in ['closed_programme_cassette_air','staff_open_programme_cubby','lower_wing_staff_knee_proposal']:
    scenarios.append({**vr,'pose':'access','name':vr['name']+'__access_persistence'})
   if vr['name']=='rear_panel_hand_gap':
    mo=m['motions'][0];dd=np.array(mo['axis_source'])*(mo['access_m']-mo['closed_m']);scenarios.append({**vr,'pose':'access','name':vr['name']+'__access_translated','min_source_m':(np.array(vr['min_source_m'])+dd).tolist(),'max_source_m':(np.array(vr['max_source_m'])+dd).tolist()})
  for vr in scenarios:
   t,g=state[vr['pose']];gl=nlabels_access if vr['pose']=='access'and derivatives and all(x['pass']for x in derivatives)else nlabels;lo=np.array(vr['min_source_m']);hi=np.array(vr['max_source_m']);sr=empty_box(t,labels,lo,hi);nr=empty_box(g,gl,lo,hi);cv=[]
   for cr in col:
    pts=np.array(cr['points_source_m'])if 'points_source_m'in cr else corners(cr['min_source_m'],cr['max_source_m'])
    if vr['pose']=='access':
     for mo in m['motions']:
      if cr['owner']==mo['root']:pts+=np.array(mo['axis_source'])*(mo['access_m']-mo['closed_m'])
    hh=Hull(pts)
    if ((hh.lo>hi+TOL)|(hh.hi<lo-TOL)).any():continue
    hit=continuous_overlap(hh,Hull(corners(lo,hi)),np.zeros(3))
    if hit['material_intrusion']:cv.append({'shape':cr['name'],**hit})
   synthetic=Hull(corners((lo+hi)/2-.0001,(lo+hi)/2+.0001));injected=triangle_box_mask(synthetic.tris,lo,hi).any();row={'name':vr['name'],'pose':vr['pose'],'min_source_m':lo.tolist(),'max_source_m':hi.tolist(),'source':sr,'native':nr,'collision_intrusions':cv,'inserted_solid_positive_control_detected':bool(injected),'pass':sr['pass']and nr['pass']and not cv and bool(injected)};voids.append(row)
   for ax in range(3):
    others=[i for i in range(3)if i!=ax]
    for u,v in itertools.product([.05,.5,.95],repeat=2):
     p=lo.copy();q=hi.copy()
     for k,f in zip(others,[u,v]):p[k]=q[k]=lo[k]+f*(hi[k]-lo[k])
     sv=bool(segment_triangles(p,q,t));nv=bool(segment_triangles(p,q,g));probes.append({'void':vr['name'],'pose':vr['pose'],'segment_source_m':[p.tolist(),q.tolist()],'source_blocked':sv,'native_blocked':nv,'pass':not sv and not nv})
  backing=[];nesting=[];public_envelope=[]
  if ident=='AST-CUL-002':
   vr=next(x for x in m['receiver_voids']if x['name']=='staff_open_programme_cubby');lo=np.array(vr['min_source_m']);hi=np.array(vr['max_source_m']);surface=np.array([[[lo[0],0,lo[2]],[hi[0],0,lo[2]],[hi[0],0,hi[2]]],[[lo[0],0,lo[2]],[hi[0],0,hi[2]],[lo[0],0,hi[2]]]])
   shellnames=[x for x in sourceparts if x.startswith('curved_public_shell_segment_')];proofs=[]
   for frame,tr,lab in [('source',tri,labels),('native',nt,nlabels)]:
    projected=[];ys=[]
    for name in shellnames:
     v=np.unique(tr[lab==name].reshape(-1,3),axis=0);ys.extend(v[:,1]);p=v.copy();p[:,1]=-.5;q=v.copy();q[:,1]=.5;projected.append(Hull(np.vstack([p,q])))
    uncovered=sum(triangle_uncovered_area(t,projected)for t in surface);area=(hi[0]-lo[0])*(hi[2]-lo[2]);proofs.append({'frame':frame,'complete_useful_width_height_m':[float(hi[0]-lo[0]),float(hi[2]-lo[2])],'backing_projected_area_m2':float(area),'uncovered_projected_area_m2':float(uncovered),'actual_shell_y_bounds_m':[float(min(ys)),float(max(ys))],'minimum_shell_to_reserved_void_clearance_m':float(lo[1]-max(ys)),'pass':uncovered<1e-10 and max(ys)<=lo[1]+TOL})
   backing.append({'name':'useful_cubby_continuous_actual_walnut_backing','physical_parts':shellnames,'material_roles':[so[x]['properties']['material_role']for x in shellnames],'proofs':proofs,'method':'Project actual convex walnut shell solids onto XZ, extrude that projection only for 2D set subtraction, and subtract their full union from the entire cubby width/height rectangle. Zero residual proves a material backing on every Y-directed line through the useful cross-section; actual depths are independently required to remain behind the declared empty space. No sample-ray-only backing claim.','pass':all(x['pass']for x in proofs)and all(so[x]['properties']['material_role']=='warm_walnut'for x in shellnames)})
   bottomproofs=[]
   for frame,tr,lab in [('source',tri,labels),('native',nt,nlabels)]:
    floortri=tr[lab=='open_programme_cubby_floor'];z=float(floortri[:,:,2].max());xleft=float(tr[lab=='counter_central_divider'][:,:,0].max());xright=float(tr[lab=='right_full_height_cheek'][:,:,0].min());rear=float(floortri[:,:,1].max());tops=floortri[np.max(np.abs(floortri[:,:,2]-z),axis=1)<TOL];floor_hulls=[Hull(np.vstack([t-[0,0,.001],t+[0,0,.001]]))for t in tops];sections=[]
    for name in shellnames:
     vs=np.unique(tr[lab==name].reshape(-1,3),axis=0);xmin=float(vs[:,0].min());xmax=float(vs[:,0].max());a=max(xmin,xleft);b=min(xmax,xright)
     if b-a<=TOL:continue
     ymin=float(vs[np.abs(vs[:,0]-xmin)<TOL,1].max());ymax=float(vs[np.abs(vs[:,0]-xmax)<TOL,1].max());ya=ymin+(ymax-ymin)*(a-xmin)/(xmax-xmin);yb=ymin+(ymax-ymin)*(b-xmin)/(xmax-xmin);p=np.array([a,ya,z]);q=np.array([b,yb,z]);pa=np.array([a,rear,z]);qb=np.array([b,rear,z]);target=np.array([[p,q,qb],[p,qb,pa]]);uncovered=sum(triangle_uncovered_area(t,floor_hulls)for t in target);needed=(b-a)*(rear-(ya+yb)/2);seam_intervals=sorted(h.segment(p,q)for h in floor_hulls if h.segment(p,q)is not None);covered=0.;gap=0.
     for l,h in seam_intervals:gap=max(gap,l-covered);covered=max(covered,h)
     gap=max(gap,1-covered);sections.append({'shell_part':name,'front_seam_source_m':[p.tolist(),q.tolist()],'required_floor_area_m2':float(needed),'uncovered_bottom_area_m2':float(uncovered),'maximum_front_seam_fraction_gap':float(gap),'pass':uncovered<1e-8 and gap<TOL})
    xspan=sum(x['front_seam_source_m'][1][0]-x['front_seam_source_m'][0][0]for x in sections);bottomproofs.append({'frame':frame,'actual_container_sides_x_m':[xleft,xright],'floor_top_z_m':z,'floor_rear_y_m':rear,'required_bottom_area_m2':sum(x['required_floor_area_m2']for x in sections),'uncovered_bottom_area_m2':sum(x['uncovered_bottom_area_m2']for x in sections),'sections':sections,'pass':all(x['pass']for x in sections)and abs(xspan-(xright-xleft))<TOL})
   backing.append({'name':'whole_cubby_bottom_to_curved_walnut_backing','proofs':bottomproofs,'method':'Derive each actual walnut shell inner edge at the measured floor height, clip to actual divider/right-cheek inner planes, and require continuous floor-top triangle coverage of every full plan strip from that edge to the actual staff-side shelf edge. Verify the complete curved front seam by union of exact segment/triangle-prism intervals. This tests the bottom behind the declared useful box as well as the box itself.','area_tolerance_m2':1e-8,'pass':all(x['pass']for x in bottomproofs)})
   internal=['open_programme_cubby_floor','drawer_separation_shelf','left_fixed_slide_bearing','right_fixed_slide_bearing','left_drawer_slide','right_drawer_slide','drawer_tray_floor','drawer_left_wall','drawer_right_wall','drawer_inner_back'];partchecks=[];profiles={}
   for frame,tr,lab in [('source',tri,labels),('native_closed',nt,nlabels),('native_access',state['access'][1],nlabels_access)]:
    profile=[]
    for name in shellnames:
     v=np.unique(tr[lab==name].reshape(-1,3),axis=0);a=float(v[:,0].min());b=float(v[:,0].max());ya=float(v[np.abs(v[:,0]-a)<TOL,1].max());yb=float(v[np.abs(v[:,0]-b)<TOL,1].max());slope=(yb-ya)/(b-a);profile.append({'part':name,'x_interval_m':[a,b],'inner_y_line':[slope,ya-slope*a]})
    profiles[frame]=profile
    for name in internal:partchecks.append({'frame':frame,'physical_part':name,**nesting_check(tr[lab==name],profile)})
   # Deliberately over-deep former rectangular separator demonstrates complete-tab detection.
   testh=Hull(corners([-.19,-.29,.655],[.665,.28,.683]));control=nesting_check(testh.tris,profiles['source']);control['expected_failure_detected']=not control['pass']
   excluded={x:('deliberate public artwork/inset and its carrier'if x.startswith(('usher_mark_','original_usher_','low_public_','amber_insert_'))else 'staff-side moving fascia or grip; complete motion already checked'if x.startswith(('drawer_walnut_fascia','drawer_pull_boss','drawer_brass_pull'))else 'outer structural support, enclosing shell, counter or floor plinth; reviewed as physical construction')for x in sourceparts if x not in internal}
   nesting.append({'name':'all_internal_storage_parts_within_actual_curved_front','covered_parts':internal,'explicit_exclusions':excluded,'actual_piecewise_inner_shell_profiles':profiles,'complete_triangle_checks':partchecks,'overdeep_rectangular_separator_positive_control':control,'continuous_motion_basis':'Every moving interior part is rigidly translated in positive source Y with fixed X/Z. Every tested inner-boundary signed clearance therefore increases linearly over the full motion, so the exact closed minimum is the continuous minimum; actual terminal native access geometry is checked separately.','method':'Clip every complete actual triangle by every local shell X interval and evaluate every resulting polygon vertex against that actual inward wall halfspace. Affine extrema occur at clipped polygon vertices; no sampled rays or global enclosing hull replace the piecewise profile.','pass':all(x['pass']for x in partchecks)and control['expected_failure_detected']})
   outerchecks=[];dividerchecks=[];outerprofiles={};staffparts=['drawer_walnut_fascia','drawer_pull_boss_0.145','drawer_pull_boss_0.325','drawer_brass_pull'];outerparts=internal+staffparts+['counter_central_divider']
   for frame,tr,lab in [('source',tri,labels),('native_closed',nt,nlabels),('native_access',state['access'][1],nlabels_access)]:
    profile=[]
    for name in shellnames:
     v=np.unique(tr[lab==name].reshape(-1,3),axis=0);a=float(v[:,0].min());b=float(v[:,0].max());ya=float(v[np.abs(v[:,0]-a)<TOL,1].min());yb=float(v[np.abs(v[:,0]-b)<TOL,1].min());slope=(yb-ya)/(b-a);profile.append({'part':name,'x_interval_m':[a,b],'inner_y_line':[slope,ya-slope*a],'boundary':'actual outer public-facing shell face'})
    outerprofiles[frame]=profile
    for name in outerparts:outerchecks.append({'frame':frame,'physical_part':name,**nesting_check(tr[lab==name],profile)})
    dtri=tr[lab=='counter_central_divider'];inner=nesting_check(dtri,profiles[frame]);outer=nesting_check(dtri,profile);dh,unused=convex_parts(dtri);contacts=[]
    for name in shellnames:
     sh,unused=convex_parts(tr[lab==name])
     for a in dh:
      for b in sh:
       if ((a.lo>b.hi+TOL)|(a.hi<b.lo-TOL)).any():continue
       hit=continuous_overlap(a,b,np.zeros(3))
       if hit['material_intrusion']:contacts.append({'shell_part':name,**hit})
    dividerchecks.append({'frame':frame,'classification':'intentional fixed buried structural bearing; penetrates inner shell boundary while remaining behind every outer public face','inner_boundary':inner,'outer_boundary':outer,'maximum_buried_source_y_depth_m':max(0.,-inner['minimum_source_y_clearance_m']),'maximum_buried_normal_depth_m':max(0.,-inner['minimum_inward_normal_clearance_m']),'minimum_material_cover_source_y_m':outer['minimum_source_y_clearance_m'],'minimum_material_cover_normal_m':outer['minimum_inward_normal_clearance_m'],'actual_shared_solid_bearings':contacts,'pass':inner['all_vertices_inside_tested_profile_width']and not inner['pass']and outer['pass']and bool(contacts)})
   remaining_exclusions={k:v for k,v in excluded.items()if k not in staffparts+['counter_central_divider']}
   public_envelope.append({'name':'all_storage_divider_and_staff_parts_behind_actual_public_faces','covered_parts':outerparts,'actual_piecewise_outer_shell_profiles':outerprofiles,'complete_triangle_checks':outerchecks,'intentional_buried_divider_bearing':dividerchecks,'remaining_explicit_exclusions':remaining_exclusions,'continuous_motion_basis':'Source +Y travel increases every local public-boundary clearance with X unchanged. Complete closed-state extrema therefore bound the full motion; actual access exports are independently checked.','method':'The same complete local-X triangle clipping proof is applied to actual outer shell faces. Divider inner-boundary penetration is measured separately and confirmed as actual fixed-solid bearing, rather than silently excluded as a generic exception.','pass':all(x['pass']for x in outerchecks+dividerchecks)})
  # Actual occupied floor slab: one crossed surface and one fully enclosed cube test both branches.
  floor=next(x['physical_part']for x in m['physical_and_proposal_markers']if x['name']=='FLOOR_CONTACT');p=np.array([0.,0.,-.01]);q=np.array([0.,0.,.04]);floorcontrol={'source_surface_crossing_detected':bool(segment_triangles(p,q,tri[labels==floor])),'native_surface_crossing_detected':bool(segment_triangles(p,q,ntris(floor))),'source_containment_detected':not empty_box(tri,labels,[-.001,-.001,.02],[.001,.001,.03])['pass'],'native_containment_detected':not empty_box(nt,nlabels,[-.001,-.001,.02],[.001,.001,.03])['pass']}
  for name,rows in [('markers',markers),('joins',joins),('voids',voids),('motions',movements),('native ownership',native_ownership),('rays',probes),('access derivatives',derivatives),('cubby backing',backing),('internal front nesting',nesting),('whole public front envelope',public_envelope)]:
   failed=[x.get('name',x.get('root',x.get('part',x.get('void',x.get('state')))))for x in rows if not x['pass']]
   if failed:failures.append(name+': '+', '.join(sorted(set(failed))))
  if not all(floorcontrol.values()):failures.append('Actual floor positive controls')
  unchanged=all(sha(p)==inputbindings[k]['sha256']for k,p in inputpaths)
  if not unchanged:failures.append('Inputs changed during review')
  if not metadata_consistent:failures.append('Marker API or collision void/motion metadata differs from asset manifest')
  r={'catalogue_id':ident,'passed':not failures,'input_bindings_current':current,'failures':failures,'bindings':inputbindings,'inputs_unchanged_during_review':unchanged,'manifest_marker_collision_metadata_consistent':metadata_consistent,'actual_native_access_derivatives':derivatives,'continuous_useful_cubby_backing':backing,'complete_internal_storage_nesting':nesting,'complete_public_front_envelope':public_envelope,'native_semantic_ownership':native_ownership,'physical_and_proposal_markers':markers,'physical_join_witnesses':joins,'complete_useful_voids':voids,'complete_linear_motions':movements,'clear_ray_supplement':probes,'actual_occupied_geometry_positive_controls':floorcontrol,'numeric_tolerance_m':TOL,'methods':{'voids':'Every actual source and native triangle versus complete box by separating axes, plus closed-solid midpoint containment. Full box checked; 0.2 micrometre inward inset classifies boundary contact only. Supplemental rays never substitute for volume tests.','motion':'Actual closed convex semantic solids or exact axial cap-prism decomposition. Linear programming maximizes shared interior radius with every fixed convex piece across continuous t in [0,1], including t=0 and the first millimetre; zero-radius support contact distinguished from material intrusion. Native actual hierarchy ownership and exact per-triangle correspondence bind the same complete translation proof to export.'},'limits':['Component geometry only; no host placement, room adjacency, audience route, species or cart fit, engine/collision implementation, ergonomics, mechanism, load or certification acceptance.','Panel removal requires the declared tool release and hand support. Translation geometry does not model that operation or an actor holding the panel.','Actual access GLBs are independently matched to complete transformations of the closed source hierarchy. They are geometric terminal states, not implemented runtime animations.','Supports, finish collisions, UVs, source-only rebuild, and visual imported captures are independently reviewed elsewhere.','Numerical tolerance is0.0000002m; continuous proof is limited to declared rigid +Y translations and these exact hashes.']}
  results.append(r);print(ident,'PASS',r['passed'],'FAILURES',r['failures'],flush=True)
  (OUT/f'independent_arrival_access_{ident}.json').write_text(json.dumps(r,indent=2,default=json_default)+'\n')
 receipt={'passed':all(r['passed']for r in results),'assets':results,'reviewer_scope':'Physical markers/normals/opposing joins, complete source/native useful voids and service reservations, continuous true-closed removal/drawer translation, native ownership. No captures.','executed_script_sha256':sha(Path(__file__)),'helper_bindings':[bind(ROOT/p)for p in ['qa/batch07/independent_geometry.py','qa/inspect_glb_independent.py','qa/batch08/independent_collision_geometry.py','qa/batch12/independent_void_geometry.py','qa/batch15/independent_contact_graph.py']]}
 (OUT/'independent_arrival_access_review.json').write_text(json.dumps(receipt,indent=2,default=json_default)+'\n')
if __name__=='__main__':main()
