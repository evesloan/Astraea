"""Fresh checks of the reconstructed derivative; no historical receipt is reused.

blender --background --threads 4 --python assets/primary_atrium_core/qa/verify_upper_link.py -- --render
Render mode makes labelled diagnostic cutaways from the actual imported GLB,
without modifying either delivered source or export. This is not runtime QA.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
AID = 'AST-CIR-005_upper_link'
SOURCE = ROOT / 'source' / (AID + '.blend')
EXPORT = ROOT / 'exports' / (AID + '.glb')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
TOL = 1e-5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def geometry(source=False):
    meshes = {}
    uv_ratios = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        assert mesh.uv_layers.active, obj.name
        mesh.calc_loop_triangles()
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        assert all(math.isfinite(c) for v in points for c in v), obj.name
        lo, hi = bounds(points)
        center = (Vector(lo) + Vector(hi)) / 2
        corners = []
        for tri in mesh.loop_triangles:
            p = [points[i] for i in tri.vertices]
            normal = (p[1] - p[0]).cross(p[2] - p[0])
            assert normal.length > 1e-8, (obj.name, 'degenerate triangle')
            assert normal.dot(sum(p, Vector()) / 3 - center) > 0, (obj.name, 'inward face')
            uv = [mesh.uv_layers.active.data[i].uv.copy() for i in tri.loops]
            assert all(math.isfinite(c) for v in uv for c in v), obj.name
            uv_area = abs((uv[1].x - uv[0].x) * (uv[2].y - uv[0].y) -
                          (uv[2].x - uv[0].x) * (uv[1].y - uv[0].y))
            ratio = uv_area / normal.length
            assert abs(ratio - 1) < 1e-4, (obj.name, 'non-metric UV', ratio)
            uv_ratios.append(ratio)
            for point, tex in zip(p, uv):
                corners.append(tuple(point) + tuple(tex))
        if source:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            assert all(e.is_manifold for e in bm.edges), (obj.name, 'not closed')
            assert bm.calc_volume(signed=True) > 0, (obj.name, 'negative volume')
            bm.free()
            assert len(mesh.vertices) == 8 and len(mesh.polygons) == 6, obj.name
            assert not obj.modifiers, obj.name
        meshes[obj.name] = {'bounds': [lo, hi], 'points': [tuple(p) for p in points],
                            'corners': corners, 'triangles': len(mesh.loop_triangles),
                            'materials': [m.name for m in mesh.materials]}
    markers = {o.name: tuple(o.matrix_world.translation)
               for o in bpy.context.scene.objects if o.type == 'EMPTY'}
    return meshes, markers, uv_ratios


def maximum_nearest(a, b):
    # Each box has few corners, so exact exhaustive comparison is inexpensive.
    return max(min(math.dist(x, y) for y in b) for x in a)


def close(a, b, label):
    assert len(a) == len(b) and max(abs(x - y) for x, y in zip(a, b)) < TOL, (label, a, b)


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.context.scene.unit_settings.system == 'METRIC'
assert bpy.context.scene.unit_settings.scale_length == 1
source_meshes, source_markers, source_uv_ratios = geometry(source=True)
assert len(source_meshes) == 89
assert sum(m['triangles'] for m in source_meshes.values()) == 1068
used_images = [n.image for m in bpy.data.materials if m.use_nodes
               for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
assert used_images and all(im.packed_file for im in used_images)
packed_images = sorted({im.name for im in used_images})
expected_markers = {
    'DATUM_landing_01': (-5.4, 0, 0),
    'DATUM_landing_02': (-5.4, 0, 4.5),
}
for i, ceiling in enumerate([4.26, 7.73]):
    for side in [-1, 1]:
        expected_markers['DATUM_light_%02d_%s' % (i, side)] = (side * 5.6, 0, ceiling - .23)
assert set(source_markers) == set(expected_markers)
for name, expected in expected_markers.items():
    close(source_markers[name], expected, name)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(EXPORT))
import_meshes, import_markers, import_uv_ratios = geometry()
assert set(source_meshes) == set(import_meshes)
assert set(import_markers) == set(expected_markers)
point_deviation = 0
uv_corner_deviation = 0
for name, sm in source_meshes.items():
    im = import_meshes[name]
    assert sm['triangles'] == im['triangles'] == 12, name
    assert sm['materials'] == im['materials'], name
    point_deviation = max(point_deviation, maximum_nearest(sm['points'], im['points']),
                          maximum_nearest(im['points'], sm['points']))
    uv_corner_deviation = max(uv_corner_deviation, maximum_nearest(sm['corners'], im['corners']),
                              maximum_nearest(im['corners'], sm['corners']))
assert point_deviation < TOL
assert uv_corner_deviation < TOL
for name, expected in expected_markers.items():
    close(import_markers[name], expected, name)

# Check the actual imported boxes, rather than trusting the contract or builder.
# Convert Blender coordinates back to contract (x, vertical y, z around -100).
contract_bounds = {name: bounds([(x, z, -y - 100) for x, y, z in row['points']])
                   for name, row in import_meshes.items()}
guard_checks = []
for level, y in enumerate([0, 4.5]):
    for end, z in [('Fore', -113), ('Rear', -80)]:
        for side in [-1, 1]:
            a, b = (-7.8, -4) if side < 0 else (4, 7.8)
            for h in [.14, 1.06]:
                name = 'CORE_%sWingRail_%02d_%s_%s' % (end, level, side, h)
                lo, hi = contract_bounds[name]
                close(lo, [a, y+h, z-.04], name)
                close(hi, [b, y+h+.08, z+.04], name)
            for xpost in [a+.12, b-.12]:
                name = 'CORE_%sWingPost_%02d_%s_%s' % (end, level, side, xpost)
                lo, hi = contract_bounds[name]
                close(lo, [xpost-.04, y, z-.04], name)
                close(hi, [xpost+.04, y+1.14, z+.04], name)
            guard_checks.append({'floor_y_m': y, 'end_z_m': z, 'side': side,
                                 'x_span_m': [a, b], 'top_y_m': y+1.14})
lo, hi = contract_bounds['CORE_TopCover']
close(lo, [-7.88, 7.73, -113], 'cover minimum')
close(hi, [7.88, 7.85, -80], 'cover maximum')
for name in ['CORE_ShaftRear', 'CORE_ShaftNorth', 'CORE_ShaftSouth']:
    lo, hi = contract_bounds[name]
    close([lo[1], hi[1]], [-.24, 7.85], name)
for level, y in enumerate([0, 4.5]):
    lo, hi = contract_bounds['CORE_GateSpandrel_%02d' % level]
    close([lo[1], hi[1]], [y+2.82, 4.26 if level == 0 else 7.73], 'gate spandrel')
assert not any(name.startswith('CORE_StairSideRail_00') for name in import_meshes)
assert 'CORE_TopNoFurtherStair_0.14' in import_meshes
assert 'CORE_TopNoFurtherStair_1.06' in import_meshes

# Only end-plane opening clearance of this enclosure is claimed. Full paths,
# host floors, physics, stairs, lift operation and fitted species remain separate.
end_portals = []
for y in [0, 4.5]:
    for z in [-113, -80]:
        low, high = [-3.999, y+.001, z-.039], [3.999, y+2.8, z+.039]
        overlapping = [name for name, (lo, hi) in contract_bounds.items()
                       if all(min(hi[i], high[i]) - max(lo[i], low[i]) > TOL for i in range(3))]
        assert not overlapping, (low, high, overlapping)
        end_portals.append({'floor_y_m': y, 'end_z_m': z, 'tested_width_m': 7.998,
                            'tested_clear_height_m': 2.799, 'overlapping_meshes': []})

source_bounds = bounds([p for m in source_meshes.values() for p in m['points']])
import_bounds = bounds([p for m in import_meshes.values() for p in m['points']])
world_bounds = bounds([(x, z+102, -y+119) for m in import_meshes.values() for x, y, z in m['points']])
base_source = ROOT / 'source/AST-CIR-005.blend'
base_export = ROOT / 'exports/AST-CIR-005.glb'
assert sha(base_source) == '021f8d0064d0920adbb0001f14f9609cfefc6c0892c6865efb911097bb753181'
assert sha(base_export) == '524b54ad6aac1e35f68e0090b655929479c045d541c3001468a3d5cbf860769a'
report = {
    'representation': AID, 'parent_design_id': 'AST-CIR-005',
    'evidence_kind': 'Fresh reconstruction validation; historical receipts are not reused',
    'passed': True, 'blender_version': bpy.app.version_string,
    'source_sha256': sha(SOURCE), 'export_sha256': sha(EXPORT),
    'builder_sha256': sha(ROOT / 'source/build_primary_atrium_core.py'),
    'contract_sha256': sha(ROOT / 'source/upper_link_section_contract.json'),
    'verifier_sha256': sha(Path(__file__)),
    'editable_source_meshes': len(source_meshes), 'source_closed_positive_volume_meshes': len(source_meshes),
    'export_meshes': len(import_meshes), 'export_triangles': 1068,
    'all_source_and_export_faces_outward': True,
    'all_source_and_export_triangles_non_degenerate': True,
    'all_source_and_export_uvs_finite_non_degenerate': True,
    'source_uv_area_per_square_metre_range': [min(source_uv_ratios), max(source_uv_ratios)],
    'import_uv_area_per_square_metre_range': [min(import_uv_ratios), max(import_uv_ratios)],
    'packed_texture_images': packed_images,
    'source_and_import_material_roles_match': True,
    'per_mesh_bidirectional_vertex_max_deviation_m': point_deviation,
    'per_mesh_bidirectional_position_uv_corner_max_deviation': uv_corner_deviation,
    'source_bounds_blender_xyz_m': source_bounds,
    'import_bounds_blender_xyz_m': import_bounds,
    'intended_world_placement_gltf_xyz_m': [0, 102, 119],
    'measured_bounds_at_intended_placement_gltf_xyz_m': world_bounds,
    'nominal_floor_plan_xz_m': [15.6, 33],
    'nominal_floor_plan_note': 'Wall thickness and wing guard rails enlarge the physical envelope beyond the floor boundary',
    'required_source_and_import_markers': expected_markers,
    'guard_assemblies_measured': guard_checks,
    'end_plane_opening_measurements': end_portals,
    'base_source_and_export_preserved_byte_for_byte': True,
    'visual_review_status': 'Pending independent and in-engine visual review; optional renders are diagnostic cutaways',
    'scope': 'Source and actual imported GLB geometry, UV, normals, markers and end-plane openings only. Does not certify continuous routes, floor support, guard collision or infill, lift/stair use, species fit, hull fit, final art or performance.',
}
(ROOT / 'qa/upper_link_validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed','export_triangles','editable_source_meshes','per_mesh_bidirectional_vertex_max_deviation_m','per_mesh_bidirectional_position_uv_corner_max_deviation']}, indent=2))

if args.render:
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('DiagnosticWorld')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.20,.23,.28,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .8
    target = Vector((0,-3.5,3.5))
    for name, loc, power, size in [('Key',(0,4,23),7000,16),('Fill',(18,-10,13),4500,14)]:
        light = bpy.data.lights.new(name, 'AREA')
        light.energy = power
        light.size = size
        obj = bpy.data.objects.new(name, light)
        scene.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (target-obj.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(32,38,27))
    camera = bpy.context.object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 48
    scene.camera = camera
    scene.view_settings.view_transform = 'AgX'
    captures = []
    for filename, loc in [('upper_link_fore_cutaway.png',(32,38,27)),
                          ('upper_link_rear_cutaway.png',(-32,-48,27))]:
        hidden = []
        side = '_1' if loc[0] > 0 else '_-1'
        for obj in scene.objects:
            if obj.type != 'MESH':
                continue
            obj.hide_render = (obj.name == 'CORE_TopCover' or
                               (obj.name.startswith(('CORE_OuterWall','CORE_WallDado')) and obj.name.endswith(side)))
            if obj.hide_render:
                hidden.append(obj.name)
        camera.location = loc
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.use_stamp = True
        scene.render.use_stamp_note = True
        scene.render.stamp_note_text = 'AST-CIR-005 upper_link | Actual GLB diagnostic cutaway | Roof + near wall hidden; floors/stairs/cabin absent | Not runtime approval'
        scene.render.stamp_font_size = 12
        scene.render.filepath = str(ROOT / 'qa' / filename)
        bpy.ops.render.render(write_still=True)
        captures.append({'path': filename, 'sha256': sha(ROOT/'qa'/filename), 'hidden_meshes': hidden,
                         'scope': 'Actual imported GLB cutaway only; no source mesh edits or save'})
    (ROOT/'qa/upper_link_diagnostic_captures.json').write_text(json.dumps(captures, indent=2)+'\n')
