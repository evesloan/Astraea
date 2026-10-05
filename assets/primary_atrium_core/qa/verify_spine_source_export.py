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
report,meshes=validate(CORE,"AST-CIR-005_spine_core",markers,839,4)
assert report["export_triangles"]==10068
protected=json.loads((CORE/"qa/spine_core_protected_hashes.json").read_text())
assert all(sha(CAT/path)==value for path,value in protected.items())
report["protected_original_files_unchanged"]=len(protected)
(CORE/"qa/spine_core_validation.json").write_text(json.dumps(report,indent=2)+"\n")
print(report)
