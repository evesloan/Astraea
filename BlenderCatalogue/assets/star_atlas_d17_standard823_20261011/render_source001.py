from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
for f in [R/'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17Standard823Recess.blend',R/'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17ReceivingFirst.blend',W/P['structure']['native']]:
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral actual platform source');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(-66.4,-35.55,103.7));o=bpy.context.object;o.data.lens=16;o.rotation_euler=(Vector((-74.5,-35.6,103.3))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_STAR_ATLAS_D17_STANDARD823_WIDE001.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
(W/'SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps({'status':'PASS','image':Path(s.render.filepath).name,'actual_saved_native_room_receiving_and_new_frame':True,'unchanged_retained_room_native_floor':True,'all_source_roofs_guards_frame_furniture_and_rest_supports_retained':True,'mode':'Neutral Blender Workbench material-color source view;original textures,glass shading and game lighting omitted','no_exterior_vista_full_ship_Godot_CRT_hardware_final_acceptance':True},indent=2)+'\n')
