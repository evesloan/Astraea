"""Actual native GLB hierarchy/contact/motion and conservative opening tests."""
from pathlib import Path
import json,math,hashlib,importlib.util,numpy as np
BASE=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('g',BASE/'qa/validate_glb.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
def rot(axis,a):
 axis=np.array(axis,float);axis/=np.linalg.norm(axis);x,y,z=axis;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);return np.eye(3)+math.sin(a)*K+(1-math.cos(a))*(K@K)
def rays(origin,direction,tri):
 e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];p=np.cross(np.broadcast_to(direction,e2.shape),e2);d=np.einsum('ij,ij->i',e1,p);valid=abs(d)>1e-10;inv=np.zeros_like(d);inv[valid]=1/d[valid];t=origin-tri[:,0];u=np.einsum('ij,ij->i',t,p)*inv;q=np.cross(t,e1);v=np.einsum('j,ij->i',direction,q)*inv;distance=np.einsum('ij,ij->i',e2,q)*inv;ok=valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(distance>=-1e-7);return distance[ok]
def hierarchy(path):
 d,b=g.read(path);nodes={};points={};triangles={};tris={}
 def walk(i,parent):
  n=d['nodes'][i];m=parent@g.matrix(n);nodes[n['name']]={'matrix':m,'node':n};pp=[];tt=[];count=0
  if'mesh'in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    v=g.accessor(d,b,p['attributes']['POSITION']);ix=g.accessor(d,b,p['indices']).reshape(-1,3);v=(m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];pp.extend(v);tt.extend(v[ix]);count+=len(ix)
   points[n['name']]=np.array(pp);triangles[n['name']]=np.array(tt);tris[n['name']]=count
  for child in n.get('children',[]):walk(child,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return d,nodes,points,triangles,tris
reports={};cost=[];asset_triangles={}
for aid in['AST-HSP-005','AST-HSP-006']:
 m=json.loads((BASE/(aid+'.manifest.json')).read_text());d,nodes,points,triangles,tris=hierarchy(BASE/'exports'/(aid+'.glb'));marks=[]
 for row in m['native_marker_records']:
  name=row['node'];expected=C@np.array(row['position_blender_m']);actual=nodes[name]['matrix'][:3,3];error=float(np.linalg.norm(actual-expected));wrong=float(np.linalg.norm(actual-np.array(row['position_blender_m'])));floor='floor_contact'in name
  if aid.endswith('005'):targets=[n for n in triangles if n.startswith('005_fixed_carcass')]
  elif floor:
   prefix=name.replace('_floor_contact','');targets=[n for n in triangles if n.startswith(prefix+'_axle')]
  else:targets=[n for n in triangles if n.startswith('006_fixed_chassis')]
  tri=np.concatenate([triangles[n]for n in targets]);direction=np.array([0,1 if floor else-1,0]);origin=expected-direction*.010;hits=rays(origin,direction,tri);near=min(abs(hits-.010))if len(hits)else 1e10
  marks.append({'node':name,'hierarchy_position_gltf_yup_m':actual.tolist(),'expected_from_source_m':expected.tolist(),'hierarchy_error_m':error,'actual_mesh_contact_ray_error_m':float(near),'wrong_unmapped_source_point_error_m':wrong,'passed':error<2e-6 and near<2e-6})
 rotations=[]
 for w in m.get('wheels',[]):
  pivot=np.array(w['swivel_pivot_gltf_yup_m']);center=np.array(w['wheel_center_gltf_yup_m']);node=nodes[w['swivel_node']]['matrix'];axle=nodes[w['axle_node']]['matrix'];allpoints=np.concatenate([p for n,p in points.items()if n.startswith('006_'+w['tag'])]);radial=np.linalg.norm((allpoints-pivot)[:,[0,2]],axis=1);sweep=[]
  # Bind proposed rotation to native hierarchy sample points, compare C R_source C^-1.
  p=allpoints[np.argmax(radial)];source=C.T@p;sp=C.T@pivot
  for degrees in[30,90,180]:
   a=math.radians(degrees);correct=pivot+rot([0,1,0],a)@(p-pivot);expected=C@(sp+rot([0,0,1],a)@(source-sp));wrong=pivot+rot([0,0,1],a)@(p-pivot)
   sweep.append({'degrees':degrees,'correct_axis_error_m':float(np.linalg.norm(correct-expected)),'wrong_source_Z_used_as_native_Z_error_m':float(np.linalg.norm(wrong-expected))})
  wheelpts=np.concatenate([p for n,p in points.items()if n.startswith(w['axle_node'])]);sample=wheelpts[np.argmax(abs(wheelpts[:,1]-center[1]))];a=math.radians(60);correct=center+rot([1,0,0],a)@(sample-center);wrong=center+rot([0,0,1],a)@(sample-center)
  rotations.append({'swivel_node':w['swivel_node'],'native_pivot_error_m':float(np.linalg.norm(node[:3,3]-pivot)),'axle_node':w['axle_node'],'native_wheel_center_error_m':float(np.linalg.norm(axle[:3,3]-center)),'native_swivel_world_axis_from_node':(node[:3,:3]@np.array([0,0,1])).tolist(),'native_axle_world_axis_from_node':(axle[:3,:3]@np.array([1,0,0])).tolist(),'measured_full_swivel_radial_bound_m':float(max(radial)),'proposed_sweep_radius_m':.091,'sweep_within_proposal':bool(max(radial)<=.091),'swivel_rotation_tests':sweep,'wheel_axle_wrong_Z_error_m':float(np.linalg.norm(correct-wrong)),'status':'Numerical proposed-axis validation on actual exported geometry; no rolling solver'})
 asset_triangles[aid]=np.concatenate([tt@C for name,tt in triangles.items() if 'stock'not in name and'context_lower_tray'not in name]);stockcost=sum(t for n,t in tris.items()if'stock'in n or'context_lower_tray'in n);cost.append({'catalogue_id':aid,'total_triangles':sum(tris.values()),'fixed_furnishing_plus_castors_triangles':sum(tris.values())-stockcost,'configurable_context_stock_triangles':stockcost,'runtime_meshes':len(d['meshes']),'runtime_primitives':sum(len(x['primitives'])for x in d['meshes']),'by_export_group':tris})
 reports[aid]={'sha256':hashlib.sha256((BASE/'exports'/(aid+'.glb')).read_bytes()).hexdigest(),'contact_and_marker_tests':marks,'proposed_wheel_axis_tests':rotations,'all_contact_checks_passed':all(x['passed']for x in marks),'all_axis_checks_passed':all(x['native_pivot_error_m']<2e-6 and x['native_wheel_center_error_m']<2e-6 and x['sweep_within_proposal'] and x['wheel_axle_wrong_Z_error_m']>.001 and all(y['correct_axis_error_m']<2e-6 and y['wrong_source_Z_used_as_native_Z_error_m']>.001 for y in x['swivel_rotation_tests']) for x in rotations)}
# Conservative collision opening tests: AABB envelopes of proposals must not enter named free probe volumes.
coll=json.loads((BASE/'collision_proposals.json').read_text());openings=[]
def bounds(shape,frame):
 p=shape[frame]
 if shape['type']=='box':return np.array(p['min_m']),np.array(p['max_m'])
 a=np.array(p['a_m']);b=np.array(p['b_m']);r=p['radius_m'];extent=np.array([r,r,r])
 if shape['type']=='cylinder':
  axis=(b-a)/np.linalg.norm(b-a);extent=r*np.sqrt(np.maximum(0,1-axis*axis))
 return np.minimum(a,b)-extent,np.maximum(a,b)+extent
def tri_box_hits(tris,lo,hi):
 center=(lo+hi)/2;half=(hi-lo)/2;v=tris-center;edges=[v[:,1]-v[:,0],v[:,2]-v[:,1],v[:,0]-v[:,2]];active=np.ones(len(v),bool)
 axes=[np.broadcast_to(a,(len(v),3))for a in np.eye(3)]+[np.cross(edges[0],edges[1])]
 for e in edges:
  for a in np.eye(3):axes.append(np.cross(e,a))
 for axis in axes:
  projection=np.einsum('tvi,ti->tv',v,axis);radius=np.abs(axis)@half;nonzero=np.linalg.norm(axis,axis=1)>1e-12;separate=(projection.min(1)>radius+1e-8)|(projection.max(1)<-radius-1e-8);active&=~(separate&nonzero)
 return int(active.sum())
def probe_overlaps(lo,hi,sl,sh):return bool(np.all(np.minimum(hi,sh)-np.maximum(lo,sl)>1e-7))
for aid,row in coll['assets'].items():
 for probe in row['open_probe_volumes_blender']:
  lo=np.array(probe['min_m']);hi=np.array(probe['max_m']);conflicts=[]
  for shape in row['shapes']:
   sl,sh=bounds(shape,'blender_z_up');overlap=np.minimum(hi,sh)-np.maximum(lo,sl)
   if probe_overlaps(lo,hi,sl,sh):conflicts.append(shape['name'])
  # Sensitive intentional full-volume blocker must be detected by the same predicate.
  blocked=probe_overlaps(lo,hi,lo-.01,hi+.01);actual_hits=tri_box_hits(asset_triangles[aid],lo,hi)
  openings.append({'asset':aid,'probe':probe['name'],'intersecting_proposal_shapes':conflicts,'intentional_full_body_box_control_detected':bool(blocked),'actual_fixed_geometry_triangle_intersections':actual_hits,'passed':not conflicts and bool(blocked) and actual_hits==0})
 framechecks=[]
 for shape in row['shapes']:
  lo,hi=bounds(shape,'blender_z_up');expected=np.array([C@np.array([x,y,z])for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]]);gl,gh=bounds(shape,'gltf_y_up');framechecks.append(float(max(np.max(abs(expected.min(0)-gl)),np.max(abs(expected.max(0)-gh)))))
 row['tested_shape_frame_error_max_m']=max(framechecks)
result={'frame_contract':'Native GLB hierarchy resolved; C(source)=(x,z,−y)','assets':reports,'runtime_cost':cost,'collision_opening_probes':openings,'collision_shape_frame_max_errors_m':{k:v['tested_shape_frame_error_max_m']for k,v in coll['assets'].items()},'all_passed':all(v['all_contact_checks_passed']and v['all_axis_checks_passed']for v in reports.values())and all(x['passed']for x in openings)and all(v['tested_shape_frame_error_max_m']<2e-6 for v in coll['assets'].values())}
(BASE/'qa/exchange_contact_opening_checks.json').write_text(json.dumps(result,indent=2,default=lambda o:o.item())+'\n');(BASE/'qa/runtime_cost_breakdown.json').write_text(json.dumps(cost,indent=2)+'\n');print(json.dumps({'all_passed':result['all_passed'],'openings':openings,'runtime_cost':cost},indent=2));assert result['all_passed']
