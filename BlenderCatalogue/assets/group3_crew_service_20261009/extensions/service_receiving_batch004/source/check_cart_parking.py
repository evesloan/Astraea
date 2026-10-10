"""Bounded conservative native-body/driver proxies inside the three new bays."""
from pathlib import Path
import json
import math
import sys

sys.path.insert(0, '/workspace/shared/astraea_python_deps')
from shapely import affinity
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
spec = json.loads((HERE / 'source/SERVICE_RECEIVING.json').read_text())
native = json.loads((HERE / 'qa/SERVICE_RECEIVING_NATIVE_GEOMETRY.json').read_text())
assert native['status'] == 'PASS'
header = json.loads((HERE / 'source/HEADER_EQUIPMENT_SUCCESSOR.json').read_text())
bounds = {q['instance']: q for q in native['actual_native_component_bounds']}

def part_shape(p):
    if 'aabb' in p:
        a, b, y0, y1, c, d = p['aabb']
        return box(a, c, b, d), y0
    return Polygon(p['boundary'], p['holes']), p['y'][0]

fixed = []
for p in spec['parts'] + header['parts']:
    shape, minimum_y = part_shape(p)
    if minimum_y < 22.95:
        fixed.append(shape)
clear_floor = unary_union([box(*q['bounds_xz']) for q in spec['bays']] + [LineString(q['points_xz']).buffer(1.8, cap_style=2, join_style=2) for q in header['routes']])
fixed_source = unary_union(fixed)

def local_cart(q):
    a, b, y0, y1, c, d = q['world_aabb']
    x, y, z = q['position']
    return affinity.rotate(affinity.translate(box(a, c, b, d), -x, -z), math.degrees(q['yaw']), origin=(0, 0))

paths = {
    'CleanSupplyTrolleyParking': {'rear_driver_local_z': -.9, 'poses': [
        (35.6, -496.6, 180), (35.6, -497.4, 180), (35.6, -497.4, 225), (35.6, -497.4, 270),
        (34.3, -497.4, 270), (33, -497.4, 270), (33, -497.4, 225), (33, -497.4, 180),
        (33, -498, 180), (33, -498.6, 180)]},
    'CustodialCartParking': {'rear_driver_local_z': 1.29, 'poses': [
        (43, -496, 0), (43, -496.6, 0), (43, -497.2, 0), (43, -497.8, 0), (43, -498.4, 0)]},
    'UsedOnlyCarrierParking': {'rear_driver_local_z': -.9, 'poses': [
        (40.7, -508.4, 0), (40.7, -507.6, 0), (40.7, -506.8, 0), (40.7, -506.8, 45),
        (40.7, -506.8, 90), (41.6, -506.8, 90), (43, -506.8, 90), (43, -506.8, 45),
        (43, -506.8, 0), (43, -506.1, 0), (43, -505.4, 0)]}
}
checks = []
parking_fits = []
for name, path in paths.items():
    q = bounds[name]
    cart = local_cart(q)
    obstacles = list(fixed)
    for other_name, other in bounds.items():
        if other_name == name:
            continue
        a, b, y0, y1, c, d = other['world_aabb']
        obstacles.append(box(a, c, b, d))
        if other['asset'] == 'AST-STF-007':
            # Exact retained continuous door sweep bounds, converted from source
            # Blender XYZ to native XZ and the approved pi-yaw cabinet placement.
            x, y, z = other['position']
            obstacles.append(box(x + .0643698, z - 1.0896303, x + 1.0559138, z - .2849999))
    obstacle = unary_union(obstacles)
    for x, z, degrees in path['poses']:
        angle = math.radians(degrees)
        body = affinity.translate(affinity.rotate(cart, -degrees, origin=(0, 0)), x, z)
        rear = path['rear_driver_local_z']
        driver = Point(x + rear * math.sin(angle), z + rear * math.cos(angle)).buffer(.28)
        proxy = body.union(driver)
        collision = proxy.intersection(obstacle).area
        outside = proxy.difference(clear_floor).area
        checks.append({'instance': name, 'position_xz': [x, z], 'yaw_degrees': degrees,
                       'native_bounds_and_driver_collision_area_m2': collision, 'outside_proposed_clear_floor_m2': outside,
                       'minimum_proxy_to_fixed_boundary_m': proxy.distance(obstacle), 'pass': collision < 1e-7 and outside < 1e-7})
    park = next(r for r in spec['off_corridor_cart_parking'] if r['asset'] == q['asset'])
    a, b, y0, y1, c, d = q['world_aabb']
    missing = box(a, c, b, d).difference(box(*park['bounds_xz'])).area
    parking_fits.append({'instance': name, 'native_parked_body_outside_reserved_parking_m2': missing, 'pass': missing < 1e-7})
report = {'status': 'PASS' if all(q['pass'] for q in checks + parking_fits) else 'FAIL', 'bounded_body_driver_poses': checks,
          'actual_native_parking_bounds_checks': parking_fits, 'loaded_cart_dynamics_or_tether_or_loose_contents_tested': False,
          'scope': 'Twenty-six conservative native cart-body AABB plus radius 0.28 driver proxy poses through the new receiving bays only, including retained cabinet continuous sweep bounds. Proposed floor and coarse proxies are not actual moving-cart/species acceptance.'}
(HERE / 'qa/CART_PARKING_PROXY_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'poses': len(checks), 'parking_fits': parking_fits, 'failed': [q for q in checks if not q['pass']]}))
assert report['status'] == 'PASS'
