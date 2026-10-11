from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));pins={q['native']:hashlib.sha256((W/q['native']).read_bytes()).hexdigest()for q in P['native_export_records']};rows=[]
for name,mode,at,target in [('SOURCE_COMMONS_SHORT_TRANSITIONS001.png','commons',[-73.0,18,-.7],[-73,17.8,-5.5]),('SOURCE_FORE_STAFF_LANES001.png','fore',[-49,13.6,-447],[-35,13.4,-447]),('SOURCE_FORE_STAIR_AND_COURT001.png','fore',[-35,18.6,-444],[-28,17.8,-447.1])]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if mode=='commons':
  bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/D04_PORT_CENTRAL_CO_r003.glb'))
  rec=P['commons_structure']
 else:rec=P['fore_structure']
 with bpy.data.libraries.load(str(W/rec['native']),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
 for ob in bpy.data.objects:
  if ob.get('category')=='stair_walk_surface':ob.hide_render=True
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-.3;s.world=bpy.data.worlds.new('Diagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.3,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 lamps=[(-74.5,18.85,-6),(-71,18.85,-6),(-73,19.5,-1)]if mode=='commons'else[(-47,14.7,-447),(-35,14.7,-447),(-29,19.5,-447)]
 for x,y,z in lamps:bpy.ops.object.light_add(type='AREA',location=(x,-z,y));bpy.context.object.data.energy=100;bpy.context.object.data.size=.7
 bpy.ops.object.camera_add(location=(at[0],-at[2],at[1]));o=bpy.context.object;o.data.lens=25;o.rotation_euler=(Vector((target[0],-target[2],target[1]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);assert not(W/name).exists();bpy.ops.render.render(write_still=True);rows.append(name)
for n,h in pins.items():assert hashlib.sha256((W/n).read_bytes()).hexdigest()==h
(W/'SOURCE_VIEW_RUN001.json').write_text(json.dumps({'status':'PARTIAL_SOURCE_VIEWS_NATIVES_UNCHANGED','images':rows,'native_pins':pins,'diagnostic_fill':True,'commons_source_cupboard_bottles_individual_binding_meshes_omitted':True,'fore_original_underlying_cover_floor_homes_and_staff_enclosure_omitted':True,'Game_controllers_shaders_privacy_providers_omitted':True,'ordinary_game_CRT_hardware_final_accepted':False},indent=2)+'\n')
