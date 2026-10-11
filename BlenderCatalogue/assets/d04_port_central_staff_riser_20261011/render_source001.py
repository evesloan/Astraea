from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={v['native']:sha(W/v['native'])for v in P['native_export_records']};images=[]
for name,at,target in [('SOURCE_D04_CLEAN_RECEIVING001.png',[-60.4,18.15,-46],[-60.4,17.7,-38.3]),('SOURCE_D04_USED_RETURN001.png',[-63.2,18.15,-46],[-63.2,17.4,-38.4]),('SOURCE_D01_BRANCH_LANDING001.png',[-48,1.65,-97.8],[-25,1.65,-97.8])]:
 bpy.ops.wm.open_mainfile(filepath=str(W/'D04PortCentralStaffStructure_r001.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for item in P['lights']:
  pos=item['at'];bpy.ops.object.light_add(type='AREA',location=(pos[0],-pos[2],pos[1]));bpy.context.object.data.energy=70;bpy.context.object.data.size=.6
 bpy.ops.object.camera_add(location=(at[0],-at[2],at[1]));o=bpy.context.object;o.data.lens=25;o.rotation_euler=(Vector((target[0],-target[2],target[1]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);assert not(W/name).exists();bpy.ops.render.render(write_still=True);images.append(name)
for f,h in pins.items():assert sha(W/f)==h
(W/'SOURCE_VIEW_RUN001.json').write_text(json.dumps({'status':'PASS_NATIVES_UNCHANGED','images':images,'native_pins':pins,'partial_source_views':True,'diagnostic_fill':True,'controller_cabin_gates_service_doors_not_in_these_native_views':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
