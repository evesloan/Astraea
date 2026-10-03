"""Independent complete use/motion/interface review; source/native inputs read only.

The rotations are certified with conservative exact sinusoidal projection bounds
over closed angle intervals, not inferred from a finite pose grid. Convex hulls
here enclose independently evaluated semantic part triangles; no author helper is
imported. A hull separation therefore safely proves visual separation even before
the recorded source convex-equivalence check. Near-zero boundary contact is
reported separately from interior intrusion.
"""
from pathlib import Path
import sys,json,hashlib,itertools,math
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch17';BASE=ROOT/'assets/housekeeping_equipment'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances,inside_mesh,segment_triangles,Hull
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import normal_witness

TOL=2e-7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def cloud(t):return np.unique(np.asarray(t).reshape(-1,3),axis=0)
def equal(a,b):
 a=cloud(a);b=cloud(b)
 return float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max()))
def rotation_matrix(axis,angle):
 d=np.asarray(axis,float);d/=np.linalg.norm(d);x,y,z=d;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);a=math.radians(angle);return np.eye(3)+math.sin(a)*K+(1-math.cos(a))*(K@K)
def pose(v,rec,fraction):
 if rec['kind']=='translation':return np.asarray(v)+np.asarray(rec['axis_source'])*rec['travel']*fraction
 p=np.array(rec['pivot_source_m']);return (np.asarray(v)-p)@rotation_matrix(rec['axis_source'],rec['travel']*fraction).T+p
def unit_axes(a):
 a=np.asarray(a).reshape(-1,3);n=np.linalg.norm(a,axis=1);a=a[n>1e-10]/n[n>1e-10,None]
 return np.unique(np.round(a,12),axis=0)
def axes_for(a,b):
 ha=ConvexHull(a);hb=ConvexHull(b)
 return unit_axes(np.concatenate([np.eye(3),ha.equations[:,:3],hb.equations[:,:3]]))
def interval_projection(v,p,axes,angle0,angle1,axis):
 v=np.asarray(v)-p;d=np.asarray(axis,float);d/=np.linalg.norm(d);a,b=sorted(np.deg2rad([angle0,angle1]));axes=np.asarray(axes)
 parallel=np.outer(v@d,d);const=(parallel+p)@axes.T;co=(v-parallel)@axes.T;si=np.cross(d,v)@axes.T
 v0=const+co*np.cos(a)+si*np.sin(a);v1=const+co*np.cos(b)+si*np.sin(b);lo=np.minimum(v0,v1);hi=np.maximum(v0,v1);base=np.arctan2(si,co)
 for k in range(-3,4):
  th=base+k*np.pi;ok=(th>=a)&(th<=b);val=const+co*np.cos(th)+si*np.sin(th);lo=np.where(ok,np.minimum(lo,val),lo);hi=np.where(ok,np.maximum(hi,val),hi)
 return lo.min(0),hi.max(0)
def overlap_radius(a,b):
 """Positive common inscribed radius means true 3D interior intrusion."""
 ha=ConvexHull(a);hb=ConvexHull(b);eq=np.concatenate([ha.equations,hb.equations]);aa=np.column_stack([eq[:,:3],np.ones(len(eq))])
 res=linprog([0,0,0,-1],A_ub=aa,b_ub=-eq[:,3],bounds=[(None,None)]*3+[(None,None)],method='highs')
 return {'common_interior_radius_m':float(res.x[3]),'witness_source_m':res.x[:3].tolist()}if res.success else {'common_interior_radius_m':None,'solver':res.message}
def static_pair(a,b):
 axes=axes_for(a,b);ap=a@axes.T;bp=b@axes.T;g=np.maximum(ap.min(0)-bp.max(0),bp.min(0)-ap.max(0));ix=int(g.argmax())
 if g[ix]>=-TOL:return {'pass':True,'separation_axis':axes[ix].tolist(),'minimum_gap_m':float(g[ix]),'classification':'separated'if g[ix]>TOL else'boundary_or_roundoff_only'}
 ov=overlap_radius(a,b);r=ov['common_interior_radius_m'];return {'pass':r is not None and r<=TOL,**ov,'classification':'interior_intrusion'if r is not None and r>TOL else'boundary_or_roundoff_only'}
