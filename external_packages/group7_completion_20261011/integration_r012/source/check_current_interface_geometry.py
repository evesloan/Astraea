"""Narrow offline current-source checks; no engine import or combined build."""
from pathlib import Path
import json, sys, hashlib
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
sys.path.insert(0, str(C.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read, acc, nodes
current = P/'qa/group1_current'
floors = []
for filename in ['structural_meshes.json', 'received_structural_meshes.json']:
    name = 'Game/data/generated/'+filename
    assert (current/name).read_bytes() == (R/name).read_bytes()
    floors += json.loads((current/name).read_text())['regions']
floor_shapes = [(row, unary_union([Polygon(t) for t in row['triangles']])) for row in floors]

def coverage(query, ys):
    result = []
    for row, shape in floor_shapes:
        if not any(abs(row['floor_y']-y) < .0001 for y in ys): continue
        area = shape.intersection(query).area
        if area > 1e-7:
            result.append({'floor_id': row['id'], 'floor_y': row['floor_y'],
                           'underside_y': row['floor_y']-row['thickness'],
                           'intersection_area_m2': area, 'query_area_m2': query.area})
    return result

data = json.loads((R/'Game/data/architecture/GROUP7_COMPLETION.json').read_text())
thermal = []
dep = P/'qa/current_dependencies'
for key in ['02', '03']:
    file = dep/('BlenderCatalogue/assets/group6_completion_20261011/thermal_targets/D08_directory_'+key+'_section_contract.json')
    row = json.loads(file.read_text()); polygon = Polygon(row['source_containment_boundary_xz'])
    x0, z0, x1, z1 = polygon.bounds
    thermal.append({'programme_key': row['programme_key'],
                    'minimum': [x0, row['floor_y'], z0],
                    'maximum': [x1, row['maximum_source_roof_or_service_top_y'], z1],
                    'historical_allocation_not_prescribed_box_walls': True,
                    'current_upper_compiler_floor_coverage': coverage(polygon, [row['next_deck_floor_y']]),
                    'group7_surface_candidates': []})
rootroof = json.loads((dep/'BlenderCatalogue/assets/group2_completion_20261011/prior_handoff/ROYALTY790_PROTECTED_ROOF_BLOCKER.json').read_text())
royalty = []
for reservation in rootroof['conflicts']:
    polygon = Polygon(reservation['intersection_polygon_xz'])
    royalty.append({'reservation': reservation['reservation'], 'polygon_xz': reservation['intersection_polygon_xz'],
                    'protected_roof_intersection_area_m2': polygon.area,
                    'actual_compiler_layer_intersections': coverage(polygon, [102, 106.5]),
                    'roof_or_floor_cut_applied': False})

wetpolys = [box(-95.88, -383.711784, -64.12, -374.138572),
            box(64.12, -383.711784, 95.88, -374.138572)]
wet_roof_hits = [[], []]
counts = []
for row in data['models']:
    file = R/'Game/assets/models'/row['file']
    assert hashlib.sha256(file.read_bytes()).hexdigest() == row['sha256']
    d, b = read(file); triangles = []
    for node, matrix in nodes(d):
        for primitive in d['meshes'][node['mesh']]['primitives']:
            points = acc(d, b, primitive['attributes']['POSITION'])
            points = (np.c_[points, np.ones(len(points))] @ matrix.T)[:, :3]
            idx = acc(d, b, primitive['indices']).ravel(); triangles.append(points[idx].reshape(-1, 3, 3))
    triangles = np.concatenate(triangles); lo = triangles.min(1); hi = triangles.max(1)
    counts.append({'cell': row['cell'], 'triangles': len(triangles)})
    for query in thermal:
        # A zero triangle-bounds candidate result is a conservative separation
        # proof for the whole historical allocation, stronger than a source-only
        # subset check. A nonzero result stays held, not called penetration.
        mn = np.array(query['minimum']); mx = np.array(query['maximum'])
        mask = np.all(hi > mn-.005, axis=1) & np.all(lo < mx+.005, axis=1)
        if np.any(mask): query['group7_surface_candidates'].append({'cell': row['cell'], 'triangles': int(mask.sum())})
    if row['cell'].startswith('Roof_'):
        projected = unary_union([Polygon(t[:, [0, 2]]) for t in triangles if abs(np.cross(t[1]-t[0], t[2]-t[0])[1]) > 1e-9])
        for i, polygon in enumerate(wetpolys):
            area = projected.intersection(polygon).area
            if area > 1e-7: wet_roof_hits[i].append({'cell': row['cell'], 'intersection_area_m2': area})
report = {'status': 'OFFLINE_EXACT_CURRENT_FLOORS_AND_SELECTED_SOURCE_GEOMETRY',
          'parent_frozen_source_commit': '47eb8359caa5531e04122b6e56292f8c44d4281a',
          'group7_source_commit': '455e381c3bf9b89e661651f9e5508065554c075e',
          'parent_compiled_floor_files_byte_identical_to_tested_baseline': True,
          'thermal_interfaces': thermal, 'royalty790_circulation_apertures': royalty,
          'royalty_protected_roof_original_export_sha256': rootroof['protected_export_sha256'],
          'wet_roof_envelope_queries': [{'kit': kit, 'bounds_xz': list(poly.bounds), 'area_m2': poly.area,
                                         'selected_group7_roof_intersections': hits}
                                        for kit, poly, hits in zip(['TIDAL', 'QUIET'], wetpolys, wet_roof_hits)],
          'selected88_model_hashes_verified': True, 'selected_model_triangles': counts,
          'total_selected_triangles': sum(q['triangles'] for q in counts),
          'no_original_geometry_floor_or_roof_changed': True, 'no_engine_import_build_or_parent_write': True,
          'current_combined_physics_or_primary_capacity_accepted': False}
(P/'qa/CURRENT_INTERFACE_GEOMETRY_CHECK.json').write_text(json.dumps(report, indent=2)+'\n')
print('G7_CURRENT_INTERFACES', [(q['programme_key'], q['group7_surface_candidates']) for q in thermal],
      'wetG7roofhits', wet_roof_hits, 'Royaltyapertures', sum(q['protected_roof_intersection_area_m2'] for q in royalty),
      'selectedtriangles', report['total_selected_triangles'])
