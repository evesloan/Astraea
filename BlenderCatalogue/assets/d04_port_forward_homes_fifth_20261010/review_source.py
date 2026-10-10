from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2]
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((W/'PLAN.json').read_text());images=[]
files=[W/('D04Home_'+str(r['source_index'])+'.blend')for r in P['rooms']]+[W/'D04FifthHomesReceivingAndCourts.blend',R/'BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010/D04NorthernReceivingAndTransfer_r003.blend',R/'BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend',W/'D04FifthHomeEntryGuardSuccessors.blend']
pins={str(p.relative_to(R)):sha(p)for p in files}
previous_guard=R/'BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/D04FourthHomeEntryGuardSuccessors.blend';pins[str(previous_guard.relative_to(R))]=sha(previous_guard)
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
bpy.ops.wm.open_mainfile(filepath=str(files[6]))
for p in files[:6]+[files[7]]:append(p)
append(R/'BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/D04FourthHomeEntryGuardSuccessors.blend')
# Full native rooms and receiving source intentionally share structural parts.
# Hide only redundant unsaved diagnostic copies, preserving each actual part.
for o in bpy.data.objects:
 if o.get('category','')in['floor','frame','truss_brace']and '.'in o.name and o.name.startswith('D04H'):o.hide_render=True
for o in bpy.data.objects:
 if o.type=='MESH'and o.get('runtime_visual',True)is False:o.hide_render=True
# Compose the future connected guard subsets unsaved; source originals stay pinned.
for name in ['D04NR_WestGuard_1','D04NR_EastGuard_0']:
 o=bpy.data.objects.get(name);assert o is not None;o.hide_render=True
append(files[9])
for record in P['guard_preimages']:
 ob=bpy.data.objects.get(record['name']);assert ob is not None,record['name'];ob.hide_render=True
setup()
for room in P['rooms']:
 for item in room['lights']:light(item['at'],220,2)
for item in json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010/BUILD_PLAN.json'))['lights']:light(item['at'],200,2)
for r in P['rooms']:
 west=r['court_side']=='west';a=r['allocation'];cz=r['entry']['origin'][2];front=a['allocation_x'][1]if west else a['allocation_x'][0]
 if r['allocation']['proposed_rest_place_count']==2 and not west:
  view('SOURCE_HOME_'+str(r['source_index'])+'_ACTIVITY_GALLERY.png',[front+1.5,18.15,cz-.1],[a['allocation_x'][1]-4.2,17.8,cz+1.95],24)
 else:
  view('SOURCE_HOME_'+str(r['source_index'])+'_ACTIVITY_GALLERY.png',[front+(-3.2 if west else 3.2),18.15,cz+1.3],[a['allocation_x'][0]+(3.1 if west else 9.5),17.8,cz],24)
view('SOURCE_NORTHERN_HOME_STREET.png',[-44,18.15,-318],[-44,18.15,-295.8],24)
door_instances={}
for r in [q for q in P['rooms']if q['source_index']in[970,982]]:
 doors=append(files[8]);bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in doors};T=Matrix.Translation(Vector(B(r['entry']['origin'])))@Matrix.Rotation(r['entry']['yaw'],4,'Z');leaves=[]
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
for idx in[970,982]:
 T,leaves=door_instances[idx]
 for o,side in leaves:o.matrix_world.translation+=T.to_3x3()@Vector((side*.84,0,0))
 bpy.context.view_layer.update();r=next(r for r in P['rooms']if r['source_index']==idx);cz=r['entry']['origin'][2]
 view('SOURCE_ENTRY_'+str(idx)+'_OPEN.png',[-44,18.15,cz+.6],[r['entry']['origin'][0],17.75,cz],24)
for p,h in pins.items():assert sha(R/p)==h,p
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'redundant_structure_copies_hidden':True,'current_three_guard_layers_composed_unsaved':True,'original_registered_doors_rigid_instances':True,'two_open_source_leaf_poses_unsaved':True,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
