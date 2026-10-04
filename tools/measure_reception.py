from pathlib import Path
import bpy,json
from mathutils import Vector
r=Path(__file__).resolve().parents[1]/'assets/arrivals_reception';bpy.ops.wm.open_mainfile(filepath=str(r/'source/AST-ARR-003.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v)for o in meshes for v in o.bound_box];lo=[min(v[i]for v in points)for i in range(3)];hi=[max(v[i]for v in points)for i in range(3)]
assert abs(lo[2])<1e-6
assert all(o.data.uv_layers for o in meshes)
assert bpy.data.objects.get('DATUM_lower_guest_approach')
# A frontal knee-space prism must not meet any individual actual triangle bounds.
from mathutils.bvhtree import BVHTree
bad=[]
for o in meshes:
 if 'stone_worktop' in o.name:continue
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  v=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  if all(max(q[i]for q in v)>a and min(q[i]for q in v)<b for i,a,b in [(0,-.65,.65),(1,-.25,.42),(2,.08,.64)]):bad.append(o.name)
assert not bad,bad
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(r/'exports/AST-ARR-003.glb'))
points=[o.matrix_world@Vector(v)for o in bpy.context.scene.objects if o.type=='MESH'for v in o.bound_box];elo=[min(v[i]for v in points)for i in range(3)];ehi=[max(v[i]for v in points)for i in range(3)];assert max(abs(lo[i]-elo[i])for i in range(3))<.002 and max(abs(hi[i]-ehi[i])for i in range(3))<.002
result={'source_floor_origin':True,'all_mesh_uvs':True,'roundtrip_bounds_match':True,'central_knee_envelope_clear':True,'tested_knee_prism_source_m':[[-.65,.65],[-.25,.42],[.08,.64]],'scope':'Component geometry only; not broad-species accessibility, ergonomics or in-game approach acceptance'}
(r/'geometry_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
