from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2]
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((W/'PLAN.json').read_text())
files=[W/'D04PortForwardReceiving.blend',W/'D04StaffWallPortalSuccessor.blend',R/'BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend',R/'Game/assets/models'/P['staff_wall_cut']['source_model'],R/'Game/data/spatial_layout.json']
pins={str(p.relative_to(R)):sha(p)for p in files};images=[]
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
bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for o in bpy.data.objects:
 if o.type=='MESH' and o.get('runtime_visual',True) is False:o.hide_render=True
append(files[1])
# Original source staff network context, bounded to this D03 receiving slice;
# only the3 exact successor batch nodes are omitted. Nothing is saved/exported.
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(files[3]));bpy.context.view_layer.update();staff=[]
for o in set(bpy.data.objects)-before:
 if o.type!='MESH':continue
 vv=[o.matrix_world@Vector(v)for v in o.bound_box];lo=[min(v[i]for v in vv)for i in range(3)];hi=[max(v[i]for v in vv)for i in range(3)]
 # Blender y=-shipZ,z=shipY. Keep the actual corridor neighborhood.
 include=not(hi[0]<-66 or lo[0]>-53 or hi[1]<356 or lo[1]>445 or hi[2]<11.7 or lo[2]>15.5)
 if o.name.split('.')[0]in P['staff_wall_cut']['meshes']or not include:o.hide_render=True
 else:staff.append(o.name)
# Registered door as a rigid source instance, exact production pose.
doors=append(files[2]);bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in doors}
T=Matrix.Translation(Vector(B(P['staff_door']['origin'])))@Matrix.Rotation(P['staff_door']['yaw'],4,'Z')
for o in doors:
 if 'PreviewGround'in o.name:o.hide_render=True
 if o.parent not in doors:o.matrix_world=T@worlds[o]
bpy.context.view_layer.update()
# These small exact local slab rectangles are within original source regions
# and correspond to the216 checked witnesses/public axial arrival. Context only.
contexts=[('D03_protected_crew_cover',[-54,11.76,-466],[-8,12,-398]),('D03_port_forward_staff_floor_0',[-58.8,11.76,-445.2],[-55.2,12,-356]),('D04_fore_route',[-4,16.26,-408],[4,16.5,-402])]
for name,lo,hi in contexts:
 bpy.ops.mesh.primitive_cube_add(size=1,location=B([(a+b)/2 for a,b in zip(lo,hi)]));o=bpy.context.object;o.name='DiagnosticOriginalSlab_'+name;o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);mat=bpy.data.materials.new(o.name);mat.diffuse_color=(.42,.38,.3,1);o.data.materials.append(mat)
setup()
for p in [(-44,19.8,-405.2),(-20,19.8,-405.2),(-60,19.8,-369.5),(-68,19.8,-369.5),(-61.8,17,-379.8),(-61,14.6,-369),(-57,14.6,-369)]:light(p)
view('SOURCE_PUBLIC_BRANCH.png',[-8.5,18.15,-405.2],[-44,18,-405.2],24)
view('SOURCE_COMMONS_ENTRY.png',[-65.5,18.1,-367.8],[-69,17.5,-371],24)
view('SOURCE_STAIR_FROM_UPPER.png',[-60,18.15,-368],[-61.8,15,-379.8],24)
view('SOURCE_STAFF_DOOR_CLOSED.png',[-61,13.65,-367],[-58.8,13.3,-369],24)
for o in doors:
 if o.name.endswith('LEAF_LEFT'):o.location.x-=.84
 if o.name.endswith('LEAF_RIGHT'):o.location.x+=.84
bpy.context.view_layer.update()
view('SOURCE_STAFF_DOOR_OPEN.png',[-61,13.65,-367],[-58.8,13.3,-369],24)
hidden=[]
for o in bpy.data.objects:
 if o.get('category','')in ['roof','roof_frame']or 'Roof'in o.name:
  if not o.hide_render:o.hide_render=True;hidden.append(o.name)
view('SOURCE_FOUNDATION_CONNECTION.png',[-82,20,-418],[-40,14,-406],25)
for p,h in pins.items():assert sha(R/p)==h,p
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'unsaved_context':True,'original_staff_context_meshes':staff,'local_original_slab_context':contexts,'door_pose_from_runtime_plan':P['staff_door'],'door_opened_unsaved_for_review':True,'unsaved_roof_cutaway_hidden':hidden,'rooms_adopted':0,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
