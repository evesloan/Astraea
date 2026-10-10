"""Three fitted exterior fore service bays; no frozen source or game edits."""
from pathlib import Path
import copy
import hashlib
import json
import math
import sys

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
GAME = ROOT / 'Game'
CAT = ROOT / 'BlenderCatalogue'
HEADER = Path('/workspace/shared/astraea_group3_crew_work/extensions/clinical_fore_header_batch003')
CLINICAL = Path('/workspace/shared/astraea_group3_crew_work/extensions/clinical_streets_batch002')
FIRST = CAT / 'assets/group3_crew_service_20261009'
catalogue = json.loads((CAT / 'catalogue_manifest.json').read_text())['assets']
assert not any(q['catalogue_id'] == 'AST-STF-G3-004' and q.get('family') != 'group3_crew_service_20261009' for q in catalogue)
parts = []
fixtures = []
bays = [
    {'name': 'clean_linen_supply', 'bounds_xz': [29, -498.2, 37, -494.2], 'receiver': [33, 21, -498.2], 'front': -1},
    {'name': 'maintenance_and_custodial_cart', 'bounds_xz': [39, -498.2, 47, -493], 'receiver': [43, 21, -498.2], 'front': -1},
    {'name': 'used_linen_and_closed_waste', 'bounds_xz': [39, -509.8, 47, -505.8], 'receiver': [43, 21, -505.8], 'front': 1}
]
floor_shape = unary_union([box(*q['bounds_xz']) for q in bays])
mouths = unary_union([box(q['receiver'][0] - 1.2, q['receiver'][2] - .3, q['receiver'][0] + 1.2, q['receiver'][2] + .3) for q in bays])
wall_shape = floor_shape.buffer(.14, join_style=2).difference(floor_shape).difference(mouths)

def prisms(target, name, geometry, y0, y1, role, category):
    if geometry.is_empty:
        return
    for k, p in enumerate(shapely.get_parts(geometry)):
        if p.geom_type != 'Polygon' or p.area < 1e-8:
            continue
        a, b, c, d = p.bounds
        target.append({'name': f'{name}_{k}', 'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors],
                       'triangles': [list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms],
                       'y': [y0, y1], 'role': role, 'category': category, 'batch_cell': f'{math.floor(a / 12)}_{math.floor(b / 12)}'})

def cube(name, bounds, role='staff_white_paint', category='service_fittings'):
    parts.append({'name': name, 'aabb': bounds, 'role': role, 'category': category,
                  'batch_cell': f'{math.floor(bounds[0] / 12)}_{math.floor(bounds[4] / 12)}'})

prisms(parts, 'ServiceBayWallLow', wall_shape, 21, 22.02, 'staff_bluegrey_paint', 'screen_wall')
prisms(parts, 'ServiceBayWallHigh', wall_shape, 22.02, 25.2, 'staff_white_paint', 'screen_wall')
prisms(parts, 'ServiceBayRoof', floor_shape, 25.2, 25.34, 'staff_bluegrey_paint', 'overhead')
for i, q in enumerate(bays):
    x, y, z = q['receiver']
    lintel_z = [z - .14, z] if q['front'] == -1 else [z, z + .14]
    cube(q['name'] + '_ReceiverLintel', [x - 1.2, x + 1.2, 23.8, 25.2, *lintel_z], 'staff_white_paint', 'receiver_header')
    light_z = (q['bounds_xz'][1] + q['bounds_xz'][3]) / 2
    cube(q['name'] + '_LightHousing', [x - .45, x + .45, 25.04, 25.2, light_z - .14, light_z + .14], 'staff_zinc', 'lighting_fixture')
    cube(q['name'] + '_LightDiffuser', [x - .4, x + .4, 25.015, 25.04, light_z - .1, light_z + .1], 'staff_opal', 'lighting_fixture')
    fixtures.append({'name': q['name'] + '_TaskLight', 'position': [x, 24.995, light_z], 'color': [.8, .9, 1], 'range_m': 6, 'energy': .8,
                     'budget_owner': 'Existing receiving_source_lights.gd / lighting_budget.gd'})

