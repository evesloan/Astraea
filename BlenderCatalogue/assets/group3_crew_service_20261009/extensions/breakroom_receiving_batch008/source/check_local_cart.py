"""Ten stationary native cart/contact/driver proxies at the local receiver."""
from pathlib import Path
import hashlib,json,math,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps');sys.path.insert(0,str(Path(__file__).resolve().parent))
from shapely import affinity
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');FIRST=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dep=FIRST/'extensions/depot_receiving_batch005';nativepath=dep/'qa/DEPOT_NATIVE_GEOMETRY.json';native=json.loads(nativepath.read_text());assert native['status']=='PASS';dep_spec=json.loads((dep/'source/DEPOT_RECEIVING.json').read_text());cartdep=next(q for q in dep_spec['reused_asset_dependencies']if q['catalogue_id']=='AST-HSK-005');assert sha(ROOT/cartdep['path'])==cartdep['sha256'];cart=next(q for q in native['actual_native_component_bounds']if q['asset']=='AST-HSK-005');x0,x1,_,_,z0,z1=cart['world_aabb'];cx,_,cz=cart['position'];body=affinity.rotate(affinity.translate(box(x0,z0,x1,z1),-cx,-cz),math.degrees(cart['yaw']),origin=(0,0))
contactpath=ROOT/'Game/data/architecture/cleaning_cart_contacts.json';contacts=json.loads(contactpath.read_text());pieces=[body]
for q in contacts['boxes']:
 x,_,z=q['center'];sx,_,sz=q['size'];pieces.append(box(x-sx/2-.001,z-sz/2-.001,x+sx/2+.001,z+sz/2+.001))
for q in contacts['wheel_contacts']:
 x,_,z=q['center'];pieces.append(Point(x,z).buffer(q['radius']))
body=unary_union(pieces);local=box(45,-425,60,-415);fixed=[]
receivedpath=ROOT/'Game/assets/models/SOL_D03_directory_02_source001.glb';received=GLB(receivedpath);included=[]
for q in received.doc['nodes']:
 if'mesh'not in q:continue
 a,b,lo,hi,c,d=received.bounds(q['name'],(8,12,-466))
 if hi>12.05 and lo<13.9 and box(a,c,b,d).intersects(local):fixed.append(box(a,c,b,d).intersection(local));included.append(q['name'])
collar=json.loads((HERE/'source/BREAKROOM_COLLAR.json').read_text());branch=json.loads((HERE/'source/BREAKROOM_REUSED_BRANCH.json').read_text());patch=json.loads((HERE/'source/CREW_STREET_BREAKROOM_PATCH.json').read_text());street=json.loads((FIRST/'source/CREW_STREETS.json').read_text())
for q in collar['parts']+branch['parts']+patch['parts']+[q for q in street['parts']if q['name']not in [s['name']for s in patch['original_semantic_parts']]]:
 if'aabb'in q:a,b,lo,hi,c,d=q['aabb'];shape=box(a,c,b,d)
 elif'vertices_godot'in q:v=q['vertices_godot'];lo=min(p[1]for p in v);hi=max(p[1]for p in v);shape=box(min(p[0]for p in v),min(p[2]for p in v),max(p[0]for p in v),max(p[2]for p in v))
 else:lo,hi=q['y'];shape=Polygon(q['boundary'],q['holes'])
 if hi>12.05 and lo<13.9 and shape.intersects(local):fixed.append(shape.intersection(local))
obstacles=unary_union(fixed);compiledpath=ROOT/'Game/data/generated/structural_meshes.json';compiled=json.loads(compiledpath.read_text());actual=unary_union([Polygon(t)for q in compiled['regions']if q['deck']=='D03'for t in q['triangles']]);crew=json.loads((FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').read_text());support=json.loads((HERE/'source/BREAKROOM_MISSING_SUPPORT_PROPOSAL.json').read_text());floor=actual.union(unary_union([Polygon(q['boundary'],q['holes'])for q in crew['floor_proposal']['polygons']+support['polygons']]))
poses=[(47.5,-420,-90),(49,-420,-90),(50.7,-420,-90),(52.7,-420,-90),(54.5,-420,-90),(56,-420,-90),(57,-420,-90),(57,-420,0),(57,-422,0),(57,-418,0)];checks=[]
for x,z,degrees in poses:
 angle=math.radians(degrees);moved=affinity.translate(affinity.rotate(body,-degrees,origin=(0,0)),x,z);driver=Point(x+1.29*math.sin(angle),z+1.29*math.cos(angle)).buffer(.28);proxy=moved.union(driver);collision=proxy.intersection(obstacles).area;outside=proxy.difference(floor).area;checks.append({'cart_position_xz':[x,z],'yaw_degrees':degrees,'body_contacts_driver_collision_m2':collision,'outside_actual_or_explicit_proposed_floor_m2':outside,'proxy_gap_to_fixed_surfaces_m':proxy.distance(obstacles),'pass':collision<1e-8 and outside<1e-8})
passed=all(q['pass']for q in checks);report={'status':'PASS'if passed else'FAIL','bounded_cart_body_contact_driver_poses':checks,'source_input_pins':{'retained_cart_export':cartdep['sha256'],'retained_native_cart_bounds_receipt':sha(nativepath),'retained_cart_contacts':sha(contactpath),'actual_compiled_floor':sha(compiledpath),'received_breakroom_native':sha(receivedpath)},'included_original_received_mesh_names':included,'existing_cart_or_room_identities_modified':False,'gate_sweep_species_or_loaded_motion_tested':False,'scope':'Ten stationary conservative native-body AABB, retained contacts and radius0.28 driver proxies. Exact retained breakroom furniture and actual versus explicitly held support included. No continuous cart journey or service acceptance.'};(HERE/'qa/BREAKROOM_LOCAL_CART_PROXY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'poses':len(checks),'minimum_proxy_gap_m':min(q['proxy_gap_to_fixed_surfaces_m']for q in checks),'failed':[q for q in checks if not q['pass']]}));assert passed
