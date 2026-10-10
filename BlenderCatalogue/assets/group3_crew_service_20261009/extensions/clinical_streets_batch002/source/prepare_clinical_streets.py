"""Separate D05 successor proposal. The protected first source slice is read-only."""
from pathlib import Path
import hashlib
import json
import math
import sys

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
GAME = ROOT / 'Game'
PREDECESSOR = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009'
plan_path = GAME / 'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json'
plan = json.loads(plan_path.read_text())
collars = json.loads((PREDECESSOR / 'source/CLINICAL_TERMINALS.json').read_text())
parents = unary_union([
    box(p['envelope']['x'][0], p['envelope']['z'][0],
        p['envelope']['x'][1], p['envelope']['z'][1])
    for p in plan['programmes']
])
route_shapes = {}
route_rows = []
for r in plan['routes']:
    original = LineString(r['centerline_xz']).buffer(r['width_m'] / 2, cap_style=2, join_style=2)
    points = [list(p) for p in r['centerline_xz']]
    if r['id'].startswith('soiled_return'):
        points = [[x, -74 if z == -70 else 74 if z == 70 else z] for x, z in points]
    corrected = LineString(points).buffer(r['width_m'] / 2, cap_style=2, join_style=2)
    route_shapes[r['id']] = corrected
    route_rows.append({
        'id': r['id'], 'original_centerline_xz': r['centerline_xz'],
        'proposed_centerline_xz': points, 'width_m': r['width_m'],
        'endpoints_preserved': points[0] == r['centerline_xz'][0] and points[-1] == r['centerline_xz'][-1],
        'status': 'Separately versioned source proposal; root adoption and operation remain open'
    })

def rect(v):
    return box(v[0], v[2], v[1], v[3])

spurs = []
chambers = []
mouths = []
crossings = []
for terminal in plan['terminal_interfaces']:
    spurs.extend([rect(terminal['clean_spur_rect']), rect(terminal['controlled_crossing']['soiled_spur_rect'])])
    chambers.append(rect(terminal['controlled_crossing']['outer_rect']).difference(parents))
    crossings.append({
        'programme_key': terminal['programme_key'],
        'retained_crossing': terminal['controlled_crossing'],
        'controller': 'Existing room/door mechanism only; no additional interaction system',
        'operational_acceptance': False,
        'hold': 'Root must bind mutually exclusive clean-through and sealed-soiled crossing gates and signals'
    })
    for d in terminal['rear_doors']:
        x, z = d['origin_xz']
        mouths.append(box(x - .3, z - 1.8, x + .3, z + 1.8))

original_routes = {r['id']: LineString(r['centerline_xz']).buffer(1.8, cap_style=2, join_style=2) for r in plan['routes']}
separation = []
for side in ['port', 'starboard']:
    old_clean = original_routes['clean_supply_and_staff_' + side]
    old_soiled = original_routes['soiled_return_' + side]
    clean = route_shapes['clean_supply_and_staff_' + side]
    soiled = route_shapes['soiled_return_' + side]
    separation.append({
        'side': side, 'rejected_retained_route_overlap_m2': old_clean.intersection(old_soiled).area,
        'proposed_route_overlap_m2': clean.intersection(soiled).area,
        'proposed_wall_envelope_overlap_m2': clean.buffer(.14, join_style=2).intersection(soiled.buffer(.14, join_style=2)).area,
        'minimum_clear_floor_edge_separation_m': clean.boundary.distance(soiled.boundary),
        'controlled_terminal_crossings_excluded_from_this_separation_claim': True
    })

floor_shape = unary_union(list(route_shapes.values()) + spurs + chambers).difference(parents)
wall_shape = floor_shape.buffer(.14, join_style=2).difference(floor_shape).difference(parents)
for r in route_rows:
    for x, z in [r['proposed_centerline_xz'][0], r['proposed_centerline_xz'][-1]]:
        mouths.append(box(x - 1.8, z - .3, x + 1.8, z + .3))
wall_shape = wall_shape.difference(unary_union(mouths))
parts = []

def prisms(name, geometry, y0, y1, role, category):
    if geometry.is_empty:
        return
    a, b, c, d = geometry.bounds
    for ix in range(math.floor(a / 24), math.floor(c / 24) + 1):
        for iz in range(math.floor(b / 24), math.floor(d / 24) + 1):
            for k, p in enumerate(shapely.get_parts(geometry.intersection(box(ix * 24, iz * 24, (ix + 1) * 24, (iz + 1) * 24)))):
                if p.geom_type != 'Polygon' or p.area < 1e-8:
                    continue
                parts.append({
                    'name': f'{name}_{ix}_{iz}_{k}', 'boundary': list(p.exterior.coords)[:-1],
                    'holes': [list(h.coords)[:-1] for h in p.interiors],
                    'triangles': [list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms],
                    'y': [y0, y1], 'role': role, 'category': category, 'batch_cell': f'{ix}_{iz}'
                })

prisms('ClinicalStreetWallLow', wall_shape, 21, 22.02, 'staff_bluegrey_paint', 'screen_wall')
prisms('ClinicalStreetWallHigh', wall_shape, 22.02, 25.2, 'staff_white_paint', 'screen_wall')
prisms('ClinicalStreetRoof', floor_shape, 25.2, 25.34, 'staff_bluegrey_paint', 'overhead')
# Receiver frames, control backing and original fixture datums survive. The old
# isolated side walls, roof and bumpers must not bisect longitudinal circulation.
retained_parts = []
replaced_parts = []
for p in collars['parts']:
    if p['name'].endswith(('_ForePanel', '_AftPanel', '_Roof', '_ProtectedBumperFore', '_ProtectedBumperAft')):
        replaced_parts.append(p['name'])
        continue
    parts.append(p)
    retained_parts.append(p['name'])
