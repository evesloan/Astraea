"""Bounded fresh native successor review. No game or protected batch edits."""
from pathlib import Path
import bpy
import hashlib
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parents[1]
spec = json.loads((HERE / 'source/CLINICAL_STREETS.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
glb = HERE / 'exports/AST-MED-G3-002.glb'
bpy.ops.import_scene.gltf(filepath=str(glb))
bpy.context.view_layer.update()

def gv(p):
    return Vector((p[0], -p[2], p[1]))

vertices = []
faces = []
for o in bpy.context.scene.objects:
    if o.type != 'MESH':
        continue
    o.data.calc_loop_triangles()
    base = len(vertices)
    vertices.extend(o.matrix_world @ v.co for v in o.data.vertices)
    faces.extend(tuple(base + i for i in t.vertices) for t in o.data.loop_triangles)
bvh = BVHTree.FromPolygons(vertices, faces, all_triangles=True)
samples = []
for route in spec['routes']:
    points = route['proposed_centerline_xz']
    for x, z in points:
        samples.append((route['id'], x, z))
    for a, b in zip(points, points[1:]):
        samples.append((route['id'], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
for terminal in spec['retained_terminal_interfaces']:
    for role in [terminal['role']]:
        q = terminal
        x, y, z = q['source_origin']
        side = -1 if x < 0 else 1
        samples.append((q['programme_key'] + '_' + role + '_receiver', x + side * .6, z))
        if abs(x) == 54:
            for zz in [z - 3.6, z, z + 3.6]:
                samples.append((q['programme_key'] + '_' + role + '_clean_through', side * 57, zz))
        else:
            for zz in [z - 3.6, z, z + 3.6]:
                samples.append((q['programme_key'] + '_' + role + '_clean_through', side * 102, zz))
checks = []
for name, x, z in samples:
    distances = [bvh.find_nearest(gv([x, 21 + h, z]))[3] for h in [.31, .8, 1.3, 1.65]]
    checks.append({'name': name, 'floor_point': [x, 21, z], 'minimum_native_surface_distance_m': min(distances), 'pass': min(distances) > .28})
report = {
    'status': 'PASS' if all(q['pass'] for q in checks) else 'FAIL',
    'glb_sha256': hashlib.sha256(glb.read_bytes()).hexdigest(),
    'native_vertices': len(vertices), 'native_triangles': len(faces),
    'bounded_stationary_witnesses': checks,
    'controlled_gate_operation_tested': False, 'actual_existing_receiver_opened': False,
    'scope': 'Fresh native successor source only; no floor, gate or live programme integration acceptance'
}
(HERE / 'qa/CLINICAL_STREET_NATIVE_GEOMETRY.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'witnesses': len(checks), 'failed': [q for q in checks if not q['pass']]}))
assert report['status'] == 'PASS'

# Transient QA floor is never written to the native source or runtime export.
bpy.ops.mesh.primitive_cube_add(size=1, location=gv([-57, 20.96, -404]))
o = bpy.context.object
o.name = 'QA_FLOOR_NOT_EXPORTED'
o.dimensions = (14, 18, .08)
m = bpy.data.materials.new('QA_floor')
m.diffuse_color = (.24, .28, .28, 1)
o.data.materials.append(m)
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
camera.data.lens = 25
camera.data.clip_start = .04
camera.data.clip_end = 100
camera.location = gv([-57, 22.6, -411])
camera.rotation_euler = (gv([-54.1, 22.5, -402]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/CLINICAL_corrected_crossing_native_eye.png')
bpy.ops.render.render(write_still=True)

# A separate native plan crop exposes the corrected paired diversion corners.
for o in scene.objects:
    if o.get('category') == 'overhead':
        o.hide_render = True
bpy.ops.mesh.primitive_cube_add(size=1, location=gv([-82, 20.96, -73]))
o = bpy.context.object
o.name = 'QA_DIVERSION_FLOOR_NOT_EXPORTED'
o.dimensions = (64, 40, .08)
o.data.materials.append(m)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 64
camera.location = gv([-82, 70, -73])
camera.rotation_euler = (gv([-82, 21, -73]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/CLINICAL_corrected_diversion_native_plan.png')
bpy.ops.render.render(write_still=True)
