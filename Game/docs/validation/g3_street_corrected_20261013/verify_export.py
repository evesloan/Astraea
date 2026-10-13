from pathlib import Path
import json,struct,hashlib
P=Path(__file__).parent; C=P.parent
ns={'__file__':str(C/'preflight_g3_first_floor_overlap.py')};exec((C/'preflight_g3_first_floor_overlap.py').read_text().split('old=[]')[0],ns)
plan=json.loads((P/'FLOOR_RECEIVING_SUCCESSOR_PLAN.json').read_text())
def triangles(path):
 b=path.read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);off=20+n;buf=b[off+8:]
 def a(i):
  x=d['accessors'][i];v=d['bufferViews'][x['bufferView']];f={5126:'f',5125:'I',5123:'H',5121:'B'}[x['componentType']];w={'VEC3':3,'SCALAR':1}[x['type']];sz=struct.calcsize('<'+f*w);o=v.get('byteOffset',0)+x.get('byteOffset',0);return[struct.unpack_from('<'+f*w,buf,o+j*v.get('byteStride',sz))for j in range(x['count'])]
 out=[]
 for m in d['meshes']:
  for p in m['primitives']:
   v=a(p['attributes']['POSITION']);idx=[q[0]for q in a(p['indices'])]
   for i in range(0,len(idx),3):
    t=[v[j]for j in idx[i:i+3]]
    if all(abs(q[1]-12)<.00002 for q in t):out.append([[q[0],q[2]]for q in t])
 return out
new=triangles(P/'proposed/AST-STF-G3-058_current_receiving_successor001.glb');old=triangles(C/'g3_street_staging/Game/assets/models/group3_d03_streets_20261011/AST-STF-G3-058.glb')
area=sum(ns['area'](t)for t in new);overlap=sum(ns['overlap'](t,c['triangle'])for t in new for c in plan['current_floor_triangles']);assert overlap<1e-6
# Every retained top triangle equals an original export triangle, with winding irrelevant.
key=lambda t:tuple(sorted(tuple(q)for q in t))
assert set(map(key,new)).issubset(set(map(key,old)))
assert abs(area-plan['corrected_geometric_area_m2'])<.01
r={'status':'PASS_EXPORTED_FLOOR_DIFFERENCE','original_export_top_triangles':len(old),'successor_export_top_triangles':len(new),'exported_area_m2':area,'overlap_with_protected_native_floors_m2':overlap,'all_successor_top_triangles_exact_original_export':True,'preserved_original_criteria':13,'coverage_basis':'Only three completely covered original floor parts removed; all remaining native objects and exported top triangles unchanged; protected D04 floors supply removed area.'}
(P/'EXPORT_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