# Two physical closed staging receivers are missing from the retained catalogue.
# Thin actual walls/base, discrete feet, continuous gasket and seated lid retain
# the empty core. They are fixed source hardware; no certified vessel or contents.
containers = []
for name, x in [('used_textile_closed_staging', 42.55), ('closed_waste_staging', 45.45)]:
    z = -508.65
    a, b, c, d = x - .45, x + .45, z - .4, z + .4
    for ix in [-1, 1]:
        for iz in [-1, 1]:
            xx, zz = x + ix * .35, z + iz * .3
            cube(name + f'_FloorPad_{ix}_{iz}', [xx - .05, xx + .05, 21, 21.04, zz - .05, zz + .05], 'staff_rubber', 'container_support')
            cube(name + f'_SupportLeg_{ix}_{iz}', [xx - .035, xx + .035, 21.04, 21.16, zz - .035, zz + .035], 'staff_zinc', 'container_support')
    cube(name + '_ActualBase', [a, b, 21.14, 21.18, c, d], 'staff_bluegrey_paint', 'container_body')
    cube(name + '_LeftWall', [a, a + .02, 21.18, 22, c, d], 'staff_white_paint', 'container_body')
    cube(name + '_RightWall', [b - .02, b, 21.18, 22, c, d], 'staff_white_paint', 'container_body')
    cube(name + '_RearWall', [a + .02, b - .02, 21.18, 22, c, c + .02], 'staff_white_paint', 'container_body')
    cube(name + '_FrontWall', [a + .02, b - .02, 21.18, 22, d - .02, d], 'staff_white_paint', 'container_body')
    for suffix, bb in [('Left', [a, a + .025, 22, 22.025, c, d]), ('Right', [b - .025, b, 22, 22.025, c, d]),
                       ('Rear', [a + .025, b - .025, 22, 22.025, c, c + .025]), ('Front', [a + .025, b - .025, 22, 22.025, d - .025, d])]:
        cube(name + '_ContinuousGasket' + suffix, bb, 'staff_rubber', 'container_gasket')
    cube(name + '_SeatedClosedLid', [a - .015, b + .015, 22.025, 22.06, c - .015, d + .015], 'staff_bluegrey_paint', 'container_lid')
    for ix in [-1, 1]:
        xx = x + ix * .27
        cube(name + f'_RearHingeMount_{ix}', [xx - .05, xx + .05, 21.94, 22.065, c - .018, c + .025], 'staff_zinc', 'container_hardware')
        cube(name + f'_FrontLatch_{ix}', [xx - .035, xx + .035, 21.9, 22.065, d - .005, d + .025], 'staff_zinc', 'container_hardware')
    for ix in [-1, 1]:
        xx = x + ix * .15
        cube(name + f'_LidGripMount_{ix}', [xx - .015, xx + .015, 22.06, 22.115, z + .17, z + .2], 'staff_zinc', 'container_hardware')
    cube(name + '_ActualLidGrip', [x - .165, x + .165, 22.095, 22.125, z + .17, z + .2], 'staff_rubber', 'container_hardware')
    cube(name + '_IdentificationBacking', [x - .22, x + .22, 21.58, 21.75, d, d + .008], 'staff_label', 'container_identification')
    containers.append({'name': name, 'floor_position': [x, 21, z], 'outside_bounds_xz': [a - .015, c - .018, b + .015, d + .025],
                       'empty_core_world_bounds': [a + .025, b - .025, 21.18, 22, c + .025, d - .025],
                       'physical_grip': [x, 22.125, z + .185], 'operator_floor_position': [x, 21, -507.2],
                       'lid_hinge_datum': [x, 22.04, c], 'content_or_mass_capacity_registered': False,
                       'status': 'Geometrically closed source staging receiver; latch/lid operation, load and hygienic/fluid performance are not accepted'})

wanted = ['AST-STF-007', 'AST-AQU-007', 'AST-MED-004', 'AST-HSK-005', 'AST-HSK-004', 'AST-ENG-003']
dependencies = []
for asset in wanted:
    row = next(q for q in catalogue if q['catalogue_id'] == asset)
    path = CAT / row['export']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == row['export_sha256']
    dependencies.append({'catalogue_id': asset, 'path': str(path.relative_to(ROOT)), 'sha256': digest, 'copy_required': False})
