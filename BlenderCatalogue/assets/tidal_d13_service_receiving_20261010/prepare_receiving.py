from pathlib import Path
import json,hashlib,sys,numpy as np
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon,box,shape
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
U={'W':W};exec((R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005/glb_source_reader.py').read_text(),U)
a=json.loads((F/'source/TIDAL_STAFF_INTERFACE.json').read_text());d=json.loads((G/'data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json').read_text());assert sha(G/'assets/models'/d['model_file'])==d['source_sha256']
for p,h in a['source_pins'].items():assert sha(R/p)==h,p
# Full manifest exact-ID screen. This derivative is unregistered pending parent review.
id='AST-RES-TIDAL-D13-SERVICE-001';manifest=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
def assert_id(v):
 if isinstance(v,dict):
  for x in v.values():assert_id(x)
 elif isinstance(v,list):
  for x in v:assert_id(x)
 elif isinstance(v,str):assert v!=id,'ID already used'
assert_id(manifest)
parts=[x for x in a['parts'] if 'D13' in x['name'] and x['category'] not in ['upper_shaft','landing_threshold']];assert len(parts)==64
new=[]
def cube(n,b,role='staff_bluegrey_paint',cat='d13_receiver_collar'):
 p={'name':n,'aabb':b,'role':role,'category':cat};new.append(p);return p
cube('D13_UnfinishedShaftPhysicalClosure',[-23.18,-23.02,84,87.34,-492.2,-487.8],cat='unfinished_shaft_closed')
doors=[];cuts=[]
for role,z in [('clean_linen_supply',-493),('sealed_soiled_waste',-487)]:
 # Existing 2.76m overall frame/2.30m clear jamb gap remains unscaled.
 for side,z0,z1 in [('Fore',z-1.8,z-1.38),('Aft',z+1.38,z+1.8)]:cube('D13_'+role+'_Collar'+side,[-63.34,-62.8,84,86.84,z0,z1],'staff_white_paint')
 cube('D13_'+role+'_HeaderPacking',[-63.34,-62.98,86.81,86.84,z-1.38,z+1.38],'staff_zinc')
 cube('D13_'+role+'_HeaderReceiver',[-63.34,-62.8,86.84,87.2,z-1.8,z+1.8],'staff_white_paint')
 doors.append({'name':'D13_CleanSupplyDoor'if role=='clean_linen_supply'else'D13_SealedReturnsDoor','persistent_id':'tidal_d13_clean_supply_door_001'if role=='clean_linen_supply'else'tidal_d13_sealed_returns_door_001','role':role,'position':[-63.16,84,z],'yaw':1.5707963267948966,'scale':[1,1,1],'source_file':'AST-STF-008.glb','gross_group3_mouth_m':3.6,'actual_fixed_jamb_clear_width_m':2.3,'actual_fixed_header_clear_height_m':2.54,'overall_existing_frame_width_m':2.76,'swing_into':'existing principal court, not private verge'})
 cuts.append({'role':role,'min':[-63.12,83.99,z-1.38],'max':[-63.02,85.25,z+1.38]})
compiled=json.loads((G/'data/generated/structural_meshes.json').read_text());received=json.loads((G/'data/generated/received_structural_meshes.json').read_text());old=[];oldowners=[]
for data in [compiled,received]:
 for q in data['regions']:
  if abs(q['floor_y']-84)<1e-5:
   old.extend(Polygon(t)for t in q['triangles']);oldowners.append(q['id'])
old=unary_union(old);housefloors=[];houseowners={};houseall={}
for n,t in U['triangles'](d['model_file']):
 houseall[n]=t
 tops=t[np.all(abs(t[:,:,1]-84)<2e-4,axis=1)]
 if len(tops):
  poly=unary_union([Polygon(tri[:,[0,2]]) for tri in tops if Polygon(tri[:,[0,2]]).area>1e-8]);housefloors.append(poly);houseowners[n]=poly
house=unary_union(housefloors)
p=next(x for x in a['floor_proposals']if x['deck']=='D13');requested=unary_union([Polygon(x['boundary'],x['holes'])for x in p['polygons']]);missing=requested.difference(old.union(house));regions=[]
def region(n,poly,role):
 for i,q in enumerate(shapely.get_parts(poly)):
  if q.geom_type!='Polygon'or q.area<1e-7:continue
  regions.append({'id':n+'_'+str(i),'deck':'D13','floor_y':84,'thickness':.24,'material_role':'staff_floor','source_role':role,'rings':[list(q.exterior.coords)[:-1]]+[list(h.coords)[:-1]for h in q.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(q).geoms],'area_m2':q.area})
region('TIDAL_D13_ServiceApproach',missing,'missing-only approach')
collars=[];current=old.union(house).union(missing)
for role,z in [('clean_linen_supply',-493),('sealed_soiled_waste',-487)]:
 collar=box(-63.34,z-1.8,-62.8,z+1.8);add=collar.difference(current);region('TIDAL_D13_'+role+'_MissingThreshold',add,'missing-only threshold collar');collars.append({'role':role,'gross_bounds_xz':list(collar.bounds),'gross_area_m2':collar.area,'existing_imported_court_area_m2':collar.intersection(house).area,'already_proposed_approach_area_m2':collar.intersection(missing).area,'new_missing_only_area_m2':add.area});current=current.union(add)
private=shape(next(x for x in d['floor_regions']if x['name']=='TG_PrivateWindowVerge')['geometry']);newfloor=unary_union([Polygon(q['rings'][0],q['rings'][1:])for q in regions]);assert newfloor.intersection(old.union(house)).area<1e-7;assert newfloor.intersection(private).area<1e-7
# No doorway modifies a batch already changed by earlier specialty frontage installs.
for j in(G/'data/architecture').glob('TIDAL_*.json'):
 q=json.loads(j.read_text());assert not set(x['batch']for x in q.get('frontage',{}).get('changed_batches',[])).intersection(['TG_Batch_144','TG_Batch_145'])
pins={}
for f in [F/'source/TIDAL_STAFF_INTERFACE.json',F/'source/AST-STF-G3-003.blend',F/'exports/AST-STF-G3-003.glb',G/'assets/models'/d['model_file'],G/'assets/models/AST-STF-008.glb',G/'assets/models/AST-STF-009_pool_market_home_equipment.glb',G/'scripts/service_door.gd',G/'scripts/lower_staff_network.gd',G/'scripts/tidal_lift_candidate.gd',G/'scripts/tidal_garden_receiving.gd',G/'scripts/tidal_garden_adoption.gd',G/'scripts/static_contact_cache.gd',G/'scripts/structural_floor_builder.gd',G/'scripts/receiving_source_lights.gd',G/'data/generated/structural_meshes.json',G/'data/generated/received_structural_meshes.json',G/'data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json',G/'data/architecture/received_sections.json',G/'data/architecture/received_section_floors.json',R/'BlenderCatalogue/catalogue_manifest.json',R/'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',R/'Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json']:
 pins[str(f.relative_to(R))]=sha(f)
# All current Tidal allocations/receiving inputs bound without copying their large assets.
for f in(G/'data/architecture').glob('TIDAL_*.json'):pins[str(f.relative_to(R))]=sha(f)
plan={'schema':'astraea.tidal.d13_service_receiving.v1','catalogue_id':id,'source_floor_y':84,'retained_source_parts':parts,'additive_parts':new,'fixtures':[x for x in a['fixtures']if 'D13' in x['name']],'doors':doors,'guard_cut_boxes':cuts,'named_guard_replacement_map':{'TG_Batch_144':'TG_Batch_144','TG_Batch_145':'TG_Batch_145'},'floor_regions':regions,'floor_reconciliation':{'compiled_and_received_floor_owners_checked':oldowners,'actual_imported_house_floor_meshes_checked':list(houseowners),'proposed_approach_area_m2':requested.area,'approach_existing_floor_overlap_m2':requested.intersection(old.union(house)).area,'missing_only_approach_area_m2':missing.area,'collars':collars,'total_new_floor_area_m2':newfloor.area,'existing_floor_duplicate_area_m2':newfloor.intersection(old.union(house)).area,'private_verge_overlap_m2':newfloor.intersection(private).area,'private_verge_first_z':-482.2,'service_route_end_z':-483.86},'source_pins':pins,'preserved_staff_lift_stops_y':[0,6,12,46.2,52.5],'preserved_staff_shaft_cap_y':[55.6,55.74],'no_staff_lift_extension':True,'upper_d14_d17_held':True,'no_new_guest_units':True,'unfinished':['Continuous upper staff lift and D14-D17 joins remain held','Whole-species/loaded-cart/full traversal and final Godot/CRT art','Local stock, returns cupboards and cart parking; no stock/inventory operation added','Primary-hull load transfer and structural capacity remain uncertified']}
(W/'D13_RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'retained_parts':len(parts),'new_parts':len(new),'fixtures':len(plan['fixtures']),'floor_reconciliation':plan['floor_reconciliation']}))
