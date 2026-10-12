"""Verify final terraces against exact source contact polygons, not convex walls."""
import gzip, hashlib, json, pathlib
from shapely.geometry import Polygon, MultiPoint, LineString
from shapely.ops import unary_union
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
plan_path = ROOT / 'Game/data/group2_pit_perimeters/PLAN_r003.json'
plan = json.loads(plan_path.read_text())
rows = []
for row in plan['suites']:
    key = str(row['source_index'])
    saved = ROOT / f'BlenderCatalogue/assets/group2_completion_20261011/retained_evidence/{key}/SAVED_NATIVE_VERTICES.json.gz'
    vertices = json.loads(gzip.decompress(saved.read_bytes()))
    contract = json.loads((ROOT / f'Game/data/group2_completion/contracts/{key}.json').read_text())
    terrace = unary_union([Polygon(r['boundary'], r['holes']) for r in row['raised_regions']])
    assert terrace.geom_type == 'Polygon' and terrace.is_valid
    routes = unary_union([LineString([(p[0], p[2]) for p in r[1]]).buffer(r[2] + .03)
                          for r in contract['source_routes_world']])
    assert terrace.intersection(routes).area < 1e-7
    supports = []
    for name in row['furniture_pose_patch']['exact_mesh_names']:
        pts = vertices[name]
        if min(p[1] for p in pts) > 102.021:
            continue
        delta = row['furniture_pose_patch']['per_mesh_world_delta'].get(name, [0, .45, 0])
        foot = MultiPoint([(p[0] + delta[0], p[2] + delta[2]) for p in pts if p[1] < 102.021]).convex_hull
        if foot.area > 1e-8:
            assert foot.difference(terrace).area < 1e-6, name
            supports.append(name)
    walls = []
    for name, pts in vertices.items():
        if name != 'HeldFrontageOpaqueEnclosure' and not name.startswith('RestSideCheek'):
            continue
        if min(p[1] for p in pts) > 102.451:
            walls.append({'name': name, 'above_terrace': True, 'actual_overlap_m2': 0})
            continue
        # Native authoring stores each prism's ordered bottom ring, then its top.
        foot = Polygon([(p[0], p[2]) for p in pts if abs(p[1] - 102) < .002])
        assert foot.is_valid and foot.area > 0, name
        overlap = foot.intersection(terrace).area
        assert overlap < 1e-6, (key, name, overlap)
        walls.append({'name': name, 'actual_bottom_ring_overlap_m2': overlap})
    rows.append({'source_index': int(key), 'raised_area_m2': terrace.area,
                 'one_connected_terrace': True, 'supported_contact_meshes': supports,
                 'original_route_buffer_overlap_m2': terrace.intersection(routes).area,
                 'source_walls': walls})
native = json.loads((P / 'evidence/NATIVE_r003.json').read_text())
assert native['plan_sha256'] == hashlib.sha256(plan_path.read_bytes()).hexdigest()
result = {'pass': True, 'plan_sha256': native['plan_sha256'], 'suites': rows,
          'scope': 'Final floor polygons, selected furniture contact feet and named actual source wall bottom rings',
          'engineering_cart_species_acceptance': False}
out = P / 'evidence/EXACT_GEOMETRY_FINAL.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2) + '\n')
print('PASS final geometry, five connected terraces, zero protected route/wall overlap')
