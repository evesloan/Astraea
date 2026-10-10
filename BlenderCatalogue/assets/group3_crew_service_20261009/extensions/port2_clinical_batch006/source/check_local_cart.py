"""Twelve stationary native-body/contact/driver proxy poses at the new header."""
from pathlib import Path
import hashlib, json, math, sys
sys.path.insert(0, '/workspace/shared/astraea_python_deps')
from shapely import affinity
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parents[1]
ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
FIRST=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009'
depot=FIRST/'extensions/depot_receiving_batch005'
nativepath=depot/'qa/DEPOT_NATIVE_GEOMETRY.json'
native=json.loads(nativepath.read_text());assert native['status']=='PASS'
deps=json.loads((depot/'source/DEPOT_RECEIVING.json').read_text())['reused_asset_dependencies']
cartdep=next(q for q in deps if q['catalogue_id']=='AST-HSK-005')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/cartdep['path'])==cartdep['sha256']
cart=next(q for q in native['actual_native_component_bounds'] if q['asset']=='AST-HSK-005')
x0,x1,_,_,z0,z1=cart['world_aabb'];cx,_,cz=cart['position']
body=affinity.rotate(affinity.translate(box(x0,z0,x1,z1),-cx,-cz),math.degrees(cart['yaw']),origin=(0,0))
contactpath=ROOT/'Game/data/architecture/cleaning_cart_contacts.json'
contacts=json.loads(contactpath.read_text())
pieces=[body]
for q in contacts['boxes']:
    x,_,z=q['center'];sx,_,sz=q['size'];pieces.append(box(x-sx/2-.001,z-sz/2-.001,x+sx/2+.001,z+sz/2+.001))
for q in contacts['wheel_contacts']:
    x,_,z=q['center'];pieces.append(Point(x,z).buffer(q['radius']))
body=unary_union(pieces)
clinicalpath=FIRST/'extensions/clinical_streets_batch002/source/CLINICAL_STREETS.json'
clinical=json.loads(clinicalpath.read_text())
patch=json.loads((HERE/'source/CLINICAL_PORT2_RECEIVER_PATCH.json').read_text())
header=json.loads((HERE/'source/PORT2_CLINICAL_HEADER.json').read_text())
riser=json.loads((HERE/'source/PORT_SECOND_STAFF_RISER.json').read_text())
parts=[q for q in clinical['parts'] if q['name'] not in patch['original_semantic_parts_in_these_batches']]+patch['parts']+header['parts']+riser['parts']
fixed=[]
local=box(-64,-303,-18,-275)
for q in parts:
    if 'aabb' in q:
        a,b,lo,hi,c,d=q['aabb'];shape=box(a,c,b,d)
    else:
        lo,hi=q['y'];shape=Polygon(q['boundary'],q['holes'])
    if hi<=21.05 or lo>=22.9:continue
    if shape.intersects(local):fixed.append(shape.intersection(local))
obstacles=unary_union(fixed)
compiledpath=ROOT/'Game/data/generated/structural_meshes.json'
compiled=json.loads(compiledpath.read_text())
floor=unary_union([Polygon(t)for q in compiled['regions'] if q['deck']=='D05' for t in q['triangles']])
for rows in [clinical['floor_proposal']['polygons'],header['floor_proposal']['polygons'],next(q for q in riser['floor_proposals'] if q['deck']=='D05')['missing_floor_polygons']]:
    floor=floor.union(unary_union([Polygon(q['boundary'],q.get('holes',[])) for q in rows]))
poses=[(-21,-286,0),(-21,-291,0),(-33,-293,90),(-45,-293,90),(-55,-293,90),(-57,-293,0),(-21,-295,0),(-23,-297,45),(-33,-297,90),(-54.6,-297,90),(-57,-297,90),(-61,-297,0)]
checks=[]
for x,z,degrees in poses:
    angle=math.radians(degrees)
    moved=affinity.translate(affinity.rotate(body,-degrees,origin=(0,0)),x,z)
    driver=Point(x+1.29*math.sin(angle),z+1.29*math.cos(angle)).buffer(.28)
    proxy=moved.union(driver)
    collision=proxy.intersection(obstacles).area;unsupported=proxy.difference(floor).area
    checks.append({'cart_position_xz':[x,z],'yaw_degrees':degrees,'body_contact_driver_collision_m2':collision,'outside_existing_or_proposed_source_floor_m2':unsupported,'proxy_gap_to_fixed_surfaces_m':proxy.distance(obstacles),'pass':collision<1e-8 and unsupported<1e-8})
passed=all(q['pass'] for q in checks)
report={'status':'PASS' if passed else 'FAIL','bounded_local_cart_proxies':checks,'retained_native_cart_export_sha256':cartdep['sha256'],'retained_native_cart_bounds_receipt_sha256':sha(nativepath),'retained_cart_contacts_sha256':sha(contactpath),'local_fixed_source_footprints':len(fixed),'held_four_crossing_gates_included':False,'cab_or_threshold_boarding_tested':False,'existing_cart_or_stock_identities_modified':False,'scope':'Twelve declared stationary conservative native-body AABB, retained contact and radius 0.28 driver proxy poses. Includes exact held two-cell successor and explicit floor proposals. No continuous movement, driven cart, gates, lift boarding, species or sterile-flow acceptance.'}
(HERE/'qa/PORT2_LOCAL_CART_PROXY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'poses':len(checks),'minimum_source_proxy_gap_m':min(q['proxy_gap_to_fixed_surfaces_m'] for q in checks),'failed':[q for q in checks if not q['pass']]}))
assert passed
