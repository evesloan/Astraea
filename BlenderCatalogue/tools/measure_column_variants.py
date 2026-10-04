"""Assert real source/export heights and connected shaft/capital variants."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]/'assets/structural_hospitality'
def interval(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return min(v.z for v in p),max(v.z for v in p)
results=[]
for suffix,height in [('H826',8.26),('H576',5.76),('H426',4.26),('H810',8.10)]:
 aid='AST-STR-001-'+suffix;bpy.ops.wm.open_mainfile(filepath=str(R/'source'/(aid+'.blend')))
 shaft=interval(bpy.data.objects['STR_TaperedShaft']);capital=interval(bpy.data.objects['STR_Capital']);bearing=interval(bpy.data.objects['STR_CeilingBearing'])
 assert abs(shaft[1]-(height-1.13))<1e-5
 assert capital[0]<shaft[1] and shaft[1]-capital[0]<.041
 assert abs(bearing[1]-height)<1e-5
 assert all(interval(o)[1]<=height+1e-5 for o in bpy.context.scene.objects if o.type=='MESH')
 assert all(o.data.uv_layers for o in bpy.context.scene.objects if o.type=='MESH')
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'exports'/(aid+'.glb')))
 exported=max(interval(o)[1] for o in bpy.context.scene.objects if o.type=='MESH');assert abs(exported-height)<1e-5
 results.append({'id':aid,'shaft_y':shaft,'capital_y':capital,'bearing_y':bearing,'export_height_m':exported,'source_export_height_pass':True,'shaft_capital_connection_pass':True})
(R/'COLUMN_VARIANT_GEOMETRY_CHECKS.json').write_text(json.dumps({'variants':results,'scope':'Measured geometry and UV presence; not structural-load or final-art acceptance'},indent=2)+'\n');print(results)
