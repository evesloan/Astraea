"""Independent Batch18 work-component geometry checks; consumes source cache, never author QA.
Writes only work_review_* receipts. No render, production mutation or author helper import.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.dont_write_bytecode=True
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'qa/batch18'; BASE=ROOT/'assets/retail_work'
sys.path.insert(0,str(ROOT/'qa/batch08'))
from independent_collision_geometry import Hull,nearest_distances,sample_triangles,triangle_uncovered_area
sys.path.insert(0,str(ROOT/'qa/batch15'))
from independent_contact_graph import normal_witness,contact_graph
sys.path.insert(0,str(ROOT/'qa/batch07'))
from independent_geometry import Native,C
TOL=2e-5
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def conv(t):return Hull(np.unique(np.round(np.asarray(t).reshape(-1,3),9),axis=0))
def compact_planes(p):return np.unique(np.round(p,10),axis=0)
def overlap(a,b):
 """Positive-volume intersection of actual convex parts, not AABB overlap."""
 if ((a.lo>b.hi+1e-7)|(b.lo>a.hi+1e-7)).any():return None
 p=compact_planes(np.concatenate([a.planes,b.planes]));r=linprog([0,0,0,-1],A_ub=np.column_stack([p[:,:3],np.ones(len(p))]),b_ub=-p[:,3],bounds=[(None,None)]*4,method='highs')
 if not r.success:raise RuntimeError(r.message)
 return {'interior_radius_m':float(r.x[3]),'point_source_m':r.x[:3].tolist(),'positive_volume':bool(r.x[3]>1e-6)}
def box_hull(lo,hi):return Hull(np.asarray(list(itertools.product(*zip(lo,hi)))))
def shifted(h,p):return Hull(h.points+np.asarray(p))
def volume(t):return abs(float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6))
def check_normal(p,t,n):
 d=float(nearest_distances([p],t)[0]);r=normal_witness(p,t,n);r.update(distance_m=d,pass_=d<TOL and r['pass']);r['pass']=r.pop('pass_');return r
def serial(x):
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,np.ndarray):return x.tolist()
 raise TypeError(type(x).__name__)
def part_groups(m):return {p['name']:p['motion_group']for p in m['parts']}
def active_states(m):return m['details'].get('states') or {'closed':{'fixed':[0,0,0],'lid':[0,0,0],'carrier':[0,0,0]}}
def pshift(states,state,group):return np.asarray(states[state].get(group,[0,0,0]))
def mesh_normals(t):
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return n/np.maximum(np.linalg.norm(n,axis=1),1e-25)[:,None]
def verify_asset(ident):
 mp=BASE/(ident+'.manifest.json');m=json.loads(mp.read_text());audit=OUT/('independent_source_'+ident+'.json');s=json.loads(audit.read_text());source=ROOT/s['path']
 assert sha(source)==s['sha256']==m['source_sha256'],'Source cache or author manifest is stale'
 assert sha(BASE/m['export'])==m['glb_sha256'],'Export manifest is stale'
 cache=ROOT/s['geometry_cache'];npz=np.load(cache);tri=npz['triangles'];labels=npz['object_names'];names=sorted(np.unique(labels));parts={str(n):tri[labels==n]for n in names};hulls={n:conv(t)for n,t in parts.items()};groups=part_groups(m);states=active_states(m)
 collfile=BASE/m['collision_proposal_file'];coll=json.loads(collfile.read_text())[ident];detail={r['name']:Hull(r['points_source_m'],r)for r in coll['precise_reference']};retained=coll['optional_body_candidate']['retained_shape_names'];body={n:detail[n]for n in retained}
 checks={};solid=[]
 for n,t in parts.items():
  h=hulls[n];v=volume(t);e=abs(v-h.hull.volume);es=np.round(t[:,[[0,1],[1,2],[2,0]]].reshape(-1,2,3),8);es=np.sort(es,axis=1) if False else np.asarray([sorted(x.tolist())for x in es]);_,counts=np.unique(es,axis=0,return_counts=True)
  norm=mesh_normals(t);face_violation=float(max(np.max((h.points-tt[0])@nn)for tt,nn in zip(t,norm)))
  solid.append({'part':n,'maximum_outward_face_halfspace_violation_m':face_violation,'mesh_signed_absolute_volume_m3':v,'hull_volume_m3':float(h.hull.volume),'volume_difference_m3':e,'all_edges_have_two_faces':bool((counts==2).all()),'pass':bool(e<1e-8 and face_violation<1e-7 and (counts==2).all())})
 checks['convex_actual_source_solids']={'parts':solid,'passed':all(r['pass']for r in solid),'method':'Closed oriented source triangles must equal their exact vertex convex hull volume; hull is then usable for continuous containment/intersection, not an enclosing approximation of an opening'}
 # All declared joins require actual two-sided contact at the declared point.
 joins=[]
 for j in m['joins']:
  p=np.asarray(j['probe_source_m']);a,b=j['parts'];da=float(nearest_distances([p],parts[a])[0]);db=float(nearest_distances([p],parts[b])[0]);na=mesh_normals(parts[a]);nb=mesh_normals(parts[b]);nearA=np.asarray([nearest_distances([p],[t])[0]for t in parts[a]])<TOL;nearB=np.asarray([nearest_distances([p],[t])[0]for t in parts[b]])<TOL
  dot=float((na[nearA]@nb[nearB].T).min())if nearA.any()and nearB.any()else None
  joins.append({'name':j['name'],'parts':[a,b],'point_source_m':p,'part_distances_m':[da,db],'best_opposing_normal_dot':dot,'pass':bool(max(da,db)<TOL and dot is not None and dot<-.999)})
 checks['declared_join_witnesses']={'joins':joins,'passed':all(r['pass']for r in joins)}
 roots=[n for n,t in parts.items()if abs(t[:,:,2].min())<TOL]
 checks['actual_contact_connectivity']=contact_graph(tri,labels,roots)
 # Source physical markers + native marker transforms and actual grouped surfaces per state.
 native_paths={'closed':BASE/m['export']};native_paths.update({r['state']:BASE/r['export']for r in m['state_derivatives']});natives={state:Native(p)for state,p in native_paths.items()}
 marks=[];roles={p['name']:p['material_role']for p in m['parts']}
 for mark in m['physical_and_proposal_markers']:
  if not mark['physical_part']:continue
  p=np.asarray(mark['source_m']);name=mark['physical_part'];row={'name':mark['name'],'part':name,'source':check_normal(p,parts[name],mark['normal_source']),'native_states':[]}
  for state,native in natives.items():
   pos=p+pshift(states,state,mark['motion_group']);pn=pos@C.T;nn=np.asarray(mark['normal_source'])@C.T;selected=native.select(role=roles[name],node='__'+mark['motion_group']+'__');actual=check_normal(pn,native.tris[selected],nn)
   idx=next(i for i,n in enumerate(native.g.doc['nodes'])if n.get('name')==mark['name']);actual_node=native.world[idx][:3,3];err=float(np.linalg.norm(actual_node-pn));actual.update(state=state,actual_node_position_gltf_m=actual_node,expected_position_gltf_m=pn,marker_position_error_m=err);actual['pass']&=err<TOL;row['native_states'].append(actual)
  row['pass']=row['source']['pass']and all(r['pass']for r in row['native_states']);marks.append(row)
 checks['physical_markers']={'markers':marks,'passed':all(r['pass']for r in marks)}
 patches=[]
 for patch in m['support_patches']:
  p=np.asarray(patch['polygon_source_m']);n=np.asarray(patch['normal_source']);part=patch['physical_part'];polyvec=np.sum(np.cross(p,np.roll(p,-1,axis=0)),axis=0);wind=float(polyvec@n/max(np.linalg.norm(polyvec),1e-30));samples=np.concatenate([p,(p+np.roll(p,-1,axis=0))/2,p.mean(0)[None,:]]);w=[check_normal(x,parts[part],n)for x in samples];contained=hulls[part].inside(p,tol=TOL)
  patches.append({'name':patch['name'],'part':part,'polygon_area_m2':float(np.linalg.norm(polyvec)/2),'winding_normal_cosine':wind,'whole_convex_polygon_contained_in_actual_support':bool(contained.all()),'surface_witness_count':len(w),'max_distance_m':max(r['distance_m']for r in w),'pass':bool(contained.all()and wind>.999 and all(r['pass']for r in w))})
 checks['physical_support_patches']={'patches':patches,'passed':all(r['pass']for r in patches),'method':'Every polygon vertex lies within the actual convex support; same-plane normal and distance at vertices, edge midpoints and centre establish entire convex patch surface, including winding'}
 # Voids are tested as full convex volumes against every actual convex part and both collision sets.
 voids=[];alias={'open':'open_lid_parked'}
 for v in m['receiver_voids']:
  stated=v['valid_states'];group=v.get('motion_group','fixed');valid=[alias.get(x,x)for x in stated if alias.get(x,x)in states]
  for state in valid:
   off=pshift(states,state,group);vh=box_hull(np.asarray(v['min_source_m'])+off,np.asarray(v['max_source_m'])+off);row={'name':v['name'],'state':state,'motion_group':group,'dimensions_m':vh.hi-vh.lo,'representations':{}}
   for rep,data in [('actual_source',hulls),('detailed',detail),('literal_optional_body',body)]:
    hits=[]
    for name,h in data.items():
     test=overlap(vh,shifted(h,pshift(states,state,groups[name])))
     if test and test['positive_volume']:hits.append({'part':name,**test})
    # Real blocked negative control: duplicate test volume deliberately surrounds an actual retained part centre.
    centre=next(iter(body.values())).points.mean(0);rad=np.minimum((vh.hi-vh.lo)/2,.003);neg=box_hull(centre-rad,centre+rad);negtest=overlap(neg,next(iter(data.values())))
    # Named first part order varies; search all rather than assuming coincident list order.
    negparts=[name for name,h in data.items()if (lambda x:x and x['positive_volume'])(overlap(neg,h))]
    row['representations'][rep]={'intersecting_parts':hits,'blocked_negative_control_parts':negparts,'pass':not hits and bool(negparts)}
   row['pass']=all(x['pass']for x in row['representations'].values());voids.append(row)
 checks['whole_void_volumes']={'voids':voids,'passed':all(r['pass']for r in voids)and all(v.get('motion_group')in set(groups.values())and set(v['valid_states'])<=set(states)for v in m['receiver_voids']),'method':'Convex halfspace intersection maximizes inscribed radius; actual named meshes verified convex first. AABB rejects disjoint pairs only. Positive-volume negative controls placed within real source/detailed/body geometry.'}
 # The bench stock openings must connect their useful inner volumes to the rear approach.
 if ident=='AST-RTL-003':
  access=[]
  for v in m['receiver_voids']:
   if v['name']not in ['upper_paper_stock_access','lower_paper_stock_access','staff_stock_access']:continue
   lo=np.asarray(v['min_source_m']);hi=np.asarray(v['max_source_m']);hi[1]=.65;vh=box_hull(lo,hi);hits=[]
   for n,h in hulls.items():
    q=overlap(vh,h)
    if q and q['positive_volume']:hits.append({'part':n,**q})
   # A deliberately lowered sweep penetrates the actual shelf, showing the same volume test detects obstruction.
   ztop=lo[2]-.010;badlo=lo.copy();badhi=hi.copy();badlo[2]=ztop-.002;badhi[2]=ztop+.002;bad=box_hull(badlo,badhi);blocked=[]
   for n,h in hulls.items():
    q=overlap(bad,h)
    if q and q['positive_volume']:blocked.append(n)
   access.append({'name':v['name'],'rear_access_volume_min_source_m':lo,'rear_access_volume_max_source_m':hi,'intersections':hits,'lowered_negative_control_intersections':blocked,'pass':not hits and bool(blocked)})
  checks['bench_rear_stock_retrieval']={'volumes':access,'passed':all(r['pass']for r in access),'scope':'Geometric empty access volumes connect shelves to rear Y0.65m; no hand, species, load or room-route claim'}
 # Detailed semantic compounds cover every source triangle continuously; body is literal subset.
 coverage=[]
 for n,t in parts.items():
  uncovered=sum(triangle_uncovered_area(x,[detail[n]])for x in t);coverage.append({'part':n,'uncovered_surface_area_m2':uncovered,'pass':uncovered<1e-9})
 omitted=[];bodytris=np.concatenate([h.tris for h in body.values()]);spacing=.008
 for n in coll['optional_body_candidate']['omitted_shape_names']:
  pts,step=sample_triangles(parts[n],spacing=spacing);d=nearest_distances(pts,bodytris)
  for h in body.values():d[h.inside(pts)]=0
  verts=np.unique(parts[n].reshape(-1,3),axis=0);upper=[]
  for backing,h in body.items():
   vd=nearest_distances(verts,h.tris);vd[h.inside(verts)]=0;upper.append((float(vd.max()),backing))
  tight,backing=min(upper)
  omitted.append({'part':n,'certified_upper_bound_supporting_body_part':backing,'sample_count':len(pts),'surface_sample_max_spacing_m':step,'sampled_max_distance_to_body_union_m':float(d.max()),'certified_upper_bound_m':tight,'sample_grid_lipschitz_upper_bound_m':float(d.max()+step),'farthest_sample_source_m':pts[d.argmax()],'interpretation':'Euclidean source-surface distance to retained body solid union; Sampled maximum is a lower bound. For each retained convex hull, maximum vertex distance bounds the entire convex omitted part by convexity of distance; the minimum such bound certifies distance to the retained union. The independently reported sample-grid Lipschitz bound is looser. This is not material thickness.'})
 literal=set(retained)=={r['name']for r in coll['precise_reference']if r['body_candidate_retained']}and set(detail)==set(parts)and not coll['optional_body_candidate']['new_enclosing_hulls']
 checks['collision_proposals']={'detailed_shape_count':len(detail),'optional_body_shape_count':len(body),'literal_subset_verified':literal,'per_part_continuous_coverage':coverage,'omitted_details':omitted,'passed':literal and all(r['pass']for r in coverage)}
 if ident=='AST-RTL-004':
  # Recover inward-facing shell planes from actual source triangles, not metadata polygon.
  shell=np.concatenate([t for n,t in parts.items()if n.startswith('case_faceted_shell_')]);ns=mesh_normals(shell);p=[]
  for t,n in zip(shell,ns):
   if abs(n[2])<1e-7 and n@t[0]<-.01:
    probe=t.mean(0)+n*.0001
    if not any(h.inside([probe],tol=1e-7)[0]for name,h in hulls.items()if name.startswith('case_faceted_shell_')):p.append(np.r_[-n,n@t[0]])
  cavity=compact_planes(np.asarray(p));profile=[]
  for n,t in parts.items():
   if groups[n]!='carrier'and not n.startswith('lid_recessed_locator_'):continue
   pts=np.unique(t.reshape(-1,3),axis=0);margin=-(pts@cavity[:,:3].T+cavity[:,3]);profile.append({'part':n,'actual_vertex_count':len(pts),'minimum_actual_shell_side_clearance_m':float(margin.min()),'all_vertices_within_full_profile':bool((margin>=-TOL).all()),'pass':bool((margin>=-TOL).all())})
  # Known AABB false-positive point lies within rectangular bounds and beyond actual corner plane.
  shellpts=shell.reshape(-1,3);xymins=np.array([-.214,-.149]);xymaxs=-xymins;bad=np.array([.212,.147,.16]);viol=float((bad@cavity[:,:3].T+cavity[:,3]).max());negative=bool(((bad[:2]>=xymins)&(bad[:2]<=xymaxs)).all()and viol>.001)
  checks['whole_nested_profile']={'recovered_actual_inner_planes':cavity,'plane_count':len(cavity),'parts':profile,'carrier_and_locator_vertical_bounds_source_m':{n:[float(t[:,:,2].min()),float(t[:,:,2].max())]for n,t in parts.items()if groups[n]=='carrier'or n.startswith('lid_recessed_locator_')},'negative_control':{'point_source_m':bad,'inside_simple_inner_AABB':True,'actual_corner_violation_m':viol,'rejected':negative},'passed':len(cavity)==8 and negative and all(r['pass']for r in profile),'method':'Eight actual inward-facing source shell planes form convex cavity; buried segment-end faces are excluded only when their outward centroid probe enters an adjacent actual shell solid. Every evaluated carrier and locator vertex satisfies every plane; linearity proves all edges, triangles and contained solids, not only centres or bounding boxes. Lid cap intentionally covers shell rim rather than fitting within cavity.'}
  moves=[]
  for owner in ['lid','carrier']:
   path=m['details']['manual_path'][owner]['waypoints'];moving=[n for n in parts if groups[n]==owner];fixed=[n for n in parts if groups[n]!=owner];otherpose=states['open_lid_parked']if owner=='carrier'else states['closed']
   for leg,(start,end)in enumerate(zip(path,path[1:])):
    hits=[];touch=[]
    for a in moving:
     sweep=Hull(np.concatenate([hulls[a].points+np.asarray(start),hulls[a].points+np.asarray(end)]))
     for b in fixed:
      test=overlap(sweep,shifted(hulls[b],np.asarray(otherpose.get(groups[b],[0,0,0]))))
      if test:
       if test['positive_volume']:hits.append({'moving_part':a,'static_part':b,**test})
       elif abs(test['interior_radius_m'])<2e-6:touch.append({'moving_part':a,'static_part':b,'radius_m':test['interior_radius_m']})
    moves.append({'owner':owner,'leg':leg,'start_source_m':start,'end_source_m':end,'positive_volume_collisions':hits,'boundary_contacts':touch,'pass':not hits})
  checks['manual_detached_handling_sweeps']={'legs':moves,'passed':all(r['pass']for r in moves),'method':'For each convex named part and straight translation leg, convex hull of endpoint copies is the exact continuous swept solid. Positive-volume intersection tested against each stationary actual part. Starts at true closed/seated state. No retained-joint claim.'}
  parked=[]
  for state in ['open_lid_parked','handling']:
   lidtri=np.concatenate([t+pshift(states,state,'lid')for n,t in parts.items()if groups[n]=='lid']);bottom=float(lidtri[:,:,2].min());parked.append({'state':state,'lid_minimum_z_m':bottom,'actual_downward_face_count_at_support_datum':int(sum(abs(t[:,2].max())<TOL and n[2]<-.999 for t,n in zip(lidtri,mesh_normals(lidtri)))),'carrier_support_status':'Seated on exact bearings'if state=='open_lid_parked'else'Detached and externally held, intentionally no support claim','pass':abs(bottom)<TOL})
  checks['detached_state_support']={'states':parked,'passed':all(r['pass']for r in parked)}
 # Geometry state exports must exactly match transformed source vertices per ownership/material.
 derivatives=[]
 for state,native in natives.items():
  errs=[]
  for group in sorted(set(groups.values())):
   for role in sorted(set(roles.values())):
    chunks=[t+pshift(states,state,group)for n,t in parts.items()if groups[n]==group and roles[n]==role]
    if not chunks:continue
    a=np.concatenate(chunks).reshape(-1,3);b=(native.tris[native.select(role=role,node='__'+group+'__')]@C).reshape(-1,3);d=max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max());errs.append({'group':group,'role':role,'vertex_hausdorff_m':float(d)})
  derivatives.append({'state':state,'export':str(native_paths[state].relative_to(ROOT)),'sha256':sha(native_paths[state]),'groups':errs,'pass':all(r['vertex_hausdorff_m']<TOL for r in errs)})
 checks['actual_native_states']={'states':derivatives,'passed':all(r['pass']for r in derivatives)}
 passed=all(v.get('passed',False)for v in checks.values());inputs=[source,mp,cache,audit,collfile,BASE/'marker_api.json',BASE/m['generator']]+list(native_paths.values())
 report={'catalogue_id':ident,'passed':passed,'executed_script_sha256':sha(Path(__file__)),'input_bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in inputs],'checks':checks,'limits':['Geometric component proposals only; no host/shop/activity-slot/door adoption or transaction behavior.','No universal body/species/reach/hand fit, load, forces, mechanical retention, runtime implementation or engine performance acceptance.','Native state checks verify exported positions by ownership/material and physical marker surfaces; main reviewer handles full corner/material/export/source-only/preservation audits.']}
 (OUT/('work_review_'+ident+'.json')).write_text(json.dumps(report,indent=2,default=serial)+'\n');print(ident,passed,{k:v['passed']for k,v in checks.items()},flush=True)
 return report
if __name__=='__main__':
 result=[verify_asset(i)for i in (sys.argv[1:]or ['AST-RTL-003','AST-RTL-004'])]
 helpers=[ROOT/'qa/batch08/independent_collision_geometry.py',ROOT/'qa/batch15/independent_contact_graph.py',ROOT/'qa/batch07/independent_geometry.py',ROOT/'qa/inspect_glb_independent.py']
 summary={'passed':all(r['passed']for r in result),'reports':[{'catalogue_id':r['catalogue_id'],'passed':r['passed'],'receipt':'qa/batch18/work_review_'+r['catalogue_id']+'.json'}for r in result],'executed_script_sha256':sha(Path(__file__)),'read_only_helper_bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in helpers]}
 (OUT/'work_review_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
