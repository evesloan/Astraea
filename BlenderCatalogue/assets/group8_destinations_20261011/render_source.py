"""Wide photographs of actual native construction and retained source context.
Workbench studio presentation is explicitly separate from ordinary Godot/CRT acceptance.
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(W/'CrownInteriors_r003.blend'))
for family,filename in [('bridge_enclosure','AST-CMD-004.blend'),('bridge_platform','AST-CMD-003.blend')]:
    path=R/'BlenderCatalogue/assets'/family/'source'/filename
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
    for ob in dst.objects:
        if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update()
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.15;scene.display.shading.curvature_valley_factor=.8
scene.display.shading.background_type='WORLD';scene.world.color=(.08,.1,.13)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
cam=bpy.data.cameras.new('SourcePhotographCamera');ob=bpy.data.objects.new('SourcePhotographCamera',cam);scene.collection.objects.link(ob);scene.camera=ob;cam.lens=25
def photo(name,at,target):
    ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
photo('SOURCE_COMMAND_BRIDGE_WIDE001.png',(-29,110.2,-121),(5,108,-153))
photo('SOURCE_COMMAND_BRIDGE_WIDE002.png',(29,109.2,-164),(-9,108,-134))
(W/'SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps({'source_native':'CrownInteriors_r003.blend','retained_context':['bridge_enclosure/source/AST-CMD-004.blend','bridge_platform/source/AST-CMD-003.blend'],'images':['SOURCE_COMMAND_BRIDGE_WIDE001.png','SOURCE_COMMAND_BRIDGE_WIDE002.png'],'presentation':'Actual editable native objects; Blender Workbench studio material colours, 1600x900; no source geometry edited or persisted','not_acceptance':['Original textured finish','Godot lighting','CRT','Hardware','Whole crown','Gameplay','Engineering']},indent=2)+'\n')
