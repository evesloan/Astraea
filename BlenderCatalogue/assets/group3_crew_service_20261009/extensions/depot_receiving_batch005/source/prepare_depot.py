"""Fit the retained D03 receiving threshold; do not author another enclosure."""
from pathlib import Path
import hashlib
import json
import math
import sys

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
GAME = ROOT / 'Game'
CAT = ROOT / 'BlenderCatalogue'
catalogue = json.loads((CAT / 'catalogue_manifest.json').read_text())
asset_id = 'AST-STF-G3-005'
assert not any(a['catalogue_id'] == asset_id and a.get('family') != 'group3_crew_service_20261009' for a in catalogue['assets'])

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

network = json.loads((GAME / 'data/architecture/LOWER_STAFF_NETWORK.json').read_text())
deck = next(d for d in network['decks'] if d['deck'] == 3)
threshold = next(t for t in deck['thresholds'] if t['name'] == 'depot_threshold')
assert threshold['rectangle'] == [-54, -48, -219, -213]
assert threshold['status'] == 'bounded_unfurnished_threshold_no_stock'
requested = box(-54, -219, -48, -213)
compiled = json.loads((GAME / 'data/generated/structural_meshes.json').read_text())
floor_row = next(q for q in compiled['regions'] if q['id'] == 'D03_port_forward_staff_floor_0')
actual_floor = unary_union([Polygon(t) for t in floor_row['triangles']])
missing_floor = requested.difference(actual_floor).area
assert missing_floor < 1e-8
crew_path = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json'
crew = json.loads(crew_path.read_text())
crew_overlap = sum(requested.intersection(box(q['source_envelope']['x'][0], q['source_envelope']['z'][0], q['source_envelope']['x'][1], q['source_envelope']['z'][1])).area for q in crew['instances'])
assert crew_overlap == 0

reused = []
for asset in ['AST-STF-009', 'AST-STF-007', 'AST-AQU-007', 'AST-HSK-005', 'AST-ENG-003']:
    row = next(a for a in catalogue['assets'] if a['catalogue_id'] == asset)
    source = CAT / row['source']
    export = CAT / row['export']
    assert sha(source) == row['source_sha256']
    assert sha(export) == row['export_sha256']
    reused.append({'catalogue_id': asset, 'path': str(export.relative_to(ROOT)), 'sha256': sha(export), 'original_editable_source': str(source.relative_to(ROOT)), 'original_editable_sha256': sha(source), 'copy_required': False})

instances = [
    {'name': 'DepotCleanWorkCabinet', 'asset': 'AST-STF-007', 'position': [-52.5, 12, -217.85], 'yaw': 0, 'role': 'front clean-supply work and storage; rear inspection approach preserved'},
    {'name': 'DepotDryLinenNiche', 'asset': 'AST-AQU-007', 'position': [-49.8, 12, -217.85], 'yaw': 0, 'role': 'front-loaded dry linen; native folded forms are visual stock only, with a rear inspection stance'},
    {'name': 'ExistingCustodialCartParkingCandidate', 'asset': 'AST-HSK-005', 'position': [-51.4, 12, -214.55], 'yaw': math.pi, 'role': 'off-street candidate for the existing physical cart; no new cart or relocation of custodian_cart_001'},
    {'name': 'DepotMaintenanceConsole', 'asset': 'AST-ENG-003', 'position': [-48.12, 13.45, -214.5], 'yaw': -math.pi / 2, 'role': 'four-pad mount on the retained east wall; live utility operation remains unbound'},
]
parts = [
    {'name': 'DepotTaskFixtureCeilingBackplate', 'aabb': [-50.98, -50.02, 15.16, 15.2, -216.065, -215.735], 'role': 'staff_zinc', 'category': 'fixture_support'},
    {'name': 'DepotTaskFixtureHousing', 'aabb': [-50.92, -50.08, 15.04, 15.16, -216.025, -215.775], 'role': 'staff_bluegrey_paint', 'category': 'lighting_fixture'},
    {'name': 'DepotTaskFixtureLens', 'aabb': [-50.87, -50.13, 15.015, 15.04, -215.99, -215.81], 'role': 'staff_opal', 'category': 'lighting_fixture'},
]
for p in parts:
    p['batch_cell'] = 'D03_depot_receiving'
