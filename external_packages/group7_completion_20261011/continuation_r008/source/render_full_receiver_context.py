"""Wide real-source theatre receiver and corrected weatherline photograph."""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
auth = json.loads((P / 'docs/AUTHORED_THEATER_SUCCESSOR.json').read_text())
native = P / auth['native']
assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
sources = []
OLD = C.parent / 'group7_hull_atrium_20261009'
for document in ['MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json', 'MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json']:
    for row in json.loads((OLD / 'docs' / document).read_text())['exports']:
        path = OLD / row['path']
        bpy.ops.import_scene.gltf(filepath=str(path))
        sources.append({'path': path.relative_to(R).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'origin': [0, 0, 0]})
for file in ['AST-HUL-001.glb', 'AST-HUL-002.glb', 'AST-CUL-005_static_003.glb',
             'AST-CUL-005_moving_003.glb', 'AST-CUL-005_bridge_002.glb',
             'AST-CUL-005_D11_exterior_call_024.glb']:
    path = R / 'Game/assets/models' / file
    bpy.ops.import_scene.gltf(filepath=str(path))
    sources.append({'path': path.relative_to(R).as_posix(),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'origin': [0, 0, 0]})
# Exact compiler triangles are only review context, with the same upward normals
# supplied by Game/scripts/ship.gd; no floor file or floor ownership is changed.
for filename in ['structural_meshes.json', 'received_structural_meshes.json']:
    path = R / 'Game/data/generated' / filename
    for row in json.loads(path.read_text())['regions']:
        vs = []; fs = []
        for tri in row['triangles']:
            fs.append(tuple(range(len(vs), len(vs)+3)))
            vs.extend((x, -z, row['floor_y']) for x, z in tri)
        me = bpy.data.meshes.new('ReviewOnly_Compiled_' + row['id']); me.from_pydata(vs, [], fs); me.update()
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f.normal.z < 0]); bm.to_mesh(me); bm.free()
        me.materials.append(bpy.data.materials['G7C3_stone'])
        ob = bpy.data.objects.new(me.name, me); bpy.context.collection.objects.link(ob)
    sources.append({'path': path.relative_to(R).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'review_helper_only': True})
scene = bpy.context.scene; scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 2000; scene.render.resolution_y = 1200; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'Standard'
scene.display.shading.light = 'STUDIO'; scene.display.shading.studiolight_rotate_z = .35
scene.display.shading.color_type = 'TEXTURE'; scene.display.shading.show_shadows = False
scene.display.shading.show_cavity = True; scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1; scene.display.shading.curvature_valley_factor = .7
scene.display.shading.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('NeutralSourceWorkbenchWorld_R008'); scene.world.color = (.72, .77, .83)
for material in bpy.data.materials:
    if material.use_nodes:
        textures = [n for n in material.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
        if textures: material.node_tree.nodes.active = textures[0]
eye = (-265, 145, -310); target = (-109, 84, -190)
cam = bpy.data.cameras.new('SOURCE_R008B_THEATER_ALL_RETAINED_RECEIVERS_WIDE')
ob = bpy.data.objects.new(cam.name, cam); scene.collection.objects.link(ob)
ob.location = (eye[0], -eye[2], eye[1]); at = Vector((target[0], -target[2], target[1]))
ob.rotation_euler = (at-ob.location).to_track_quat('-Z', 'Y').to_euler()
cam.type = 'ORTHO'; cam.ortho_scale = 210; cam.clip_start = .02; cam.clip_end = 2000; scene.camera = ob
out = P / 'qa/views'; out.mkdir(exist_ok=True)
image = out / (cam.name + '.png'); assert not image.exists()
scene.render.filepath = str(image); bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
receipt = {'status': 'CREATED_VISUAL_REVIEW_PENDING', 'selected_native': auth['native'],
           'native_sha256': auth['native_sha256'], 'image': image.relative_to(P).as_posix(),
           'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
           'eye_world_xyz': eye, 'target_world_xyz': target, 'orthographic_scale_m': 210,
           'context_source_pins': sources, 'source_natives_or_exports_resaved': False,
           'actual_source_geometry': True, 'all_original_compiled_floor_receivers_included': True, 'retained_middle_frame_and_skin_included': True,
           'renderer': 'Blender Workbench source viewport, actual UV textures, neutral studio lighting',
           'in_game_crt_final_art_hardware_acceptance': False}
(P / 'qa/SOURCE_VIEW_RECEIPT002.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('G7_R008_SOURCE_VIEW', receipt['image_sha256'], flush=True)
