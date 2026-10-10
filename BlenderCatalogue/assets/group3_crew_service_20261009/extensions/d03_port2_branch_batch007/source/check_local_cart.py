"""Eleven declared stationary cart proxies at branch, tee and depot mouth."""
from pathlib import Path
import hashlib,json,math,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely import affinity
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');FIRST=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dep=FIRST/'extensions/depot_receiving_batch005';nativepath=dep/'qa/DEPOT_NATIVE_GEOMETRY.json';native=json.loads(nativepath.read_text());assert native['status']=='PASS'
dep_spec=json.loads((dep/'source/DEPOT_RECEIVING.json').read_text());cartdep=next(q for q in dep_spec['reused_asset_dependencies']if q['catalogue_id']=='AST-HSK-005');assert sha(ROOT/cartdep['path'])==cartdep['sha256']
cart=next(q for q in native['actual_native_component_bounds']if q['asset']=='AST-HSK-005');x0,x1,_,_,z0,z1=cart['world_aabb'];cx,_,cz=cart['position'];body=affinity.rotate(affinity.translate(box(x0,z0,x1,z1),-cx,-cz),math.degrees(cart['yaw']),origin=(0,0))
contactpath=ROOT/'Game/data/architecture/cleaning_cart_contacts.json';contacts=json.loads(contactpath.read_text());pieces=[body]
for q in contacts['boxes']:
    x,_,z=q['center'];sx,_,sz=q['size'];pieces.append(box(x-sx/2-.001,z-sz/2-.001,x+sx/2+.001,z+sz/2+.001))
for q in contacts['wheel_contacts']:
    x,_,z=q['center'];pieces.append(Point(x,z).buffer(q['radius']))
body=unary_union(pieces)
branch=json.loads((HERE/'source/D03_PORT2_BRANCH.json').read_text());patch=json.loads((HERE/'source/D03_SPINE_RECEIVER_PATCH.json').read_text())
oldparts=json.loads((ROOT/patch['predecessor']['geometry_parts_path']).read_text())['boxes'];fixed=[];local=box(-60,-301,-18,-212)
for q in oldparts:
    if q['name']in patch['original_semantic_parts_in_these_batches']:continue
    a,b,lo,hi,c,d=q['world_aabb']
    if hi>12.05 and lo<13.9:
        shape=box(a,c,b,d)
        if shape.intersects(local):fixed.append(shape.intersection(local))
riser=json.loads((FIRST/'extensions/port2_clinical_batch006/source/PORT_SECOND_STAFF_RISER.json').read_text())
for q in branch['parts']+patch['parts']+riser['parts']:
    if 'aabb'in q:a,b,lo,hi,c,d=q['aabb'];shape=box(a,c,b,d)
    else:lo,hi=q['y'];shape=Polygon(q['boundary'],q['holes'])
    if hi>12.05 and lo<13.9 and shape.intersects(local):fixed.append(shape.intersection(local))
# Reused frozen depot furniture is unchanged context at the existing mouth.
# Native component bounds exclude the cart itself; it is a moving proxy here.
for q in native['actual_native_component_bounds']:
    if q['asset']=='AST-HSK-005':continue
    a,b,lo,hi,c,d=q['world_aabb'];fixed.append(box(a,c,b,d))
obstacles=unary_union(fixed)
compiledpath=ROOT/'Game/data/generated/structural_meshes.json';compiled=json.loads(compiledpath.read_text());floor=unary_union([Polygon(t)for q in compiled['regions']if q['deck']=='D03'for t in q['triangles']])
landing=next(q for q in riser['floor_proposals']if q['deck']=='D03')
floor=floor.union(unary_union([Polygon(q['boundary'],q['holes'])for q in branch['floor_proposal']['polygons']+landing['missing_floor_polygons']]))
poses=[(-21,-286,0),(-21,-291,0),(-23,-293,45),(-31,-293,90),(-51,-293,90),(-55.1,-293,90),(-57,-293,90),(-57,-293,0),(-57,-218,0),(-55,-216,-90),(-53.5,-216,-90)]
checks=[]
for x,z,degrees in poses:
    angle=math.radians(degrees);moved=affinity.translate(affinity.rotate(body,-degrees,origin=(0,0)),x,z);driver=Point(x+1.29*math.sin(angle),z+1.29*math.cos(angle)).buffer(.28);proxy=moved.union(driver)
    collision=proxy.intersection(obstacles).area;unsupported=proxy.difference(floor).area
    checks.append({'cart_position_xz':[x,z],'yaw_degrees':degrees,'body_contacts_driver_collision_m2':collision,'outside_actual_or_proposed_support_m2':unsupported,'proxy_gap_to_fixed_surfaces_m':proxy.distance(obstacles),'pass':collision<1e-8 and unsupported<1e-8})
passed=all(q['pass']for q in checks)
report={'status':'PASS'if passed else'FAIL','bounded_cart_body_contact_driver_poses':checks,'source_input_pins':{'retained_cart_export':cartdep['sha256'],'retained_native_bounds_receipt':sha(nativepath),'retained_cart_contacts':sha(contactpath),'actual_compiled_floors':sha(compiledpath)},'frozen_depot_furniture_native_bounds_included':True,'cabinet_sweep_or_open_doors_tested':False,'existing_cart_stop_or_stock_keys_modified':False,'scope':'Eleven stationary native-body AABB, retained solid-contact and radius 0.28 driver proxy poses. Existing spine/depot mouth and held branch/lobby floors included. No driven cart, continuous route, cabinet sweep, species, load or moving-cabin boarding acceptance.'}
(HERE/'qa/D03_BRANCH_LOCAL_CART_PROXY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'poses':len(checks),'minimum_source_proxy_gap_m':min(q['proxy_gap_to_fixed_surfaces_m']for q in checks),'failed':[q for q in checks if not q['pass']]}));assert passed
