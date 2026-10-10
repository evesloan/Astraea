"""Held port2 clinical join and two exact clinical wall-batch replacements."""
from pathlib import Path
import copy
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
CAT = ROOT / 'BlenderCatalogue'
CLINICAL = CAT / 'assets/group3_crew_service_20261009/extensions/clinical_streets_batch002'
clinical_path = CLINICAL / 'source/CLINICAL_STREETS.json'
clinical = json.loads(clinical_path.read_text())
riser = json.loads((HERE / 'source/PORT_SECOND_STAFF_RISER.json').read_text())
landing = next(q for q in riser['floor_proposals'] if q['deck'] == 'D05')
assert landing['district_link_center'] == [-21, 21.0, -289]
assert len(clinical['controlled_crossings']) == 10
catalogue = json.loads((CAT / 'catalogue_manifest.json').read_text())
assert not any(a['catalogue_id'] == 'AST-MED-G3-004' and a.get('family') != 'group3_crew_service_20261009' for a in catalogue['assets'])
door = next(q for q in catalogue['assets'] if q['catalogue_id'] == 'AST-STF-008')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CAT / door['export']) == door['export_sha256']
assert sha(CAT / door['source']) == door['source_sha256']

def geometry(p):
    if 'aabb' in p:
        a, b, _, _, c, d = p['aabb']
        return box(a, c, b, d)
    return Polygon(p['boundary'], p['holes'])

