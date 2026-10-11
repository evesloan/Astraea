from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);P=json.load(open(W/'RUNTIME_PLAN.json'));files=[W/'D04CommonsGardenOutlook_r001.blend',R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend',R/'BlenderCatalogue/assets/d04_commons_social_dayroom_20261011/D04SocialDayroom_r001.blend'];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for p in files[1:]:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
bpy.data.objects[P['preimage']['name']].hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.5;s.world=bpy.data.worlds.new('ScopedGardenSourceWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for at in [[-74.6,20.04,-370.5],[-71.5,20.1,-370]]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=240;bpy.context.object.data.size=2
images=[]
for item in P['outlook_cases']:
 name='SOURCE_'+item['name']+'.png';assert not(W/name).exists();bpy.ops.object.camera_add(location=B(item['eye']));o=bpy.context.object;o.data.lens=27;o.rotation_euler=(Vector(B(item['target']))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'diagnostic_fill':True,'normal_game_CRT_hardware_accepted':False},indent=2)+'\n')