def rotation_pair(a,b,rec,max_depth=22):
 p=np.asarray(rec['pivot_source_m']);travel=rec['travel'];leaves=[];bad=[]
 def check(f0,f1,depth):
  aa=pose(a,rec,(f0+f1)/2);axes=axes_for(aa,b);lo,hi=interval_projection(a,p,axes,travel*f0,travel*f1,rec['axis_source']);bp=b@axes.T;g=np.maximum(lo-bp.max(0),bp.min(0)-hi);ix=int(g.argmax())
  if g[ix]>=-TOL:
   leaves.append({'fraction_interval':[f0,f1],'constant_separation_axis':axes[ix].tolist(),'minimum_gap_over_entire_interval_m':float(g[ix]),'classification':'separated'if g[ix]>TOL else'boundary_or_roundoff_only'});return
  # A positive-volume witness at an actual pose is a failure, not a proof from samples.
  ov=overlap_radius(aa,b)
  if ov['common_interior_radius_m'] is not None and ov['common_interior_radius_m']>TOL:
   bad.append({'fraction':(f0+f1)/2,**ov,'classification':'actual_pose_interior_intrusion'});return
  if depth>=max_depth:
   bad.append({'fraction_interval':[f0,f1],'classification':'uncertified_interval'});return
  check(f0,(f0+f1)/2,depth+1);check((f0+f1)/2,f1,depth+1)
 check(0,1,0)
 return {'pass':not bad,'continuous_angle_range_degrees':[0,travel],'certificate_intervals':leaves,'failures':bad}
def linear_pair(a,b,rec):
 swept=np.concatenate([a,pose(a,rec,1)]);r=static_pair(swept,b)
 return {**r,'continuous_translation_source_m':(np.asarray(rec['axis_source'])*rec['travel']).tolist(),'method':'Complete convex swept hull of actual part at both closed translation endpoints; exact for convex part translating on straight segment'}
def motion_pair(a,b,rec):return rotation_pair(a,b,rec)if rec['kind']=='rotation'else linear_pair(a,b,rec)
def boxcloud(lo,hi):return np.array(list(itertools.product(*zip(lo,hi))),float)
def descendants(native,name):
 nodes=native.g.doc['nodes'];root=next(i for i,n in enumerate(nodes)if n.get('name')==name);out=[]
 for i,n in enumerate(nodes):
  k=i
  while k in native.parents:
   k=native.parents[k]
   if k==root:out.append(i);break
 return out
