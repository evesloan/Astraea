from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);P=json.load(open(W/'RUNTIME_PLAN.json'))
files=[W/'D04SocialDayroom_r001.blend',W/'D04SocialDayroomGallery_r001.blend',R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend',R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010/D04CommonsServiceActivity.blend'];pins={str(p.relative_to(R)):sha(p)for p in files}
bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for p in files[1:]:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
for pre in P['preimages']:bpy.data.objects[pre['name']].hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-2.5;s.world=bpy.data.worlds.new('SourceDiagnosticWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for l in P['lights']+json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json'))['lights']:
 bpy.ops.object.light_add(type='AREA',location=B(l['at']));bpy.context.object.data.energy=240;bpy.context.object.data.size=2
images=[]
for name,at,target in [('SOURCE_DAYROOM.png',[-76.15,18.15,-365.1],[-79.5,17.6,-371.6]),('SOURCE_ENTRY.png',[-78.5,18.15,-362.3],[-78.7,17.8,-369])]:
 assert not(W/name).exists();bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=20;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'diagnostic_fill':True,'final_game_CRT_hardware_accepted':False},indent=2)+'\n')
