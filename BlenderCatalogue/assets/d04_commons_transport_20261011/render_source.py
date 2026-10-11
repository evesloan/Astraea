from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);files=[W/'D04CommonsSouthChairRouting_r001.blend',R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend',R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend',R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010/D04CommonsServiceActivity.blend',R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010/D04CommonsEntrySuccessors_r002.blend'];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.open_mainfile(filepath=str(files[0]));preimages={p['name']for p in json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json'))['preimages']}
for f in files[1:]:
 with bpy.data.libraries.load(str(f),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if not o:continue
  if 'CommonsSouthChair'in o.name or o.name in preimages:bpy.data.objects.remove(o,do_unlink=True);continue
  bpy.context.collection.objects.link(o)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.5;s.world=bpy.data.worlds.new('ScopedRoutingDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for at in [[-67,20.2,-365.8],[-64.5,20.2,-361.8]]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=240;bpy.context.object.data.size=2
images=[]
for name,at,target in [('SOURCE_SOUTH_ACTIVITY_REVISION.png',[-64.1,18.15,-368.0],[-67.0,17.2,-365.8]),('SOURCE_CART_ENTRY_REVISION.png',[-64.2,18.15,-360.4],[-64.0,17.25,-365.7])]:
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'original_south_chair_rigid_repositioned_no_rescaling':True,'diagnostic_fill':True,'final_graphics_accepted':False},indent=2)+'\n')
