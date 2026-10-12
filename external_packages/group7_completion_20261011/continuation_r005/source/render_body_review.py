"""Photograph the selected real source successor with immutable receiving context."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]
C = P.parent
R = C.parents[1]
OLD = C.parent / 'group7_hull_atrium_20261009'
out = P / 'qa/views'
out.mkdir(exist_ok=True)
authored = json.loads((P / 'docs/AUTHORED_BODY_SUCCESSOR.json').read_text())
native = P / authored['native']
assert hashlib.sha256(native.read_bytes()).hexdigest() == authored['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
sources = []

def append_glb(path, at=(0, 0, 0), yaw=0, scale=1):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = list(set(bpy.data.objects) - before)
    root = bpy.data.objects.new('ImmutableContext_' + path.stem, None)
    bpy.context.collection.objects.link(root)
    root.location = (at[0], -at[2], at[1])
    root.rotation_euler.z = yaw
    root.scale = (scale,) * 3
    for ob in objects:
        if ob.parent is None:
            ob.parent = root
    bpy.context.view_layer.update()
    sources.append({'path': path.relative_to(R).as_posix(),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'origin_world_xyz': at, 'rotation_y': yaw, 'scale': scale})
    return objects

for doc in ['MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json',
            'MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json']:
    for row in json.loads((OLD / 'docs' / doc).read_text())['exports']:
        append_glb(OLD / row['path'])
for row in json.loads((OLD / 'continuation_r002/docs/TERMINAL_DELIVERY_R002.json').read_text())['assemblies']:
    append_glb(OLD / 'continuation_r002' / row['export'])
    for door in row['doors']:
        append_glb(OLD / 'continuation_r002' / door['preview_export'])
for row in json.loads((C / 'continuation_r004/docs/EXPORTS.json').read_text())['exports']:
    append_glb(C / 'continuation_r004' / row['path'])
for file in ['AST-HUL-001.glb', 'AST-HUL-002.glb', 'AST-CMD-001.glb',
             'AST-CMD-002.glb', 'AST-CMD-003.glb', 'AST-CMD-004.glb',
             'AST-CMD-005.glb', 'AST-CMD-006.glb']:
    append_glb(R / 'Game/assets/models' / file)
resolution = json.loads((P / 'docs/FACADE_RESOLUTION.json').read_text())
for file in resolution['source_pins']:
    if file.endswith('.glb'):
        append_glb(R / file)
for file in ['structural_meshes.json', 'received_structural_meshes.json']:
    for row in json.loads((R / 'Game/data/generated' / file).read_text())['regions']:
        vs, fs = [], []
        for tri in row['triangles']:
            fs.append(tuple(range(len(vs), len(vs) + 3)))
            vs.extend((x, -z, row['floor_y']) for x, z in tri)
        mesh = bpy.data.meshes.new('RetainedFloor_' + row['id'])
        mesh.from_pydata(vs, [], fs)
        mesh.update()
        ob = bpy.data.objects.new(mesh.name, mesh)
        bpy.context.collection.objects.link(ob)
        mesh.materials.append(bpy.data.materials['G7C3_stone'])
garden = append_glb(R / 'Game/assets/models/AST-GAR-001.glb', (0, 6, 0))
for marker in ['DATUM_CANOPY_A', 'DATUM_CANOPY_B']:
    at = next(ob for ob in garden if ob.name.startswith(marker)).matrix_world.translation
    append_glb(R / 'Game/assets/models/AST-BOT-011.glb', (at.x, at.z, -at.y),
               0 if marker.endswith('A') else 1.8, 1 if marker.endswith('A') else .82)
append_glb(R / 'Game/assets/models/AST-ATR-001.glb')
for row in json.loads((R / 'Game/data/architecture/ATRIUM_GALLERY_RECEIVING.json').read_text())['rooms']:
    append_glb(R / 'Game/assets/models' / row['model_file'], row['origin_world_xyz'])

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.cycles.use_denoising = False  # supplied build has no usable denoiser
scene.render.resolution_x = 1800
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
world = bpy.data.worlds.new('SourceReviewDaylight_R005')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.69, .74, .80, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .9
scene.world = world
light = bpy.data.lights.new('Diagnostic daylight_R005', 'SUN')
light.energy = 2.2
ob = bpy.data.objects.new(light.name, light)
scene.collection.objects.link(ob)
ob.rotation_euler = (.45, -.6, -.25)
eye, target = (840, 720, -940), (0, 52, 0)
cam = bpy.data.cameras.new('SOURCE_R005_BODY_WIDE')
ob = bpy.data.objects.new(cam.name, cam)
scene.collection.objects.link(ob)
ob.location = (eye[0], -eye[2], eye[1])
at = Vector((target[0], -target[2], target[1]))
ob.rotation_euler = (at - ob.location).to_track_quat('-Z', 'Y').to_euler()
cam.type = 'ORTHO'
cam.ortho_scale = 1200
cam.clip_start = .02
cam.clip_end = 5000
scene.camera = ob
image = out / 'SOURCE_R005_BODY_WIDE.png'
assert not image.exists()
scene.render.filepath = str(image)
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest() == authored['native_sha256']
receipt = {'status': 'CREATED_VISUAL_REVIEW_PENDING', 'selected_native': authored['native'],
           'native_sha256': authored['native_sha256'], 'image': image.relative_to(P).as_posix(),
           'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
           'eye_world_xyz': eye, 'target_world_xyz': target, 'orthographic_scale_m': 1200,
           'context_source_pins': sources, 'source_natives_or_exports_resaved': False,
           'diagnostic_daylight': True, 'actual_source_geometry': True,
           'in_game_crt_final_art_hardware_acceptance': False}
(P / 'qa/SOURCE_VIEW_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('G7_R005_SOURCE_VIEW', receipt['image_sha256'], flush=True)