fixtures = [{'name': 'DepotCleanReceivingTaskLight', 'position': [-50.5, 14.995, -215.9], 'color': [.8, .9, 1], 'range_m': 5.5, 'energy': .75, 'budget_owner': 'Existing receiving_source_lights.gd / lighting_budget.gd'}]
approaches = [
    {'name': 'existing_street_before_receiver', 'position': [-55.0, 12, -216]},
    {'name': 'retained_west_receiver', 'position': [-54, 12, -216]},
    {'name': 'inside_clean_receiving', 'position': [-53.2, 12, -216]},
    {'name': 'clean_cabinet_work', 'position': [-52.5, 12, -216.3]},
    {'name': 'cabinet_rear_inspection', 'position': [-52.5, 12, -218.5]},
    {'name': 'dry_linen_front_load', 'position': [-49.8, 12, -216.65]},
    {'name': 'dry_linen_rear_inspection', 'position': [-49.8, 12, -218.5]},
    {'name': 'existing_cart_rear_grip', 'position': [-51.4, 12, -215.84]},
    {'name': 'maintenance_console_service', 'position': [-49.4, 12, -214.5]},
]
pins = {str(p.relative_to(ROOT)): sha(p) for p in [GAME / 'data/architecture/LOWER_STAFF_NETWORK.json', GAME / 'data/generated/structural_meshes.json', GAME / 'data/whole_ship_layout.json', GAME / 'scripts/cleaning_cart.gd', GAME / 'scripts/staff_section.gd', GAME / 'scripts/receiving_source_lights.gd', GAME / 'scripts/lighting_budget.gd', GAME / 'docs/master_source/MASTER_FULL_CONTENT_INDEX.json', GAME / 'docs/master_source/MASTER_CURRENT_APPLICATION.json', CAT / 'catalogue_manifest.json', CAT / 'materials/staff/manifest.json', CAT / 'assets/staff_workbay/AST-STF-007_supply_work_cabinet.manifest.json', crew_path]}
for p in (CAT / 'materials/staff').glob('*.png'):
    pins[str(p.relative_to(ROOT))] = sha(p)
spec = {'schema': 1, 'catalogue_id': asset_id, 'family': 'group3_crew_service_20261009', 'coordinate_system': 'Godot world metres; retained D03 depot receiving threshold only', 'parts': parts, 'fixtures': fixtures, 'retained_enclosure_asset': 'AST-STF-009', 'retained_threshold': threshold, 'gross_receiving_bounds_xz': [-54, -219, -48, -213], 'receiver': {'position': [-54, 12, -216], 'existing_gross_connection_z': [-217.8, -214.2], 'new_opening_created': False}, 'reused_asset_dependencies': reused, 'reused_asset_instances': instances, 'operator_and_maintenance_approaches': approaches, 'cart_parking': {'bounds_xz': [-52.05, -215.45, -50.75, -213.65], 'existing_identity': 'custodian_cart_001', 'new_cart_spawned_or_existing_cart_relocated': False}, 'floor': {'owner': floor_row['id'], 'floor_y': 12, 'existing_compiled_area_m2': 36, 'additional_missing_floor_m2': missing_floor, 'general_floor_exported': False}, 'source_pins': pins, 'controller_policy': 'Reuse existing static-contact, physical-cart, receiving-light and future root-owned cupboard/stock bindings. The inspected cabinet/stock examples are static; functional restocking and cabinet control are not assumed. No second room, interaction, transport or inventory system.', 'stock_or_capacity_or_occupancy_keys_registered': False, 'clinical_cleanliness_or_sterilized_flow_claimed': False, 'soiled_or_waste_loads_received_here': False, 'retained_east_closure_or_existing_enclosure_changed': False, 'full_depot_or_group3_complete': False, 'unfinished': ['Root adoption of exact rigid asset placements, ceiling light, wall/contact and existing cart binding', 'Functional stock/cabinet state, consumption and save continuity', 'Loaded moving cart, broad body/species, source receiving and actual-main visual/light checks', 'Full D03 depot equipment programme, separate used/waste receiving and all remaining Group 3 obligations']}
(HERE / 'source/DEPOT_RECEIVING.json').write_text(json.dumps(spec, indent=2) + '\n')
report = {'status': 'PASS', 'retained_threshold_area_m2': 36, 'actual_compiled_missing_floor_m2': missing_floor, 'protected_crew_bank_overlap_m2': crew_overlap, 'retained_exact_dependency_assets': len(reused), 'proposed_rigid_equipment_placements': len(instances), 'new_fixture_parts': len(parts), 'new_general_floor_or_enclosure_created': False, 'scope': 'Exact retained threshold, source identities and compiled floor only; native usable fits and operation remain separate.'}
(HERE / 'qa/DEPOT_PLAN_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
