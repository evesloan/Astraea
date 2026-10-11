"""Additive successor interfaces; never cut existing ship or checkpoint floors."""
import hashlib, json, pathlib
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACKAGE = pathlib.Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), 'Preserve prior revision'
    path.write_text(json.dumps(value, indent=2) + '\n')

manifest = json.loads((ROOT / 'BlenderCatalogue/catalogue_manifest.json').read_text())
families = {a['catalogue_id']: a for a in manifest['assets']}
assert families['AST-CIR-003']['family'] == 'commons_lift_cabin'
assert families['AST-DOR-003']['family'] == 'telescoping_gate'
prior = ROOT / 'BlenderCatalogue/assets/group2_completion_20261011'
addendum = json.loads((prior / 'prior_handoff/PRIVATE_MULTILEVEL_FLOOR_ADDENDUM.json').read_text())
floor_path = ROOT / 'Game/data/group2_completion/FLOOR_INTERFACE.json'
floor = json.loads(floor_path.read_text())
pins = {}
for rel in ['BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003.blend',
            'Game/assets/models/AST-CIR-003.glb', 'BlenderCatalogue/assets/telescoping_gate/source/AST-DOR-003.blend',
            'Game/assets/models/AST-DOR-003.glb', 'Game/scripts/commons_lift.gd',
            'Game/scripts/lift_gate.gd', 'Game/scripts/lift_button.gd', 'Game/scripts/player.gd']:
    pins[rel] = sha(ROOT / rel)
suites = []
for old in addendum['entries']:
    key = str(old['source_index'])
    assert key != '790'
    contract_path = ROOT / 'Game/data/group2_completion/contracts' / (key + '.json')
    contract = json.loads(contract_path.read_text())
    assert contract['native_sha256'] == old['native_sha256'] and contract['export_sha256'] == old['export_sha256']
    lift = old['private_lift_proposal']
    pit = Polygon(old['rigid_lift_void_world_xz'])
    lower = next(r for r in floor['rows'] if r['source_owner'] == key and r['floor_y'] == 102)
    lower_geometry = Polygon(lower['boundary'], lower['holes'])
    assert lower_geometry.covers(pit)
    successor = lower_geometry.difference(pit)
    assert successor.is_valid and successor.geom_type == 'Polygon'
    triangles = [list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(successor).geoms]
    assert abs(sum(Polygon(t).area for t in triangles) - successor.area) < 1e-6
    source = {'source_index': old['source_index'], 'contract_sha256': sha(contract_path),
              'native_sha256': old['native_sha256'], 'runtime_sha256': old['export_sha256'],
              'origin_world': lift['lower_origin_world'], 'cabin_yaw': lift['proper_yaw_radians'],
              'landing_gate_outward_mount_m': .26,
              'stops_y': [102, 106.5], 'same_private_unit': True, 'new_unit': False,
              'pit_outline_xz': old['rigid_lift_void_world_xz'],
              'pit_receiver_top_y': 101.58, 'pit_receiver_thickness': .12,
              'platform_bottom_lower_y': 101.82, 'platform_to_pit_clearance_m': .24,
              'lower_successor': {**lower, 'id': lower['id'] + '_PRIVATE_PIT_SUCCESSOR',
                                  'boundary': list(successor.exterior.coords)[:-1],
                                  'holes': [list(h.coords)[:-1] for h in successor.interiors],
                                  'triangles': triangles},
              'replaces_only_unadopted_group2_proposal_region': lower['id'],
              'upper_floor_unchanged_with_existing_lift_void': True,
              'remaining_holds': ['Private lower-neighbour/pit support; no existing protected slab cut authorized',
                                  'Shared receiving/actual body boarding and private access/persistence',
                                  'Whole ship/engineering/species/cart/final game appearance']}
    suites.append(source)
assert len(suites) == 5
write(ROOT / 'Game/data/group2_private_vertical/INTERFACES.json', {
    'schema': 'astraea.group2_private_vertical_interfaces.v1',
    'parent_checkpoint': '75068311728a44aac02732496edf2f810c624841',
    'original_floor_interface_sha256': sha(floor_path), 'new_catalogue_ids': [],
    'only_unadopted_private_proposals_may_be_replaced': True,
    '790_excluded': True, 'shared_root_changed': False,
    'production_floor_or_identity_adoption': False, 'dependency_pins': pins, 'suites': suites})
print('PASS five private lower-pit successors; existing checkpoint floors unchanged')
