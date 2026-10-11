from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);files=[W/'D04CommonsServiceActivity.blend',W/'D04CommonsEntrySuccessors.blend',R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend',R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend'];pins={str(p.relative_to(R)):sha(p)for p in files}
bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for p in files[1:]:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
# Compose the future connected slice without modifying native originals.
for q in P['preimages']:
 o=bpy.data.objects.get(q['name']);assert o is not None,q['name'];o.hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('DiagnosticSourceWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for l in P['lights']+json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'))['lights']:
 bpy.ops.object.light_add(type='AREA',location=B(l['at']));o=bpy.context.object;o.data.energy=240;o.data.size=2
images=[]
p=W/'D04CommonsClosedStockProducts.blend';pins[str(p.relative_to(R))]=sha(p)
with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.object.camera_add(location=B([-76.8,18.15,-359.5]));o=bpy.context.object;o.data.lens=20;o.rotation_euler=(Vector(B([-77.9,17.3,-357.2]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_STAGED_PRODUCTS.png');bpy.ops.render.render(write_still=True);images.append('SOURCE_STAGED_PRODUCTS.png')
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_PRODUCT_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
