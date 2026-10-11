from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={q['native']:sha(W/q['native'])for q in P['native_export_records']};images=[]
for name,index,at,target,opened in [('SOURCE_REAR_STAFF_PORTAL001.png',0,[-98,18.1,0],[-93.8,18.1,0],True),('SOURCE_RELOCATED_SERVICE001.png',1,[-92.5,18.1,1.4],[-87.5,18.1,-2],True),('SOURCE_QUIET_GUEST_ARRIVAL001.png',0,[-81,18.1,10],[-88,18.1,7],False)]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 for f in sorted({q['source_model']for q in P['cuts']+P['moves']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/f))
 for q in P['runtime_preimages']:
  ob=next(o for o in bpy.data.objects if o.name.replace('.','_')==q['name']);bpy.data.objects.remove(ob,do_unlink=True)
 for rec in P['native_export_records']:
  with bpy.data.libraries.load(str(W/rec['native']),link=False)as(src,dst):dst.objects=src.objects
  for ob in dst.objects:
   if ob:bpy.context.collection.objects.link(ob)
 if opened:
  g=P['gates'][index];v=g['pivot'];pv=Vector((v[0],-v[2],v[1]));M=Matrix.Translation(pv)@Matrix.Rotation(-math.radians(g['candidate_open_degrees']),4,'Z')@Matrix.Translation(-pv)
  for n in g['members']:bpy.data.objects[n].matrix_world=M@bpy.data.objects[n].matrix_world
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-.5;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 z=P['gates'][index].get('z',P['gates'][index]['pivot'][2])
 for x,y,Z in [(at[0],19.35,at[2]),(target[0],19.35,target[2]),(-94.5,19.35,0)]:bpy.ops.object.light_add(type='AREA',location=(x,-Z,y));bpy.context.object.data.energy=100;bpy.context.object.data.size=.7
 bpy.ops.object.camera_add(location=(at[0],-at[2],at[1]));o=bpy.context.object;o.data.lens=25;o.rotation_euler=(Vector((target[0],-target[2],target[1]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);assert not(W/name).exists();bpy.ops.render.render(write_still=True);images.append(name)
for n,h in pins.items():assert sha(W/n)==h
(W/'SOURCE_VIEW_RUN001.json').write_text(json.dumps({'status':'PASS_NATIVES_UNCHANGED','native_pins':pins,'images':images,'partial_source_views':True,'diagnostic_fill':True,'source_floor_and_roof_present':True,'gate_open_images_are_native_pose_diagnostics_not_consent_provider_or_live_game_views':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
