"""Prepare exact retained proposals for the original compiler; never install them."""
from pathlib import Path
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parent
GAME = Path('/workspace/astraea-protected-integration-20261012/Game')
INPUT = ROOT / 'immutable_inputs/Game/data'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def polygon_area(ring):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2


floor_bytes = (INPUT / 'group2_completion/FLOOR_INTERFACE.json').read_bytes()
interface_bytes = (INPUT / 'group2_private_vertical/INTERFACES.json').read_bytes()
source = json.loads(floor_bytes)
private = json.loads(interface_bytes)
assert sha(floor_bytes) == private['original_floor_interface_sha256']
assert private['only_unadopted_private_proposals_may_be_replaced']
assert private['790_excluded'] and source['790_excluded']
current_bytes = (GAME / 'data/generated/structural_meshes.json').read_bytes()
current = json.loads(current_bytes)
assert len(current['regions']) == 303
current_ids = {r['id'] for r in current['regions']}
rows = copy.deepcopy(source['rows'])
replacements = []
for suite in private['suites']:
    old_id = suite['replaces_only_unadopted_group2_proposal_region']
    matches = [i for i, row in enumerate(rows) if row['id'] == old_id]
    assert len(matches) == 1 and old_id not in current_ids
    i = matches[0]
    old, new = rows[i], copy.deepcopy(suite['lower_successor'])
    for key in ['source_owner', 'deck', 'floor_y', 'thickness']:
        assert old[key] == new[key], (old_id, key)
    # The retained successor starts the same oriented ring at its next vertex.
    assert len(old['boundary']) == len(new['boundary'])
    rotations = [old['boundary'][offset:] + old['boundary'][:offset]
                 for offset in range(len(old['boundary']))]
    assert new['boundary'] in rotations, (old_id, 'boundary_geometry')
    assert old['holes'] == [] and len(new['holes']) == 1
    assert suite['upper_floor_unchanged_with_existing_lift_void']
    rows[i] = new
    replacements.append({'old_id': old_id, 'new_id': new['id'],
                         'exact_retained_pit_area_m2': polygon_area(new['holes'][0])})

compiled = []
installed_pairs = {'port_forward_upper_house', 'starboard_forward_upper_house',
                   'port_central_upper_house', 'starboard_central_upper_house'}
skipped = []
for row in rows:
    # Installed adjuncts have separately verified relief/approach successors.
    if row['source_owner'] in installed_pairs:
        skipped.append(row['id'])
        continue
    assert row['id'] not in current_ids and row['source_owner'] != '790'
    ring_area = polygon_area(row['boundary']) - sum(map(polygon_area, row['holes']))
    triangle_area = sum(polygon_area(t) for t in row['triangles'])
    assert abs(ring_area - triangle_area) < 0.00001, row['id']
    assert all(polygon_area(t) > 0 for t in row['triangles']), row['id']
    row['rings'] = [copy.deepcopy(row['boundary']), *copy.deepcopy(row['holes'])]
    row['structural_area_m2'] = triangle_area
    row['material_role'] = 'guest_floor'
    row['render_chunks'] = []
    compiled.append(row)
assert len(compiled) == 87
assert sum(r['floor_y'] == 106.5 for r in compiled) == 5
assert len({r['id'] for r in compiled}) == 87
out = ROOT / 'source_floor_regions'
out.mkdir(exist_ok=True)
payload = json.dumps({'schema': 'astraea.approved_receiver_source_floors.v1',
                      'production_adoption': False, 'regions': compiled}, indent=2) + '\n'
(out / 'REGIONS.json').write_text(payload)
receipt = {'status': 'PASS_EXACT_SOURCE_COMPILER_CONVERSION_NOT_INSTALLED',
           'source_floor_interface_sha256': sha(floor_bytes),
           'private_interface_sha256': sha(interface_bytes),
           'current_303_regions_file_sha256': sha(current_bytes),
           'output_sha256': sha(payload.encode()), 'source_rows': len(rows),
           'prepared_regions': len(compiled), 'unchanged_installed_pair_rows_excluded': skipped,
           'source_pit_successors': replacements,
           'home_lower_regions': sum(r['floor_y'] == 102 and str(r['source_owner']).isdigit()
                                     for r in compiled),
           'same_unit_upper_regions': 5, 'uninstalled_aft_adjunct_regions': 2,
           'prepared_area_m2': sum(r['structural_area_m2'] for r in compiled),
           'original_303_regions_changed': False, 'source_triangles_changed': False,
           'geometry_bearings_or_clearance_accepted': False,
           'engines_or_imports_started': False}
(out / 'VERIFICATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'prepared_regions', 'home_lower_regions',
                                         'same_unit_upper_regions', 'prepared_area_m2']}))
