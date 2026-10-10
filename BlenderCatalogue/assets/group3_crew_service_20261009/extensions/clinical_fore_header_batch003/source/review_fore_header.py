"""Combined native source interfaces, with no protected-source or game writes."""
from pathlib import Path
import bpy
import hashlib
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
FIRST = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009'
CLINICAL = Path('/workspace/shared/astraea_group3_crew_work/extensions/clinical_streets_batch002')
inputs = [HERE / 'exports/AST-MED-G3-003.glb', FIRST / 'exports/AST-STF-G3-002.glb', CLINICAL / 'exports/AST-MED-G3-002.glb']
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for p in inputs:
    bpy.ops.import_scene.gltf(filepath=str(p))
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
points = [
    (21, -490), (22.5, -490), (21, -495.5), (21, -496), (21, -496.5),
    (21, -499), (21, -500), (21, -503), (21, -504), (24, -500), (24, -504),
    (33, -500), (45, -500), (57, -500), (57, -492), (57, -480.5), (57, -480), (57, -479.5),
    (33, -504), (49, -504), (61, -504), (61, -493), (61, -480.5), (61, -480), (61, -479.5)
]
checks = []
for x, z in points:
    distances = [bvh.find_nearest(gv([x, 21 + h, z]))[3] for h in [.31, .8, 1.3, 1.65]]
    checks.append({'floor_point': [x, 21, z], 'minimum_native_surface_distance_m': min(distances), 'radius_m': .28, 'pass': min(distances) > .28})
report = {'status': 'PASS' if all(q['pass'] for q in checks) else 'FAIL',
          'source_input_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
          'combined_native_triangles': len(faces), 'bounded_stationary_witnesses': checks,
          'source_interface_count': 3, 'protected_or_game_sources_modified': False,
          'dynamic_cabin_or_gate_or_loaded_cart_tested': False,
          'scope': 'Fresh native combined header, reserved D05 lobby and clinical street ends. Proposed floors, actual cabin boarding, dispatch and runtime acceptance remain open.'}
(HERE / 'qa/FORE_HEADER_NATIVE_GEOMETRY.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'witnesses': len(checks), 'failed': [q for q in checks if not q['pass']]}))
assert report['status'] == 'PASS'

# Keep only the near source region for diagnostic rendering, including the real
# reserved lobby and clinical end meshes. The QA slab remains transient.
for o in list(bpy.context.scene.objects):
    if o.type != 'MESH':
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    if max(c.z for c in corners) < 20.9 or min(c.z for c in corners) > 25.4:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1, location=gv([40, 20.96, -492]))
o = bpy.context.object
o.name = 'QA_FLOOR_NOT_EXPORTED'
o.dimensions = (46, 32, .08)
material = bpy.data.materials.new('QA_floor')
material.diffuse_color = (.24, .28, .28, 1)
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
camera.data.lens = 24
camera.data.clip_start = .04
camera.data.clip_end = 120
camera.location = gv([21, 22.6, -494])
camera.rotation_euler = (gv([21, 22.5, -500]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/FORE_HEADER_combined_lobby_native_eye.png')
bpy.ops.render.render(write_still=True)
camera.location = gv([23, 22.6, -500])
camera.rotation_euler = (gv([36, 22.5, -500]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/FORE_HEADER_clean_branch_native_eye.png')
bpy.ops.render.render(write_still=True)
for o in scene.objects:
    if o.get('category') == 'overhead':
        o.hide_render = True
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 52
camera.location = gv([40, 70, -492])
camera.rotation_euler = (gv([40, 21, -492]) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(HERE / 'qa/FORE_HEADER_combined_native_plan.png')
bpy.ops.render.render(write_still=True)
