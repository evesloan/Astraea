"""Measure decoded export sections and the exact retained horizontal cap."""
from pathlib import Path
import json, sys, hashlib
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
sys.path.insert(0, str(C.parent / 'group7_hull_atrium_20261009/source'))
from check_retained_exports import read, acc, nodes

def triangles(file):
    d, b = read(file); result = []
    for n, m in nodes(d):
        for primitive in d['meshes'][n['mesh']]['primitives']:
            v = acc(d, b, primitive['attributes']['POSITION'])
            v = (np.c_[v, np.ones(len(v))] @ m.T)[:, :3]
            idx = acc(d, b, primitive['indices']).ravel()
            result.append(v[idx].reshape(-1, 3, 3))
    return np.concatenate(result)

source_file = R / 'Game/assets/models/AST-HUL-002.glb'
old = triangles(source_file)
caps = [Polygon(t[:, [0, 2]]) for t in old if np.max(np.abs(t[:, 1]-92)) < .0001]
cap = unary_union(caps)
assert cap.area > 0
plan = json.loads((P / 'docs/THEATER_SEAM_PLAN.json').read_text())
e = json.loads((P / 'docs/EXPORTS.json').read_text())
models = {row['cell']: triangles(P / row['path']) for row in e['exports']}

def x_crossings(mesh, y, z):
    lo = mesh.min(1); hi = mesh.max(1)
    t = mesh[(lo[:, 1] <= y+1e-7) & (hi[:, 1] >= y-1e-7)
             & (lo[:, 2] <= z+1e-7) & (hi[:, 2] >= z-1e-7)]
    a = t[:, 1, [1, 2]] - t[:, 0, [1, 2]]
    b = t[:, 2, [1, 2]] - t[:, 0, [1, 2]]
    delta = np.array([y, z]) - t[:, 0, [1, 2]]
    determinant = a[:, 0]*b[:, 1] - a[:, 1]*b[:, 0]
    good = abs(determinant) > 1e-10
    a, b, delta, t, determinant = a[good], b[good], delta[good], t[good], determinant[good]
    u = (delta[:, 0]*b[:, 1]-delta[:, 1]*b[:, 0]) / determinant
    v = (a[:, 0]*delta[:, 1]-a[:, 1]*delta[:, 0]) / determinant
    good = (u >= -1e-6) & (v >= -1e-6) & (u+v <= 1+1e-6)
    return (t[:, 0, 0] + u*(t[:, 1, 0]-t[:, 0, 0]) + v*(t[:, 2, 0]-t[:, 0, 0]))[good]

checks = []; worst = 0
for panel in plan['panels']:
    za, zb = panel['z']
    gasket = box(-109.58, za, -109.44, zb)
    uncovered = gasket.difference(cap.buffer(.0001)).area
    assert uncovered < 1e-7, (panel['id'], uncovered)
    for u in [.02, .2, .5, .8, .98]:
        z = za+(zb-za)*u
        for y in [92.005, 92.1, 92.5, 92.999, 93.001, 93.1, 94.2, 96, 97.49]:
            xs = x_crossings(models[panel['cell']], y, z)
            outer = -109.6 + .4*(y-92)
            inner = outer + .18*np.sqrt(1+.4**2)
            assert len(xs), (panel['id'], y, z)
            errors = [float(np.min(abs(xs-x))) for x in [outer, inner]]
            assert max(errors) < .0001, (panel['id'], y, z, errors)
            worst = max(worst, *errors)
            checks.append({'cell': panel['cell'], 'z': z, 'y': y,
                           'decoded_outer_x': float(xs[np.argmin(abs(xs-outer))]),
                           'decoded_inner_x': float(xs[np.argmin(abs(xs-inner))])})
report = {'status': 'PASS', 'decoded_finite_sections': len(checks), 'sections': checks,
          'maximum_outer_inner_section_error_m': worst, 'exact_old_cap_projection_area_m2': cap.area,
          'gasket_projections_fully_within_actual_retained_cap': len(plan['panels']),
          'weather_length_m': 170, 'true_normal_skin_depth_m': .18,
          'original_skin_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
          'original_source_modified': False, 'primary_bearing_capacity_accepted': False,
          'scope': 'Exact decoded old cap and selected finite weather/body sections. This establishes source contact geometry, not watertight pressure engineering or primary support capacity.'}
(P / 'qa/FINITE_WEATHER_SECTIONS.json').write_text(json.dumps(report, indent=2)+'\n')
print('G7_R008_FINITE_SECTIONS_PASS', len(checks), 'sections', worst, 'maxError', len(plan['panels']), 'cap seats')
