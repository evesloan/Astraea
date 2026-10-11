from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={r['native']:sha(W/r['native'])for r in P['native_export_records']};records=[]
def append(native):
 with bpy.data.libraries.load(str(W/native),link=False)as(src,dst):dst.objects=src.objects
 for obj in dst.objects:
  if obj:bpy.context.collection.objects.link(obj)
for native,name,at,target,idx in [('D04PortCentralCO_r003.blend','SOURCE_PORT_CENTRAL_SALON003.png',[-65,18.15,0],[-83,17.8,0],None),('D04PortCentralCO_r003.blend','SOURCE_PORT_CENTRAL_QUIET003.png',[-87.8,18.15,7],[-92,17.8,7],None),('D04PortCentralCO_r003.blend','SOURCE_PORT_CENTRAL_SERVICE003.png',[-70.9,18.15,-.5],[-70.9,17.8,-7],None)]:
 bpy.ops.wm.open_mainfile(filepath=str(W/native));append('D04PortCentralCombinedStructure_r001.blend');s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 lights=P['lights']if idx is None else next(r for r in P['rooms']if r['source_index']==idx)['lights']
 for item in lights:
  bpy.ops.object.light_add(type='AREA',location=B(item['at']));bpy.context.object.data.energy=160;bpy.context.object.data.size=1.2
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);records.append(name)
for f,h in pins.items():assert sha(W/f)==h
(W/'SOURCE_VIEW_RUN003.json').write_text(json.dumps({'status':'PASS_NATIVE_UNCHANGED','images':records,'native_pins_unchanged':pins,'eye_height_m':1.65,'diagnostic_fill':True,'partial_source_views':True,'moving_runtime_doors_absent':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
