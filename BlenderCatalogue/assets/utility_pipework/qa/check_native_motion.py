"""Bind actual GLB port nodes and a wheel vertex to both coordinate frames."""
import json,math,runpy,contextlib,io
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
with contextlib.redirect_stdout(io.StringIO()):p=runpy.run_path(str(BASE/'qa/validate_glb.py'))
read,accessor,matrix=p['read'],p['accessor'],p['matrix'];C=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def rot(axis,ang):
 a=np.array(axis,dtype=float);a/=np.linalg.norm(a);x,y,z=a;c=math.cos(ang);s=math.sin(ang);K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 return c*np.eye(3)+(1-c)*np.outer(a,a)+s*K
records=[]
for path in sorted((BASE/'exports').glob('*.glb')):
 d,b=read(path);world={};parents={}
 def walk(i,parent):
  world[i]=parent@matrix(d['nodes'][i])
  for child in d['nodes'][i].get('children',[]):parents[child]=i;walk(child,world[i])
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 rec={'file':path.name,'ports':[]}
 for i,node in enumerate(d['nodes']):
  if node.get('name','').startswith('PORT_'):
   e=node['extras'];ps=np.array(e['position_blender_source_m']);pg=np.array(e['position_gltf_yup_m']);ns=np.array(e['normal_blender_source']);ng=np.array(e['normal_gltf_yup']);actual=world[i][:3,3]
   rec['ports'].append({'name':node['name'],'actual_native_node_position_m':actual.tolist(),'position_error_m':float(np.linalg.norm(actual-C@ps)),'field_position_error_m':float(np.linalg.norm(pg-C@ps)),'normal_field_error':float(np.linalg.norm(ng-C@ns)),'naive_source_as_glb_position_error_m':float(np.linalg.norm(actual-ps)),'passed':np.linalg.norm(actual-C@ps)<1e-6 and np.linalg.norm(pg-C@ps)<1e-6 and np.linalg.norm(ng-C@ns)<1e-6})
 if path.stem=='AST-ENG-006':
  wi=next(i for i,n in enumerate(d['nodes'])if n.get('name')=='VALVE_CONTROL_WHEEL');wn=d['nodes'][wi];e=wn['extras'];pivot=np.array(e['pivot_gltf_yup_m']);sourcepivot=np.array(e['pivot_blender_source_m']);wverts=[]
  for ci in wn['children']:
   n=d['nodes'][ci]
   if'mesh'not in n:continue
   for prim in d['meshes'][n['mesh']]['primitives']:
    a=accessor(d,b,prim['attributes']['POSITION']);wverts.extend((world[ci]@np.column_stack([a,np.ones(len(a))]).T).T[:,:3])
  wverts=np.array(wverts);grips=json.loads(e['grip_records_json']);grip=np.array(grips[0]['position_gltf_yup_m']);index=int(np.argmin(np.linalg.norm(wverts-grip,axis=1)));vertex=wverts[index];theta=math.radians(35)
  sourcevertex=C.T@vertex;source_expected=C@(sourcepivot+rot(e['wheel_axis_blender_source'],theta)@(sourcevertex-sourcepivot))
  localaxis=np.linalg.inv(world[wi][:3,:3])@np.array(e['wheel_axis_gltf_yup']);localpoint=(np.linalg.inv(world[wi])@np.append(vertex,1))[:3]
  actual=(world[wi]@np.append(rot(localaxis,theta)@localpoint,1))[:3];wrong=pivot+rot([0,0,1],theta)@(vertex-pivot)
  motion={'actual_wheel_root_native_position_m':world[wi][:3,3].tolist(),'declared_pivot_native_m':pivot.tolist(),'root_pivot_error_m':float(np.linalg.norm(world[wi][:3,3]-pivot)),'nearest_grip_vertex_before_native_m':vertex.tolist(),'grip_centreline_to_nearest_vertex_m':float(np.linalg.norm(vertex-grip)),'actual_vertex_after_35deg_native_m':actual.tolist(),'source_expected_after_35deg_native_m':source_expected.tolist(),'source_glb_rotation_error_m':float(np.linalg.norm(actual-source_expected)),'wrong_unconverted_Z_axis_rotation_error_m':float(np.linalg.norm(wrong-source_expected)),'wheel_bounds_native_m':{'min':wverts.min(0).tolist(),'max':wverts.max(0).tolist()},'passed':np.linalg.norm(world[wi][:3,3]-pivot)<1e-6 and np.linalg.norm(actual-source_expected)<1e-6 and np.linalg.norm(vertex-grip)<.019 and np.linalg.norm(wrong-source_expected)>.05}
  rec['actual_native_vertex_motion']=motion
 rec['passed']=all(x['passed']for x in rec['ports'])and rec.get('actual_native_vertex_motion',{'passed':True})['passed'];records.append(rec)
out={'inspection':'Native GLB accessor vertices and resolved node hierarchy; no source geometry substitution','results':records,'all_passed':all(r['passed']for r in records)}
(BASE/'qa/native_motion_and_ports.json').write_text(json.dumps(out,indent=2,default=bool)+'\n');print(json.dumps(out,indent=2,default=bool))
