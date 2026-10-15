from pathlib import Path
import json,struct,hashlib,numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game')
def meshes(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);buf=b[28+n:];out={}
 for node in j['nodes']:
  if 'mesh'not in node:continue
  if 'r004'in path.name and not(node['name'].startswith('East_')or '_fixture_housing'in node['name']or 'ThreadCeiling'in node['name']):continue
  assert not any(k in node for k in['rotation','matrix','scale','translation']),node['name']
  ps=[]
  for pr in j['meshes'][node['mesh']]['primitives']:
   a=j['accessors'][pr['attributes']['POSITION']];v=j['bufferViews'][a['bufferView']];ps.append(np.ndarray((a['count'],3),dtype='<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4)).copy())
  p=np.concatenate(ps)+np.array([8,52.5,-216]);out[node['name']]=(p.min(0),p.max(0))
 return out
source=meshes(G/'assets/models/AST-RTL-007.glb');candidate=meshes(D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/exports/thread_stock/thread_stock_repair_r004.glb');rows=[]
for name,(lo,hi)in candidate.items():
 if not(name.startswith('East_')or '_fixture_housing'in name or 'ThreadCeiling'in name):continue
 for old,(a,b)in source.items():
  overlap=np.minimum(hi,b)-np.maximum(lo,a)
  if np.all(overlap>.0001):rows.append({'candidate':name,'retained_source':old,'candidate_bounds':[lo.tolist(),hi.tolist()],'source_bounds':[a.tolist(),b.tolist()],'aabb_overlap_xyz_m':overlap.tolist()})
r={'status':'READONLY_AABB_CANDIDATE_PLANNING_ONLY_NOT_CONTACT_ACCEPTANCE','source_meshes':len(source),'candidate_meshes':len(candidate),'source_bounds':{k:[a.tolist(),b.tolist()]for k,(a,b)in source.items()if 'Ceiling'in k or 'StaffRoof'in k},'fixture_bounds':{k:[a.tolist(),b.tolist()]for k,(a,b)in candidate.items()if 'fixture_housing'in k},'suspected_contacts':rows,'r002_still_selected':True};(D/'RETAINED_SUCCESSOR_AABB_INTERFACE_SURVEY.json').write_text(json.dumps(r,indent=2)+'\n');print('SOURCE_MESHES',len(source),'CANDIDATE',len(candidate),'SUSPECTED',len(rows));print('\n'.join(x['candidate']+' / '+x['retained_source']+' '+str(x['aabb_overlap_xyz_m'])for x in rows))
