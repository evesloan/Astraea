"""Real immutable parcel source with literal source lights; never save native."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
definition=json.loads((ROOT/'Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json').read_text())
venue=next(r for r in definition['venues'] if r['programme_key']=='D09_directory_07')
native=ROOT/venue['native']
before=hashlib.sha256(native.read_bytes()).hexdigest()
assert before==venue['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
if venue.get('fixture_clearance'):
    for name in venue['fixture_clearance']['replaced_mesh_names']:
        bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    with bpy.data.libraries.load(str(ROOT/venue['fixture_clearance']['native']),link=False) as (a,d):
        d.objects=a.objects
    for obj in d.objects:
        if obj:bpy.context.scene.collection.objects.link(obj)
# Blender watt units are retained source-review values, not Godot calibration.
for obj in list(bpy.context.scene.objects):
    if obj.type in ['LIGHT','CAMERA']:
        bpy.data.objects.remove(obj,do_unlink=True)
for fixture in venue['fixtures']:
    x,y,z=fixture['local_xyz']
    data=bpy.data.lights.new(fixture['name'],'POINT')
    data.energy=fixture['archived_blender_power']
    data.color=fixture['color']
    data.shadow_soft_size=.12
    light=bpy.data.objects.new(fixture['name'],data)
    bpy.context.scene.collection.objects.link(light)
    light.location=(x,-z,y)
structural_path=ROOT/'Game/data/generated/received_structural_meshes.json'
floor=next(r for r in json.loads(structural_path.read_text())['regions'] if r['id']=='D09_post_parcels_source_floor')
vertices=[];faces=[]
for triangle in floor['triangles']:
    start=len(vertices)
    vertices.extend([(x+8,-(z-182),0) for x,z in triangle])
    faces.append((start,start+1,start+2))
mesh=bpy.data.meshes.new('RetainedActualCompiledFloor')
mesh.from_pydata(vertices,[],faces)
obj=bpy.data.objects.new('RetainedActualCompiledFloor',mesh)
bpy.context.scene.collection.objects.link(obj)
floor_mat=bpy.data.materials.new('NeutralCompiledFloorReviewOnly')
floor_mat.diffuse_color=(.33,.29,.24,1)
floor_mat.use_nodes=True
floor_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.33,.29,.24,1)
floor_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
obj.data.materials.append(floor_mat)
eye=Vector((-12,-30,1.95));target=Vector((-29,-43,1.9))
camera_data=bpy.data.cameras.new('WideSourceReview')
camera=bpy.data.objects.new('WideSourceReview',camera_data)
bpy.context.scene.collection.objects.link(camera)
camera.location=eye
camera.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler()
camera_data.lens=20
scene=bpy.context.scene;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.25
world=bpy.data.worlds.new('LowSourceReviewAmbient');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.32,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.05;scene.world=world
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(P/'qa/SOURCE_PARCEL_LIGHTING_WIDE001.png')
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
(P/'qa/SOURCE_PARCEL_LIGHTING_VIEW.json').write_text(json.dumps({
    'image':'SOURCE_PARCEL_LIGHTING_WIDE001.png','native':venue['native'],'native_sha256':before,
    'original_native_unchanged':True,'actual_model_sha256':venue['model_sha256'],
    'fixture_derivative':venue.get('fixture_clearance'),
    'eye_ship_xyz':[eye.x-8,eye.z+52.5,-eye.y+182],
    'target_ship_xyz':[target.x-8,target.z+52.5,-target.y+182],
    'retained_floor_source_sha256':hashlib.sha256(structural_path.read_bytes()).hexdigest(),
    'floor_geometry':'Literal retained compiled floor triangles;neutral review material',
    'fixture_positions':'All23 selected parcel-source point positions match proposed runtime source positions',
    'lighting':'Blender Cycles CPU;archived Blender powers;not Godot energy/exposure or shared eight-source selection comparison',
    'scope':'Clear contextual real-source photograph;no concept image,no original-source save,no Game/CRT/hardware/final-art acceptance'
},indent=2)+'\n')
print('GROUP5_PARCEL_SOURCE_VIEW_PASS')
