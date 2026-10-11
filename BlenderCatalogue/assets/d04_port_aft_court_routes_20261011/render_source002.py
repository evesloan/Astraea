from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_court_routes_20261011');R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pins={f:sha(R/f)for f in P['source_pins']};bpy.ops.wm.read_factory_settings(use_empty=True)
source=json.load(open(R/'Game/data/architecture/D04_PORT_AFT_NEIGHBORHOOD.json'))
for f in [source['combinedstructure_structure']['model_file'],source['co_structure']['model_file']]+[q['model_file']for q in source['rooms']]:bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/f))
for q in P['runtime_preimages']:bpy.data.objects.remove(bpy.data.objects[q['name']],do_unlink=True)
for rec in P['native_export_records']:
 with bpy.data.libraries.load(str(W/rec['native']),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.5;s.display.shading.curvature_valley_factor=1.2;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral source context');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(-37,-289,18.2));o=bpy.context.object;o.data.lens=20;o.rotation_euler=(Vector((-24,-294,18.15))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_PORT_AFT_WIDE_NORTH002.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h
(W/'SOURCE_VIEW_RUN002.json').write_text(json.dumps({'status':'PASS_SOURCE_INPUTS_UNCHANGED','image':'SOURCE_PORT_AFT_WIDE_NORTH002.png','mode':'Neutral Workbench view of actual broad north platform and new east staff threshold','roofs_walls_fixtures_and_gates_retained':True,'gates_closed':True,'textures_glass_shading_game_lighting_and_whole_ship_context_omitted':True,'ordinary_game_CRT_hardware_final_visual_acceptance':False},indent=2)+'\n')
