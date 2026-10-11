from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={a['native']:sha(W/a['native'])for a in P['native_export_records']};records=[]
for name,at,target in [('SOURCE_FINAL_STAIR003.png',[64.45,13.65,-371],[64.45,14.4,-379]),('SOURCE_FINAL_COMMONS003.png',[68.1,18.15,-369.5],[79,18,-369.5])]:
 bpy.ops.wm.open_mainfile(filepath=str(W/'D04StarboardFullCommons_r002.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for item in P['lights']:
  bpy.ops.object.light_add(type='AREA',location=B(item['at']));bpy.context.object.data.energy=160;bpy.context.object.data.size=1.2
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);records.append(name)
for f,h in pins.items():assert sha(W/f)==h
(W/'SOURCE_VIEW_RUN003.json').write_text(json.dumps({'status':'PASS_NATIVE_UNCHANGED','images':records,'native_pins_unchanged':pins,'eye_height_m':1.65,'diagnostic_fill':True,'partial_source_views':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
