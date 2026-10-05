import bpy,json,hashlib
from pathlib import Path
root=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/bridge_platform')
source=root/'source/AST-CMD-003.blend'
parts=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 verts=[]
 for v in ob.data.vertices:
  q=ob.matrix_world@v.co;verts.append([float(q.x),float(q.z),float(-q.y)])
 lo=[min(p[i]for p in verts)for i in range(3)];hi=[max(p[i]for p in verts)for i in range(3)]
 parts.append({'name':ob.name,'assembly':ob.get('assembly',''),'group':ob.get('group',''),'vertices':verts,'faces':[list(f.vertices)for f in ob.data.polygons],'aabb':[lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]]})
result={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':parts,'objects':len(parts),'method':'Read bpy mesh vertices and world matrix from reopened editable source. Geometry ledger not used for measured coordinates.'}
(root/'qa/independent_review_geometry.json').write_text(json.dumps(result))
print('INDEPENDENT_GEOMETRY',len(parts),result['source_sha256'])
