from pathlib import Path
import json,hashlib,sys,numpy as np
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
u={'__file__':str(W/'survey_d14.py')};exec((W/'survey_d14.py').read_text().replace("print(json.dumps({k:result[k]for k in ['collars','approach_existing_floor_overlap_m2','nearby_floor_owners','local_source_mesh_candidates']},indent=2))",''),u)
id='AST-RES-TIDAL-D14-SERVICE-001'
def unused(v):
 if isinstance(v,dict):
  for x in v.values():unused(x)
 elif isinstance(v,list):
  for x in v:unused(x)
 elif isinstance(v,str):assert v!=id,'Already owned catalogue ID'
unused(json.load(open(R/'BlenderCatalogue/catalogue_manifest.json')))
# Gross footprint includes wall bases. Subtract actual retained floors and proposed retained approach.
footprint=box(-45.84,-498.2,-42.16,-493.5);missing=footprint.difference(u['old'].union(u['request']))
assert missing.geom_type=='Polygon'
floor={'id':'TIDAL_D14_SharedReceivingLink_MissingOnly','floor_y':88.5,'thickness':.24,'material_role':'staff_floor','rings':[list(missing.exterior.coords)[:-1]]+[list(x.coords)[:-1]for x in missing.interiors],'triangles':[list(x.exterior.coords)[:3]for x in shapely.constrained_delaunay_triangles(missing).geoms],'area_m2':missing.area}
parts=[]
def cube(n,b,role='staff_white_paint',cat='d14_shared_receiver'):
 parts.append({'name':n,'aabb':b,'role':role,'category':cat})
# Two side enclosures, roof, and the fitted existing service-door reveal at the street end.
for side,x0,x1 in [('West',-45.84,-45.7),('East',-42.3,-42.16)]:
 cube('D14_LinkSide_'+side,[x0,x1,88.5,91.7,-498.06,-493.6])
 cube('D14_LinkReceivingBeam_'+side,[x0-.03,x1+.03,87.96,88.26,-498.18,-493.35],'staff_zinc','receiving_frame')
 cube('D14_LinkStreetSaddle_'+side,[x0-.07,x1+.07,88.08,88.26,-493.72,-493.35],'staff_zinc','named_existing_street_receiver')
 # Toe plates reach the installed D13 floor north-edge while stems remain outside its closed corridor wall.
 xc=(x0+x1)/2
 cube('D14_LinkFloorToe_'+side,[xc-.17,xc+.17,84,84.12,-498.30,-497.78],'staff_zinc','named_d13_floor_receiver')
 cube('D14_LinkPost_'+side,[xc-.12,xc+.12,84.12,87.96,-498.02,-497.78],'staff_bluegrey_paint','receiving_frame')
 cube('D14_LinkPostCapital_'+side,[xc-.18,xc+.18,87.92,88.08,-498.1,-497.7],'staff_zinc','receiving_frame')
for side,x0,x1 in [('West',-45.84,-45.38),('East',-42.62,-42.16)]:cube('D14_SharedPortalInfill_'+side,[x0,x1,88.5,91.34,-493.78,-493.42])
cube('D14_SharedPortalHeaderPacking',[-45.38,-42.62,91.31,91.34,-493.78,-493.42],'staff_zinc')
cube('D14_SharedPortalHeader',[-45.84,-42.16,91.34,91.7,-493.78,-493.42])
cube('D14_LinkRoof',[-45.84,-42.16,91.7,91.84,-498.2,-493.42],'staff_bluegrey_paint','overhead')
for side,x0,x1 in [('West',-45.84,-45.7),('East',-42.3,-42.16)]:cube('D14_ServiceOpeningReveal_'+side,[x0,x1,88.5,91.4,-498.2,-498.06])
# Future physical closure prevents an unfinished upper approach being mistaken for an active lift.
# No shaft/cabin/stop geometry is supplied by this small module.
old=json.load(open(G/'data/architecture/TIDAL_D13_SERVICE_RECEIVING.json'));d13=unary_union([Polygon(x['rings'][0],x['rings'][1:])for x in old['floor_regions']if abs(x['floor_y']-84)<1e-5]);bearings=[]
for p in parts:
 if p['category']=='named_d13_floor_receiver':
  b=p['aabb'];poly=box(b[0],b[4],b[1],b[5]);area=poly.intersection(d13).area;assert area>.08
  bearings.append({'member':p['name'],'receiver':'TIDAL_D13_ServiceApproach_0','receiver_y':84,'bearing_area_m2':area,'intentional_existing_screen_foot_overlap':'same north-edge wall-base region only; no deletion/cut; post stem has0.04m wall separation'})
 if p['category']=='named_existing_street_receiver':
  b=p['aabb'];poly=box(b[0],b[4],b[1],b[5]);street=u['ownerpoly']['D14_final_south_street/D14_SouthStreetFloor'];area=poly.intersection(street).area;assert area>.06
  bearings.append({'member':p['name'],'receiver':'D14_SouthStreetFloor','receiver_y':88.25999725073576,'member_top_y':88.26,'plane_error_m':.00000274926424,'bearing_area_m2':area})
