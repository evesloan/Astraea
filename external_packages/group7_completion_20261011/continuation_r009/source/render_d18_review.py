"""Wide source photograph of the raised fore neck in retained receiving context."""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
auth = json.loads((P / 'docs/AUTHORED_D18_SUCCESSOR.json').read_text())
native = P / auth['native']; assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native)); sources = []
data = json.loads((R / 'Game/data/architecture/GROUP7_COMPLETION.json').read_text())
OLD = C.parent / 'group7_hull_atrium_20261009'

def original(path):
    bpy.ops.import_scene.gltf(filepath=str(path))
    sources.append({'path': path.relative_to(R).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'origin_world_xyz': [0, 0, 0]})

for row in data['models']:
    if row['cell'] in ['Body_-1_00', 'Body_1_00', 'Roof_00', 'G7C4_Fore_BodySeals'] or row['cell'].startswith('G7C2_Fore'):
        original(R / 'Game/assets/models' / row['file'])
for document in ['MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json', 'MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json']:
    for row in json.loads((OLD / 'docs' / document).read_text())['exports']:
        original(OLD / row['path'])
original(R / 'Game/assets/models/AST-HUL-001.glb')
stone = bpy.data.materials.new('ReviewOnly_RetainedCompiledFloorStone')
stone.diffuse_color = (.57, .55, .49, 1)
for filename in ['structural_meshes.json', 'received_structural_meshes.json']:
    file = R / 'Game/data/generated' / filename
    for row in json.loads(file.read_text())['regions']:
        vs = []; fs = []
        for triangle in row['triangles']:
            fs.append(tuple(range(len(vs), len(vs)+3)))
            vs.extend((x, -z, row['floor_y']) for x, z in triangle)
        me = bpy.data.meshes.new('ReviewOnly_' + row['id']); me.from_pydata(vs, [], fs); me.update()
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f.normal.z < 0]); bm.to_mesh(me); bm.free()
        me.materials.append(stone); ob = bpy.data.objects.new(me.name, me); bpy.context.collection.objects.link(ob)
    sources.append({'path': file.relative_to(R).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'review_helper_only': True})
scene = bpy.context.scene; scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 2000; scene.render.resolution_y = 1200; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'Standard'
scene.display.shading.light = 'STUDIO'; scene.display.shading.studiolight_rotate_z = .35
scene.display.shading.color_type = 'TEXTURE'; scene.display.shading.show_shadows = False
scene.display.shading.show_cavity = True; scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1; scene.display.shading.curvature_valley_factor = .7
scene.display.shading.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('NeutralSourceWorkbenchWorld_R009'); scene.world.color = (.72, .77, .83)
for material in bpy.data.materials:
    if material.use_nodes:
        textures = [q for q in material.node_tree.nodes if q.type == 'TEX_IMAGE' and q.image]
        if textures: material.node_tree.nodes.active = textures[0]
eye = (-128, 172, -618); target = (0, 90, -521)
cam = bpy.data.cameras.new('SOURCE_R009_D18_FORE_NECK_RECEIVING_CONTEXT_WIDE')
ob = bpy.data.objects.new(cam.name, cam); scene.collection.objects.link(ob)
ob.location = (eye[0], -eye[2], eye[1]); at = Vector((target[0], -target[2], target[1]))
ob.rotation_euler = (at-ob.location).to_track_quat('-Z', 'Y').to_euler()
cam.type = 'ORTHO'; cam.ortho_scale = 170; cam.clip_start = .02; cam.clip_end = 400; scene.camera = ob
out = P / 'qa/views'; out.mkdir(exist_ok=True); image = out / (cam.name+'.png'); assert not image.exists()
scene.render.filepath = str(image); bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
receipt = {'status': 'CREATED_VISUAL_REVIEW_PENDING', 'selected_native': auth['native'],
           'native_sha256': auth['native_sha256'], 'image': image.relative_to(P).as_posix(),
           'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
           'eye_world_xyz': eye, 'target_world_xyz': target, 'orthographic_scale_m': 170, 'far_clip_m': 400,
           'context_source_pins': sources, 'actual_source_geometry': True, 'all_original_compiled_receivers_included': True,
           'native_or_original_sources_resaved': False,
           'renderer': 'Blender Workbench actual source viewport with UV textures and neutral studio lighting',
           'in_game_crt_hardware_final_art_or_primary_capacity_acceptance': False}
(P / 'qa/SOURCE_VIEW_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('G7_R009_SOURCE_VIEW', receipt['image_sha256'], flush=True)
