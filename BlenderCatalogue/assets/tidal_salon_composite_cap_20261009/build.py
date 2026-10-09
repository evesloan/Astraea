import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
plan=root/'Game/data/architecture/TIDAL_SALON_COMPOSITE_CAP.json'
# Bounded additive assembly: existing Salon skin remains in its own native source.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for row in json.loads(plan.read_text())['members']:
 lo,hi=row['min'],row['max']; mid=[(a+b)/2 for a,b in zip(lo,hi)];size=[b-a for a,b in zip(lo,hi)]
 bpy.ops.mesh.primitive_cube_add(size=1,location=(mid[0],-mid[2],mid[1]))
 o=bpy.context.object;o.name=row['name'];o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o['source_role']='Embedded receiving core for retained WP07_opaque_ceiling_cap';o['runtime_collision']=True
bpy.context.scene['scope']='13-member additive composite-cap core; retained Salon visible skin unchanged; fictional geometric support, no load certification.'
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).with_name('composite_cap.blend')))
