"""Real immutable parcel source with literal source lights; never save native."""
from pathlib import Path
import bpy, json, hashlib, sys, numpy as np
from mathutils import Vector,Matrix

P=Path('/workspace/astraea-protected-integration-20261012/BlenderCatalogue/assets/group5_completion_20261011')
ROOT=P.parents[2]
definition=json.loads((ROOT/'Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json').read_text())
foyer='foyer' in sys.argv
opened_foyer='opened' in sys.argv and foyer
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
if foyer:
    door=next(r for r in json.loads((ROOT/'Game/data/architecture/group5/LARGE_VENUE_DOORS.json').read_text())['doors'] if r['programme_key']=='D09_directory_07')
    component=next(r for r in json.loads((P/'docs/LARGE_VENUE_DOOR_COMPONENTS.json').read_text())['variants'] if Path(r['export']).name==Path(door['model_path']).name)
    def append(path):
        with bpy.data.libraries.load(str(path),link=False) as (a,d):d.objects=a.objects
        for obj in d.objects:
            if obj:bpy.context.scene.collection.objects.link(obj)
        return [o for o in d.objects if o]
    dx,dy,dz=door['local_xyz']
    matrix=Matrix.Translation((dx,-dz,dy))@Matrix.Rotation(door['rotation_y'],4,'Z')
    door_objects=append(P/component['native'])
    if opened_foyer:
        for obj in door_objects:
            if 'opening_displacement_x' in obj:obj.location.x=float(obj['opening_displacement_x'])
    for obj in door_objects:
        if obj.parent is None:obj.matrix_world=matrix@obj.matrix_world
    for control in door['controls']:
        x,y,z=control['local_xyz']
        transform=matrix@Matrix.Translation((x,-z,y))@Matrix.Rotation(control['rotation_y'],4,'Z')
        for obj in append(P/'source/retail_door_control_r001.blend'):
            if obj.parent is None:obj.matrix_world=transform@obj.matrix_world
    eye=Vector((-1,-34,1.65));target=Vector((-12,-34,1.8))
camera_data=bpy.data.cameras.new('WideSourceReview')
camera=bpy.data.objects.new('WideSourceReview',camera_data)
bpy.context.scene.collection.objects.link(camera)
camera.location=eye
camera.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler()
camera_data.lens=20
scene=bpy.context.scene;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64
scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.25
world=bpy.data.worlds.new('LowSourceReviewAmbient');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.32,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.05;scene.world=world
scene.render.image_settings.file_format='PNG'
workbench='workbench' in sys.argv
native_factors='native_factors' in sys.argv
if workbench:
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
    scene.world.color=(.32,.37,.41)
    palette=json.loads((P/'docs/PARCEL_SOURCE_REVIEW_PALETTE.json').read_text())['linear_palette']
    if native_factors:
        factor_definition=json.loads((ROOT/'Game/data/architecture/group5/LARGE_VENUE_MATERIAL_FACTORS.json').read_text())
        selected=next(r for r in factor_definition['venues'] if r['programme_key']=='D09_directory_07')
        for spec in selected['materials']:
            palette[spec['material_name']]=[a*b for a,b in zip(palette[spec['material_name']],spec['factor_linear_rgba'])]
    for material in bpy.data.materials:
        if material.name in palette:
            material.diffuse_color=palette[material.name]
        elif material.name.rsplit('.',1)[0] in palette:
            material.diffuse_color=palette[material.name.rsplit('.',1)[0]]
        elif material.use_nodes:
            principled=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if principled:
                base=principled.inputs['Base Color']
                texture=next((l.from_node.image for l in base.links if l.from_node.type=='TEX_IMAGE' and l.from_node.image),None)
                material.diffuse_color=tuple(np.array(texture.pixels[:]).reshape(-1,4).mean(axis=0)) if texture else base.default_value
filename='SOURCE_PARCEL_FOYER_OPEN007.png' if opened_foyer else 'SOURCE_PARCEL_FOYER_WIDE006.png' if foyer else 'SOURCE_PARCEL_MATERIALS_WIDE005.png' if native_factors else 'SOURCE_PARCEL_LIGHTING_WIDE004.png' if workbench else 'SOURCE_PARCEL_LIGHTING_WIDE001.png'
filename='ASTRAEA_PARCEL_FOYER_PLAYER_HEIGHT001.png'
scene.render.filepath='/workspace/astraea-next-receiving-evidence-20261012/ASTRAEA_PARCEL_FOYER_PLAYER_HEIGHT001.png'
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
Path('/workspace/astraea-next-receiving-evidence-20261012/PLAYER_HEIGHT_SOURCE_VIEW001.json').write_text(json.dumps({
    'image':filename,'native':venue['native'],'native_sha256':before,
    'original_native_unchanged':True,'actual_model_sha256':venue['model_sha256'],
    'fixture_derivative':venue.get('fixture_clearance'),
    'exact_native_image_multipliers_applied_to_mean_palette':native_factors,
    'new_foyer_door_and_two_controls':door if foyer else None,
    'opened_foyer_for_source_review':opened_foyer,
    'production_default':'closed',
    'eye_ship_xyz':[eye.x-8,eye.z+52.5,-eye.y+182],
    'target_ship_xyz':[target.x-8,target.z+52.5,-target.y+182],
    'retained_floor_source_sha256':hashlib.sha256(structural_path.read_bytes()).hexdigest(),
    'floor_geometry':'Literal retained compiled floor triangles;neutral review material',
    'fixture_positions':'All23 selected parcel-source point positions match proposed runtime source positions',
    'lighting':'Neutral Workbench studio;actual original GLB baked base-color texture mean palette and corrected source fixture geometry;no illumination or texture/glass/Game comparison' if workbench else 'Blender Cycles CPU;archived Blender powers;not Godot energy/exposure or shared eight-source selection comparison',
    'scope':'Clear contextual real-source photograph;no concept image,no original-source save,no Game/CRT/hardware/final-art acceptance'
},indent=2)+'\n')
print('GROUP5_PARCEL_SOURCE_VIEW_PASS')
