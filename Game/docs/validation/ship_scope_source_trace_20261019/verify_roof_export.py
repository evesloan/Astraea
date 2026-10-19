import json,struct,hashlib,math,pathlib
root=pathlib.Path('/workspace/Astraea');work=pathlib.Path('/workspace/ship-scope-reconciliation-20261019')
native=json.loads((work/'ROYALTY790_NATIVE_INSPECTION.json').read_text());roof=next(x for x in native['parts_intersecting_circulation_height_bbox'] if x['name']=='CR_RoyaltyLowerRoof')
p=root/'Game/assets/models/AST-RES-006.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);binary=b[28+n:]
def acc(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];types={5126:'f',5125:'I',5123:'H',5121:'B'};dim={'VEC3':3,'SCALAR':1}[a['type']];fmt='<'+types[a['componentType']]*dim;size=struct.calcsize(fmt);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from(fmt,binary,offset+j*v.get('byteStride',size)) for j in range(a['count'])]
candidates=[]
for node in g['nodes']:
 if 'mesh' not in node:continue
 assert not any(k in node for k in ['matrix','translation','rotation','scale'])
 for prim in g['meshes'][node['mesh']]['primitives']:
  pts=acc(prim['attributes']['POSITION']);idx=[x[0] for x in acc(prim['indices'])];faces=[idx[i:i+3] for i in range(0,len(idx),3)]
  roof_faces=[f for f in faces if all(any(math.dist(pts[j],v)<.0001 for v in roof['world_vertices']) for j in f)]
  if roof_faces:candidates.append({'node':node['name'],'matching_roof_triangles':len(roof_faces),'all20_roof_vertices_found':all(any(math.dist(v,q)<.0001 for q in pts) for v in roof['world_vertices'])})
assert sum(x['matching_roof_triangles'] for x in candidates)==36,candidates
assert any(x['all20_roof_vertices_found'] for x in candidates)
hashval=hashlib.sha256(b).hexdigest();assert hashval=='5375179c3d89b92a4f950b7fad0a0936aafdeca37797aa388264f9bdf6d8e664'
r=json.loads((work/'RUNTIME_SURVEY.json').read_text())['rows'];matches=[x for x in r if x['scene_source']=='res://assets/models/AST-RES-006.glb']
out={'native_sha256':native['native_sha256'],'current_glb_sha256':hashval,'native_roof_triangle_matches_in_export':candidates,'observed_runtime_instances':matches,'transform_contract':'Game/data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json integration_transforms AST-RES-006 identity; d17_connected_house.gd instantiates at Vector3.ZERO','scope':'Exact native roof triangles remain in unchanged current export, observed as a main-scene asset. No collision/visual or revised geometry acceptance.'}
(work/'ROYALTY790_EXPORT_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'matches':candidates,'runtime_instances':len(matches)}))
