from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pins={f:sha(R/f)for f in P['source_pins']};bpy.ops.wm.read_factory_settings(use_empty=True)
for f in [R/P['source_native'],W/P['structure']['native']]:
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.5;s.display.shading.curvature_valley_factor=1.2;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral actual source context');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(78,-371,18.25));o=bpy.context.object;o.data.lens=18;o.rotation_euler=(Vector((73.5,-359.5,18.15))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_STARBOARD_AFT_COMMONS_WIDE001.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h
(W/'SOURCE_CONTEXT_RENDER001.json').write_text(json.dumps({'status':'PASS_SOURCE_GEOMETRY_UNCHANGED','image':Path(s.render.filepath).name,'mode':'Neutral studio Workbench material-color actual native geometry;original textures/glass shading and game lighting omitted','source_native':P['source_native'],'additive_native':P['structure']['native'],'walls_roofs_furnishings_not_hidden':True,'wide_interior_context':True,'full_ship_context_omitted':True,'Godot_CRT_hardware_or_final_visual_acceptance':False},indent=2)+'\n')
