"""Bounded fresh-native fits inside the actual retained D03 receiving enclosure."""
from pathlib import Path
import bpy
import hashlib
import json
import math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
spec = json.loads((HERE / 'source/DEPOT_RECEIVING.json').read_text())
deps = {q['catalogue_id']: q for q in spec['reused_asset_dependencies']}
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version = 0

def gv(p):
    return Vector((p[0], -p[2], p[1]))

def import_exact(path):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.context.scene.objects if o not in before]

new_path = HERE / 'exports/AST-STF-G3-005.glb'
new_objects = import_exact(new_path)
enclosure_path = ROOT / deps['AST-STF-009']['path']
assert hashlib.sha256(enclosure_path.read_bytes()).hexdigest() == deps['AST-STF-009']['sha256']
enclosure = import_exact(enclosure_path)
instances = {}
hinges = []
for q in spec['reused_asset_instances']:
    path = ROOT / deps[q['asset']]['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == deps[q['asset']]['sha256']
    objects = import_exact(path)
    parent = bpy.data.objects.new(q['name'], None)
    bpy.context.collection.objects.link(parent)
    for o in objects:
        if o.parent not in objects:
            o.parent = parent
    parent.location = gv(q['position'])
    parent.rotation_euler.z = q['yaw']
    bpy.context.view_layer.update()
    instances[q['name']] = objects
    if q['asset'] == 'AST-STF-007':
        hinge = next(o for o in objects if 'door_hinge_pivot' in o.name)
        hinges.append((hinge, hinge.matrix_world.copy()))

def bvh_for(objects):
    vertices, faces = [], []
    for o in objects:
        if o.type != 'MESH':
            continue
        o.data.calc_loop_triangles()
        base = len(vertices)
        vertices.extend(o.matrix_world @ v.co for v in o.data.vertices)
        faces.extend(tuple(base + i for i in t.vertices) for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(vertices, faces, all_triangles=True), vertices, faces

bpy.context.view_layer.update()
enclosure_bvh, _, _ = bvh_for(enclosure)
floor_contacts, component_bounds = [], []
for q in spec['reused_asset_instances']:
    _, vertices, _ = bvh_for(instances[q['name']])
    component_bounds.append({'instance': q['name'], 'asset': q['asset'], 'position': q['position'], 'yaw': q['yaw'],
                             'world_aabb': [min(v.x for v in vertices), max(v.x for v in vertices), min(v.z for v in vertices), max(v.z for v in vertices), min(-v.y for v in vertices), max(-v.y for v in vertices)]})
    if q['asset'] == 'AST-ENG-003':
        continue
    low = min(v.z for v in vertices)
    floor_contacts.append({'instance': q['name'], 'actual_lowest_y': low, 'compiled_floor_y': 12, 'pass': abs(low - 12) < .002})

console_bvh, _, _ = bvh_for(instances['DepotMaintenanceConsole'])
console_contacts = []
for z in [-214.5 - .305, -214.5 + .305]:
    for y in [13.45 - .221, 13.45 + .221]:
        point = [-48.12, y, z]
        wall_distance = enclosure_bvh.find_nearest(gv(point))[3]
        pad_distance = console_bvh.find_nearest(gv(point))[3]
        console_contacts.append({'world_pad': point, 'actual_native_wall_distance_m': wall_distance, 'actual_native_pad_distance_m': pad_distance, 'pass': max(wall_distance, pad_distance) < .002})
fixture_bvh, _, _ = bvh_for([o for o in new_objects if o.type == 'MESH' and o.get('category') == 'fixture_support'])
fixture_contacts = []
for x in [-50.9, -50.1]:
    for z in [-216.01, -215.79]:
        point = [x, 15.2, z]
        ceiling_distance = enclosure_bvh.find_nearest(gv(point))[3]
        backplate_distance = fixture_bvh.find_nearest(gv(point))[3]
        fixture_contacts.append({'world_support_point': point, 'actual_native_ceiling_distance_m': ceiling_distance, 'actual_native_fixture_distance_m': backplate_distance, 'pass': max(ceiling_distance, backplate_distance) < .002})

checks = []
for angle in [0, -45, -105]:
    for hinge, closed in hinges:
        origin = closed.translation
        hinge.matrix_world = Matrix.Translation(origin) @ Matrix.Rotation(math.radians(angle), 4, 'Z') @ Matrix.Translation(-origin) @ closed
    bpy.context.view_layer.update()
    bvh, _, _ = bvh_for(bpy.context.scene.objects)
    for q in spec['operator_and_maintenance_approaches']:
        x, y, z = q['position']
        distances = [bvh.find_nearest(gv([x, y + h, z]))[3] for h in [.31, .8, 1.3, 1.65]]
        checks.append({'name': q['name'], 'floor_point': q['position'], 'cabinet_angle_degrees': angle, 'minimum_native_surface_distance_m': min(distances), 'radius_m': .28, 'pass': min(distances) > .28})
for hinge, closed in hinges:
    hinge.matrix_world = closed
bpy.context.view_layer.update()
bvh, vertices, faces = bvh_for(bpy.context.scene.objects)
all_checks = checks + floor_contacts + console_contacts + fixture_contacts
passed = all(q['pass'] for q in all_checks)
report = {'status': 'PASS' if passed else 'FAIL', 'new_export_sha256': hashlib.sha256(new_path.read_bytes()).hexdigest(), 'reused_dependency_hashes': {q['catalogue_id']: q['sha256'] for q in spec['reused_asset_dependencies']}, 'fitted_native_triangles': len(faces), 'bounded_stationary_witnesses': checks, 'actual_native_component_bounds': component_bounds, 'actual_native_floor_contacts': floor_contacts, 'actual_console_pad_wall_contacts': console_contacts, 'actual_fixture_ceiling_contacts': fixture_contacts, 'existing_cart_identity_reassigned_or_spawned': False, 'stock_restocks_or_dynamic_cart_or_full_depot_accepted': False, 'scope': 'Fresh native retained enclosure, fixture and exact rigid component proposals; three cabinet poses and fixed contacts only. No actual-main or loaded physical cart test.'}
(HERE / 'qa/DEPOT_NATIVE_GEOMETRY.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'stationary_witnesses': len(checks), 'floor_contacts': len(floor_contacts), 'console_contacts': len(console_contacts), 'fixture_contacts': len(fixture_contacts), 'failed': [q for q in all_checks if not q['pass']]}))
assert passed

# A separate editable fitted assembly retains the original exact assets, with no
# duplicate runtime export. General floors below are transient diagnostic data.
bpy.context.scene['review_scope'] = 'Retained D03 depot receiving threshold only; no operational or full-depot acceptance'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'source/D03_depot_fitted_assembly.blend'), compress=True)

# Actual compiled support is transient diagnostic data, never exported.
compiled = json.loads((ROOT / 'Game/data/generated/structural_meshes.json').read_text())
row = next(q for q in compiled['regions'] if q['id'] == 'D03_port_forward_staff_floor_0')
floor_mat = bpy.data.materials.new('ActualCompiledFloor_QA_ONLY')
floor_mat.diffuse_color = (.21, .25, .26, 1)
verts, faces = [], []
for tri in row['triangles']:
    base = len(verts)
    verts.extend(gv([x, 12, z]) for x, z in tri)
    faces.append(tuple(base + i for i in range(3)))
mesh = bpy.data.meshes.new('QA_actual_compiled_floor')
mesh.from_pydata(verts, [], faces)
obj = bpy.data.objects.new('QA_actual_compiled_floor_NOT_EXPORTED', mesh)
bpy.context.collection.objects.link(obj)
mesh.materials.append(floor_mat)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 640
scene.render.resolution_y = 400
scene.render.resolution_percentage = 100
scene.world.color = (.15, .15, .15)
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.background_type = 'WORLD'
scene.display.shading.show_object_outline = False
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.lens = 24
camera.data.clip_start = .04
camera.data.clip_end = 30
views = [
    ('D03_depot_receiving_native_eye.png', [-53.75, 13.6, -216.15], [-50.5, 13.0, -217.2]),
    ('D03_depot_maintenance_cart_native_eye.png', [-53.6, 13.6, -215.9], [-49.7, 13.1, -214.4]),
]
for name, position, target in views:
    camera.location = gv(position)
    camera.rotation_euler = (gv(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(HERE / 'qa' / name)
    bpy.ops.render.render(write_still=True)
# Explicit transient ceiling cutaway; the saved assembly and exports stay whole.
import bmesh
for o in enclosure:
    if o.type == 'MESH' and o.get('deck') == 3:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        remove = [f for f in bm.faces if min((o.matrix_world @ v.co).z for v in f.verts) > 14.9]
        bmesh.ops.delete(bm, geom=remove, context='FACES')
        bm.to_mesh(o.data)
        bm.free()
for o in new_objects:
    o.hide_render = True
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.3
camera.location = gv([-51.5, 20, -216])
camera.rotation_euler = (gv([-51.5, 12, -216]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/D03_depot_fitted_native_plan.png')
bpy.ops.render.render(write_still=True)
