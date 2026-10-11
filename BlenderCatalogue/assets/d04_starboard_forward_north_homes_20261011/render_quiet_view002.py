from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for idx,name,at,target in [(889,'SOURCE_QUIET_HOME_889_VIEW002.png',[52.95,18.15,-327.75],[55.3,17.5,-327.75])]:
 native=W/f'D04StarboardHome_{idx}_r001.blend';pin=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native))
 court=W/'D04StarboardNorthCourtsAndTransfer_r001.blend';court_pin=sha(court)
 with bpy.data.libraries.load(str(court),link=False)as(src,dst):dst.objects=src.objects
 for obj in dst.objects:
  if obj:bpy.context.collection.objects.link(obj)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 r=next(r for r in P['rooms']if r['source_index']==idx)
 for item in r['lights']:
  bpy.ops.object.light_add(type='AREA',location=B(item['at']));bpy.context.object.data.energy=160;bpy.context.object.data.size=1.2
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
 assert sha(native)==pin and sha(court)==court_pin;records.append({'image':name,'native_sha256_unchanged':pin,'court_native_sha256_unchanged':court_pin})
(W/'SOURCE_VIEW_RUN002.json').write_text(json.dumps({'status':'PASS_NATIVE_UNCHANGED','records':records,'eye_height_m':1.65,'diagnostic_fill':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
