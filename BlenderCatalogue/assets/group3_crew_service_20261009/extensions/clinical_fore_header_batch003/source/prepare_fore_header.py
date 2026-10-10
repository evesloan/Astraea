"""Starboard D05 source header only; preserved source slices are read-only."""
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
FIRST = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009'
CLINICAL = Path('/workspace/shared/astraea_group3_crew_work/extensions/clinical_streets_batch002')
riser = json.loads((FIRST / 'source/STARBOARD_FORWARD_STAFF_RISER.json').read_text())
clinical = json.loads((CLINICAL / 'source/CLINICAL_STREETS.json').read_text())
port = json.loads((GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text())['staff']
assert port['proposed_all_stops_y'] == [0, 6, 12, 46.2, 52.5]
assert any('No new D04' in q for q in port['rules'])
landing = next(q for q in riser['floor_proposals'] if q['deck'] == 'D05')
assert landing['district_link_center'] == [21, 21.0, -496]

def polygons(rows):
    return unary_union([Polygon(q['boundary'], q.get('holes', [])) for q in rows])

def footprint(p):
    if 'aabb' in p:
        x0, x1, y0, y1, z0, z1 = p['aabb']
        return box(x0, z0, x1, z1)
    return Polygon(p['boundary'], p['holes'])

routes = [
    {'id': 'D05_fore_clean_supply', 'points_xz': [[21, -496], [21, -500], [57, -500], [57, -480]], 'role': 'clean_supply'},
    {'id': 'D05_fore_sealed_soiled_return', 'points_xz': [[21, -496], [21, -504], [61, -504], [61, -480]], 'role': 'sealed_soiled_return'}
]
route_shapes = [LineString(q['points_xz']).buffer(1.8, cap_style=2, join_style=2) for q in routes]
route = unary_union(route_shapes)
# The two paths share the source lift transfer area. It is deliberately labelled
# and held for sequential sealed-load operation, not claimed as sterile routing.
transfer_buffer = box(19.06, -505.94, 23.5, -495.86)
shared = route_shapes[0].intersection(route_shapes[1])
wall_shape = route.buffer(.14, join_style=2).difference(route)
mouths = unary_union([box(19.2, -496.3, 22.8, -495.7), box(55.2, -480.3, 58.8, -479.7), box(59.2, -480.3, 62.8, -479.7)])
wall_shape = wall_shape.difference(mouths)
old_clinical_walls = unary_union([footprint(p) for p in clinical['parts'] if p['category'] == 'screen_wall'])
old_clinical_roof = unary_union([footprint(p) for p in clinical['parts'] if p['category'] == 'overhead'])
# Exact face ownership at the two source end seams avoids doubled corner strips.
walls = wall_shape.difference(old_clinical_walls)
roof = route.difference(old_clinical_roof)
parts = []

def prisms(name, geometry, y0, y1, role, category):
    a, b, c, d = geometry.bounds
    for ix in range(math.floor(a / 12), math.floor(c / 12) + 1):
        for iz in range(math.floor(b / 12), math.floor(d / 12) + 1):
            for k, p in enumerate(shapely.get_parts(geometry.intersection(box(ix * 12, iz * 12, (ix + 1) * 12, (iz + 1) * 12)))):
                if p.geom_type != 'Polygon' or p.area < 1e-8:
                    continue
                parts.append({'name': f'{name}_{ix}_{iz}_{k}', 'boundary': list(p.exterior.coords)[:-1],
                              'holes': [list(h.coords)[:-1] for h in p.interiors],
                              'triangles': [list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms],
                              'y': [y0, y1], 'role': role, 'category': category, 'batch_cell': f'{ix}_{iz}'})

def cube(name, bounds, role, category):
    parts.append({'name': name, 'aabb': bounds, 'role': role, 'category': category,
                  'batch_cell': f'{math.floor(bounds[0] / 12)}_{math.floor(bounds[4] / 12)}'})

prisms('ForeHeaderWallLow', walls, 21, 22.02, 'staff_bluegrey_paint', 'screen_wall')
prisms('ForeHeaderWallHigh', walls, 22.02, 25.2, 'staff_white_paint', 'screen_wall')
prisms('ForeHeaderRoof', roof, 25.2, 25.34, 'staff_bluegrey_paint', 'overhead')
# Close the one-metre ceiling step outside the source lobby without modifying its
# real 2.8 m fore opening, its roof or any of the seventeen shaft interfaces.
cube('D05_RiserForeCeilingStep', [19.2, 22.8, 23.8, 25.34, -496.14, -496], 'staff_white_paint', 'receiver_header')
fixtures = []
for i, (x, z) in enumerate([(21, -498), (21, -503), (33, -500), (45, -500), (57, -492), (33, -504), (49, -504), (61, -493)]):
    cube(f'ForeHeaderLightHousing_{i}', [x - .4, x + .4, 25.04, 25.2, z - .14, z + .14], 'staff_zinc', 'lighting_fixture')
    cube(f'ForeHeaderLightDiffuser_{i}', [x - .35, x + .35, 25.015, 25.04, z - .1, z + .1], 'staff_opal', 'lighting_fixture')
    fixtures.append({'name': f'ForeHeaderLight_{i}', 'position': [x, 24.995, z], 'color': [.8, .9, 1], 'range_m': 8, 'energy': .8,
                     'budget_owner': 'Existing receiving_source_lights.gd / lighting_budget.gd'})

compiled_path = GAME / 'data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
old_floor = unary_union([Polygon(t) for r in compiled['regions'] if r['deck'] == 'D05' for t in r['triangles']])
reserved_clinical = polygons(clinical['floor_proposal']['polygons'])
reserved_lobby = polygons(landing['missing_floor_polygons'])
requested = route.buffer(.14, join_style=2)
missing = requested.difference(old_floor.union(reserved_clinical).union(reserved_lobby))
medical = json.loads((GAME / 'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json').read_text())
programmes = unary_union([box(q['envelope']['x'][0], q['envelope']['z'][0], q['envelope']['x'][1], q['envelope']['z'][1]) for q in medical['programmes']])
body = json.loads((GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
inner = Polygon(next(q for q in body['levels'] if q['deck'] == 'D05')['inner_reservation_boundary'])
voids = json.loads((GAME / 'data/spatial_layout.json').read_text())['voids']
void_overlaps = {q['id']: requested.intersection(Polygon(q['boundary'])).area for q in voids if 'D05' in q['decks']}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in [
    FIRST / 'source/STARBOARD_FORWARD_STAFF_RISER.json', FIRST / 'exports/AST-STF-G3-002.glb',
    CLINICAL / 'source/CLINICAL_STREETS.json', CLINICAL / 'exports/AST-MED-G3-002.glb',
    GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json', GAME / 'scripts/lower_staff_network.gd',
    GAME / 'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json', compiled_path,
    GAME / 'data/spatial_layout.json', GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json'
]}
floor = {'deck': 'D05', 'floor_y': 21, 'thickness': .24, 'missing_only_area_m2': missing.area,
         'polygons': [{'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors]} for p in shapely.get_parts(missing) if p.geom_type == 'Polygon' and p.area > 1e-7],
         'dependency': 'Subtract actual compiled slabs plus separately proposed clinical street and starboard lobby floors. Root must adopt all three sources together and recompute; reservations are not existing floor.',
         'general_floor_exported': False}
spec = {'schema': 1, 'catalogue_id': 'AST-MED-G3-003', 'family': 'group3_crew_service_20261009',
        'coordinate_system': 'Godot world metres; bounded starboard D05 fore staff header',
        'parts': parts, 'fixtures': fixtures, 'routes': routes, 'floor_proposal': floor, 'source_pins': pins,
        'interfaces': [{'role': 'reserved_starboard_D05_lobby', 'position': [21, 21, -496], 'clear_aperture_m': [3.6, 2.8],
                        'source': 'AST-STF-G3-002', 'installed': False},
                       {'role': 'clinical_clean_source_end', 'position': [57, 21, -480], 'clear_width_m': 3.6, 'source': 'AST-MED-G3-002', 'installed': False},
                       {'role': 'clinical_soiled_source_end', 'position': [61, 21, -480], 'clear_width_m': 3.6, 'source': 'AST-MED-G3-002', 'installed': False}],
        'shared_lift_transfer_buffer': {'bounds_xz': list(transfer_buffer.bounds), 'shared_floor_area_m2': shared.area,
                                       'sequential_sealed_load_operation_accepted': False,
                                       'policy': 'Shared source arrival uses the existing staff lift. Main branches separate outside this explicit transfer buffer; no simultaneous segregated or sterile lift operation is certified.'},
        'port_D05_stop_constructed': False, 'retained_port_stop_ids_preserved': port['proposed_stop_ids'],
        'port_hold': 'Retained source expressly keeps D04-D07 shaft blank. A port clinical stop needs a separate root-resolved source/identity decision, not a silent extension.',
        'existing_or_frozen_source_modified': False, 'new_controller_or_dynamic_asset': False,
        'unfinished': ['Root combined floor/source/lighting adoption and actual staff cabin boarding',
                       'Shared clean/soiled sealed-load dispatch and source screen/door operation',
                       'Port clinical vertical access, remaining district riser links and service equipment',
                       'Actual body/cart/species, source contact, structure/hull and runtime graphical acceptance']}
(HERE / 'source/CLINICAL_FORE_HEADER.json').write_text(json.dumps(spec, indent=2) + '\n')
checks = {'status': 'PASS', 'source_parts': len(parts), 'clinical_programme_intrusion_m2': requested.intersection(programmes).area,
          'outside_conservative_hull_m2': requested.difference(inner).area, 'protected_void_overlap_m2': void_overlaps,
          'clean_soiled_overlap_outside_shared_buffer_m2': shared.difference(transfer_buffer).area,
          'main_wall_envelope_overlap_outside_shared_buffer_m2': route_shapes[0].buffer(.14, join_style=2).intersection(route_shapes[1].buffer(.14, join_style=2)).difference(transfer_buffer).area,
          'duplicate_clinical_screen_wall_m2': walls.intersection(old_clinical_walls).area,
          'duplicate_clinical_roof_m2': roof.intersection(old_clinical_roof).area,
          'duplicate_compiled_or_reserved_floor_m2': missing.intersection(old_floor.union(reserved_clinical).union(reserved_lobby)).area,
          'unsupported_wall_foot_m2': walls.difference(old_floor.union(reserved_clinical).union(reserved_lobby).union(missing)).area,
          'missing_only_floor_area_m2': missing.area, 'shared_transfer_floor_area_m2': shared.area,
          'port_protected_blank_shaft_preserved': True, 'frozen_sources_modified': False,
          'scope': 'Exact source interfaces and bounded header geometry, not accepted moving cart, lift dispatch or sterile flow.'}
failure = any(checks[k] > 1e-7 for k in ['clinical_programme_intrusion_m2', 'outside_conservative_hull_m2', 'clean_soiled_overlap_outside_shared_buffer_m2',
              'main_wall_envelope_overlap_outside_shared_buffer_m2', 'duplicate_clinical_screen_wall_m2', 'duplicate_clinical_roof_m2',
              'duplicate_compiled_or_reserved_floor_m2', 'unsupported_wall_foot_m2']) or any(v > 1e-7 for v in void_overlaps.values())
checks['status'] = 'FAIL' if failure else 'PASS'
(HERE / 'qa/FORE_HEADER_PLAN_CHECKS.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks))
assert checks['status'] == 'PASS'
