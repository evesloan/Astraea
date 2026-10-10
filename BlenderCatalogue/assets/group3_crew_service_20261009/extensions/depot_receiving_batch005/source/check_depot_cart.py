"""Nine native-body/contact and driver proxy poses at the retained depot only."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
from shapely import affinity
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
spec = json.loads((HERE / 'source/DEPOT_RECEIVING.json').read_text())
native = json.loads((HERE / 'qa/DEPOT_NATIVE_GEOMETRY.json').read_text())
assert native['status'] == 'PASS'
deps = {q['catalogue_id']: q for q in spec['reused_asset_dependencies']}
bounds = {q['instance']: q for q in native['actual_native_component_bounds']}
cart = bounds['ExistingCustodialCartParkingCandidate']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Retained enclosure nodes are identity transforms and contain actual world
# vertices. Project only source surfaces in the cart/driver height band.
path = ROOT / deps['AST-STF-009']['path']
assert sha(path) == deps['AST-STF-009']['sha256']
data = path.read_bytes()
length, _ = struct.unpack_from('<II', data, 12)
gltf = json.loads(data[20:20 + length])
binary_start = 20 + length + 8
binary = data[binary_start:]

def accessor(index):
    a = gltf['accessors'][index]
    view = gltf['bufferViews'][a['bufferView']]
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    columns = {'SCALAR': 1, 'VEC3': 3}[a['type']]
    fmt, size = {5126: ('f', 4), 5125: ('I', 4), 5123: ('H', 2)}[a['componentType']]
    stride = view.get('byteStride', columns * size)
    return [struct.unpack_from('<' + fmt * columns, binary, start + i * stride) for i in range(a['count'])]

local_area = box(-59, -220, -48, -212)
fixed = []
native_triangles_considered = 0
for node in gltf['nodes']:
    if node.get('extras', {}).get('deck') != 3 or 'mesh' not in node:
        continue
    assert not any(k in node for k in ['matrix', 'translation', 'rotation', 'scale'])
    for primitive in gltf['meshes'][node['mesh']]['primitives']:
        verts = accessor(primitive['attributes']['POSITION'])
        indices = [q[0] for q in accessor(primitive['indices'])]
        for offset in range(0, len(indices), 3):
            tri = [verts[i] for i in indices[offset:offset + 3]]
            if max(q[1] for q in tri) <= 12.05 or min(q[1] for q in tri) >= 13.9:
                continue
            shape = Polygon([(q[0], q[2]) for q in tri])
            if shape.area > 1e-10 and shape.intersects(local_area):
                fixed.append(shape.intersection(local_area))
                native_triangles_considered += 1

for name, q in bounds.items():
    if name == cart['instance']:
        continue
    x0, x1, y0, y1, z0, z1 = q['world_aabb']
    fixed.append(box(x0, z0, x1, z1))
manifest_path = ROOT / 'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.manifest.json'
manifest = json.loads(manifest_path.read_text())
sweep = manifest['door']['continuous_sweep_aabb_blender_m']
q = next(q for q in spec['reused_asset_instances'] if q['asset'] == 'AST-STF-007')
assert q['yaw'] == 0
x, _, z = q['position']
fixed.append(box(x + sweep['min'][0], z - sweep['max'][1], x + sweep['max'][0], z - sweep['min'][1]))
obstacles = unary_union(fixed)

compiled_path = ROOT / 'Game/data/generated/structural_meshes.json'
compiled = json.loads(compiled_path.read_text())
floor_row = next(q for q in compiled['regions'] if q['id'] == spec['floor']['owner'])
clear_floor = unary_union([Polygon(t) for t in floor_row['triangles']])
x0, x1, _, _, z0, z1 = cart['world_aabb']
cx, _, cz = cart['position']
body = affinity.rotate(affinity.translate(box(x0, z0, x1, z1), -cx, -cz), math.degrees(cart['yaw']), origin=(0, 0))
contacts_path = ROOT / 'Game/data/architecture/cleaning_cart_contacts.json'
contacts = json.loads(contacts_path.read_text())
contact_shapes = []
for b in contacts['boxes']:
    x, _, z = b['center']
    sx, _, sz = b['size']
    contact_shapes.append(box(x - sx / 2 - .001, z - sz / 2 - .001, x + sx / 2 + .001, z + sz / 2 + .001))
for b in contacts['wheel_contacts']:
    x, _, z = b['center']
    contact_shapes.append(Point(x, z).buffer(b['radius']))
body = unary_union([body] + contact_shapes)
poses = [(-51.4, -214.55, 180), (-51.4, -215.2, 180), (-51.4, -215.2, 135), (-51.4, -215.2, 90), (-52.0, -215.6, 90), (-52.7, -216, 90), (-53.4, -216, 90), (-54.0, -216, 90), (-54.8, -216, 90)]
checks = []
for x, z, degrees in poses:
    angle = math.radians(degrees)
    moved_body = affinity.translate(affinity.rotate(body, -degrees, origin=(0, 0)), x, z)
    # Source grip is +Z .67. A conservative driver centre .62 behind it is a
    # declared proxy, not a rewritten or accepted physical tether/controller.
    driver = Point(x + 1.29 * math.sin(angle), z + 1.29 * math.cos(angle)).buffer(.28)
    proxy = moved_body.union(driver)
    collision = proxy.intersection(obstacles).area
    unsupported = proxy.difference(clear_floor).area
    checks.append({'cart_position_xz': [x, z], 'yaw_degrees': degrees, 'native_body_contacts_driver_collision_m2': collision, 'outside_actual_compiled_support_m2': unsupported, 'minimum_proxy_to_fixed_surface_m': proxy.distance(obstacles), 'pass': collision < 1e-8 and unsupported < 1e-8})
parking = box(*spec['cart_parking']['bounds_xz'])
parking_outside = box(x0, z0, x1, z1).difference(parking).area
passed = all(q['pass'] for q in checks) and parking_outside < 1e-8
report = {'status': 'PASS' if passed else 'FAIL', 'bounded_body_contact_driver_poses': checks, 'actual_native_body_outside_reserved_parking_m2': parking_outside, 'native_enclosure_projected_surface_triangles': native_triangles_considered, 'source_input_pins': {str(p.relative_to(ROOT)): sha(p) for p in [path, compiled_path, contacts_path, manifest_path, ROOT / 'Game/scripts/cleaning_cart.gd']}, 'continuous_cabinet_sweep_bounds_included': True, 'existing_cart_or_bottle_identities_modified': False, 'live_loaded_cart_tether_or_loose_products_or_full_route_tested': False, 'scope': 'Nine local conservative native-body AABB, actual retained solid-contact footprint and radius 0.28 driver proxy poses. Actual compiled support and source enclosure footprints included. No driven cart or species/stock/gameplay acceptance.'}
(HERE / 'qa/DEPOT_CART_PROXY_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'poses': len(checks), 'parking_outside_m2': parking_outside, 'minimum_proxy_gap_m': min(q['minimum_proxy_to_fixed_surface_m'] for q in checks), 'failed': [q for q in checks if not q['pass']]}))
assert passed
