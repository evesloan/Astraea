"""Fresh source/export checks for forward-core and seventeen-stop derivatives.

Run with Blender 4.3.2 in background mode. This certifies saved geometry and
exchange fidelity only; game collision, routes and visual acceptance are separate.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import bmesh
from mathutils import Vector, kdtree

CAT = Path(__file__).resolve().parents[3]
CORE = CAT / 'assets/primary_atrium_core'
CABIN = CAT / 'assets/commons_lift_cabin'
FLOORS = [0, 6, 12, 16.5, 21, 27, 35.5, 44, 52.5, 61, 69.5, 78, 84, 88.5, 93, 97.5, 102]
TOL = 1e-5
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--protected-root', type=Path, default=CAT,
                    help='Read-only location of originals during isolated reproduction')
options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(points):
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


def close(a, b, label):
    assert len(a) == len(b) and max(abs(x-y) for x, y in zip(a, b)) < TOL, (label, a, b)


def oriented_triangle_key(points):
    p = [tuple(round(c, 5) for c in v) for v in points]
    return min(tuple(p[i:]+p[:i]) for i in range(3))


def geometry(source):
    meshes, corners, triangles, uv_ratios = {}, defaultdict(list), defaultdict(Counter), defaultdict(list)
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        assert mesh.uv_layers.active, obj.name
        mesh.calc_loop_triangles()
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        assert all(math.isfinite(c) for p in points for c in p), obj.name
        lo, hi = bounds(points)
        center = (Vector(lo)+Vector(hi))/2
        for tri in mesh.loop_triangles:
            p = [points[i] for i in tri.vertices]
            normal = (p[1]-p[0]).cross(p[2]-p[0])
            assert normal.length > 1e-8, (obj.name, 'degenerate')
            if source:
                assert normal.dot(sum(p, Vector())/3-center) > 1e-10, (obj.name, 'inward face')
            role = mesh.materials[tri.material_index].name
            uv = [mesh.uv_layers.active.data[i].uv.copy() for i in tri.loops]
            assert all(math.isfinite(c) for v in uv for c in v), obj.name
            uv_area = abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y) -
                          (uv[2].x-uv[0].x)*(uv[1].y-uv[0].y))
            assert uv_area > 1e-10, (obj.name, 'collapsed UV')
            ratio = uv_area/normal.length
            if source:
                scale = mesh.materials[tri.material_index].get('meters_per_tile_uv', [1, 1])
                expected = 1/(scale[0]*scale[1])
                assert abs(ratio-expected) < 2e-3, (obj.name, role, ratio, expected)
            uv_ratios[role].append(ratio)
            triangles[role][oriented_triangle_key(p)] += 1
            corners[role].extend(tuple(point)+tuple(tex) for point, tex in zip(p, uv))
        if source:
            assert not obj.modifiers, obj.name
            bm = bmesh.new()
            bm.from_mesh(mesh)
            assert all(e.is_manifold for e in bm.edges), (obj.name, 'open source')
            assert bm.calc_volume(signed=True) > 0, (obj.name, 'nonpositive volume')
            bm.free()
        meshes[obj.name] = {'points': [tuple(p) for p in points], 'bounds': [lo, hi],
                            'triangles': len(mesh.loop_triangles)}
    markers = {o.name: tuple(o.matrix_world.translation)
               for o in bpy.context.scene.objects if o.type == 'EMPTY'}
    return meshes, markers, corners, triangles, uv_ratios


def nearest_corner_deviation(a, b):
    # Join/export duplicates UV seams but must preserve each geometric/UV corner.
    tree = kdtree.KDTree(len(b))
    for i, p in enumerate(b):
        tree.insert(p[:3], i)
    tree.balance()
    max_position = max_corner = 0
    for p in set(a):
        nearby = tree.find_range(p[:3], TOL)
        assert nearby, ('missing vertex', p)
        max_position = max(max_position, min(row[2] for row in nearby))
        max_corner = max(max_corner, min(math.dist(p, b[row[1]]) for row in nearby))
    return max_position, max_corner


def validate(family, aid, markers, expected_source_count, expected_export_count):
    src, out = family/'source'/(aid+'.blend'), family/'exports'/(aid+'.glb')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    assert bpy.context.scene.unit_settings.system == 'METRIC'
    assert bpy.context.scene.unit_settings.scale_length == 1
    sm, sd, sc, st, su = geometry(True)
    assert len(sm) == expected_source_count, len(sm)
    assert set(sd) == set(markers), (set(sd)-set(markers), set(markers)-set(sd))
    for name, position in markers.items():
        close(sd[name], position, name)
    images = [n.image for m in bpy.data.materials if m.use_nodes
              for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    assert images and all(im.packed_file for im in images)
    packed = sorted({im.name for im in images})
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(out))
    em, ed, ec, et, eu = geometry(False)
    assert len(em) == expected_export_count, len(em)
    assert set(ed) == set(markers)
    for name, position in markers.items():
        close(ed[name], position, name)
    assert set(sc) == set(ec)
    assert st == et, 'Material batching changed oriented triangle surfaces or multiplicity'
    position_error = corner_error = 0
    for role in sc:
        for a, b in [(sc[role], ec[role]), (ec[role], sc[role])]:
            pd, cd = nearest_corner_deviation(a, b)
            position_error = max(position_error, pd)
            corner_error = max(corner_error, cd)
    assert position_error < TOL and corner_error < TOL, (position_error, corner_error)
    report = {
        'passed': True, 'representation': aid, 'new_unique_design_count': 0,
        'source_sha256': sha(src), 'export_sha256': sha(out), 'verifier_sha256': sha(Path(__file__)),
        'blender_version': bpy.app.version_string,
        'editable_source_meshes': len(sm), 'closed_positive_volume_source_meshes': len(sm),
        'export_meshes': len(em), 'export_triangles': sum(row['triangles'] for row in em.values()),
        'all_triangles_non_degenerate': True, 'source_faces_outward': True,
        'source_and_export_oriented_triangle_multisets_identical_per_material': True,
        'batching_preserves_concave_surface_geometry': True,
        'finite_noncollapsed_metric_uvs': True, 'packed_texture_images': packed,
        'material_roles': sorted(sc),
        'source_uv_area_per_square_metre_range_by_role': {k: [min(v), max(v)] for k, v in su.items()},
        'export_uv_area_per_square_metre_range_by_role': {k: [min(v), max(v)] for k, v in eu.items()},
        'bidirectional_vertex_max_deviation_m': position_error,
        'bidirectional_position_uv_corner_max_deviation': corner_error,
        'source_bounds_blender_xyz_m': bounds([p for row in sm.values() for p in row['points']]),
        'export_bounds_blender_xyz_m': bounds([p for row in em.values() for p in row['points']]),
        'required_source_and_export_markers_blender_xyz_m': markers,
        'scope': 'Fresh saved source and actual imported GLB geometry, UV, material and marker validation. Does not certify runtime collision, continuous routes, lift/controller behavior, species/cart fit, hull fit, visual quality or performance.',
        'runtime_and_visual_status': 'Pending separate receiving-game integration and visual review',
    }
    return report, sm


markers = {'DATUM_landing_%02d' % (i+1): (-5.4, 0, y) for i, y in enumerate(FLOORS)}
for i, y in enumerate(FLOORS):
    ceil = FLOORS[i+1]-.24 if i < 16 else 105.78
    for side in [-1, 1]:
        markers['DATUM_light_%02d_%s' % (i, side)] = (side*5.6, 0, ceil-.23)
core, meshes = validate(CORE, 'AST-CIR-005_forward_core', markers, 845, 4)
assert core['export_triangles'] == 10140
local = {name: bounds([(x, z, -y) for x, y, z in row['points']]) for name, row in meshes.items()}


def overlaps(low, high):
    return [name for name, (lo, hi) in local.items()
            if all(min(hi[i], high[i])-max(lo[i], low[i]) > TOL for i in range(3))]


guards, ends, portals, intact_walls = [], [], [], []
for i, y in enumerate(FLOORS):
    for end, z in [('Fore', -13), ('Rear', 20)]:
        for side in [-1, 1]:
            a, b = (-7.8, -4) if side < 0 else (4, 7.8)
            for h in [.14, 1.06]:
                name = 'CORE_%sWingRail_%02d_%s_%s' % (end, i, side, h)
                lo, hi = local[name]
                close(lo, [a, y+h, z-.04], name)
                close(hi, [b, y+h+.08, z+.04], name)
            for xpost in [a+.12, b-.12]:
                name = 'CORE_%sWingPost_%02d_%s_%s' % (end, i, side, xpost)
                lo, hi = local[name]
                close(lo, [xpost-.04, y, z-.04], name)
                close(hi, [xpost+.04, y+1.14, z+.04], name)
            guards.append({'level_index': i, 'side': side, 'end_local_z_m': z, 'x_span_m': [a, b]})
        assert not overlaps([-3.999, y+.001, z-.039], [3.999, y+2.8, z+.039])
        ends.append({'level_index': i, 'end_local_z_m': z, 'tested_width_m': 7.998, 'tested_height_m': 2.799})
    for side in [-1, 1]:
        if i in [0, 1] and side == -1:
            assert not overlaps([-7.9, y+.001, -2.999], [-7.5, y+3.199, 2.999])
            name = 'CORE_LateralPortalLintel_%02d_%s' % (i, side)
            lo, hi = local[name]
            close([lo[1], lo[2], hi[2]], [y+3.2, -3, 3], name)
            for prefix in ['CORE_OuterWall', 'CORE_WallDado']:
                fore = local['%s_%02d_%s_Fore' % (prefix, i, side)]
                rear = local['%s_%02d_%s_Rear' % (prefix, i, side)]
                close([fore[1][2], rear[0][2]], [-3, 3], prefix)
            portals.append({'level_index': i, 'side': side, 'nominal_width_m': 6, 'clear_height_m': 3.2})
        else:
            name = 'CORE_OuterWall_%02d_%s' % (i, side)
            lo, hi = local[name]
            close([lo[2], hi[2], lo[1]], [-13, 20, y], name)
            dado = local['CORE_WallDado_%02d_%s' % (i, side)]
            close([dado[0][2], dado[1][2]], [-13, 20], 'continuous dado')
            intact_walls.append({'level_index': i, 'side': side})
lo, hi = local['CORE_TopCover']
close(lo, [-7.88, 105.78, -13], 'cap low')
close(hi, [7.88, 105.9, 20], 'cap high')
for name in ['CORE_ShaftRear', 'CORE_ShaftNorth', 'CORE_ShaftSouth']:
    lo, hi = local[name]
    close([lo[1], hi[1]], [-.24, 105.9], name)
assert 'CORE_TopNoFurtherStair_0.14' in meshes
assert 'CORE_TopNoFurtherStair_1.06' in meshes
assert not any('_17_' in name for name in meshes), 'Eighteenth level remains'
core.update({
    'builder_sha256': sha(CORE/'source/build_forward_atrium_core.py'),
    'contract_sha256': sha(CORE/'source/forward_core_section_contract.json'),
    'floor_y_m': FLOORS, 'cap_y_m': [105.78, 105.9],
    'wing_guard_assemblies_measured': guards, 'end_plane_opening_measurements': ends,
    'lateral_portal_measurements': portals, 'intact_sidewalls_measured': intact_walls,
    'portal_levels': [0, 1], 'portal_sides': [-1],
    'intended_world_placement_gltf_xyz_m': [0, 0, -432],
    'measured_bounds_at_intended_placement_gltf_xyz_m': bounds([
        (x, z, -y-432) for row in meshes.values() for x, y, z in row['points']]),
})

markers = {'DATUM_floor_button_'+str(i): (1.73, .56+.42*(i%3), .75+.22*(i//3)) for i in range(17)}
markers.update({'DATUM_light_'+str(side): (side*1.7, 1.7, 2.6) for side in [-1, 1]})
cabin, _ = validate(CABIN, 'AST-CIR-003_seventeen_stop', markers, 24, 7)
cabin.update({'floor_button_count': 17, 'unused_eighteenth_button_absent': True,
              'builder_sha256': sha(CABIN/'source/build_seventeen_stop_cabin.py')})
_, _, derived_corners, derived_triangles, _ = geometry(False)
base_cabin = CABIN/'source/AST-CIR-003_eighteen_stop.blend'
if not base_cabin.exists():
    base_cabin = options.protected_root/'assets/commons_lift_cabin/source/AST-CIR-003_eighteen_stop.blend'
bpy.ops.wm.open_mainfile(filepath=str(base_cabin))
_, base_markers, base_corners, base_triangles, _ = geometry(True)
assert derived_triangles == base_triangles, 'Cabin derivative changed the existing physical design'
assert set(base_markers) == set(markers) | {'DATUM_floor_button_17'}
for name, position in markers.items():
    close(base_markers[name], position, 'existing button/light grid '+name)
base_corner_error = 0
for role in derived_corners:
    for a, b in [(derived_corners[role], base_corners[role]), (base_corners[role], derived_corners[role])]:
        _, deviation = nearest_corner_deviation(a, b)
        base_corner_error = max(base_corner_error, deviation)
assert base_corner_error < TOL
cabin.update({'physical_meshes_and_uvs_match_existing_eighteen_stop_cabin': True,
              'existing_eighteen_stop_source_sha256': sha(base_cabin),
              'existing_cabin_position_uv_corner_max_deviation': base_corner_error})

protected_path = CORE/'qa/forward_core_protected_hashes.json'
protected = json.loads(protected_path.read_text())['protected_existing_source_export_hashes']
assert all(sha(options.protected_root/path) == value for path, value in protected.items()), 'Protected original bytes changed'
for report, path in [(core, CORE/'qa/forward_core_validation.json'),
                     (cabin, CABIN/'qa/seventeen_stop_validation.json')]:
    report['protected_existing_source_export_files_unchanged'] = len(protected)
    report['protected_hash_inventory_sha256'] = sha(protected_path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ['representation', 'passed', 'editable_source_meshes',
          'export_meshes', 'export_triangles', 'bidirectional_vertex_max_deviation_m',
          'bidirectional_position_uv_corner_max_deviation']}, indent=2))
