from pathlib import Path
import json,struct,hashlib
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');result=[]
for key,file,target in [('port_forward_upper_house','AST-RES-TIDAL_lift_fit_r003.glb',[-70,-68,-384.1,-383.9]),('starboard_forward_upper_house','QUIET_GROVE_ARCHITECTURE_lift_r003.glb',[68,70,-384.1,-383.9])]:
 b=(G/'assets/models'/file).read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);binary=b[28+n:];rows=[]
 for node in d['nodes']:
  if'mesh'not in node:continue
  extra=node.get('extras',{});ranges=extra.get('source_part_ranges',[])
  if not ranges:continue
  prim=d['meshes'][node['mesh']]['primitives'][0];a=d['accessors'][prim['attributes']['POSITION']];view=d['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',12);vs=[struct.unpack_from('<fff',binary,offset+i*stride)for i in range(a['count'])]
  for part in ranges:
   pts=vs[part['vertex_start']:part['vertex_start']+part['vertex_count']];lo=[min(v[i]for v in pts)for i in range(3)];hi=[max(v[i]for v in pts)for i in range(3)]
   if lo[1]>103.3 or hi[1]<101.75 or min(hi[0],target[1])<max(lo[0],target[0])or min(hi[2],target[3])<max(lo[2],target[2]):continue
   rows.append({'batch':node['name'],'category':extra.get('category'),'role':extra.get('role'),'source_part_id':part['source_part_id'],'min':lo,'max':hi})
 result.append({'key':key,'file':file,'sha256':hashlib.sha256(b).hexdigest(),'near_threshold_parts':rows})
(P/'FORWARD_THRESHOLD_SOURCE_PARTS.json').write_text(json.dumps(result,indent=2)+'\n')
for row in result:
 print(row['key'])
 for p in row['near_threshold_parts']:print(p['batch'],p['category'],p['source_part_id'],p['min'],p['max'])
