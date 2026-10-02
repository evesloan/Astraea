"""Check proposal frame conversion, node attachments and intended open-space probes."""
from pathlib import Path
import json,math,struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1];p=json.loads((ROOT/'collision_proposals.json').read_text());data=(ROOT/'AST-ENG-003.glb').read_bytes();size,kind=struct.unpack_from('<II',data,12);glb=json.loads(data[20:20+size]);names={n.get('name') for n in glb['nodes']}
def C(v):return [v[0],v[2],-v[1]]
def close(a,b):return np.max(abs(np.array(a)-b))<1e-9
def contains(s,point):
 q=np.array(point)
 if s['type']=='box':return bool(np.all(q>=s['min_blender_source_m']) and np.all(q<=s['max_blender_source_m']))
 if s['type']=='cylinder':
  v=q-s['centre_blender_source_m'];axis=np.array(s['axis_blender_source']);t=np.dot(v,axis);return abs(t)<=s['length_m']/2 and np.linalg.norm(v-t*axis)<=s['radius_m']
 vv=np.array(s['vertices_blender_source_m']);centre=vv.mean(axis=0)
 for face in s['faces']:
  a,b,c=vv[face[:3]];n=np.cross(b-a,c-a)
  if np.dot(n,centre-a)>0:n=-n
  if np.dot(n,q-a)>1e-10:return False
 return True
issues=[]
for s in p['parts']:
 if 'follows_named_node' in s and s['follows_named_node'] not in names:issues.append('Missing GLB attachment '+s['follows_named_node'])
 if s['type']=='box':
  lo=s['min_blender_source_m'];hi=s['max_blender_source_m']
  if not close(s['min_gltf_yup_m'],[lo[0],lo[2],-hi[1]]) or not close(s['max_gltf_yup_m'],[hi[0],hi[2],-lo[1]]):issues.append('Wrong box frame '+s['name'])
 elif s['type']=='cylinder':
  if not close(C(s['centre_blender_source_m']),s['centre_gltf_yup_m']) or not close(C(s['axis_blender_source']),s['axis_gltf_yup']):issues.append('Wrong cylinder frame '+s['name'])
 else:
  if not close([C(v) for v in s['vertices_blender_source_m']],s['vertices_gltf_yup_m']):issues.append('Wrong prism frame '+s['name'])
probes=[('service_bay_behind_left_hatch',[-.10,-.180,-.245]),('vent_pocket_before_baffle',[.10,-.180,-.245])]+[('button_'+name+'_fully_pressed_rear',[x,-.2085,-.133]) for name,x in [('START',-.263),('HOLD',-.127),('ISOLATE',.009)]]
rows=[]
for name,q in probes:
 hits=[s['name'] for s in p['parts'] if not s.get('follows_named_node') and contains(s,q)]
 old_hull_hits=all(a<=x<=b for x,a,b in zip(q,[-.41,-.214,-.34],[.41,-.079,.34]))
 rows.append({'probe':name,'point_blender_source_m':q,'point_gltf_yup_m':C(q),'fixed_proposal_hits':hits,'negative_control_old_whole_case_hull_would_block':old_hull_hits,'passes':not hits and old_hull_hits})
 if hits or not old_hull_hits:issues.append('Open-space probe failed '+name)
r={'status':'PASS' if not issues else 'FAIL','proposal_revision':p['revision'],'shape_count':len(p['parts']),'attached_moving_shape_count':sum('follows_named_node' in s for s in p['parts']),'frame_and_actual_node_attachment_checks':'PASS' if not issues else 'FAIL','open_space_probes':rows,'limits':'Tests the stated conservative proposals against intended open probes, not engine collision acceptance','issues':issues}
(ROOT/'qa/collision_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert not issues
