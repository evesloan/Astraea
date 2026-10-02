import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-AQU-002.blend'))
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
 for t in me.loop_triangles:
  vs=[me.vertices[v].co for v in t.vertices]
  if (vs[1]-vs[0]).cross(vs[2]-vs[0]).length_squared < 1e-18:rows.append({'object':ob.name,'triangle':t.index,'coordinates':[list(v) for v in vs]})
 eo.to_mesh_clear()
(R/'qa/initial_rejected/degenerate_coordinates.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
