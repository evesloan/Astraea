from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'BUILD_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);native=W/P['native_file'];prior=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend';pins={str(p.relative_to(R)):sha(p)for p in[native,prior]};bpy.ops.wm.open_mainfile(filepath=str(native))
with bpy.data.libraries.load(str(prior),link=False)as(a,b):b.objects=a.objects
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
removed=[]
for g in P['guard_preimages']:
 o=next(o for o in b.objects if o and o.name==g['name']);removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)==3
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('StaffSourceDiagnosticWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65

for item in P['lights']:
 bpy.ops.object.light_add(type='AREA',location=B(item['at']));o=bpy.context.object;o.data.energy=220;o.data.size=2
bpy.ops.object.camera_add(location=B([-43.8,18.15,-367.2]));o=bpy.context.object;o.data.lens=24;o.rotation_euler=(Vector(B([-43.8,18.0,-330]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_CONNECTED_NORTHERN_THRESHOLD.png');bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_CONNECTED_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','image':'SOURCE_CONNECTED_NORTHERN_THRESHOLD.png','native_pins_unchanged':pins,'only_original_guard_nodes_removed_unsaved':removed,'source_only':True,'ordinary_graphics_CRT_hardware_accepted':False},indent=2)+'\n')
