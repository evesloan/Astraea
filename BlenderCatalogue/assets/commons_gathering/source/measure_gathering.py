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
bpy.ops.wm.open_mainfile(filepath=str(r/'source/AST-COM-002.blend'));lo,hi,tri=bounds()
assert lo[2]>=-.001 and hi[2]<8.17,'Fits the existing commons roof'
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for vertex in o.data.vertices:
   p=o.matrix_world@vertex.co
   if p.z>4.26:assert abs(p.x)<.9 and abs(p.y)<.9,'Pendant must remain within the real upper opening'
assert lo[0]>-5.2 and hi[0]<5.2 and lo[1]>-9.0 and hi[1]<1.6,'Fits reserved planting/conversation footprint'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(r/'exports/AST-COM-002.glb'));elo,ehi,etri=bounds()
assert max(abs(a-b)for a,b in zip(lo+hi,elo+ehi))<.002
(r/'geometry_checks.json').write_text(json.dumps({'source_bounds_min':lo,'source_bounds_max':hi,'source_triangles':tri,'source_reopened':True,'export_roundtrip':True,'section_fit':True,'status':'Asset geometry only; main-scene route, plant contact and visual checks pending'},indent=2)+'\n')
print('GATHERING SOURCE PASS',tri,'triangles; section bounds and export roundtrip verified')
