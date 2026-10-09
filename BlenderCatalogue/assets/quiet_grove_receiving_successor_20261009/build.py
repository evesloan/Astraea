import bpy,json
from pathlib import Path
here=Path(__file__).resolve().parent
plan=json.loads((here/'RECEIVING_PLAN.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for item in plan['parts']:
 lo,hi=item['min'],item['max'];mid=[(a+b)*.5 for a,b in zip(lo,hi)];size=[b-a for a,b in zip(lo,hi)]
 bpy.ops.mesh.primitive_cube_add(size=1,location=(mid[0],-mid[2],mid[1]))
 obj=bpy.context.object;obj.name=item['name'];obj.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 obj['construction_role']=item['role'];obj['runtime_collision']=True
bpy.context.scene['scope']='Additive Quiet Grove/Library roof-composite receiving WIP; no replacement of Library source; not structural certification.'
bpy.ops.wm.save_as_mainfile(filepath=str(here/'quiet_grove_composite_support.blend'))
