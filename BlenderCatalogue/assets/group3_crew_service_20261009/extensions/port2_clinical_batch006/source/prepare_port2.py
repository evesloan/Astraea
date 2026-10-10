"""Distinct reserved port2 shaft; no alteration of the protected fore shaft."""
from pathlib import Path
import copy
import hashlib
import json
import math
import sys
import struct

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
GAME = ROOT / 'Game'
FIRST = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009'
catalogue = json.loads((ROOT / 'BlenderCatalogue/catalogue_manifest.json').read_text())
assert not any(a['catalogue_id'] == 'AST-STF-G3-006' and a.get('family') != 'group3_crew_service_20261009' for a in catalogue['assets'])
plan = json.loads((GAME / 'data/whole_ship_layout.json').read_text())
reservation = next(q for q in plan['staff_riser_reservations'] if q['id'] == 'port_service_riser_2')
assert reservation['center_xz'] == [-25, -283]
assert reservation['shaft_x'] == [-27.2, -22.8] and reservation['shaft_z'] == [-285.2, -280.8]
fore = json.loads((GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text())['staff']
assert fore['proposed_stop_ids'] == ['D01', 'D02', 'D03', 'D08_WET', 'D09']
assert any('No new D04' in q for q in fore['rules'])
prototype_path = FIRST / 'source/STARBOARD_FORWARD_STAFF_RISER.json'
prototype = json.loads(prototype_path.read_text())
parts = copy.deepcopy(prototype['parts'])
for p in parts:
    a, b, y0, y1, c, d = p['aabb']
    p['aabb'] = [-b, -a, y0, y1, c + 207, d + 207]
    p['name'] = 'Port2_' + p['name']
fixtures = copy.deepcopy(prototype['fixtures'])
for q in fixtures:
    q['position'][0] *= -1
    q['position'][2] += 207
    q['name'] = 'Port2_' + q['name']
contract = json.loads((GAME / 'data/design_contract.json').read_text())
stops = [q for q in contract['deck_datums'] if q['deck_id'] != 'D18']
assert len(stops) == 17
compiled_path = GAME / 'data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
body = json.loads((GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
voids = json.loads((GAME / 'data/spatial_layout.json').read_text())['voids']
crew_path = FIRST / 'source/CREW_BANK_PLACEMENTS_PROPOSAL.json'
crew = json.loads(crew_path.read_text())
requested = box(-23.18, -289, -18.8, -277)
shaft = box(-27.2, -285.2, -23.18, -280.8)
envelope = box(-27.2, -289, -18.8, -277)
crew_overlap = sum(envelope.intersection(box(q['source_envelope']['x'][0], q['source_envelope']['z'][0], q['source_envelope']['x'][1], q['source_envelope']['z'][1])).area for q in crew['instances'])
assert crew_overlap == 0

def rows(geometry):
    return [{'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors]} for p in shapely.get_parts(geometry) if p.geom_type == 'Polygon' and p.area > 1e-8]

floor_rows, checks = [], []
for i, datum in enumerate(stops):
    deck, y = datum['deck_id'], datum['floor_elevation_m']
    current = unary_union([Polygon(t) for q in compiled['regions'] if q['deck'] == deck for t in q['triangles']])
    missing = requested.difference(current)
    cuts = current.intersection(shaft)
    inner = Polygon(next(q for q in body['levels'] if q['deck'] == deck)['inner_reservation_boundary'])
    overlap = {q['id']: envelope.intersection(Polygon(q['boundary'])).area for q in voids if deck in q['decks']}
    next_y = contract['deck_datums'][i + 1]['floor_elevation_m']
    floor_rows.append({'deck': deck, 'floor_y': y, 'missing_floor_polygons': rows(missing), 'missing_area_m2': missing.area, 'existing_supported_lobby_area_m2': requested.intersection(current).area, 'existing_floor_cut_required_m2': cuts.area, 'existing_floor_cut_polygons': rows(cuts), 'floor_owners_requiring_root_cut_review': [q['id'] for q in compiled['regions'] if q['deck'] == deck and unary_union([Polygon(t) for t in q['triangles']]).intersection(shaft).area > 1e-8], 'shaft_exclusion': list(shaft.exterior.coords)[:-1], 'gate_center': [-23.08, y, -283], 'district_link_center': [-21, y, -289], 'state': 'Source-only reservation receiving; no stop or floor/cut installed'})
    checks.append({'deck': deck, 'outside_conservative_hull_m2': envelope.difference(inner).area, 'protected_void_overlap_m2': overlap, 'missing_floor_duplicate_m2': missing.intersection(current).area, 'new_floor_in_shaft_m2': missing.intersection(shaft).area, 'next_canonical_datum_roof_clearance_m': next_y - .24 - (y + 3.34), 'existing_floor_cut_held_m2': cuts.area})
binding = copy.deepcopy(prototype['controller_binding_proposal'])
binding.update({'reservation_id': reservation['id'], 'center': [-25, 0, -283], 'yaw': math.pi, 'moving_cabin_floor_x': [-26.8, -23.2], 'moving_cabin_floor_z': [-285, -281], 'moving_gate_x': -23.32, 'landing_gate_x': -23.08, 'persistent_lift_identity_registered': False, 'cabin_file': 'AST-CIR-003_seventeen_stop.glb', 'gate_origin_xz_local': [-1.8, 0], 'cabin_visual_origin_at_each_stop_xz': [-23.2, -283], 'cabin_visual_world_yaw': math.pi / 2, 'protected_fore_lift_identity_reused_or_modified': False})
controller_fields = {'floor_heights': [q['floor_elevation_m'] for q in stops], 'deck_numbers': list(range(1, 18)), 'stop_ids': [q['deck_id'] for q in stops], 'stop_names': [q['historical_program_label'] for q in stops], 'stop_codes': [q['deck_id'] for q in stops], 'gate_origin_xz': [-1.8, 0], 'cabin_file': 'AST-CIR-003_seventeen_stop.glb'}
assert binding['stop_y'] == controller_fields['floor_heights']
assert controller_fields['stop_ids'] == [f'D{i:02}' for i in range(1, 18)]
assert all(b > a for a, b in zip(controller_fields['floor_heights'], controller_fields['floor_heights'][1:]))
binding['explicit_controller_fields_proposal'] = controller_fields
binding['identity_fields_held_for_root_save_review'] = ['persistent_id', 'identity_prefix', 'district_label']
binding['identity_review_rule'] = 'Resolve distinct existing reservation and save identities before controller creation. Do not inherit commons defaults or reuse any installed lift identity. This source registers no identities.'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
cabin = ROOT / 'BlenderCatalogue/assets/commons_lift_cabin/exports/AST-CIR-003_seventeen_stop.glb'
cabin_source = ROOT / 'BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003_seventeen_stop.blend'
cabin_manifest = ROOT / 'BlenderCatalogue/assets/commons_lift_cabin/AST-CIR-003_seventeen_stop.manifest.json'
raw = cabin.read_bytes()
ln = struct.unpack_from('<I', raw, 12)[0]
cabin_native = json.loads(raw[20:20 + ln])
markers = [q for q in cabin_native['nodes'] if q.get('name', '').startswith('DATUM_floor_button_')]
assert len(markers) == 17 and {q['name'] for q in markers} == {f'DATUM_floor_button_{i}' for i in range(17)}
marker_by_name = {q['name']: q for q in markers}
ordered = []
for i, datum in enumerate(stops):
    marker = marker_by_name[f'DATUM_floor_button_{i}']
    expected = [1.73, .75 + .22 * (i // 3), -.56 - .42 * (i % 3)]
    assert max(abs(a - b) for a, b in zip(marker['translation'], expected)) < 1e-6
    ordered.append({'index': i, 'marker': marker['name'], 'native_local_godot_position': marker['translation'], 'deck_number': i + 1, 'stop_id': datum['deck_id'], 'stop_name': datum['historical_program_label'], 'floor_y': datum['floor_elevation_m']})
audit = {'status': 'PASS', 'source_reservation': 'port_service_riser_2', 'controller': 'Existing commons_lift.gd', 'controller_sha256': sha(GAME / 'scripts/commons_lift.gd'), 'physical_stop_control_markers': 17, 'exact_markers_numeric_order': [q['marker'] for q in ordered], 'controller_stop_order': ordered, 'explicit_controller_fields_proposal': controller_fields, 'identity_fields_held_for_root_save_review': binding['identity_fields_held_for_root_save_review'], 'retained_cabin_export': str(cabin.relative_to(ROOT)), 'retained_cabin_export_sha256': sha(cabin), 'retained_editable_cabin_source': str(cabin_source.relative_to(ROOT)), 'retained_editable_cabin_source_sha256': sha(cabin_source), 'gate_origin_xz_local': [-1.8, 0], 'cabin_visual_origin_D05': [-23.2, 21, -283], 'cabin_visual_world_yaw': math.pi / 2, 'separate_first_starboard_correction_proposal': {'frozen_source': str(prototype_path.relative_to(ROOT)), 'frozen_source_sha256': sha(prototype_path), 'original_proposed_cabin_file': prototype['controller_binding_proposal']['cabin_file'], 'reason': 'The frozen source proposes seventeen stops but its three-stop cabin has only three physical button markers. commons_lift.gd requires every stop marker and a local gate origin matching the authored shaft.', 'explicit_controller_fields_proposal_for_root_review': controller_fields, 'cabin_visual_origin_at_each_stop_xz': [23.2, -490], 'cabin_visual_world_yaw': -math.pi / 2, 'identity_fields_held_for_root_save_review': binding['identity_fields_held_for_root_save_review'], 'stop_order_or_save_keys_changed': False, 'frozen_source_modified': False}, 'source_only_no_runtime_binding_applied': True, 'validation_scope': 'Exact native marker count, unique numeric order and physical positions versus the existing controller contract. No dynamic lift, door, save or route test.'}
(HERE / 'qa/CABIN_BINDING_AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')
pins = {str(p.relative_to(ROOT)): sha(p) for p in [prototype_path, FIRST / 'exports/AST-STF-G3-002.glb', GAME / 'data/whole_ship_layout.json', GAME / 'data/design_contract.json', compiled_path, GAME / 'data/spatial_layout.json', GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json', GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json', GAME / 'scripts/commons_lift.gd', cabin, cabin_source, cabin_manifest, crew_path, ROOT / 'BlenderCatalogue/catalogue_manifest.json', GAME / 'docs/master_source/MASTER_FULL_CONTENT_INDEX.json', GAME / 'docs/master_source/MASTER_CURRENT_APPLICATION.json']}
spec = {'schema': 1, 'catalogue_id': 'AST-STF-G3-006', 'family': 'group3_crew_service_20261009', 'coordinate_system': 'Godot world metres; distinct retained port_service_riser_2 reservation', 'parts': parts, 'fixtures': fixtures, 'source_pins': pins, 'reservation': reservation, 'controller_binding_proposal': binding, 'floor_proposals': floor_rows, 'roof_limit_y': 105.34, 'D18_connection_created': False, 'protected_fore_port_lift_modified': False, 'protected_fore_stop_ids': fore['proposed_stop_ids'], 'protected_fore_stops_y': fore['proposed_all_stops_y'], 'population_or_registered_berths_added': 0, 'new_controller_or_dynamic_asset': False, 'unfinished': ['Root floor/aperture/cut review and existing controller binding for the distinct retained reservation', 'Sixteen other same-side district receivers beyond the held D05 clinical link', 'Actual cabin/gate boarding, source support, body/cart/species and structure/hull acceptance', 'Crown/D18 connection and final in-engine visual/light acceptance']}
(HERE / 'source/PORT_SECOND_STAFF_RISER.json').write_text(json.dumps(spec, indent=2) + '\n')
passed = all(q['outside_conservative_hull_m2'] < 1e-8 and all(v < 1e-8 for v in q['protected_void_overlap_m2'].values()) and q['missing_floor_duplicate_m2'] < 1e-8 and q['new_floor_in_shaft_m2'] < 1e-8 and q['next_canonical_datum_roof_clearance_m'] > 0 for q in checks)
report = {'status': 'PASS' if passed else 'FAIL', 'source_parts': len(parts), 'protected_200_crew_envelope_overlap_m2': crew_overlap, 'checks': checks, 'additional_missing_lobby_floor_m2': sum(q['missing_area_m2'] for q in floor_rows), 'existing_floor_cut_held_m2': sum(q['existing_floor_cut_required_m2'] for q in floor_rows), 'protected_fore_blank_D04_D07_shaft_preserved': True, 'new_working_stops_or_general_floors_registered': False, 'scope': 'Seventeen source datum/reservation checks, not a full route audit or working lift acceptance. Required existing-floor cuts are explicitly held for root adoption.'}
(HERE / 'qa/PORT2_RISER_PLAN_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))
assert passed
