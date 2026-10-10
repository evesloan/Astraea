from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2]
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((W/'PLAN.json').read_text());images=[]
room_files=[W/('D04Home_'+str(r['source_index'])+'.blend')for r in P['rooms']]
receiving=W/'D04ThirdHomesReceivingAndCourts.blend'
prior=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend'
first=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomesReceivingAndCommons.blend'
second=R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/D04SecondHomesReceivingAndCourts.blend'
door_source=R/'BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend'
guard_files=[R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/D04HomeEntryGuardSuccessors.blend',R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/D04SecondHomeEntryGuardSuccessors.blend',W/'D04ThirdHomeEntryGuardSuccessors.blend']
files=room_files+[receiving,prior,first,second,door_source]+guard_files
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
for p in guard_files:append(p)
first=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/RUNTIME_PLAN.json'))
second=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/RUNTIME_PLAN.json'))
for record in first['guard_preimages']+second['guard_preimages']+P['guard_preimages']:
 ob=bpy.data.objects.get(record['name']);assert ob is not None,record['name'];ob.hide_render=True
setup()
for room in P['rooms']:
 for item in room['lights']:light(item['at'],220,2)
for at in[[-65,19.5,-374],[-65,19.5,-366],[-44,19.5,-412],[-44,19.5,-420]]:light(at,200,3)
door_instances={}
for r in P['rooms']:
 doors=append(door_source);bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in doors};T=Matrix.Translation(Vector(B(r['entry']['origin'])))@Matrix.Rotation(r['entry']['yaw'],4,'Z');leaves=[]
 for o in doors:
  oldname=o.name
  if 'PreviewGround'in oldname:o.hide_render=True
  o.matrix_world=T@worlds[o]
  if oldname.split('.')[0].endswith('LEAF_LEFT'):leaves.append((o,-1))
  if oldname.split('.')[0].endswith('LEAF_RIGHT'):leaves.append((o,1))
  o.name='D04Entry'+str(r['source_index'])+'_'+oldname
 assert len(leaves)==2,(r['source_index'],leaves)
 door_instances[r['source_index']]=(T,leaves)
 bpy.context.view_layer.update();cz=r['entry']['origin'][2]
 view('SOURCE_ENTRY_'+str(r['source_index'])+'_CLOSED.png',[-44,18.15,cz+1.15],r['entry']['origin'][:1]+[17.75,cz],24)
for idx in[976,988]:
 T,leaves=door_instances[idx]
 for o,side in leaves:o.matrix_world.translation+=T.to_3x3()@Vector((side*.84,0,0))
 bpy.context.view_layer.update();r=next(r for r in P['rooms']if r['source_index']==idx);cz=r['entry']['origin'][2]
 view('SOURCE_ENTRY_'+str(idx)+'_OPEN.png',[-44,18.15,cz+.6],[r['entry']['origin'][0],17.75,cz],24)
for p,h in pins.items():assert sha(R/p)==h,p
(W/'SOURCE_ENTRY_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'redundant_structure_copies_hidden':True,'current_three_guard_layers_composed_unsaved':True,'original_registered_doors_rigid_instances':True,'two_open_source_leaf_poses_unsaved':True,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
