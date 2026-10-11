from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=W/'D04StarboardNorthReceiving_r001.blend';pin=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.5;s.world=bpy.data.worlds.new('NorthReceivingDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for item in P['lights']:
 at=item['position'];bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=140;bpy.context.object.data.size=1.2
images=[]
for name,at,target in [('SOURCE_NORTH_PUBLIC_ARRIVAL.png',[8,18.15,-287.9],[44,17.8,-289]),('SOURCE_LOCAL_SERVICE_CELLS.png',[48,18.15,-287.2],[55.0,17.7,-291.7])]:
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
assert sha(native)==pin
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_sha256_unchanged':pin,'eye_height_m':1.65,'diagnostic_fill':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
