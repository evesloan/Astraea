from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
rows={}
for asset in ('AST-AQU-007','AST-AQU-008'):
 p=ROOT/'source'/f'{asset}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();out=[]
 for ob in bpy.data.objects:
  if ob.type not in ('MESH','FONT'):continue
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
  vs=[list(ob.matrix_world@v.co) for v in me.vertices];fs=[list(t.vertices) for t in me.loop_triangles]
  areas=[(Vector(vs[f[1]])-Vector(vs[f[0]])).cross(Vector(vs[f[2]])-Vector(vs[f[0]])).length*.5 for f in fs]
  row={'name':ob.name,'role':ob['semantic_role'],'motion_group':ob['motion_group'],'vertices':vs,'triangles':fs,'minimum_area':min(areas),'degenerate_triangles':sum(x<1e-12 for x in areas)}
  out.append(row);eo.to_mesh_clear()
  if row['degenerate_triangles']:print('DEGENERATE',asset,ob.name,row['degenerate_triangles'],row['minimum_area'])
 rows[asset]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':out}
(ROOT/'qa/source_geometry.json').write_text(json.dumps(rows))
print('SOURCE_RELOAD_COMPLETE')