# Exact named source-only replacements, preserving every other source part and triangle.
patches=[{'source_family':'group3','mesh':'screen_wall_staff_bluegrey_paint_D14_-6_-63','editable_source_part':'TidalStaffWallLow_D14_-6_-63_0','cut':{'min':[-45.84,88.499,-498.3],'max':[-42.16,91.4,-498.0]}},{'source_family':'group3','mesh':'screen_wall_staff_white_paint_D14_-6_-63','editable_source_part':'TidalStaffWallHigh_D14_-6_-63_0','cut':{'min':[-45.84,88.499,-498.3],'max':[-42.16,91.4,-498.0]}},{'source_family':'street','mesh':'D14_SouthStreetEndGuard','cut':{'min':[-45.84,88.499,-493.61],'max':[-42.16,89.601,-493.49]}}]
pins=dict(u['pins'])
for p in [G/'data/architecture/TIDAL_D13_SERVICE_RECEIVING.json',G/'assets/models/AST-RES-TIDAL_D13_service_receiving_r001.glb',G/'scripts/tidal_d13_service_receiving.gd',G/'scripts/service_door.gd',G/'assets/textures/staff_floor.png',R/'DesignArchive/Historical_Design/Editable_Source/assets/technical_reference.png',R/'DesignArchive/Historical_Design/Editable_Source/assets/habitat_reference.png',G/'assets/models/AST-STF-008.glb',R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/AST-STF-G3-003.blend',R/'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-STF-G3-003.glb',R/'BlenderCatalogue/catalogue_manifest.json',G/'docs/master_source/MASTER_CURRENT_APPLICATION.json',G/'docs/master_source/MASTER_FULL_CONTENT_INDEX.json']:
 pins[str(p.relative_to(R))]=sha(p)
plan={'schema':'astraea.tidal.d14_shared_receiver_source.v1','catalogue_id':id,'status':'held_source_proposal_no_runtime_installation','floor_y':88.5,'new_parts':parts,'missing_only_floor':floor,'gross_floor_bounds_xz':list(footprint.bounds),'gross_floor_area_m2':footprint.area,'existing_floor_reused_m2':footprint.intersection(u['old']).area,'uninstalled_retained_approach_reused_m2':footprint.intersection(u['request']).area,'floor_duplicate_area_m2':missing.intersection(u['old'].union(u['request'])).area,'receiving_contacts':bearings,'named_source_replacements':patches,'door_binding':{'source':'AST-STF-008.glb','controller':'service_door.gd','position':[-44,88.5,-493.6],'yaw':0,'scale':[1,1,1],'future_persistent_id':None,'runtime_identity_assignment':'parent must bind an unused stable identity; no existing stop/save identity changed','fixed_jamb_clear_width_m':2.3,'fully_open_hardware_clear_width_m':2.168,'conservative_open_clear_width_m':2.166,'fixed_header_clear_height_m':2.54,'swing_side':'into proposed receiver link, toward negativeZ'},'flow_use':{'physical_portal_count':1,'clean_purpose_retained':True,'returns_purpose_retained':True,'operating_proposal':'sequential sealed-load use; arrivals/returns are distinguishable service purposes sharing this door','simultaneous_segregated_flow_accepted':False,'hygiene_accepted':False},'abandoned_uninstalled_mouth_proposals':[x for x in u['a']['interfaces']if x['deck']=='D14'],'fixture':{'name':'D14SharedReceiverLight','position':[-44,91.495,-496],'retained_fixture_source':'TidalStaffLightHousing_D14_3 / TidalStaffLightDiffuser_D14_3','range_m':7.5,'energy':.9,'future_light_binding':'existing receiving_source_lights.gd / lighting_budget.gd, once on installation'},'no_runtime_changed':True,'no_upper_shaft_geometry':True,'no_lift_extension':True,'preserved_staff_stops_y':[0,6,12,46.2,52.5],'preserved_d13_shaft_closure':True,'source_pins':pins,'limits':['Held separately authored D14 shared physical portal proposal; original source mouths and guard remain retained','Actual geometry/source contacts are bounded fit evidence, not structural/load capacity certification','Public-end saddle reacts to existing street-floor source whose broader structural acceptance remains open','D13 floor toe receiver/frame reactions require parent installation review; no primary-hull transfer certified','Source-only: no door/controller/light/runtime installation, save/stop identity changes or upper staff-lift activation','Homes382/394 and all other allocations remain intact; no simultaneous segregation, hygiene, cart/species or whole-route acceptance']}
(W/'D14_SHARED_RECEIVER_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'new_parts':len(parts),'missing_floor_m2':missing.area,'floor_reused_m2':plan['existing_floor_reused_m2'],'approach_reused_m2':plan['uninstalled_retained_approach_reused_m2'],'receiving_contacts':bearings},indent=2))
