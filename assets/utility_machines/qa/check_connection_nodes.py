"""Actual GLB node-world checks with wrong-axis negative controls, no Blender."""
import json,struct,math,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def matrix(node):
 if 'matrix'in node:return np.array(node['matrix']).reshape(4,4).T
 x,y,z,w=node.get('rotation',[0,0,0,1]);r=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
 m=np.eye(4);m[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
results=[]
for path in sorted((BASE/'exports').glob('*.glb')):
 raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);rows=[];groups=[]
 def walk(i,parent):
  node=doc['nodes'][i];m=parent@matrix(node);e=node.get('extras',{})
  if 'position_blender_source_m'in e and 'position_gltf_yup_m'in e:
   p=np.array(e['position_blender_source_m']);expected=np.array([p[0],p[2],-p[1]]);actual=m[:3,3];err=np.linalg.norm(actual-expected);stated=np.array(e['position_gltf_yup_m']);wrong=np.linalg.norm(actual-p)
   rows.append({'name':node['name'],'kind':e.get('kind','open_connection_datum'),'actual_world_position_gltf_yup_m':actual.tolist(),'expected_converted_source_m':expected.tolist(),'error_m':float(err),'metadata_matches_conversion':bool(np.max(abs(stated-expected))<1e-6),'wrong_axis_error_m':float(wrong),'wrong_axis_control_rejected':bool(wrong>1e-4),'passes':bool(err<1e-6 and np.max(abs(stated-expected))<1e-6)})
  if e.get('assembly_role','static')!='static':
   v=m[:3,3];groups.append({'node_name':node['name'],'assembly_role':e['assembly_role'],'actual_origin_gltf_yup_m':v.tolist(),'actual_origin_blender_source_m':[float(v[0]),float(-v[2]),float(v[1])],'world_matrix_gltf_yup':m.tolist(),'removal_direction_blender_source':e.get('removal_direction_blender_source'),'removal_direction_gltf_yup':e.get('removal_direction_gltf_yup'),'pivot_semantics':'Actual material-mesh node origin, not a shared hinge. Translate all nodes with the same assembly_role together; service-marker datum is distinct.'})
  for c in node.get('children',[]):walk(c,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 ports=[r for r in rows if r['name'].startswith('PORT_')]
 results.append({'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'points':rows,'removable_mesh_nodes':groups,'port_count':len(ports),'passed':bool(len(ports)==2 and all(r['passes'] for r in rows) and all(r['wrong_axis_control_rejected'] for r in ports))})
(BASE/'qa/connection_node_checks.json').write_text(json.dumps({'inspector':'Independent raw GLB node hierarchy parser, actual matrices and metadata, no Blender','results':results,'all_passed':all(r['passed'] for r in results)},indent=2)+'\n');print([(r['file'],r['passed']) for r in results])
