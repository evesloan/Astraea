from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));old=json.load(open(R/'Game/data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pins={f:sha(R/f)for f in P['source_pins']};bpy.ops.wm.read_factory_settings(use_empty=True)
for f in sorted({q['source_model']for q in old['moves']+old['cuts']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/f))
for q in old['runtime_preimages']:
 ob=next(o for o in bpy.data.objects if o.name.replace('.','_')==q['name']);bpy.data.objects.remove(ob,do_unlink=True)
for rec,folder in [(q,R/'BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011')for q in old['native_export_records']]+[(P['structure'],W)]:
 with bpy.data.libraries.load(str(folder/rec['native']),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.5;s.display.shading.curvature_valley_factor=1.2;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral source context');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
# Retain all walls, roofs, original furniture, guards, gates and source room geometry.
bpy.ops.object.camera_add(location=(-74.5,-6.5,18.25));o=bpy.context.object;o.data.lens=20;o.rotation_euler=(Vector((-88,-1.5,18.15))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_COMMONS_WIDE_CONTEXT003.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h
(W/'SOURCE_CONTEXT_RENDER003.json').write_text(json.dumps({'status':'PASS_SOURCE_GEOMETRY_UNCHANGED','image':'SOURCE_COMMONS_WIDE_CONTEXT003.png','mode':'Neutral studio workbench material-color geometry view; original textures and game lighting omitted','roofs_and_walls_not_hidden':True,'closed_original_gates':True,'original_commons_and_connecting_route_sources_included':True,'wider_ship_context_omitted':True,'Godot_CRT_hardware_or_final_visual_acceptance':False},indent=2)+'\n')
