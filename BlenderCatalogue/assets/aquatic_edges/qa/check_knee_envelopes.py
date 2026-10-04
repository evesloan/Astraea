"""Read-only check of both evaluated stringers at all four finished riser fronts."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'AST-AQU-005.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
def clip(points,threshold,greater):
 out=[]
 for a,b in zip(points,points[1:]+points[:1]):
  ia=a.y>=threshold if greater else a.y<=threshold
  ib=b.y>=threshold if greater else b.y<=threshold
  if ia:out.append(a)
  if ia!=ib:
   t=(threshold-a.y)/(b.y-a.y);out.append(a.lerp(b,t))
 return out
records=[]
for name in ['30_left_tapered_stringer','30_right_tapered_stringer']:
 ob=bpy.data.objects[name];me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));me.calc_loop_triangles()
 for i in range(4):
  front=i*.32+.015;finish=-(i+1)*.18;points=[]
  for tri in me.loop_triangles:
   poly=[ob.matrix_world@me.vertices[k].co for k in tri.vertices];poly=clip(poly,front,True)
   if poly:poly=clip(poly,front+.040,False)
   points+=poly
  assert points
  top=max(v.z for v in points);minx=min(v.x for v in points);maxx=max(v.x for v in points)
  row={'stringer':name,'riser_number':i+1,'actual_front_plane_y_m':front,'checked_visible_front_strip_y_m':[front,front+.040],'finished_next_tread_top_z_m':finish,'highest_actual_evaluated_stringer_z_m':top,'clearance_below_finished_top_m':finish-top,'actual_stringer_strip_x_bounds_m':[minx,maxx],'riser_finished_half_width_m':.675,'side_containment_margin_m':.675-max(abs(minx),abs(maxx)),'passes':top<finish-.040 and minx>-.675 and maxx<.675}
  records.append(row)
 bpy.data.meshes.remove(me)
assert all(r['passes'] for r in records),records
out={'status':'PASS','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Read actual evaluated stringer triangles and clip each against a40mm strip directly in front of each of the four riser fronts. Require every resulting point beneath the finished next tread surface by at least40mm and inside the riser lateral envelope. Both stringers/all four knees checked. Exposed underside structure is intentionally retained. This is a component geometric check, not a load or actor test.','records':records}
(ROOT/'qa/knee_envelope_validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('ALL_EIGHT_KNEE_ENVELOPES_PASS',min(r['clearance_below_finished_top_m'] for r in records))
