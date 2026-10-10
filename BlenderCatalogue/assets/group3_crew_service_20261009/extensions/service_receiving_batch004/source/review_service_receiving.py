"""Fitted native bays, actual reused assets, door poses and receiving contacts."""
from pathlib import Path
import bpy
import hashlib
import json
import math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
spec = json.loads((HERE / 'source/SERVICE_RECEIVING.json').read_text())
deps = {q['catalogue_id']: q for q in spec['reused_asset_dependencies']}
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
inputs = [HERE / 'exports/AST-STF-G3-004.glb', HERE / 'exports/AST-MED-G3-003_equipment_receiving.glb']
for p in inputs:
    bpy.ops.import_scene.gltf(filepath=str(p))

def gv(p):
    return Vector((p[0], -p[2], p[1]))

instances = {}
hinges = []
for q in spec['reused_asset_instances']:
    p = ROOT / deps[q['asset']]['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == deps[q['asset']]['sha256']
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    objects = [o for o in bpy.context.scene.objects if o not in before]
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
    vertices = []
    faces = []
    for o in objects:
        if o.type != 'MESH':
            continue
        o.data.calc_loop_triangles()
        base = len(vertices)
        vertices.extend(o.matrix_world @ v.co for v in o.data.vertices)
        faces.extend(tuple(base + i for i in t.vertices) for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(vertices, faces, all_triangles=True), vertices, faces

bpy.context.view_layer.update()
bay_walls = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('source_asset') == 'AST-STF-G3-004' and o.get('category') == 'screen_wall']
wall_bvh, _, _ = bvh_for(bay_walls)
floor_contacts = []
component_bounds = []
for q in spec['reused_asset_instances']:
    _, vertices, _ = bvh_for(instances[q['name']])
    component_bounds.append({'instance': q['name'], 'asset': q['asset'], 'position': q['position'], 'yaw': q['yaw'],
                             'world_aabb': [min(v.x for v in vertices), max(v.x for v in vertices),
                                            min(v.z for v in vertices), max(v.z for v in vertices),
                                            min(-v.y for v in vertices), max(-v.y for v in vertices)]})
    if q['asset'] == 'AST-ENG-003':
        continue
    low = min(v.z for v in vertices)
    floor_contacts.append({'instance': q['name'], 'actual_native_lowest_y': low, 'required_floor_y': 21, 'pass': abs(low - 21) < .01})
console_support = []
console_bvh, _, _ = bvh_for(instances['MaintenanceConsole'])
for x in [45.5 - .305, 45.5 + .305]:
    for y in [22.45 - .221, 22.45 + .221]:
        point = [x, y, -493]
        distance = wall_bvh.find_nearest(gv(point))[3]
        pad_distance = console_bvh.find_nearest(gv(point))[3]
        console_support.append({'world_mount_point': point, 'actual_native_wall_distance_m': distance,
                                'actual_native_pad_distance_m': pad_distance, 'pass': max(distance, pad_distance) < .002})

support_bvh, _, _ = bvh_for([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('category') == 'container_support'])
container_floor_contacts = []
for q in spec['closed_staging_receivers']:
    x, y, z = q['floor_position']
    for dx in [-.35, .35]:
        for dz in [-.3, .3]:
            point = [x + dx, 21, z + dz]
            distance = support_bvh.find_nearest(gv(point))[3]
            container_floor_contacts.append({'receiver': q['name'], 'actual_floor_pad_point': point,
                                              'native_surface_distance_m': distance, 'pass': distance < .002})

gasket_bvh, _, _ = bvh_for([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('category') == 'container_gasket'])
lid_bvh, _, _ = bvh_for([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('category') == 'container_lid'])
lid_contacts = []
for q in spec['closed_staging_receivers']:
    x, y, z = q['floor_position']
    for point in [[x - .4375, 22.025, z], [x + .4375, 22.025, z], [x, 22.025, z - .3875], [x, 22.025, z + .3875]]:
        a = gasket_bvh.find_nearest(gv(point))[3]
        b = lid_bvh.find_nearest(gv(point))[3]
        lid_contacts.append({'receiver': q['name'], 'world_contact': point, 'native_gasket_distance_m': a, 'native_lid_distance_m': b, 'pass': max(a, b) < .002})

samples = list(spec['operator_and_maintenance_approaches'])
for q in spec['bays']:
    x, y, z = q['receiver']
    for offset in [-.45, 0, .45]:
        samples.append({'name': q['name'] + f'_receiver_{offset}', 'position': [x, y, z + offset]})
checks = []
for angle in [0, -45, -105]:
    for hinge, closed in hinges:
        origin = closed.translation
        hinge.matrix_world = Matrix.Translation(origin) @ Matrix.Rotation(math.radians(angle), 4, 'Z') @ Matrix.Translation(-origin) @ closed
    bpy.context.view_layer.update()
    bvh, vertices, faces = bvh_for(bpy.context.scene.objects)
    for q in samples:
        x, y, z = q['position']
        distances = [bvh.find_nearest(gv([x, y + h, z]))[3] for h in [.31, .8, 1.3, 1.65]]
        checks.append({'name': q['name'], 'floor_point': q['position'], 'cabinet_door_angle_degrees': angle,
                       'minimum_native_surface_distance_m': min(distances), 'radius_m': .28, 'pass': min(distances) > .28})
for hinge, closed in hinges:
    hinge.matrix_world = closed
bpy.context.view_layer.update()
bvh, vertices, faces = bvh_for(bpy.context.scene.objects)
passed = all(q['pass'] for q in checks + floor_contacts + container_floor_contacts + console_support + lid_contacts)
report = {'status': 'PASS' if passed else 'FAIL',
          'source_export_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
          'reused_dependency_hashes': {q['catalogue_id']: q['sha256'] for q in spec['reused_asset_dependencies']},
          'fitted_native_triangles': len(faces), 'bounded_stationary_witnesses': checks,
          'actual_native_component_bounds': component_bounds,
          'actual_native_floor_contacts': floor_contacts, 'actual_console_wall_mount_supports': console_support,
          'actual_container_floor_pad_contacts': container_floor_contacts,
          'actual_closed_lid_gasket_contacts': lid_contacts,
          'existing_custodian_cart_001_relocated': False, 'live_inventory_or_sterile_flow_or_dynamic_cart_accepted': False,
          'scope': 'Fresh native fitted service bays and exact retained components. Three bounded cabinet poses, fixed contacts and source approaches; no actual-main, loaded dynamic cart, lid/latch or stock-operation acceptance.'}
(HERE / 'qa/SERVICE_RECEIVING_NATIVE_GEOMETRY.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'stationary_witnesses': len(checks), 'floor_contacts': len(floor_contacts),
                  'console_supports': len(console_support), 'lid_contacts': len(lid_contacts),
                  'container_floor_contacts': len(container_floor_contacts),
                  'failed': [q for q in checks + floor_contacts + container_floor_contacts + console_support + lid_contacts if not q['pass']]}))
