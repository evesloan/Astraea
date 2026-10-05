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
    
markers=["DATUM_landing_%02d"%i for i in range(1,18)]+["DATUM_light_%02d_%s"%(i,side)for i in range(17)for side in [-1,1]]
report,meshes=validate(CORE,"AST-CIR-005_spine_core",markers,839,4)
protected=json.loads((CORE/"qa/spine_core_protected_hashes.json").read_text())
assert all(sha(CAT/path)==value for path,value in protected.items())
report["protected_original_files_unchanged"]=len(protected)
(CORE/"qa/spine_core_validation.json").write_text(json.dumps(report,indent=2)+"\n")
print(report)
