"""Small source-only architectural review captures. Does not save source changes."""
from pathlib import Path
import bpy,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/ROYALTY790_upper_candidate_r002.blend'))
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.08,.08,.08)
# Source model color preview, explicitly not final low-resolution game appearance.
colors={'ivory_enamel':(.64,.61,.54,1),'warm_stone':(.47,.46,.40,1),'warm_walnut':(.19,.09,.04,1),'champagne_metal':(.45,.34,.15,1),'HouseSmokedGlass':(.19,.35,.37,1),'GardenOpalLens':(.9,.8,.58,1)}
for m in bpy.data.materials:
 if m.name in colors:m.diffuse_color=colors[m.name]
camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=31
# Original lower bearings extend far down; hide only in the diagnostic composition.
for o in scene.objects:
 if o.name.startswith('PREVIEW_ONLY_'):o.hide_render=False
 if o.type=='MESH' and not o.name.startswith('RG_') and o.name.startswith('D17_'):o.hide_render=True

def frame(name,eye,target,cut=False):
 for o in scene.objects:
  if o.name in['RG_UpperRoof'] or o.name.startswith('RG_UpperCornice_'):o.hide_render=cut
 cam.location=(eye[0],-eye[2],eye[1]);target=Vector((target[0],-target[2],target[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(R/'evidence'/name);bpy.ops.render.render(write_still=True)
frame('source_upper_cutaway.png',[127,128,19],[103,106,40],True)
frame('source_stair_section.png',[88,109,38],[99,105,45],True)
frame('source_external.png',[126,120,22],[103,106,39],False)
print('ROYALTY_SOURCE_CAPTURES_COMPLETE')