def audit_asset(ident):
 mp=BASE/(ident+'.manifest.json');m=json.loads(mp.read_text());sp=BASE/m['source'];gp=BASE/m['export'];srp=OUT/f'independent_source_{ident}.json';sr=json.loads(srp.read_text());assert sha(sp)==sr['sha256']==m['source_sha256'];sobjects={x['name']:x for x in sr['objects']};cache=np.load(ROOT/sr['geometry_cache']);t=cache['triangles'];labels=cache['object_names'];parts={str(n):t[labels==n]for n in np.unique(labels)};verts={n:cloud(pt)for n,pt in parts.items()};native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ids={n.get('name'):i for i,n in enumerate(nodes)};convex=[]
 for name,pt in parts.items():
  hull=ConvexHull(verts[name]);vol=abs(np.einsum('ij,ij->i',pt[:,0],np.cross(pt[:,1],pt[:,2])).sum()/6);delta=abs(hull.volume-vol);convex.append({'part':name,'volume_difference_m3':float(delta),'passed':delta<1e-8})
 markers=[]
 for a in m['physical_and_proposal_markers']:
  p=np.array(a['source_m']);idx=ids[a['name']];row={'name':a['name'],'kind':a['kind'],'actual_source_position_error_m':float(np.linalg.norm(np.array(sobjects[a['name']]['matrix_world'])[:3,3]-p)),'actual_native_position_error_m':float(np.linalg.norm(native.world[idx][:3,3]-C@p)),'native_metadata_position_error_m':float(np.linalg.norm(a['gltf_m']-C@p)),'actual_source_parent':sobjects[a['name']]['parent'],'actual_native_parent':nodes[native.parents[idx]].get('name'),'declared_parent':a['parent_root']};row['passed']=max(v for k,v in row.items()if k.endswith('error_m'))<1e-6 and row['actual_source_parent']==row['actual_native_parent']==row['declared_parent']
  if a['physical_part']:
   part=parts[a['physical_part']];role=sobjects[a['physical_part']]['materials'][0];nn=np.array(a['direction_source']);row.update(source_distance_m=float(nearest_distances([p],part)[0]),native_distance_m=native.nearest(C@p,role=role)['distance_m'],source_normal=normal_witness(p,part,nn),native_normal=normal_witness(C@p,native.tris[native.select(role=role)],C@nn));row['passed']&=row['source_distance_m']<2e-6 and row['native_distance_m']<2e-6 and row['source_normal']['pass']and row['native_normal']['pass']
  markers.append(row)
 joins=[]
 for j in m['joins']:
  p=np.array(j['probe_source_m']);ws=[]
  for name in j['parts']:
   d=float(nearest_distances([p],parts[name])[0]);inside=bool(inside_mesh([p],parts[name])[0]);ws.append({'part':name,'boundary_distance_m':d,'inside':inside,'passed':d<2e-6 or inside})
  joins.append({'name':j['name'],'kind':j['kind'],'witnesses':ws,'passed':all(x['passed']for x in ws)})
 motions=[];states=[('closed',{},native)];records={r['root']:r for r in m['motion_records']}
 for rec in m['motion_records']:
  root=rec['root'];moving=rec['semantic_parts'];actual=sorted(n for n in parts if sobjects[n]['parent']==root);children=descendants(native,root);mesh_names=[nodes[i].get('name')for i in children if'mesh'in nodes[i]];mask=np.isin(native.nodes,mesh_names);pairs=[]
  for movingname in moving:
   for fixedname in parts:
    if fixedname in moving:continue
    pairs.append({'moving_part':movingname,'fixed_part':fixedname,**motion_pair(verts[movingname],verts[fixedname],rec)})
  d=next(x for x in m['state_derivatives']if x['root']==root);opened=Native(BASE/d['export']);ot=opened.tris@C;oi={n.get('name'):i for i,n in enumerate(opened.g.doc['nodes'])};expected=nt.copy();expected[mask]=pose(expected[mask],rec,1);markchecks=[];local_content=[]
  for name,idx in ids.items():
   node=nodes[idx]
   if 'mesh' not in node:continue
   op=opened.g.doc['nodes'][oi[name]];cp=native.g.doc['meshes'][node['mesh']]['primitives'];dp=opened.g.doc['meshes'][op['mesh']]['primitives'];same=len(cp)==len(dp)
   for cpr,dpr in zip(cp,dp):
    same &= native.g.doc['materials'][cpr['material']]==opened.g.doc['materials'][dpr['material']]
    same &= np.array_equal(native.g.accessor(cpr['indices']),opened.g.accessor(dpr['indices']))
    for attr in ['POSITION','NORMAL','TEXCOORD_0']:same &= np.array_equal(native.g.accessor(cpr['attributes'][attr]),opened.g.accessor(dpr['attributes'][attr]))
   local_content.append({'node':name,'exact_local_position_normal_uv_indices_materials':bool(same)})
  for a in m['physical_and_proposal_markers']:
   moves=a['parent_root']==root;p=np.array(a['source_m']);target=pose(p,rec,1)if moves else p;err=float(np.linalg.norm(opened.world[oi[a['name']]][:3,3]-C@target));markchecks.append({'marker':a['name'],'moving':moves,'native_descendant':ids[a['name']]in children,'terminal_position_error_m':err,'passed':moves==(ids[a['name']]in children)and err<1e-6})
  expected_affine=np.eye(4)
  if rec['kind']=='translation':expected_affine[:3,3]=C@(np.asarray(rec['axis_source'])*rec['travel'])
  else:
   rot=C@rotation_matrix(rec['axis_source'],rec['travel'])@C.T;pivot=C@np.array(rec['pivot_source_m']);expected_affine[:3,:3]=rot;expected_affine[:3,3]=pivot-rot@pivot
  actual_affine=opened.world[oi[root]]@np.linalg.inv(native.world[ids[root]]);affineerr=float(abs(actual_affine-expected_affine).max());ownerr=equal(t[np.isin(labels,moving)],nt[mask]);enderr=equal(expected,ot);states.append((root,{root:1},opened));r={'root':root,'declared_closed_to_terminal':[0,rec['travel']],'kind':rec['kind'],'source_moving_parts':actual,'native_moving_groups':mesh_names,'complete_interval_pairs':pairs,'moving_markers':markchecks,'source_native_moving_geometry_error_m':ownerr,'terminal_geometry_error_m':enderr,'terminal_affine_error':affineerr,'terminal_binding':bind(BASE/d['export']),'terminal_local_attribute_checks':local_content,'passed':all(x['exact_local_position_normal_uv_indices_materials']for x in local_content)and actual==sorted(moving)and ownerr<1e-6 and enderr<1e-6 and affineerr<1e-6 and all(x['pass']for x in pairs)and all(x['passed']for x in markchecks)};motions.append(r)
 voids=[];continuous=[]
 for v in m['receiver_voids']:
  state=v.get('state','all');localroot=state.removesuffix('_local')if state.endswith('_local')else None;terminalroot=state.removesuffix('_terminal')if state.endswith('_terminal')else None;bv=boxcloud(v['min_source_m'],v['max_source_m'])
  for statename,trans,ng in states:
   if terminalroot and statename!=terminalroot:continue
   sv={name:pose(vs,records[sobjects[name]['parent']],1)if sobjects[name]['parent']in trans else vs for name,vs in verts.items()};box=pose(bv,records[localroot],1)if localroot in trans else bv;checks=[{'part':name,**static_pair(vs,box)}for name,vs in sv.items()];nativecheck=[]
   # Every actual native triangle versus possibly rotated convex box; vertex-cloud equality separately binds native ownership.
   hb=Hull(box)
   for idx,tri in enumerate(ng.tris@C):
    if ((tri.max(0)<hb.lo-TOL)|(tri.min(0)>hb.hi+TOL)).any():continue
    from independent_collision_geometry import clip_polygon,polygon_area
    poly=tri
    for plane in hb.planes:
     if len(poly)<3:break
     shifted=plane.copy();shifted[3]+=TOL;poly=clip_polygon(poly,shifted,tol=0)
    if len(poly)>=3 and polygon_area(poly)>1e-11:nativecheck.append(idx)
   voids.append({'void':v['name'],'state':statename,'solid_box_checks':checks,'native_intruding_triangles':len(nativecheck),'passed':all(x['pass']for x in checks)and not nativecheck})
  if state=='all' or localroot:
   for rec in m['motion_records']:
    if localroot==rec['root']:
     checks=[{'part':name,**motion_pair(bv,vs,rec)}for name,vs in verts.items()if name not in rec['semantic_parts']];meaning='Complete local box motion against all other solids; own rigid attachments preserve closed relative gap'
    else:
     checks=[{'part':name,**motion_pair(verts[name],bv,rec)}for name in rec['semantic_parts']];meaning='Whole movement against declared fixed void'
    continuous.append({'void':v['name'],'root':rec['root'],'method':meaning,'checks':checks,'passed':all(x['pass']for x in checks)})
 # Whole chamber bore includes every semantic part, not merely selected internal panels or thin rays.
 shell=[]
 if ident=='AST-HSK-001':
  radius=m['details']['chamber_inner_circumradius_m'];bore=np.array([(radius*np.cos(i*np.pi/4),y,1.03+radius*np.sin(i*np.pi/4))for y in[-.419999,.284999]for i in range(8)]);center=bore.mean(0);bore=center+(bore-center)*.99999
  shell=[{'part':name,**static_pair(vs,bore)}for name,vs in verts.items()]
 # Independent moving systems are disjoint for every pair of settings by their invariant axis bands.
 simultaneous=[]
 if len(m['motion_records'])==2:
  a,b=m['motion_records'];axis=1 if ident=='AST-HSK-001'else 2;av=cloud(t[np.isin(labels,a['semantic_parts'])]);bv2=cloud(t[np.isin(labels,b['semantic_parts'])]);aa=np.eye(3)[axis:axis+1]
  if a['kind']=='rotation':alo,ahi=interval_projection(av,np.array(a['pivot_source_m']),aa,0,a['travel'],a['axis_source'])
  else:sw=np.concatenate([av,pose(av,a,1)]);alo=sw[:,axis].min();ahi=sw[:,axis].max()
  sw=np.concatenate([bv2,pose(bv2,b,1)]);blo=sw[:,axis].min();bhi=sw[:,axis].max();gap=float(max(np.asarray(alo).item()-bhi,blo-np.asarray(ahi).item()));simultaneous=[{'roots':[a['root'],b['root']],'invariant_separation_axis':axis,'whole_independent_ranges_minimum_gap_m':gap,'passed':gap>TOL}]
 result={'catalogue_id':ident,'bindings':{'source':bind(sp),'export':bind(gp),'manifest':bind(mp),'source_audit':bind(srp),'source_geometry':bind(ROOT/sr['geometry_cache'])},'convex_part_checks':convex,'marker_checks':markers,'join_checks':joins,'complete_motion_checks':motions,'complete_state_void_checks':voids,'complete_interval_void_checks':continuous,'whole_octagonal_bore_all_part_checks':shell,'independent_simultaneous_motion_checks':simultaneous,'passed':all(x['passed']for x in convex+markers+joins+motions+voids+continuous+simultaneous)and all(x['pass']for x in shell),'limits':'Complete analytic projection intervals and exact straight swept hulls are component geometry evidence only. Positive LP overlap diagnoses actual penetration only after convex part equivalence. Retained bearing and hollow shell checks are separate. No host/controller/species/load/operation or performance claim.'};(OUT/f'independent_equipment_motion_{ident}.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item())+'\n');print(ident,result['passed'],'markers',[x['name']for x in markers if not x['passed']],'joins',[x['name']for x in joins if not x['passed']],'motion',[(x['root'],[(y['moving_part'],y['fixed_part'])for y in x['complete_interval_pairs']if not y['pass']])for x in motions],'voids',[(x['void'],x['state'])for x in voids if not x['passed']],'continuous',[(x['void'],x['root'])for x in continuous if not x['passed']],'bore',[x['part']for x in shell if not x['pass']],flush=True);return result

def controls():
 cube=boxcloud([-.01,-.01,-.01],[.01,.01,.01]);r={'kind':'rotation','axis_source':[0,0,1],'pivot_source_m':[0,0,0],'travel':-105};moving=cube+[.5,0,0];obstacle=pose(moving,r,.5);rot=rotation_pair(moving,obstacle,r);lin={'kind':'translation','axis_source':[0,1,0],'travel':.28};middle=cube+[0,.14,0];lp=linear_pair(cube,middle,lin);return {'rotation_mid_arc_rejected':not rot['pass']and all(static_pair(pose(moving,r,f),obstacle)['pass']for f in[0,1]),'translation_mid_stroke_rejected':not lp['pass']and all(static_pair(pose(cube,lin,f),middle)['pass']for f in[0,1]),'touching_face_allowed':static_pair(cube,cube+[.02,0,0])['pass'],'tiny_material_overlap_rejected':not static_pair(cube,cube+[.019,0,0])['pass']}
if __name__=='__main__':
 results=[audit_asset(i)for i in(sys.argv[1:]or['AST-HSK-001','AST-HSK-002'])];cc=controls();report={'passed':all(x['passed']for x in results)and all(cc.values()),'assets':[{'catalogue_id':x['catalogue_id'],'passed':x['passed']}for x in results],'positive_negative_controls':cc,'executed_script_sha256':sha(Path(__file__))};(OUT/'independent_equipment_motion_review.json').write_text(json.dumps(report,indent=2)+'\n')
