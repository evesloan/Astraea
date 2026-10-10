from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2]
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((W/'RUNTIME_PLAN.json').read_text());images=[]
room_files=[W/('D04Home_'+str(r['source_index'])+'.blend')for r in P['rooms']]
receiving=W/'D04ThirdHomesReceivingAndCourts.blend'
prior=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend'
first=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend'
second=R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/D04SecondHomesReceivingAndCourts.blend'
files=room_files+[receiving,prior,first,second]
pins={str(p.relative_to(R)):sha(p)for p in files}
def append(path):
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
 return[o for o in b.objects if o]
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3
 s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
 s.world=bpy.data.worlds.new('DiagnosticSourceWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 bpy.context.view_layer.update()
def light(p,energy=320,size=4):
 bpy.ops.object.light_add(type='AREA',location=B(p));o=bpy.context.object;o.data.energy=energy;o.data.size=size

def view(name,p,target,lens=24,ortho=None):
 bpy.ops.object.camera_add(location=B(p));o=bpy.context.object;o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=o;bpy.context.scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
bpy.ops.wm.open_mainfile(filepath=str(prior))
for p in room_files+[receiving,first,second]:append(p)
# Full native rooms and receiving source intentionally share structural parts.
# Hide only redundant unsaved diagnostic copies, preserving each actual part.
for o in bpy.data.objects:
 if o.get('category','')in['floor','frame','truss_brace']and '.'in o.name and o.name.startswith('D04H'):o.hide_render=True
for o in bpy.data.objects:
 if o.type=='MESH'and o.get('runtime_visual',True)is False:o.hide_render=True
setup()
for room in P['rooms']:
 for item in room['lights']:light(item['at'],220,2)
for at in[[-65,19.5,-374],[-65,19.5,-366],[-44,19.5,-412],[-44,19.5,-420]]:light(at,200,3)
for r in P['rooms']:
 at=list(r['outlook_world']);at[1]+=1.65;west=r['court_side']=='west';target=[at[0]+(-4.0 if west else 4.0),17.75,at[2]]
 view('SOURCE_HOME_'+str(r['source_index'])+'_PLANTED_OUTLOOK.png',at,target,24)
for p,h in pins.items():assert sha(R/p)==h,p
(W/'SOURCE_OUTLOOK_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'redundant_structure_copies_hidden':True,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
