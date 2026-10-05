#!/usr/bin/env python3
"""Reconstructed read-only geometry harness for the independent aft-command review.

This file was reconstructed from the review's inline Python/Blender checks. It is
not an original saved execution script. It deliberately complements, rather than
invokes, verify_aft_command.py (roundtrip, moving doors and fixture exits).

Run with ordinary Python 3, not Blender's --python:
  python3 assets/aft_command/qa/independent_geometry_harness.py

Requires Blender 4.3.2-compatible bpy/bmesh through the Blender executable and
Python's standard library. No Shapely, Godot launch/import, model/contract write,
manifest change, backup action or existing-review rewrite is performed. The sole
persistent output is independent_geometry_reconstruction_validation.json beside
this file. Missing baseline files are materialized only under a temporary folder.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile


BASELINE_COMMIT = "5918f89a9ff913bd6077f2a7464f4bef66292dac"
PRELIGHT_COMMIT = "80ee80f07b1a39ddef87e0660c20e9ccb57dc450"
PRELIGHT_BLEND_SHA256 = "b5fbe7ce676ae50824151b48039f4b53bebae6897b918d78b408d407b33222e3"
PRELIGHT_PARTS_SHA256 = "b49ba3ed95079a36481b121fb17e1af40d776a913babb3d1a59e693513681c94"
BASELINE_FILES = (
    "source/AST-CMD-001.blend",
    "source/geometry_parts.json",
    "source/section_contract.json",
)
NEW_FLOOR_IDS = {
    "D18_aft_command_port_floor",
    "D18_aft_command_starboard_floor",
}
NEW_SLABS = [
    {"name": "D18_aft_command_port_floor", "world_aabb": [-36, -4, 106.26, 106.5, 80, 102]},
    {"name": "D18_aft_command_starboard_floor", "world_aabb": [4, 36, 106.26, 106.5, 80, 102]},
]


BLENDER_WORKER = r'''
import bpy, bmesh, hashlib, json, sys
from pathlib import Path

root, baseline, prelight_path = map(Path, sys.argv[sys.argv.index('--') + 1:])

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    parts, fingerprints, markers, failures = [], {}, {}, []
    triangles = 0
    for ob in bpy.context.scene.objects:
        matrix = [[round(float(v), 8) for v in row] for row in ob.matrix_world]
        props = {k: str(ob[k]) for k in ob.keys() if k != '_RNA_UI'}
        if ob.type == 'EMPTY':
            p = ob.matrix_world.translation
            markers[ob.name] = {'matrix': matrix, 'properties': props, 'world_position': [p.x, p.z, -p.y]}
            continue
        if ob.type != 'MESH':
            failures.append({'name': ob.name, 'unexpected_object_type': ob.type})
            continue
        mesh = ob.data
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        flags = {'manifold': all(e.is_manifold for e in bm.edges),
                 'consistent_winding': all(e.is_contiguous for e in bm.edges),
                 'positive_volume': bm.calc_volume(signed=True) > 0,
                 'nondegenerate_faces': all(f.calc_area() > 1e-10 for f in bm.faces)}
        bm.free()
        if not all(flags.values()):
            failures.append({'name': ob.name, **flags})
        vs = [ob.matrix_world @ v.co for v in mesh.vertices]
        world = [[v.x, v.z, -v.y] for v in vs]
        bounds = [n for k in range(3) for n in (min(v[k] for v in world), max(v[k] for v in world))]
        parts.append({'name': ob.name, 'world_aabb': bounds, 'vertices_world': world,
                      'group': ob.get('group'), 'material': [m.name for m in mesh.materials]})
        # Preserve topology, winding, UV, material, transform and properties in
        # the comparison, not only bounds or mesh-name counts.
        fingerprints[ob.name] = digest({
            'matrix': matrix, 'properties': props,
            'vertices': [[round(float(q), 6) for q in v.co] for v in mesh.vertices],
            'polygons': [[list(f.vertices), f.material_index] for f in mesh.polygons],
            'uv': [[[round(float(q), 6) for q in v.uv] for v in layer.data] for layer in mesh.uv_layers],
            'materials': [m.name for m in mesh.materials],
        })
    return {'parts': parts, 'fingerprints': fingerprints, 'markers': markers,
            'topology_failures': failures, 'triangles': triangles}

aft = snapshot(root / 'assets/aft_command/source/AST-CMD-002.blend')
crown = snapshot(root / 'assets/central_crown/source/AST-CMD-001.blend')
old = snapshot(baseline / 'source/AST-CMD-001.blend')
prelight = snapshot(prelight_path)
changed = sorted(n for n in crown['fingerprints'].keys() | old['fingerprints'].keys()
                 if crown['fingerprints'].get(n) != old['fingerprints'].get(n))
changed_markers = sorted(n for n in crown['markers'].keys() | old['markers'].keys()
                        if crown['markers'].get(n) != old['markers'].get(n))
summary = {'aft': aft, 'crown': crown,
           'baseline': {'mesh_count': len(old['parts']), 'marker_count': len(old['markers']),
                        'topology_failures': old['topology_failures'], 'triangles': old['triangles']},
           'crown_mesh_changes': changed, 'crown_marker_changes': changed_markers,
           'prelight_diff': {
               'previous_mesh_count': len(prelight['parts']),
               'previous_marker_count': len(prelight['markers']),
               'removed_meshes': sorted(prelight['fingerprints'].keys() - aft['fingerprints'].keys()),
               'added_meshes': sorted(aft['fingerprints'].keys() - prelight['fingerprints'].keys()),
               'modified_existing_meshes': sorted(n for n in prelight['fingerprints'].keys() & aft['fingerprints'].keys()
                                                 if prelight['fingerprints'][n] != aft['fingerprints'][n]),
               'removed_markers': sorted(prelight['markers'].keys() - aft['markers'].keys()),
               'added_markers': sorted(aft['markers'].keys() - prelight['markers'].keys()),
               'modified_existing_markers': sorted(n for n in prelight['markers'].keys() & aft['markers'].keys()
                                                  if prelight['markers'][n] != aft['markers'][n]),
           },
           'blender_version': bpy.app.version_string}
for tag in ('aft', 'crown'):
    summary[tag].pop('fingerprints')
print('INDEPENDENT_GEOMETRY_DATA ' + json.dumps(summary, separators=(',', ':')))
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def axes_overlap(a, b):
    return [max(0.0, min(a[2*k+1], b[2*k+1]) - max(a[2*k], b[2*k])) for k in range(3)]


def positive_contact(a, b, tolerance=1e-6):
    return all(v > tolerance for v in axes_overlap(a, b))


def pair_contacts(aa, bb):
    pairs = []
    for a in aa:
        for b in bb:
            depths = axes_overlap(a['world_aabb'], b['world_aabb'])
            if all(v > 1e-6 for v in depths):
                pairs.append({'a': a['name'], 'b': b['name'], 'overlap_xyz_m': depths})
    return {'count': len(pairs), 'pairs': pairs,
            'sum_pair_volume_m3': sum(math.prod(p['overlap_xyz_m']) for p in pairs)}


def gap_free(intervals, tolerance=1e-5):
    if not intervals:
        return False
    ordered = sorted(intervals)
    end = ordered[0][1]
    for lo, hi in ordered[1:]:
        if lo > end + tolerance:
            return False
        end = max(end, hi)
    return True


def polygon_area(poly):
    if len(poly) < 3:
        return 0.0
    return abs(sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def clip_axis(poly, axis, bound, above):
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ina = a[axis] >= bound if above else a[axis] <= bound
        inb = b[axis] >= bound if above else b[axis] <= bound
        if ina:
            out.append(a)
        if ina != inb:
            t = (bound - a[axis]) / (b[axis] - a[axis])
            out.append([a[k] + t*(b[k]-a[k]) for k in range(2)])
    return out


def clip_rect(poly, rect):
    for axis, limit, above in ((0, rect[0], True), (0, rect[1], False),
                               (1, rect[2], True), (1, rect[3], False)):
        poly = clip_axis(poly, axis, limit, above)
        if not poly:
            return []
    return poly


def convex_intersection(poly, clipper):
    """Exact convex clipping in XZ; used to detect cross-owner floor overlaps."""
    signed = sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(clipper, clipper[1:]+clipper[:1]))
    orientation = 1 if signed >= 0 else -1
    for c, d in zip(clipper, clipper[1:]+clipper[:1]):
        if not poly:
            return []
        out = []
        side = lambda p: orientation*((d[0]-c[0])*(p[1]-c[1]) - (d[1]-c[1])*(p[0]-c[0]))
        for a, b in zip(poly, poly[1:]+poly[:1]):
            sa, sb = side(a), side(b)
            if sa >= -1e-10:
                out.append(a)
            if (sa >= 0) != (sb >= 0):
                t = sa/(sa-sb)
                out.append([a[k]+t*(b[k]-a[k]) for k in range(2)])
        poly = out
    return poly


def rectangle_overlap(a, b):
    return min(a[1], b[1]) > max(a[0], b[0]) + 1e-7 and min(a[3], b[3]) > max(a[2], b[2]) + 1e-7


def planar_bounds(tri):
    return [min(v[0] for v in tri), max(v[0] for v in tri), min(v[1] for v in tri), max(v[1] for v in tri)]


def prepare_baseline(root, candidate):
    """Verify the original baseline against Git, reconstructing only when absent."""
    if not all((candidate / rel).exists() for rel in BASELINE_FILES):
        candidate = Path(tempfile.mkdtemp(prefix='astraea-independent-baseline-'))
    receipt = {}
    for rel in BASELINE_FILES:
        data = subprocess.run(['git', '-C', str(root), 'show',
                               f'{BASELINE_COMMIT}:assets/central_crown/{rel}'],
                              check=True, capture_output=True).stdout
        expected = hashlib.sha256(data).hexdigest()
        dest = candidate / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        if sha(dest) != expected:
            raise RuntimeError(f'Existing baseline does not match Git {BASELINE_COMMIT}: {dest}')
        receipt[rel] = expected
    return candidate, receipt


def prepare_prelight(args):
    """Read a pinned mirror commit only; never inspect or modify mirror WIP."""
    if args.prelight_blend:
        path = args.prelight_blend.resolve()
        if sha(path) != PRELIGHT_BLEND_SHA256:
            raise RuntimeError('Supplied pre-light .blend does not match the verified snapshot')
        return path, {'method': 'Supplied pinned .blend', 'source_sha256': sha(path)}
    folder = Path(tempfile.mkdtemp(prefix='astraea-independent-prelight-'))
    receipt = {'method': 'Read-only git show of retained mirror commit',
               'repository': str(args.prelight_git_root), 'commit': PRELIGHT_COMMIT}
    for name, expected in [('AST-CMD-002.blend', PRELIGHT_BLEND_SHA256),
                           ('geometry_parts.json', PRELIGHT_PARTS_SHA256)]:
        data = subprocess.run(['git', '-C', str(args.prelight_git_root), 'show',
                               f'{PRELIGHT_COMMIT}:BlenderCatalogue/assets/aft_command/source/{name}'],
                              check=True, capture_output=True).stdout
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError('Pinned pre-light Git content hash mismatch: ' + name)
        (folder / name).write_bytes(data)
        receipt[name] = expected
    return folder / 'AST-CMD-002.blend', receipt


def review(args):
    root, runtime = args.catalogue_root.resolve(), args.runtime_root.resolve()
    errors = []
    check = lambda condition, label: errors.append(label) if not condition else None
    baseline, baseline_hashes = prepare_baseline(root, args.baseline_directory)
    prelight_path, prelight_evidence = prepare_prelight(args)
    protected_paths = [root / p for p in (
        'assets/aft_command/source/AST-CMD-002.blend',
        'assets/aft_command/exports/AST-CMD-002.glb',
        'assets/aft_command/source/geometry_parts.json',
        'assets/aft_command/source/section_contract.json',
        'assets/central_crown/source/AST-CMD-001.blend',
        'assets/central_crown/exports/AST-CMD-001.glb',
        'assets/central_crown/source/geometry_parts.json',
        'assets/central_crown/source/section_contract.json',
        'assets/aft_command/qa/independent_aft_construction_review.json',
    )]
    structural_path = args.structural_json or runtime / 'data/generated/structural_meshes.json'
    protected_paths.append(structural_path)
    hashes = {str(p): sha(p) for p in protected_paths}
    process = subprocess.run([args.blender, '--background', '--factory-startup',
                              '--python-expr', BLENDER_WORKER, '--', str(root), str(baseline), str(prelight_path)],
                             capture_output=True, text=True)
    prefix = 'INDEPENDENT_GEOMETRY_DATA '
    lines = [line[len(prefix):] for line in process.stdout.splitlines() if line.startswith(prefix)]
    if process.returncode or len(lines) != 1:
        raise RuntimeError('Blender read-only inspection failed: ' + process.stderr[-3000:] + process.stdout[-3000:])
    actual = json.loads(lines[0])
    P, C = actual['aft']['parts'], actual['crown']['parts']
    D = json.loads((root / 'assets/aft_command/source/section_contract.json').read_text())
    CD = json.loads((root / 'assets/central_crown/source/section_contract.json').read_text())
    prelight_diff = actual['prelight_diff']
    for key in ['removed_meshes', 'modified_existing_meshes', 'removed_markers', 'modified_existing_markers']:
        check(not prelight_diff[key], 'Pre-light aft source changed beyond added fixtures: ' + key)
    check(len(prelight_diff['added_meshes']) == 12, 'Expected exactly12 new street fixture meshes')
    check(len(prelight_diff['added_markers']) == 6, 'Expected exactly6 new street light markers')
    added_parts = [p for p in P if p['name'] in prelight_diff['added_meshes']]
    check(all(p['group'] == 'fixture' and p['world_aabb'][2] >= 110.55999
              and p['world_aabb'][3] <= 111.00001 for p in added_parts),
          'New pre-light-diff meshes are not solely high-level street fixtures')
    new_positions = sorted(actual['aft']['markers'][n]['world_position'] for n in prelight_diff['added_markers'])
    expected_positions = [[x, 110.55, 63] for x in [-30, -18, -6, 6, 18, 30]]
    check(len(new_positions) == len(expected_positions) and
          all(max(abs(a-b) for a, b in zip(p, q)) < 1e-5 for p, q in zip(new_positions, expected_positions)),
          'New street-light marker positions differ from the six approved sites')
    record_checks = {}
    for tag, family in [('aft', 'aft_command'), ('crown', 'central_crown')]:
        observed = {p['name']: p for p in actual[tag]['parts']}
        records = json.loads((root / f'assets/{family}/source/geometry_parts.json').read_text())['parts']
        failures = []
        maximum = 0.0
        for p in records:
            q = observed.get(p['name'])
            if q is None or len(q['vertices_world']) != len(p['vertices_world']):
                failures.append(p['name'])
                continue
            error = max(abs(a-b) for va, vb in zip(p['vertices_world'], q['vertices_world']) for a, b in zip(va, vb))
            maximum = max(maximum, error)
            if error > 1e-5 or p['group'] != q['group']:
                failures.append(p['name'])
        record_checks[tag] = {'mesh_count': len(observed), 'triangles': actual[tag]['triangles'],
                              'maximum_record_coordinate_error_m': maximum, 'failures': failures,
                              'topology_failures': actual[tag]['topology_failures']}
        check(not failures and len(observed) == len(records), f'{tag}: geometry records differ from actual source')
        check(not actual[tag]['topology_failures'], f'{tag}: mesh topology/winding failure')

    old_diff = {'changed_meshes': actual['crown_mesh_changes'], 'changed_markers': actual['crown_marker_changes']}
    old_diff['out_of_scope_meshes'] = [n for n in old_diff['changed_meshes']
                                     if not n.startswith(('CMD_Port_CorridorEnd_', 'CMD_Starboard_CorridorEnd_'))]
    expected_markers = {'DATUM_door_central_aft_exit_port', 'DATUM_door_central_aft_exit_starboard'}
    check(not old_diff['out_of_scope_meshes'], 'Old crown changed outside the two endcaps')
    check(set(old_diff['changed_markers']) == expected_markers, 'Old crown marker diff exceeds the two exits')
    for side, x in [('port', -7.5), ('starboard', 7.5)]:
        q = actual['crown']['markers'][f'DATUM_door_central_aft_exit_{side}']['world_position']
        check(max(abs(a-b) for a, b in zip(q, [x, 106.5, 59.8])) < 1e-5, f'{side}: old exit anchor moved')
    prior_contract = json.loads((baseline / 'source/section_contract.json').read_text())
    old_diff['contract_changed_keys'] = sorted(k for k in prior_contract.keys() | CD.keys() if prior_contract.get(k) != CD.get(k))
    check(set(old_diff['contract_changed_keys']) <= {'doors', 'aft_exit_revision'}, 'Old crown contract changed outside exit revision')
    check(CD['doors'][:len(prior_contract['doors'])] == prior_contract['doors'], 'Existing crown door contracts changed')

    body = {'street_hits': [p['name'] for p in P+C if positive_contact(p['world_aabb'], [-48, 48, 106.51, 110.5, 60, 66])],
            'public_spine_hits': [p['name'] for p in P+C if positive_contact(p['world_aabb'], [-4, 4, 106.51, 110.5, 60, 102])],
            'height_max_m': max(p['world_aabb'][3] for p in P),
            'floor_meshes': [p['name'] for p in P if p['group'] == 'floor']}
    check(not body['street_hits'] and not body['public_spine_hits'], 'Protected public body belt is obstructed')
    check(body['height_max_m'] <= 114.50001 and not body['floor_meshes'], 'Height limit or no-source-floor constraint failed')

    # Recheck actual current emitters as well, including the six public-street
    # fixtures added after the first independent review. Fixture suspension is a
    # deliberately flush face contact at the underside of an actual roof mesh.
    fixture_exits = []
    all_roof = [p for p in P+C if p['group'] in ('roof', 'ceiling')]
    for marker in D['light_markers']:
        observed = actual['aft']['markers'].get(marker['name'])
        check(observed is not None, 'Missing actual light marker: ' + marker['name'])
        if observed is None:
            continue
        x, y, z = observed['world_position']
        check(max(abs(a-b) for a, b in zip([x, y, z], marker['position'])) < 1e-5,
              'Light marker differs from contract: ' + marker['name'])
        lenses = [p for p in P if any(m.endswith('staff_opal') for m in p['material'])
                  and p['world_aabb'][0]-1e-5 <= x <= p['world_aabb'][1]+1e-5
                  and p['world_aabb'][4]-1e-5 <= z <= p['world_aabb'][5]+1e-5
                  and abs(p['world_aabb'][2]-y-.01) < 1e-5]
        blockers = [p['name'] for p in P+C
                    if p['world_aabb'][0]-1e-6 <= x <= p['world_aabb'][1]+1e-6
                    and p['world_aabb'][4]-1e-6 <= z <= p['world_aabb'][5]+1e-6
                    and min(y, p['world_aabb'][3])-max(106.501, p['world_aabb'][2]) > 1e-5]
        housing = [p for p in P if p['group'] == 'fixture' and '_Housing' in p['name']
                   and p['world_aabb'][0]-1e-5 <= x <= p['world_aabb'][1]+1e-5
                   and p['world_aabb'][4]-1e-5 <= z <= p['world_aabb'][5]+1e-5]
        seats = []
        for h in housing:
            hb = h['world_aabb']
            for roof in all_roof:
                rb = roof['world_aabb']
                if abs(hb[3]-rb[2]) < 1e-5 and rectangle_overlap([hb[0], hb[1], hb[4], hb[5]],
                                                                [rb[0], rb[1], rb[4], rb[5]]):
                    seats.append([h['name'], roof['name']])
        fixture_exits.append({'marker': marker['name'], 'position': [x, y, z],
                              'lens_parts': [p['name'] for p in lenses], 'blocked_by': blockers,
                              'flush_housing_to_roof_contacts': seats})
        check(bool(lenses) and not blockers and bool(seats), 'Fixture lens/exit/ceiling-contact failure: ' + marker['name'])

    trans = [p for p in P if p['name'].startswith('AFC_TransferGirder')]
    old_frame = [p for p in C if p['name'].startswith('CMD_TransferGirder') and p['world_aabb'][4] > 70]
    links = [p for p in P if p['name'].startswith('AFC_Longitudinal')]
    girders = [p for p in P if p['name'].startswith('AFC_FloorEdgeGirder')]
    saddles = [p for p in P if p['name'].startswith('AFC_ForwardPurlinSaddle')]
    support = []
    def require_pair(label, a, b):
        result = pair_contacts(a, b)
        support.append({'stage': label, **result})
        check(result['count'] > 0, f'Missing positive bearing: {label}')
    for x, z in D['support']['pier_centres_xz']:
        piers = [p for p in P if p['group'] == 'pier' and (p['world_aabb'][0] < 0) == (x < 0)]
        check(all(p['world_aabb'][0] >= x-.40001 and p['world_aabb'][1] <= x+.40001 and
                  p['world_aabb'][4] >= z-.60001 and p['world_aabb'][5] <= z+.60001 for p in piers), f'Pier {x} exceeded audited envelope')
        check(abs(min(p['world_aabb'][2] for p in piers)+3.2) < 1e-5 and
              abs(max(p['world_aabb'][3] for p in piers)-114) < 1e-5, f'Pier {x} vertical span differs')
        check(gap_free([(p['world_aabb'][2], p['world_aabb'][3]) for p in piers if '_Web_' in p['name']]), f'Pier {x} web gap')
        require_pair(f'Pier {x} to Z86 transverse', piers, trans)
    for x in D['support']['roof_link_x']:
        row = [p for p in links if p['world_aabb'][0] <= x <= p['world_aabb'][1]]
        require_pair(f'Longitudinal {x} to Z71 transverse', row, old_frame)
        require_pair(f'Longitudinal {x} to Z86 transverse', row, trans)
        check(gap_free([(p['world_aabb'][4], p['world_aabb'][5]) for p in row]), f'Longitudinal {x} has an axial gap')
    for x in D['support']['hanger_x']:
        edge = [p for p in girders if p['world_aabb'][0] <= x <= p['world_aabb'][1]]
        roof = [p for p in links if p['world_aabb'][0] <= x <= p['world_aabb'][1]]
        for z in D['support']['hanger_z']:
            hang = [p for p in P if p['group'] == 'hanger' and p['world_aabb'][0] <= x <= p['world_aabb'][1]
                    and p['world_aabb'][4] <= z <= p['world_aabb'][5]]
            require_pair(f'Hanger {x},{z} to roof', hang, roof)
            require_pair(f'Hanger {x},{z} to floor edge', hang, edge)
            check(gap_free([(p['world_aabb'][2], p['world_aabb'][3]) for p in hang]), f'Hanger {x},{z} gap')
        tie = [p for p in P if p['group'] == 'tie' and p['world_aabb'][0] <= x <= p['world_aabb'][1]]
        require_pair(f'Apron tie {x} to girder', tie, edge)
    for saddle in saddles:
        require_pair(saddle['name'] + ' to existing longitudinal', [saddle], [p for p in C if p['name'].startswith('CMD_Longitudinal')])
        require_pair(saddle['name'] + ' to Z66 purlin', [saddle], [p for p in P if p['name'].startswith('AFC_RoofPurlin')])
    check(len(saddles) == 4, 'Expected three saddle positions split into four editable meshes')
    for z in [66, 74, 82, 90, 98, 101.8]:
        rows = [p for p in P if p['name'].startswith('AFC_RoofPurlin') and p['world_aabb'][4] < z < p['world_aabb'][5]]
        check(gap_free([(p['world_aabb'][0], p['world_aabb'][1]) for p in rows]), f'Purlin {z} has a horizontal gap')
        require_pair(f'Purlin {z} to beam/saddle', rows, links+saddles)
    for z in D['support']['floor_cross_bearer_z']:
        for side in (-1, 1):
            row = [p for p in P if p['name'].startswith('AFC_PlatformCrossBearer')
                   and p['world_aabb'][4] < z < p['world_aabb'][5] and (p['world_aabb'][0] < 0) == (side < 0)]
            require_pair(f'Cross bearer {side},{z} to edge girder', row, girders)
            check(gap_free([(p['world_aabb'][0], p['world_aabb'][1]) for p in row]), f'Cross bearer {side},{z} gap')

    structural = json.loads(structural_path.read_text())
    triangles = []
    for region in structural['regions']:
        for t in region['triangles']:
            triangles.append({'id': region['id'], 'y0': region['floor_y']-region['thickness'],
                              'y1': region['floor_y'], 'triangle': t, 'rect': planar_bounds(t)})
    floor_hits = []
    for p in P:
        b = p['world_aabb']
        rect = [b[0], b[1], b[4], b[5]]
        contacts = defaultdict(float)
        for t in triangles:
            depth = min(b[3], t['y1']) - max(b[2], t['y0'])
            if depth <= 1e-6 or not rectangle_overlap(rect, t['rect']):
                continue
            a = polygon_area(clip_rect(t['triangle'], rect))
            if a > 1e-7:
                contacts[t['id']] += a*depth
        if contacts:
            floor_hits.append({'part': p['name'], 'group': p['group'], 'owner_intersection_m3': dict(contacts)})
    allowed_owners = {'D18_aft_apron'} | NEW_FLOOR_IDS
    unexpected = [r for r in floor_hits if set(r['owner_intersection_m3']) - allowed_owners]
    check(not unexpected, 'Unintended actual structural slab contact')
    for p in [p for p in P if p['group'] == 'tie']:
        hit = next((r for r in floor_hits if r['part'] == p['name']), None)
        check(hit is not None and hit['owner_intersection_m3'].get('D18_aft_apron', 0) > 0, p['name'] + ' misses actual apron triangles')

    deck = [t for t in triangles if abs(t['y1']-106.5) < 1e-7]
    areas = defaultdict(float)
    for t in deck:
        areas[t['id']] += polygon_area(clip_rect(t['triangle'], [-36, 36, 80, 102]))
    areas = {k: v for k, v in areas.items() if v > 1e-7}
    check(abs(areas.get('D18_aft_route', 0)-176) < 1e-5, 'Existing spine ownership is not exactly176m2')
    check(not(set(areas) - ({'D18_aft_route'} | NEW_FLOOR_IDS)), 'Unexpected floor owner in proposed platform envelope')
    adopted = sum(areas.get(k, 0) for k in NEW_FLOOR_IDS)
    check(abs(adopted) < 1e-5 or abs(adopted-1408) < 1e-5, 'Partial or excessive command floor adoption')
    for slab in NEW_SLABS:
        expected = slab['world_aabb']
        owner_tris = [t for t in deck if t['id'] == slab['name']]
        if owner_tris:
            area_total = sum(polygon_area(t['triangle']) for t in owner_tris)
            area_inside = sum(polygon_area(clip_rect(t['triangle'], [expected[0], expected[1], expected[4], expected[5]])) for t in owner_tris)
            check(abs(area_total-704) < 1e-5 and abs(area_inside-704) < 1e-5, slab['name'] + ' has incorrect footprint')
            check(all(abs(t['y0']-106.26) < 1e-5 and abs(t['y1']-106.5) < 1e-5 for t in owner_tris), slab['name'] + ' has incorrect slab datums')
    # Check cross-owner overlaps directly, not only summed areas or source_checks.
    overlaps = []
    relevant = []
    for t in deck:
        poly = clip_rect(t['triangle'], [-48, 48, 60, 102])
        if polygon_area(poly) > 1e-7:
            relevant.append((t['id'], poly, planar_bounds(poly)))
    for i, (a_id, a, ar) in enumerate(relevant):
        for b_id, b, br in relevant[i+1:]:
            if a_id == b_id or not rectangle_overlap(ar, br):
                continue
            size = polygon_area(convex_intersection(a, b))
            if size > 1e-6:
                overlaps.append({'owners': [a_id, b_id], 'overlap_m2': size})
    check(not overlaps, 'Cross-owner floor overlap within the command/street envelope')
    coverage = []
    for name, rect in [('port_command', [-36, -10, 66, 102]), ('starboard_command', [10, 36, 66, 102]),
                       ('cross_street', [-48, 48, 60, 66]), ('public_spine', [-4, 4, 60, 102])]:
        current = sum(polygon_area(clip_rect(t['triangle'], rect)) for t in deck)
        proposed = 0.0
        if adopted < 1e-5:
            for slab in NEW_SLABS:
                b = slab['world_aabb']
                proposed += max(0, min(rect[1], b[1])-max(rect[0], b[0])) * max(0, min(rect[3], b[5])-max(rect[2], b[4]))
        size = (rect[1]-rect[0])*(rect[3]-rect[2])
        coverage.append({'region': name, 'footprint_m2': size, 'current_compiled_m2': current,
                         'pending_proposed_m2': proposed, 'uncovered_m2': size-current-proposed})
        check(abs(size-current-proposed) < 1e-5, name + ' has uncovered or multiply counted floor')
    for group in ['pier', 'hanger', 'platform_support', 'tie']:
        require_pair(group + ' to parent-owned slab envelope', [p for p in P if p['group'] == group], NEW_SLABS)

    invalid_room_parts = []
    for room in D['programmes']:
        ring = room['boundary']
        rect = [min(v[0] for v in ring), max(v[0] for v in ring), min(v[1] for v in ring), max(v[1] for v in ring)]
        for p in P:
            if room['programme_key'] in p['name'] and any(not(rect[0]-1e-5 <= v[0] <= rect[1]+1e-5 and
                                                            rect[2]-1e-5 <= v[2] <= rect[3]+1e-5) for v in p['vertices_world']):
                invalid_room_parts.append(p['name'])
    check(not invalid_room_parts, 'Programme-named meshes exceed room boundaries')
    # Existing persistent source/export verification is evidence only: do not run
    # it here because it writes its own distinct receipt outside this harness.
    prior_validation = json.loads((root / 'assets/aft_command/qa/source_export_validation.json').read_text())
    roundtrip_current = (prior_validation.get('source_sha256') == hashes[str(root / 'assets/aft_command/source/AST-CMD-002.blend')]
                         and prior_validation.get('export_sha256') == hashes[str(root / 'assets/aft_command/exports/AST-CMD-002.glb')]
                         and prior_validation.get('central_export_sha256') == hashes[str(root / 'assets/central_crown/exports/AST-CMD-001.glb')])
    check(roundtrip_current, 'Persistent source/export/door/light validation is stale')
    changed = [p for p, h in hashes.items() if sha(p) != h]
    check(not changed, 'Input or original review changed during reconstructed checks')
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'provenance': 'Reconstructed from the independent reviewer inline logic; first retained executable harness, not the original inline commands.',
        'checked_at_utc_executor_clock': datetime.now(timezone.utc).isoformat(),
        'blender_version': actual['blender_version'], 'baseline_commit': BASELINE_COMMIT,
        'baseline_directory': str(baseline), 'baseline_hashes': baseline_hashes,
        'prelight_snapshot': prelight_evidence, 'prelight_mesh_and_marker_diff': prelight_diff,
        'input_sha256': hashes, 'changed_inputs': changed, 'errors': errors,
        'actual_source_checks': record_checks, 'old_crown_scope': old_diff,
        'body_and_height': body, 'positive_contact_stages': support,
        'actual_fixture_count': len(fixture_exits), 'actual_fixture_exits_and_roof_contacts': fixture_exits,
        'compiled_region_count': len(structural['regions']), 'actual_floor_contacts': floor_hits,
        'unexpected_floor_contacts': unexpected, 'platform_envelope_owner_areas_m2': areas,
        'compiled_new_platform_area_m2': adopted, 'cross_owner_overlap_failures': overlaps,
        'floor_union_coverage': coverage, 'room_boundary_failures': invalid_room_parts,
        'matching_persistent_roundtrip_door_light_validation': roundtrip_current,
        'matching_validation_receipt': 'assets/aft_command/qa/source_export_validation.json',
        'scope_limits': ['Source geometry and exact compiled-floor triangles only; no Godot launch/import or runtime execution.',
                         'Positive geometric contacts are not structural load certification.',
                         'Moving door sweeps and source/export roundtrip remain in the matching persistent validator; actual final fixture exits are also checked here.',
                         'The original independent review is preserved unchanged and reflects its earlier floor-compilation snapshot.'],
    }


def main():
    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue-root', type=Path, default=default_root)
    parser.add_argument('--runtime-root', type=Path, default=default_root.with_name('astraea-godot-production-20261003'))
    parser.add_argument('--structural-json', type=Path, help='Optional exact compiled structural snapshot')
    parser.add_argument('--baseline-directory', type=Path, default=Path('/tmp/astraea-aft-central-baseline'))
    parser.add_argument('--prelight-git-root', type=Path, default=default_root.with_name('astraea-github-backup'),
                        help='Read-only retained mirror repository containing pinned pre-light commit')
    parser.add_argument('--prelight-blend', type=Path,
                        help='Portable alternative to mirror Git access; must match the pinned pre-light SHA256')
    parser.add_argument('--blender', default='/usr/bin/blender')
    args = parser.parse_args()
    receipt = Path(__file__).resolve().with_name('independent_geometry_reconstruction_validation.json')
    try:
        result = review(args)
    except Exception as exc:
        result = {'status': 'ERROR', 'provenance': 'Reconstructed independent geometry harness',
                  'error': f'{type(exc).__name__}: {exc}'}
    result['harness_sha256'] = sha(__file__)
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'receipt': str(receipt),
                      'errors': result.get('errors', result.get('error', []))}, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