assert passed

# Diagnostic render slabs and cameras never enter the editable source exports.
material = bpy.data.materials.new('QA_floor')
material.diffuse_color = (.24, .28, .28, 1)
for name, center, dimensions in [('QA_clean_floor', [33, 20.96, -496.2], [8, 4, .08]),
                                  ('QA_maintenance_floor', [43, 20.96, -495.6], [8, 5.2, .08]),
                                  ('QA_used_floor', [43, 20.96, -507.8], [8, 4, .08])]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=gv(center))
    o = bpy.context.object
    o.name = name + '_NOT_EXPORTED'
    o.dimensions = dimensions
    o.data.materials.append(material)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 640
scene.render.resolution_y = 400
scene.render.resolution_percentage = 100
scene.world.color = (.16, .16, .16)
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
camera.data.lens = 23
camera.data.clip_start = .04
camera.data.clip_end = 80
views = [
    ('SERVICE_clean_supply_native_eye.png', [33, 22.6, -497.8], [32, 22, -495.7]),
    ('SERVICE_maintenance_native_eye.png', [43, 22.6, -497.6], [44.8, 22.3, -494.1]),
    ('SERVICE_used_closed_staging_native_eye.png', [43, 22.6, -506.2], [43, 22, -508.6])
]
for name, position, target in views:
    camera.location = gv(position)
    camera.rotation_euler = (gv(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(HERE / 'qa' / name)
    bpy.ops.render.render(write_still=True)
for o in scene.objects:
    if o.get('category') == 'overhead':
        o.hide_render = True
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 28
camera.location = gv([38, 70, -501.4])
camera.rotation_euler = (gv([38, 21, -501.4]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/SERVICE_fitted_receiving_native_plan.png')
bpy.ops.render.render(write_still=True)