instances = [
    {'name': 'CleanWorkCabinet', 'asset': 'AST-STF-007', 'position': [30.25, 21, -495.7], 'yaw': math.pi, 'role': 'clean supply and work surface'},
    {'name': 'CleanDryLinenNiche', 'asset': 'AST-AQU-007', 'position': [32.5, 21, -495.7], 'yaw': math.pi, 'role': 'front-loaded dry linen; native folded forms are visual stock only'},
    {'name': 'CleanSupplyTrolleyParking', 'asset': 'AST-MED-004', 'position': [35.6, 21, -496.6], 'yaw': math.pi, 'role': 'closed-supply trolley candidate; no driving/persistent ID created'},
    {'name': 'MaintenanceWorkCabinet', 'asset': 'AST-STF-007', 'position': [40.35, 21, -494.5], 'yaw': math.pi, 'role': 'custodial work and supply storage'},
    {'name': 'CustodialCartParking', 'asset': 'AST-HSK-005', 'position': [43, 21, -496], 'yaw': 0, 'role': 'parking candidate for existing physical cart; preserve custodian_cart_001 unless root explicitly binds a relocation'},
    {'name': 'MaintenanceConsole', 'asset': 'AST-ENG-003', 'position': [45.5, 22.45, -493], 'yaw': math.pi, 'role': 'actual four-pad wall-mounted maintenance receiver; live utility connection remains unbound'},
    {'name': 'UsedOnlyCarrierParking', 'asset': 'AST-HSK-004', 'position': [40.7, 21, -508.4], 'yaw': 0, 'role': 'open used-textile carrier; never labelled sealed or mixed with clean stock'}
]
parking = [
    {'name': 'closed_supply_trolley', 'bounds_xz': [34.8, -497.6, 36.4, -495.4], 'receiver': [33, 21, -498.2], 'asset': 'AST-MED-004'},
    {'name': 'existing_custodial_cart_candidate', 'bounds_xz': [42.15, -497.1, 43.85, -494.7], 'receiver': [43, 21, -498.2], 'asset': 'AST-HSK-005'},
    {'name': 'used_only_linen_carrier', 'bounds_xz': [40.0, -509.6, 41.4, -507.3], 'receiver': [43, 21, -505.8], 'asset': 'AST-HSK-004'}
]
approaches = [
    {'name': 'clean_work', 'position': [29.95, 21, -497.15]}, {'name': 'clean_linen_retrieval', 'position': [32.5, 21, -496.9]},
    {'name': 'clean_rear_service', 'position': [32.5, 21, -494.8]}, {'name': 'clean_cart_grip', 'position': [35.6, 21, -495.7]},
    {'name': 'maintenance_work', 'position': [40.05, 21, -495.95]}, {'name': 'maintenance_rear_service', 'position': [40.35, 21, -493.6]},
    {'name': 'custodial_cart_grip', 'position': [43, 21, -494.65]}, {'name': 'console_service', 'position': [45.5, 21, -494.1]},
    {'name': 'used_carrier_front', 'position': [40.7, 21, -507.55]}, {'name': 'used_carrier_rear_grip', 'position': [40.7, 21, -509.3]},
    {'name': 'used_textile_closed_receiver', 'position': [42.55, 21, -507.2]}, {'name': 'closed_waste_receiver', 'position': [45.45, 21, -507.2]}
]

# A small derivative of the fore header opens exactly three new receiving slots.
# The protected header and its identities/controller contract are not overwritten.
header = json.loads((HEADER / 'source/CLINICAL_FORE_HEADER.json').read_text())
new_header = copy.deepcopy(header)
new_header['file_stem'] = 'AST-MED-G3-003_equipment_receiving'
new_header['parts'] = []
changed = []
for p in header['parts']:
    if p['category'] != 'screen_wall':
        new_header['parts'].append(p)
        continue
    poly = Polygon(p['boundary'], p['holes'])
    cut = poly.intersection(mouths)
    if cut.area < 1e-8:
        new_header['parts'].append(p)
        continue
    changed.append(p['name'])
    prisms(new_header['parts'], p['name'] + '_RetainedOutsideReceivers', poly.difference(mouths), *p['y'], p['role'], p['category'])
    if p['y'][1] > 23.8:
        prisms(new_header['parts'], p['name'] + '_ExistingReceiverHeader', cut, max(p['y'][0], 23.8), p['y'][1], p['role'], p['category'])
new_header['equipment_receiver_derivative'] = {'predecessor_path': str(HEADER / 'source/CLINICAL_FORE_HEADER.json'),
    'predecessor_sha256': hashlib.sha256((HEADER / 'source/CLINICAL_FORE_HEADER.json').read_bytes()).hexdigest(),
    'changed_wall_parts_only': changed, 'receiver_clear_aperture_m': [2.4, 2.8],
    'all_frozen_sources_changed': False, 'root_adoption': 'Use this small header variant instead of the original AST-MED-G3-003 export when adopting these bays. Retain the same source asset and all original lift/route identities.'}
(HERE / 'source/HEADER_EQUIPMENT_SUCCESSOR.json').write_text(json.dumps(new_header, indent=2) + '\n')