def rows(shape):
    return [{'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors]} for p in shapely.get_parts(shape) if p.geom_type == 'Polygon' and p.area > 1e-8]

def prism(name, p, y, role, category, cell):
    return {'name': name, 'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors], 'triangles': [list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms], 'y': y, 'role': role, 'category': category, 'batch_cell': cell}

routes = [{'id': 'port2_D05_clean_supply_source', 'points_xz': [[-21, -289], [-21, -293], [-57, -293]], 'role': 'clean_supply'}, {'id': 'port2_D05_sealed_load_transfer_source', 'points_xz': [[-21, -289], [-21, -297], [-61, -297]], 'role': 'sealed_soiled_return'}]
shapes = [LineString(q['points_xz']).buffer(1.8, cap_style=2, join_style=2) for q in routes]
route = unary_union(shapes)
retained_clean = LineString(clinical['routes'][0]['proposed_centerline_xz']).buffer(1.8, cap_style=2, join_style=2)
retained_corridors = unary_union([LineString(q['proposed_centerline_xz']).buffer(1.8, cap_style=2, join_style=2) for q in clinical['routes']])
lobby_buffer = box(-23.5, -298.94, -19.06, -288.86)
crossing_buffer = box(-59.34, -299.14, -54.86, -294.86)
main_shared = shapes[0].intersection(shapes[1])
new_crossing = shapes[1].intersection(retained_clean)

# Only the two named native mesh batches in this 24 m source cell are replaced.
# The original remains frozen. Unchanged portions are preserved in the patch.
selected = [p for p in clinical['parts'] if p['category'] == 'screen_wall' and p['batch_cell'] == '-3_-13']
assert len(selected) == 8
mouths = unary_union([box(-55.34, -294.8, -54.92, -291.2), box(-59.34, -298.8, -54.92, -295.2)])
patch = []
changed = []
for p in selected:
    shape = geometry(p)
    if shape.intersection(mouths).area < 1e-8:
        patch.append(copy.deepcopy(p))
        continue
    changed.append(p['name'])
    low, high = p['y']
    clipped = shape.difference(mouths)
    for i, piece in enumerate(shapely.get_parts(clipped)):
        if piece.geom_type == 'Polygon' and piece.area > 1e-8:
            patch.append(prism(p['name'] + f'_receiver_clear_{i}', piece, [low, min(high, 23.8)], p['role'], p['category'], p['batch_cell']))
    if high > 23.8:
        patch.append(prism(p['name'] + '_retained_upper_lintel', shape, [23.8, high], p['role'], p['category'], p['batch_cell']))
replacement_nodes = ['screen_wall_staff_bluegrey_paint_-3_-13', 'screen_wall_staff_white_paint_-3_-13']
patch_spec = {'schema': 1, 'catalogue_id': 'AST-MED-G3-002', 'file_stem': 'AST-MED-G3-002_port2_receiver_patch', 'family': 'group3_crew_service_20261009', 'coordinate_system': 'Godot world metres; partial native clinical wall-cell successor only', 'parts': patch, 'fixtures': [], 'predecessor': {'path': str(clinical_path), 'sha256': sha(clinical_path), 'export': str(CLINICAL / 'exports/AST-MED-G3-002.glb'), 'export_sha256': sha(CLINICAL / 'exports/AST-MED-G3-002.glb')}, 'native_mesh_batches_to_omit_only_during_root_adoption': replacement_nodes, 'original_semantic_parts_in_these_batches': [p['name'] for p in selected], 'original_semantic_parts_changed': changed, 'all_other_original_clinical_native_meshes_and_ten_junctions_retained': True, 'receiver_openings_clear_to_y': 23.8, 'original_sources_modified': False, 'automatic_runtime_adoption': False, 'full_clinical_export': False, 'root_adoption': 'Omit exactly the two named original screen-wall batches and substitute these two partial successor batches only when adopting the held port2 header. Do not load original and replacement batches together. All other clinical source meshes, identities, roofs and ten controlled junctions stay unchanged.'}
(HERE / 'source/CLINICAL_PORT2_RECEIVER_PATCH.json').write_text(json.dumps(patch_spec, indent=2) + '\n')

old_walls = unary_union([geometry(p) for p in clinical['parts'] if p['category'] == 'screen_wall'])
old_roof = unary_union([geometry(p) for p in clinical['parts'] if p['category'] == 'overhead'])
wall = route.buffer(.14, join_style=2).difference(route).difference(retained_corridors).difference(old_walls)
wall = wall.difference(box(-22.8, -289.3, -19.2, -288.7))
roof = route.difference(old_roof)
parts = []

def pieces(name, shape, y, role, category):
    a, b, c, d = shape.bounds
    for ix in range(math.floor(a / 12), math.floor(c / 12) + 1):
        for iz in range(math.floor(b / 12), math.floor(d / 12) + 1):
            for k, p in enumerate(shapely.get_parts(shape.intersection(box(ix * 12, iz * 12, (ix + 1) * 12, (iz + 1) * 12)))):
                if p.geom_type == 'Polygon' and p.area > 1e-8:
                    parts.append(prism(f'{name}_{ix}_{iz}_{k}', p, y, role, category, f'{ix}_{iz}'))

def cube(name, bounds, role, category):
    parts.append({'name': name, 'aabb': bounds, 'role': role, 'category': category, 'batch_cell': f'{math.floor(bounds[0] / 12)}_{math.floor(bounds[4] / 12)}'})

pieces('Port2HeaderWallLow', wall, [21, 22.02], 'staff_bluegrey_paint', 'screen_wall')
pieces('Port2HeaderWallHigh', wall, [22.02, 25.2], 'staff_white_paint', 'screen_wall')
pieces('Port2HeaderRoof', roof, [25.2, 25.34], 'staff_bluegrey_paint', 'overhead')
cube('Port2_D05_LobbyForeCeilingStep', [-22.8, -19.2, 23.8, 25.34, -289.14, -289], 'staff_white_paint', 'receiver_header')
fixtures = []
for i, (x, z) in enumerate([(-21, -291), (-21, -296), (-33, -293), (-45, -293), (-33, -297), (-45, -297), (-57, -297)]):
    cube(f'Port2HeaderLightHousing_{i}', [x - .4, x + .4, 25.04, 25.2, z - .14, z + .14], 'staff_zinc', 'lighting_fixture')
    cube(f'Port2HeaderLightDiffuser_{i}', [x - .35, x + .35, 25.015, 25.04, z - .1, z + .1], 'staff_opal', 'lighting_fixture')
    fixtures.append({'name': f'Port2HeaderLight_{i}', 'position': [x, 24.995, z], 'color': [.8, .9, 1], 'range_m': 8, 'energy': .8, 'budget_owner': 'Existing receiving_source_lights.gd / lighting_budget.gd'})
compiled_path = GAME / 'data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
old_floor = unary_union([Polygon(t) for q in compiled['regions'] if q['deck'] == 'D05' for t in q['triangles']])
clinical_floor = unary_union([Polygon(q['boundary'], q.get('holes', [])) for q in clinical['floor_proposal']['polygons']])
lobby_floor = unary_union([Polygon(q['boundary'], q.get('holes', [])) for q in landing['missing_floor_polygons']])
supported_or_reserved = old_floor.union(clinical_floor).union(lobby_floor)
requested = route.buffer(.14, join_style=2)
missing = requested.difference(supported_or_reserved)
medical_path = GAME / 'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json'
medical = json.loads(medical_path.read_text())
programmes = unary_union([box(q['envelope']['x'][0], q['envelope']['z'][0], q['envelope']['x'][1], q['envelope']['z'][1]) for q in medical['programmes']])
body_path = GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json'
body = json.loads(body_path.read_text())
inner = Polygon(next(q for q in body['levels'] if q['deck'] == 'D05')['inner_reservation_boundary'])
spatial_path = GAME / 'data/spatial_layout.json'
voids = json.loads(spatial_path.read_text())['voids']
void_overlap = {q['id']: requested.intersection(Polygon(q['boundary'])).area for q in voids if 'D05' in q['decks']}
door_manifest = json.loads((CAT / door['manifest']).read_text())
pins = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in [clinical_path, CLINICAL / 'exports/AST-MED-G3-002.glb', HERE / 'source/PORT_SECOND_STAFF_RISER.json', HERE / 'exports/AST-STF-G3-006.glb', compiled_path, medical_path, body_path, spatial_path, GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json', GAME / 'scripts/commons_lift.gd', GAME / 'scripts/service_door.gd', CAT / door['export'], CAT / door['manifest'], CAT / door['source']]}
controls = {'status': 'Held architectural crossing source proposal, never accepted operational segregation', 'retained_clinical_junctions_preserved': 10, 'new_crossing_registered_in_game': False, 'new_proposed_crossing_count': 1, 'bounds_xz': list(crossing_buffer.bounds), 'clean_soiled_shared_floor_area_m2': new_crossing.area, 'existing_controller': 'service_door.gd; root binding only', 'existing_door_asset': 'AST-STF-008', 'existing_door_export_sha256': door['export_sha256'], 'existing_door_frame_metadata': door_manifest, 'gate_positions_proposed_only': [{'role': 'clean_north_hold', 'position': [-57, 21, -299.14], 'yaw': 0}, {'role': 'clean_south_hold', 'position': [-57, 21, -295], 'yaw': 0}, {'role': 'sealed_load_east_hold', 'position': [-54.6, 21, -297], 'yaw': math.pi / 2}, {'role': 'sealed_load_west_hold', 'position': [-59.0, 21, -297], 'yaw': math.pi / 2}], 'dynamic_door_instances_or_new_controller_created': False, 'exact_frame_swing_support_body_and_interlock_acceptance': False, 'required_root_policy': 'Mutually exclusive clean and sealed-load movement through this new crossing, with actual gate/frame/swing/support and interlock proof. Shared geometric floor is not simultaneous segregated or sterile flow.'}
floor = {'deck': 'D05', 'floor_y': 21, 'thickness': .24, 'additional_missing_only_area_m2': missing.area, 'polygons': rows(missing), 'general_floor_exported': False, 'dependency': 'Root composes actual compiled floor with retained clinical street reservations, new port2 lobby proposal and this header; recompute on adoption.'}
spec = {'schema': 1, 'catalogue_id': 'AST-MED-G3-004', 'family': 'group3_crew_service_20261009', 'coordinate_system': 'Godot world metres; distinct port2 D05 clinical source header and held sealed-load crossing', 'parts': parts, 'fixtures': fixtures, 'routes': routes, 'floor_proposal': floor, 'source_pins': pins, 'interfaces': [{'role': 'port2_D05_lobby_fore', 'position': [-21, 21, -289], 'gross_aperture_width_height_m': [3.6, 2.8], 'installed': False}, {'role': 'retained_port_clean_clinical_street', 'position': [-57, 21, -293], 'gross_clear_width_m': 3.6, 'installed': False}, {'role': 'retained_port_soiled_clinical_street', 'position': [-61, 21, -297], 'gross_clear_width_m': 3.6, 'installed': False}], 'shared_lift_transfer_buffer': {'bounds_xz': list(lobby_buffer.bounds), 'shared_floor_area_m2': main_shared.area, 'sequential_sealed_load_operation_accepted': False}, 'held_new_clean_soiled_crossing': controls, 'clinical_partial_receiver_patch': 'CLINICAL_PORT2_RECEIVER_PATCH.json; exactly two native wall-cell batches, never a full clinical re-export', 'retained_ten_clinical_junctions_preserved': True, 'protected_fore_port_shaft_modified': False, 'original_clinical_or_other_frozen_sources_modified': False, 'new_controller_capacity_people_stock_or_live_gate_keys': 0, 'unfinished': ['Root source/floor/receiver adoption and distinct port2 cabin boarding', 'Exact four gate/frame/leaf/swing/support interfaces and mutually exclusive sealed-load crossing policy', 'Sixteen other port2 district receivers, remaining shafts and service distribution', 'Body/cart/species, source structure/hull, real dispatch and actual-main visual/light acceptance']}
(HERE / 'source/PORT2_CLINICAL_HEADER.json').write_text(json.dumps(spec, indent=2) + '\n')
lower_patch_walls = unary_union([geometry(p) for p in patch if p['y'][0] < 23.8])
original_selected_walls = unary_union([geometry(p) for p in selected])
expected_lower = original_selected_walls.difference(mouths)
checks = {'status': 'PASS', 'new_header_parts': len(parts), 'partial_patch_parts': len(patch), 'native_clinical_wall_batches_replaced': 2, 'original_semantic_parts_changed': len(changed), 'clinical_programme_intrusion_m2': requested.intersection(programmes).area, 'outside_conservative_hull_m2': requested.difference(inner).area, 'protected_void_overlap_m2': void_overlap, 'clean_soiled_overlap_outside_lobby_buffer_m2': main_shared.difference(lobby_buffer).area, 'new_sealed_load_on_retained_clean_floor_outside_held_crossing_m2': new_crossing.difference(crossing_buffer).area, 'duplicate_retained_clinical_wall_m2': wall.intersection(old_walls).area, 'duplicate_retained_clinical_roof_m2': roof.intersection(old_roof).area, 'new_missing_floor_duplicate_m2': missing.intersection(supported_or_reserved).area, 'unsupported_header_wall_foot_m2': wall.difference(supported_or_reserved.union(missing)).area, 'partial_patch_lower_wall_symmetric_error_m2': lower_patch_walls.symmetric_difference(expected_lower).area, 'additional_header_missing_floor_m2': missing.area, 'shared_lobby_floor_m2': main_shared.area, 'new_held_crossing_floor_m2': new_crossing.area, 'retained_clinical_junction_count': 10, 'new_junction_registered': False, 'original_source_modified': False, 'scope': 'Bounded port2 source connection and exact partial receiver patch. New controlled crossing is explicitly held; no automatic adoption, sterile flow or completed connection.'}
zero_keys = ['clinical_programme_intrusion_m2', 'outside_conservative_hull_m2', 'clean_soiled_overlap_outside_lobby_buffer_m2', 'new_sealed_load_on_retained_clean_floor_outside_held_crossing_m2', 'duplicate_retained_clinical_wall_m2', 'duplicate_retained_clinical_roof_m2', 'new_missing_floor_duplicate_m2', 'unsupported_header_wall_foot_m2', 'partial_patch_lower_wall_symmetric_error_m2']
passed = all(checks[k] < 1e-7 for k in zero_keys) and all(v < 1e-7 for v in void_overlap.values())
checks['status'] = 'PASS' if passed else 'FAIL'
(HERE / 'qa/PORT2_CLINICAL_PLAN_CHECKS.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks))
assert passed
