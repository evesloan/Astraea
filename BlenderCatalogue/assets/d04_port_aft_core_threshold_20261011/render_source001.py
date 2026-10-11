from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={v['native']:sha(W/v['native'])for v in P['native_export_records']};pa=json.load(open(R/'BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011/PLAN.json'));record=next(v for v in pa['native_export_records']if 'CombinedStructure'in v['native']);PA=R/'BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011'/record['native'];pa_pin=sha(PA)
def append(path,core=False):
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
 for obj in dst.objects:
  if obj:
   bpy.context.collection.objects.link(obj)
   if core and obj.parent is None:obj.location.y-=272
for name,at,target in [('SOURCE_PORT_AFT_THRESHOLD_APPROACH001.png',[-13,18.15,288.7],[-5.5,18.0,288.7]),('SOURCE_PORT_AFT_THRESHOLD_CORE_RETURN001.png',[-5.4,18.15,289.0],[-13,18.1,288.7])]:
 bpy.ops.wm.open_mainfile(filepath=str(W/'D04PortAftCoreCollar_r001.blend'));append(W/'AST-CIR-005_aft_midship_d04_port_threshold_r001.blend',True);append(PA)
 for pre in P['original_runtime_guards']:
  ob=bpy.data.objects.get(pre['name']);assert ob;bpy.data.objects.remove(ob,do_unlink=True)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1;s.world=bpy.data.worlds.new('NativeDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for pos in [P['lights'][0]['at'],[-12,20.05,288.7],[-5.6,20.25,288.7]]:
  bpy.ops.object.light_add(type='AREA',location=(pos[0],-pos[2],pos[1]));bpy.context.object.data.energy=180;bpy.context.object.data.size=1.2
 bpy.ops.object.camera_add(location=(at[0],-at[2],at[1]));o=bpy.context.object;o.data.lens=25;o.rotation_euler=(Vector((target[0],-target[2],target[1]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);assert not(W/name).exists();bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(W/f)==h
assert sha(PA)==pa_pin
(W/'SOURCE_VIEW_RUN001.json').write_text(json.dumps({'status':'PASS_NATIVES_UNCHANGED','images':['SOURCE_PORT_AFT_THRESHOLD_APPROACH001.png','SOURCE_PORT_AFT_THRESHOLD_CORE_RETURN001.png'],'native_pins':pins,'retained_PA_native_sha256_unchanged':pa_pin,'partial_source_views':True,'diagnostic_fill':True,'original_compiler_core_floor_not_in_native_view':True,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
