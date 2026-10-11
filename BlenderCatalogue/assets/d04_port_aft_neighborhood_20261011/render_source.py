from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={r['native']:sha(W/r['native'])for r in P['native_export_records']};records=[]
def append(native):
 with bpy.data.libraries.load(str(W/native),link=False)as(src,dst):dst.objects=src.objects
 for obj in dst.objects:
  if obj:bpy.context.collection.objects.link(obj)
for native,name,at,target,idx in [('D04PortAftCO_r001.blend','SOURCE_AFT_COMMONS001.png',[-68.1,18.15,369.5],[-79,18,369.5],None),('D04PortAftHome_972_r001.blend','SOURCE_AFT_PAIRED972_001.png',[-43,18.15,434.2],[-34.5,17.5,434.2],972),('D04PortAftHome_882_r001.blend','SOURCE_AFT_QUIET882_001.png',[-43,18.15,328],[-51,17.6,328],882)]:
 bpy.ops.wm.open_mainfile(filepath=str(W/native));append('D04PortAftCombinedStructure_r001.blend');s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 lights=P['lights']if idx is None else next(r for r in P['rooms']if r['source_index']==idx)['lights']
 for item in lights:
  bpy.ops.object.light_add(type='AREA',location=B(item['at']));bpy.context.object.data.energy=160;bpy.context.object.data.size=1.2
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);records.append(name)
for f,h in pins.items():assert sha(W/f)==h
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS_NATIVE_UNCHANGED','images':records,'native_pins_unchanged':pins,'eye_height_m':1.65,'diagnostic_fill':True,'partial_source_views':True,'moving_runtime_doors_absent':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
