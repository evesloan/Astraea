"""Read-only exterior-frame source views; exact retained slab context only."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
native=P/'source/natives/G7_MiddleExteriorFrame_r001.blend'
before=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False)
rows=json.loads((P/'dependencies/canonical_9d6f85/Game/data/generated/received_structural_meshes.json').read_text())['regions']
row=next(r for r in rows if r['id']=='D05_directory_05_authored_floor')
assert row['floor_y']==21
v=[];faces=[]
for t in row['triangles']:
 i=len(v);v.extend((q[0],-q[1],row['floor_y']) for q in t);faces.append((i,i+1,i+2))
me=bpy.data.meshes.new('QA exact directory05 floor');me.from_pydata(v,[],faces)
o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
m=bpy.data.materials.new('QA neutral retained floor');m.diffuse_color=(.34,.38,.41,1);me.materials.append(m)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('QA diagnostic daylight');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.71,.82,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
light=bpy.data.objects.new('QA diagnostic sun',bpy.data.lights.new('QA diagnostic sun','SUN'));s.collection.objects.link(light);light.data.energy=2;light.rotation_euler=(.6,-.3,-.5)
camera=bpy.data.objects.new('QA camera',bpy.data.cameras.new('QA camera'));s.collection.objects.link(camera);s.camera=camera
out=P/'qa/exterior_views';out.mkdir(exist_ok=True)
receipt=[]
for name,eye,target,lens,kind in [
 ('middle_frame_directory05_normal_eye',(-96,22.6,-22),(-119.7,24.5,-18),32,'Normal eye at1.6m above exact retained D05 directory05 slab; room walls/fit-out absent from diagnostic context'),
 ('middle_frame_west_diagnostic',(-156,44,-96),(-119.7,39,-86),42,'External diagnostic camera, not a supported public route or operating view'),
 ('middle_frame_forward_diagnostic',(-95,59,-575),(0,38,-490),35,'External diagnostic camera, not a supported public route or operating view')]:
 camera.location=(eye[0],-eye[2],eye[1]);q=Vector((target[0],-target[2],target[1]));camera.rotation_euler=(q-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 receipt.append({'image':s.render.filepath,'eye_world_xyz':eye,'target_world_xyz':target,'scope':kind,'lighting':'QA daylight and sun only, not new production light sources','native_sha256':before,'native_resaved':False})
assert before==hashlib.sha256(native.read_bytes()).hexdigest()
(P/'qa/middle_exterior_source_view_receipt.json').write_text(json.dumps({'views':receipt,'final_art_accepted':False,'context':'Unclosed frame source increment. No pressure skin, room windows or occupied neighbor source meshes shown.'},indent=2)+'\n')
print('MIDDLE_FRAME_SOURCE_VIEWS',len(receipt))
