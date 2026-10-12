"""Read-only reconciliation of Group2 VIPs and current Group1 standards.

No canonical files or room identities are changed. The shared integrator must
still review the actual receiving meshes/support and adopt physical interfaces.
"""
import hashlib
import json
import pathlib
import subprocess
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACKAGE = pathlib.Path(__file__).resolve().parent
CANONICAL = 'bc731d6d6d54bb2595331ee2f4368558d4d24fda'

def get(path):
    data = subprocess.check_output(['git', 'show', CANONICAL + ':' + path], cwd=ROOT)
    return json.loads(data), hashlib.sha256(data).hexdigest()

plan, plan_sha = get('Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json')
historic, historic_sha = get('Game/data/reference/historical_atlas_allocations.json')
assert historic_sha == hashlib.sha256((ROOT / 'Game/data/reference/historical_atlas_allocations.json').read_bytes()).hexdigest()
standard823, standard_sha = get('Game/data/architecture/STAR_ATLAS_D17_STANDARD823.json')
assert standard823['active'] and standard823['new_units'] == 0
receiving, receiving_sha = get('Game/data/architecture/STAR_ATLAS_D17_RECEIVING_FIRST.json')
actual, floor_sha = get('Game/data/generated/structural_meshes.json')
index = json.loads((PACKAGE / 'prior_handoff/DELIVERY_INDEX.json').read_text())
canonical_vips = {row['source_envelope_index']: row for row in plan['replacements']}
for row in index['luxury_sources']:
    assert row['placement'] == canonical_vips[row['unit_source_index']]
vips = [row for row in index['luxury_sources'] if row['placement']['house'] == 'port_central_upper_house']
standards = [row for row in plan['replanned_standard_units'] if row['house'] == 'port_central_upper_house']
vip_ids = sorted(row['unit_source_index'] for row in vips)
standard_ids = sorted(row['source_envelope_index'] for row in standards)
assert vip_ids == [781, 787, 805, 811, 829, 835, 859]
assert len(standard_ids) == 10 and 823 in standard_ids and not set(vip_ids).intersection(standard_ids)
for vip in vips:
    a = Polygon(vip['placement']['proposed_floor_boundary'])
    for standard in standards:
        assert a.intersection(Polygon(standard['proposed_floor_boundary'])).area < 1e-7
floor = json.loads((ROOT / 'Game/data/group2_completion/FLOOR_INTERFACE.json').read_text())
existing = {}
for row in actual['regions']:
    existing.setdefault(float(row['floor_y']), []).extend(Polygon(t) for t in row['triangles'])
existing = {y: unary_union(parts) for y, parts in existing.items()}
overlap = []
for row in floor['rows']:
    area = Polygon(row['boundary'], row['holes']).intersection(existing.get(float(row['floor_y']), Polygon())).area
    overlap.append({'id': row['id'], 'current_coplanar_overlap_m2': area})
assert sum(row['current_coplanar_overlap_m2'] for row in overlap) < 1e-7
result = {'schema': 'astraea.group2_star_atlas_current_interface.v1', 'pass': True,
          'canonical_checked': CANONICAL, 'group2_retains_distinct_vip_responsibility': True,
          'group2_vips': [{'source_index': row['unit_source_index'], 'tier': row['tier'],
                           'allocation_sha256': row['identity']['allocation_sha256'],
                           'proposed_identity': row['identity']['proposed_runtime_id'],
                           'identity_status': row['identity']['runtime_id_status'],
                           'floor_boundary_xz': row['placement']['proposed_floor_boundary'],
                           'runtime_source': 'Game/assets/group2_completion/' + str(row['unit_source_index']) + '.glb'} for row in vips],
          'group1_standard_source_indices': standard_ids, 'standard823_currently_active': True,
          'duplicated_source_ids': [], 'proposed_vip_standard_floor_overlap_m2': 0,
          'all80_luxury_placements_equal_current_canonical': True,
          'historical_source_sha256_unchanged': historic_sha,
          'current_pins': {'luxury_proposal_sha256': plan_sha, 'standard823_sha256': standard_sha,
                           'receiving_sha256': receiving_sha, 'compiler_floor_sha256': floor_sha},
          'floor_interface_recheck': {'regions': len(overlap), 'current_coplanar_overlap_m2': 0,
                                      'same_preimage': floor_sha == floor['structural_preimage_sha256']},
          'shared_files_changed': False, 'physical_or_identity_adoption': False,
          'remaining_interface': 'Group1 onward floors/service access to exact seven source entry markers; Supreme787 upper/pit/cabin hold; Group7 frontage/support. Recheck live custom receiving/source mesh contacts before adoption.'}
(PACKAGE / 'evidence/STAR_ATLAS_CURRENT_INTERFACE.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'pass': True, 'group2_vips': vip_ids, 'group1_standards': standard_ids,
                  'duplicate_ids': [], 'current_compiler_floor_overlap_m2': 0,
                  'floor_preimage_unchanged': result['floor_interface_recheck']['same_preimage']}))
