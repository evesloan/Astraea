from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'BUILD_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);native=W/P['native_file'];staff=R/'BlenderCatalogue/assets/lower_staff_network/source/AST-STF-009.blend';floor_path=R/'Game/data/generated/structural_meshes.json';pins={str(p.relative_to(R)):sha(p)for p in[native,staff,floor_path]};bpy.ops.wm.open_mainfile(filepath=str(native))
with bpy.data.libraries.load(str(staff),link=False)as(a,b):b.objects=a.objects
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
region=next(r for r in json.load(open(floor_path))['regions']if r['id']=='D03_port_forward_staff_floor_0');assert region['floor_y']==12
vs=[];fs=[]
for t in region['triangles']:
 k=len(vs);vs.extend([B([x,12,z])for x,z in t]);fs.append([k,k+1,k+2])
mesh=bpy.data.meshes.new('ExactRetainedD03CompiledFloorDiagnostic');mesh.from_pydata(vs,[],fs);mesh.update();mat=next((m for m in bpy.data.materials if'staff_rubber'in m.name),None)
if mat:mesh.materials.append(mat)
o=bpy.data.objects.new('ExactRetainedD03CompiledFloorDiagnostic',mesh);bpy.context.collection.objects.link(o);o['source_sha256']=sha(floor_path);o['source_region_id']=region['id']
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('StaffSourceDiagnosticWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
bpy.ops.object.light_add(type='AREA',location=B([-57,14.85,-338]));bpy.context.object.data.energy=180;bpy.context.object.data.size=2
bpy.ops.object.camera_add(location=B([-57,13.65,-340]));o=bpy.context.object;o.data.lens=24;o.rotation_euler=(Vector(B([-57,13.65,-328]))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_RETAINED_STAFF_CORRIDOR.png');bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_STAFF_FLOOR_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','image':'SOURCE_RETAINED_STAFF_CORRIDOR.png','native_pins_unchanged':pins,'original_compiled_floor_composed_unsaved':True,'region_id':region['id'],'floor_y':12,'source_only':True,'ordinary_graphics_CRT_hardware_accepted':False},indent=2)+'\n')