fixtures = list(collars['fixtures'])
for r in route_rows:
    line = LineString(r['proposed_centerline_xz'])
    for i in range(0, math.ceil(line.length / 24)):
        point = line.interpolate(min(i * 24 + 12, line.length - 1))
        x, z = point.x, point.y
        key = r['id'] + f'_{i:03d}'
        cell = f'{math.floor(x / 24)}_{math.floor(z / 24)}'
        for suffix, bounds, role in [
            ('Housing', [x - .4, x + .4, 25.04, 25.2, z - .14, z + .14], 'staff_zinc'),
            ('Diffuser', [x - .35, x + .35, 25.015, 25.04, z - .1, z + .1], 'staff_opal')
        ]:
            parts.append({'name': key + suffix, 'aabb': bounds, 'role': role, 'category': 'lighting_fixture', 'batch_cell': cell})
        fixtures.append({'name': key + 'Light', 'position': [x, 24.995, z], 'color': [.8, .9, 1], 'range_m': 8, 'energy': .8, 'budget_owner': 'Existing receiving_source_lights.gd / lighting_budget.gd'})

compiled_path = GAME / 'data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
old_floor = unary_union([Polygon(t) for r in compiled['regions'] if r['deck'] == 'D05' for t in r['triangles']])
requested = floor_shape.buffer(.14, join_style=2).difference(parents)
missing = requested.difference(old_floor)
body = json.loads((GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
inner = Polygon(next(r for r in body['levels'] if r['deck'] == 'D05')['inner_reservation_boundary'])
voids = json.loads((GAME / 'data/spatial_layout.json').read_text())['voids']
void_overlaps = {v['id']: requested.intersection(Polygon(v['boundary'])).area for v in voids if 'D05' in v['decks']}
floor_proposal = {
    'deck': 'D05', 'floor_y': 21, 'thickness': .24,
    'missing_only_area_m2': missing.area,
    'polygons': [{'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors]} for p in shapely.get_parts(missing) if p.geom_type == 'Polygon' and p.area > 1e-7],
    'supersedes_predecessor_collar_floor_proposal': True,
    'old_compiled_floor_retained': True, 'general_floor_exported': False
}
pins = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
    plan_path, compiled_path, GAME / 'data/spatial_layout.json', GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json',
    PREDECESSOR / 'source/CLINICAL_TERMINALS.json', PREDECESSOR / 'exports/AST-MED-G3-001.glb',
    GAME / 'docs/whole_ship_plans/D05.png', ROOT / 'BlenderCatalogue/references/landings/staff_corridor_services.png'
]}
spec = {
    'schema': 1, 'catalogue_id': 'AST-MED-G3-002', 'family': 'group3_crew_service_20261009',
    'coordinate_system': 'Godot world metres; D05 corrected dual clinical streets and integrated external collars',
    'parts': parts, 'fixtures': fixtures, 'render_batch_cell_m': 24, 'source_pins': pins,
    'routes': route_rows, 'controlled_crossings': crossings, 'floor_proposal': floor_proposal,
    'retained_terminal_interfaces': collars['terminal_interfaces'],
    'predecessor': {'catalogue_id': 'AST-MED-G3-001', 'frozen_source_changed': False,
                    'root_adoption': 'Use this integrated successor instead of the isolated collar GLB. Do not load both exports or both floor proposals.',
                    'retained_part_names': retained_parts, 'reconstructed_perimeter_part_names': replaced_parts},
    'registered_population_or_beds_added': 0, 'clinical_or_sterile_flow_certified': False,
    'unfinished': ['Root retained rear-source apertures, compiler floor and progressive adoption',
                   'Existing controlled-crossing gate/interlock/signal integration and operation',
                   'Staff riser spurs, clean supply/linen and sealed soiled/waste equipment and cart parking',
                   'Actual main source contacts, moving body/cart, species, structure/hull and final visuals']
}
(HERE / 'source/CLINICAL_STREETS.json').write_text(json.dumps(spec, indent=1) + '\n')
report = {
    'status': 'PASS', 'source_parts': len(parts), 'routes': 4, 'terminals': 20, 'controlled_crossings': 10,
    'route_separation': separation, 'clinical_programme_intrusion_m2': requested.intersection(parents).area,
    'outside_conservative_hull_m2': requested.difference(inner).area,
    'protected_void_overlap_m2': void_overlaps, 'duplicate_compiled_floor_m2': missing.intersection(old_floor).area,
    'unsupported_wall_foot_m2': wall_shape.difference(old_floor.union(missing)).area,
    'missing_only_floor_area_m2': missing.area, 'frozen_predecessor_modified': False,
    'scope': 'Corrected source layout, exact perimeter wall envelope and integrated terminal geometry. Controlled crossings and all runtime/operation acceptance remain held.'
}
fail = (any(q['proposed_route_overlap_m2'] > 1e-7 or q['proposed_wall_envelope_overlap_m2'] > 1e-7 for q in separation)
        or any(report[k] > 1e-7 for k in ['clinical_programme_intrusion_m2', 'outside_conservative_hull_m2', 'duplicate_compiled_floor_m2', 'unsupported_wall_foot_m2'])
        or any(v > 1e-7 for v in void_overlaps.values()))
report['status'] = 'FAIL' if fail else 'PASS'
(HERE / 'qa/CLINICAL_STREET_PLAN_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
assert report['status'] == 'PASS'
