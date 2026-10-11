from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];O=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);files=[O/'D04CommonsServiceActivity.blend',O/'D04CommonsClosedStockProducts_r002.blend',W/'D04HorticulturalWorkbay.blend',W/'D04GardenServiceSashes_r002.blend',W/'D04GardenServiceControl.blend'];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.read_factory_settings(use_empty=True)
for p in files:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
bpy.data.objects['D04CS_QuietGardenGlass'].hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=10;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('DiagnosticSourceWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for l in P['lights']+json.load(open(O/'PLAN.json'))['lights']:
 bpy.ops.object.light_add(type='AREA',location=B(l['at']));o=bpy.context.object;o.data.energy=240;o.data.size=2
images=[]
for name,at,target in [('SOURCE_HORTICULTURAL_WORKBAY.png',[-66.3,18.15,-360.8],[-67.1,17.6,-357.1]),('SOURCE_GARDEN_CLOSED.png',[-82.2,18.15,-359.95],[-82.4,18,-357])]:
 bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=18;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for q in P['sashes']:
 o=bpy.data.objects[q['name']];pivot=Vector(B(q['pivot']));o.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(60),4,'X')@Matrix.Translation(-pivot)@o.matrix_world
bpy.ops.object.camera_add(location=B([-82.2,18.15,-359.95]));o=bpy.context.object;o.data.lens=18;o.rotation_euler=(Vector(B([-82.4,18,-357]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_GARDEN_OPEN_SERVICE.png');bpy.ops.render.render(write_still=True);images.append('SOURCE_GARDEN_OPEN_SERVICE.png')
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'ordinary_Godot_CRT_hardware_accepted':False},indent=2)+'\n')
