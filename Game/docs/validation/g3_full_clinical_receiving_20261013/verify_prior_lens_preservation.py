from pathlib import Path
import json,struct,collections
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game')
def lens_triangles(path):
 b=path.read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);buf=b[28+n:];out=collections.Counter()
 def a(i):
  x=d['accessors'][i];v=d['bufferViews'][x['bufferView']];f={5126:'f',5123:'H',5125:'I'}[x['componentType']];w={'VEC3':3,'SCALAR':1}[x['type']];size=struct.calcsize('<'+f*w);base=v.get('byteOffset',0)+x.get('byteOffset',0);return[struct.unpack_from('<'+f*w,buf,base+j*v.get('byteStride',size))for j in range(x['count'])]
 for node in d['nodes']:
  if'mesh'not in node or'opal'not in node.get('name','').lower():continue
  assert not any(k in node for k in ['matrix','translation','rotation','scale'])
  for p in d['meshes'][node['mesh']]['primitives']:
   vs=a(p['attributes']['POSITION']);idx=[x[0]for x in a(p['indices'])]
   for i in range(0,len(idx),3):out[tuple(sorted(vs[j]for j in idx[i:i+3]))]+=1
 return out
old=lens_triangles(G/'assets/models/group3_port2_clinical_20261011/AST-MED-G3-006.glb');new=lens_triangles(P/'import/Game/assets/models/group3_clinical_full_20261011/AST-MED-G3-007.glb');old_points={p for t in old for p in t};new_points={p for t in new for p in t};assert old_points.issubset(new_points)
ns={'__file__':str(P.parent/'preflight_g3_first_floor_overlap.py')};exec((P.parent/'preflight_g3_first_floor_overlap.py').read_text().split('old=[]')[0],ns);rows=[]
for tri,count in old.items():
 axes=[i for i in range(3)if len({p[i]for p in tri})==1];assert len(axes)==1;axis=axes[0];plane=tri[0][axis];projection=[i for i in range(3)if i!=axis];a=[[p[i]for i in projection]for p in tri];area=ns['area'](a);covered=0.
 for candidate,n in new.items():
  if not all(p[axis]==plane for p in candidate):continue
  covered+=n*ns['overlap'](a,[[p[i]for i in projection]for p in candidate])
 assert abs(covered-area)<1e-8,(tri,area,covered);rows.append({'area_m2':area,'covered_m2':covered})
r={'status':'PASS_PRIOR_PORT2_LENS_SURFACES_EXACTLY_RETAINED_WITH_DIFFERENT_TRIANGLE_DIAGONALS','old_opal_triangles':sum(old.values()),'successor_opal_triangles':sum(new.values()),'old_vertices_exactly_present':len(old_points),'same_plane_exact_coverage_checks':len(rows),'triangulation_changed_old_triangles':sum((old-new).values()),'prior_two_light_nodes_registration_andposes_must_remain_exact':True};(P/'PRIOR_LENS_PRESERVATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
