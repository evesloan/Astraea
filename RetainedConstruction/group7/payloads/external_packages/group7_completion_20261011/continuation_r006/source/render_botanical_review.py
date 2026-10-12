"""Clear source-context photographs of the four composed terrace edges."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector

P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
auth=json.loads((P/'docs/AUTHORED_SOURCE.json').read_text());native=P/auth['native']
assert hashlib.sha256(native.read_bytes()).hexdigest()==auth['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native));sources=[]
def original(path,at=(0,0,0),yaw=0,scale=1):
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));objects=list(set(bpy.data.objects)-before)
    root=bpy.data.objects.new('ImmutableContext_'+path.stem,None);bpy.context.collection.objects.link(root)
    root.location=(at[0],-at[2],at[1]);root.rotation_euler.z=yaw;root.scale=(scale,)*3
    for ob in objects:
        if ob.parent is None:ob.parent=root
    bpy.context.view_layer.update();sources.append({'path':path.relative_to(R).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'origin_world_xyz':at,'yaw':yaw,'scale':scale})
    return objects
for file in ['structural_meshes.json','received_structural_meshes.json']:
    for row in json.loads((R/'Game/data/generated'/file).read_text())['regions']:
        if 'atrium' not in row['id']:continue
        vs=[];fs=[]
        for tri in row['triangles']:
            fs.append(tuple(range(len(vs),len(vs)+3)));vs.extend((x,-z,row['floor_y'])for x,z in tri)
        mesh=bpy.data.meshes.new('Retained_'+row['id']);mesh.from_pydata(vs,[],fs);mesh.update();mesh.materials.append(bpy.data.materials['G7C6_stone'])
        ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(ob)
original(R/'Game/assets/models/AST-ATR-001.glb')
garden=original(R/'Game/assets/models/AST-GAR-001.glb',(0,6,0))
for name in ['DATUM_CANOPY_A','DATUM_CANOPY_B']:
    at=next(q for q in garden if q.name.startswith(name)).matrix_world.translation
    original(R/'Game/assets/models/AST-BOT-011.glb',(at.x,at.z,-at.y),0 if name.endswith('A') else 1.8,1 if name.endswith('A') else .82)
for row in json.loads((R/'Game/data/architecture/ATRIUM_GALLERY_RECEIVING.json').read_text())['rooms']:
    original(R/'Game/assets/models'/row['model_file'],row['origin_world_xyz'])
for row in json.loads((C/'docs/RUNTIME_INTERFACE.json').read_text()).get('models',[]):
    if '_Court_' in row.get('cell',''):
        original(R/'Game/assets/models'/row['file'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
world=bpy.data.worlds.new('BotanicalSourceReviewDaylight');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.77,.83,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.05;scene.world=world
light=bpy.data.lights.new('DiagnosticAtriumDaylight','SUN');light.energy=2.0
ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.rotation_euler=(.38,-.25,.6)
# These daylight helpers make source form legible; they do not represent the
# actual game's output or its optical/budget acceptance tested separately.
for name,at,energy,size in [('OpenVoidFill',(0,82,0),1500,35),('D12SourceFill',(-36,82.7,0),1800,18)]:
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob);ob.location=(at[0],-at[2],at[1])
out=P/'qa/views';out.mkdir(exist_ok=True);views=[]
def photograph(name,eye,target,lens):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
    ob.location=(eye[0],-eye[2],eye[1]);at=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(at-ob.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.02;data.clip_end=5000;scene.camera=ob
    image=out/(name+'.png');assert not image.exists();scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
    views.append({'image':image.relative_to(P).as_posix(),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'eye_world_xyz':eye,'target_world_xyz':target,'lens_mm':lens})
photograph('SOURCE_R006B_D12_EDGE_CONTEXT_WIDE',(-29,80.6,-30),(-43.3,79.2,0),25)
assert hashlib.sha256(native.read_bytes()).hexdigest()==auth['native_sha256']
(P/'qa/SOURCE_VIEW_RECEIPT.json').write_text(json.dumps({'status':'SOURCE_CREATED_VISUAL_REVIEW_PENDING','selected_native':auth['native'],'native_sha256':auth['native_sha256'],'views':views,'retained_context_source_pins':sources,'exact_compiled_atrium_floor_context':True,'supplemental_diagnostic_daylight':True,'native_or_original_sources_resaved':False,'in_game_crt_hardware_final_art_acceptance':False},indent=2)+'\n')
print('G7_R006_SOURCE_VIEWS',len(views),flush=True)
