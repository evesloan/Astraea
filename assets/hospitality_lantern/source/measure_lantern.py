from pathlib import Path
import bpy,json
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
def bounds():
 points=[];triangles=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  points.extend(o.matrix_world@Vector(p)for p in o.bound_box)
  o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 return [min(v[i]for v in points)for i in range(3)],[max(v[i]for v in points)for i in range(3)],triangles
bpy.ops.wm.open_mainfile(filepath=str(r/'source/AST-LGT-001.blend'));lo,hi,tri=bounds()
assert lo[2]>=-.001 and hi[2]<.90
assert hi[0]-lo[0]<.42 and hi[1]-lo[1]<.33
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(r/'exports/AST-LGT-001.glb'));elo,ehi,etri=bounds()
assert max(abs(a-b)for a,b in zip(lo+hi,elo+ehi))<.002
(r/'geometry_checks.json').write_text(json.dumps({'source_bounds_min':lo,'source_bounds_max':hi,'source_triangles':tri,'source_reopened':True,'export_roundtrip':True,'wall_fixture_bounds':True,'status':'Asset geometry only; main-scene route, plant contact and visual checks pending'},indent=2)+'\n')
print('WALL LANTERN SOURCE PASS',tri,'triangles; section bounds and export roundtrip verified')