compiled_path = GAME / 'data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
old_floor = unary_union([Polygon(t) for q in compiled['regions'] if q['deck'] == 'D05' for t in q['triangles']])
poly_rows = lambda rows: unary_union([Polygon(q['boundary'], q.get('holes', [])) for q in rows])
clinical = json.loads((CLINICAL / 'source/CLINICAL_STREETS.json').read_text())
reserved = poly_rows(header['floor_proposal']['polygons']).union(poly_rows(clinical['floor_proposal']['polygons']))
riser = json.loads((FIRST / 'source/STARBOARD_FORWARD_STAFF_RISER.json').read_text())
reserved = reserved.union(poly_rows(next(q for q in riser['floor_proposals'] if q['deck'] == 'D05')['missing_floor_polygons']))
requested = floor_shape.buffer(.14, join_style=2)
missing = requested.difference(old_floor.union(reserved))
medical = json.loads((GAME / 'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json').read_text())
programmes = unary_union([box(q['envelope']['x'][0], q['envelope']['z'][0], q['envelope']['x'][1], q['envelope']['z'][1]) for q in medical['programmes']])
body = json.loads((GAME / 'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
inner = Polygon(next(q for q in body['levels'] if q['deck'] == 'D05')['inner_reservation_boundary'])
voids = json.loads((GAME / 'data/spatial_layout.json').read_text())['voids']
void_overlap = {q['id']: requested.intersection(Polygon(q['boundary'])).area for q in voids if 'D05' in q['decks']}
pins = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
    HEADER / 'source/CLINICAL_FORE_HEADER.json', HEADER / 'exports/AST-MED-G3-003.glb', CLINICAL / 'source/CLINICAL_STREETS.json',
    compiled_path, GAME / 'scripts/cleaning_cart.gd', GAME / 'scripts/staff_section.gd', GAME / 'scripts/grand_pool_receiving_stock.gd', GAME / 'scripts/service_door.gd',
    GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json', CAT / 'catalogue_manifest.json'
]}
floor = {'deck': 'D05', 'floor_y': 21, 'thickness': .24, 'additional_missing_only_area_m2': missing.area,
         'polygons': [{'boundary': list(p.exterior.coords)[:-1], 'holes': [list(h.coords)[:-1] for h in p.interiors]} for p in shapely.get_parts(missing) if p.geom_type == 'Polygon' and p.area > 1e-7],
         'general_floor_exported': False, 'dependency': 'Root composes with actual slabs and previously proposed clinical/header/riser floors; reservations are not installed floors.'}
spec = {'schema': 1, 'catalogue_id': 'AST-STF-G3-004', 'family': 'group3_crew_service_20261009',
        'coordinate_system': 'Godot world metres; exterior D05 fore service receiving bays', 'parts': parts, 'fixtures': fixtures,
        'bays': bays, 'reused_asset_dependencies': dependencies, 'reused_asset_instances': instances,
        'off_corridor_cart_parking': parking, 'operator_and_maintenance_approaches': approaches, 'closed_staging_receivers': containers,
        'floor_proposal': floor, 'source_pins': pins, 'receiver_clear_aperture_m': [2.4, 2.8],
        'header_derivative': 'HEADER_EQUIPMENT_SUCCESSOR.json / AST-MED-G3-003_equipment_receiving.glb; do not load the original header concurrently',
        'live_stock_or_new_inventory_or_person_keys_registered': False, 'existing_cart_identity_reassigned': False,
        'controller_policy': 'Use the existing physical-cart, static-contact, receiving-light and room/service-door infrastructure. Current cabinet and receiving stock examples are static; functional cabinet, lid and stock bindings are root-owned and not assumed to exist. No second interaction, room or transport system is written.',
        'clinical_or_sterile_or_fluid_certification': False, 'frozen_source_or_blank_port_shaft_modified': False,
        'unfinished': ['Root floor/source receiving, door/light and exact existing asset/stock/cart bindings',
                       'Closed staging latch/lid operation and sealed-load handling policy', 'Real utility trunk connection and maintenance safety/acoustics',
                       'Detailed dynamic loaded-cart/actor/species and in-engine/source structure acceptance', 'Distributed equipment elsewhere in the crew/service network']}
(HERE / 'source/SERVICE_RECEIVING.json').write_text(json.dumps(spec, indent=2) + '\n')
checks = {'status': 'PASS', 'new_source_parts': len(parts), 'bays': len(bays), 'reused_asset_instances': len(instances),
          'clinical_programme_intrusion_m2': requested.intersection(programmes).area, 'outside_conservative_hull_m2': requested.difference(inner).area,
          'protected_void_overlap_m2': void_overlap, 'duplicate_actual_or_reserved_floor_m2': missing.intersection(old_floor.union(reserved)).area,
          'unsupported_new_wall_foot_m2': wall_shape.difference(old_floor.union(reserved).union(missing)).area,
          'additional_missing_only_floor_m2': missing.area, 'header_receiver_wall_parts_changed': changed,
          'existing_port_or_frozen_sources_modified': False, 'scope': 'Source receiving geometry and actual component proposals; detailed native fits and all live operation remain separate.'}
failure = any(checks[k] > 1e-7 for k in ['clinical_programme_intrusion_m2', 'outside_conservative_hull_m2', 'duplicate_actual_or_reserved_floor_m2', 'unsupported_new_wall_foot_m2']) or any(v > 1e-7 for v in void_overlap.values())
checks['status'] = 'FAIL' if failure else 'PASS'
(HERE / 'qa/SERVICE_RECEIVING_PLAN_CHECKS.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks))
assert checks['status'] == 'PASS'
