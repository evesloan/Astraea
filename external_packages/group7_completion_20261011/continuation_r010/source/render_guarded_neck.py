"""Clear source-eye view of the whole guarded fore neck and retained route."""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
auth = json.loads((P/'docs/AUTHORED_GUARDS.json').read_text())
native = P/auth['native']; assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native)); sources = []
data = json.loads((R/'Game/data/architecture/GROUP7_COMPLETION.json').read_text())
for row in data['models']:
    if row['cell'] in ['G7C3_Fore_Closure', 'G7C4_Fore_NeckLanding', 'G7C4_Fore_BodySeals', 'Body_-1_00', 'Body_1_00', 'Roof_00'] or row['cell'].startswith('G7C2_Fore'):
        file = R/'Game/assets/models'/row['file']; bpy.ops.import_scene.gltf(filepath=str(file))
        sources.append({'path': file.relative_to(R).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'origin_world_xyz': [0, 0, 0]})
floorfile = R/'Game/data/generated/structural_meshes.json'
floor = next(row for row in json.loads(floorfile.read_text())['regions'] if row['id'] == 'D18_fore_route')
vs = []; fs = []
for tri in floor['triangles']:
    fs.append(tuple(range(len(vs), len(vs)+3))); vs.extend((x, -z, floor['floor_y']) for x, z in tri)
me = bpy.data.meshes.new('ReviewOnly_Exact_D18_fore_route'); me.from_pydata(vs, [], fs); me.update()
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f.normal.z < 0]); bm.to_mesh(me); bm.free()
stone = bpy.data.materials.new('ReviewOnly_RetainedCompiledFloorStone'); stone.diffuse_color = (.57, .55, .49, 1); me.materials.append(stone)
ob = bpy.data.objects.new(me.name, me); bpy.context.collection.objects.link(ob)
sources.append({'path': floorfile.relative_to(R).as_posix(), 'sha256': hashlib.sha256(floorfile.read_bytes()).hexdigest(), 'exact_receiving_region': floor['id'], 'review_helper_only': True})
scene = bpy.context.scene; scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 1800; scene.render.resolution_y = 1100; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'Standard'
scene.display.shading.light = 'STUDIO'; scene.display.shading.studiolight_rotate_z = .35
scene.display.shading.color_type = 'TEXTURE'; scene.display.shading.show_shadows = False
scene.display.shading.show_cavity = True; scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1; scene.display.shading.curvature_valley_factor = .7
scene.display.shading.background_type = 'WORLD'; scene.world = bpy.data.worlds.new('NeutralSourceWorkbenchWorld_R010'); scene.world.color = (.72, .77, .83)
for material in bpy.data.materials:
    if material.use_nodes:
        textures = [q for q in material.node_tree.nodes if q.type == 'TEX_IMAGE' and q.image]
        if textures: material.node_tree.nodes.active = textures[0]
eye = (-1.5, 108.15, -506.8); target = (0, 108.2, -524.8)
cam = bpy.data.cameras.new('SOURCE_R010_D18_FORE_GUARDED_NECK_PUBLIC_CONTEXT_WIDE')
ob = bpy.data.objects.new(cam.name, cam); scene.collection.objects.link(ob)
ob.location = (eye[0], -eye[2], eye[1]); at = Vector((target[0], -target[2], target[1]))
ob.rotation_euler = (at-ob.location).to_track_quat('-Z', 'Y').to_euler()
cam.lens = 21; cam.clip_start = .02; cam.clip_end = 140; scene.camera = ob
out = P/'qa/views'; out.mkdir(exist_ok=True); image = out/(cam.name+'.png'); assert not image.exists()
scene.render.filepath = str(image); bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest() == auth['native_sha256']
receipt = {'status': 'CREATED_VISUAL_REVIEW_PENDING', 'selected_native': auth['native'],
           'native_sha256': auth['native_sha256'], 'image': image.relative_to(P).as_posix(),
           'image_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
           'eye_world_xyz': eye, 'eye_height_over_original_floor_m': 1.65, 'target_world_xyz': target,
           'lens_mm': 21, 'far_clip_m': 140, 'context_source_pins': sources,
           'actual_source_geometry': True, 'native_or_original_sources_resaved': False,
           'renderer': 'Blender Workbench source UV texture viewport, neutral studio lighting',
           'in_game_camera_graphical_crt_hardware_or_final_art_acceptance': False}
(P/'qa/SOURCE_VIEW_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('G7_R010_SOURCE_VIEW', receipt['image_sha256'], flush=True)
