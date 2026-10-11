from pathlib import Path
import json,math,hashlib,copy
from shapely.geometry import box,shape,mapping
from shapely.ops import unary_union
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_commons_social_dayroom_20261011';W.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();ns={'R':R,'W':W};exec(s[:s.index('from shapely import affinity')].replace('R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent',''),ns);parts=ns['parts'];cube=ns['cube'];prism=ns['prism'];segment=ns['segment']
cs=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json'));first=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_HOMES_FIRST.json'));old=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_RECEIVING.json'));cat=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));sources=[next(a for a in cat['assets']if a['catalogue_id']==i)for i in ['AST-FUR-001','AST-FUR-002']]
floor=box(-84.8,-375.9,-73,-364);existing=[shape(old['floor_geometry']),shape(cs['floor_geometry']),box(-73,-375.9,-70,-364.1)];assert all(floor.intersection(p).area<1e-7 for p in existing)
units=json.load(open(R/'BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json'))['records']
assert all(floor.intersection(box(*[a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1]])).area<1e-7 for a in units)
prism('D04SD_Floor',floor,16.26,16.5);prism('D04SD_Roof',floor,20.46,20.66,role='ivory_enamel',category='roof')
cube('D04SD_WestWall',[-84.8,16.5,-375.9],[-84.62,20.46,-364],role='ivory_enamel',category='shell');cube('D04SD_SouthWall',[-84.62,16.5,-375.9],[-73,20.46,-375.72],role='ivory_enamel',category='shell')
# Close the two0.1m end gaps alongside retained garden: reuse its privacy/glass wall unchanged.
cube('D04SD_EastNorthJoint',[-73,16.5,-364.1],[-72.82,20.46,-364],role='ivory_enamel',category='shell')
pre=copy.deepcopy(next(p for p in cs['parts']if p['name']=='D04CS_SouthWall_0'));successors=[]
for j,(lo,hi)in enumerate([([-85,16.5,-364],[-80.3,20.46,-363.82]),([-76.7,16.5,-364],[-73,20.46,-363.82]),([-80.3,19.2,-364],[-76.7,20.46,-363.82])]):
 n=len(parts);cube('D04SD_GallerySuccessor_'+str(j),lo,hi,role=pre['role'],category='contained_preimage_successor');successors.extend(parts[n:]);del parts[n:]
# Rounded social table; original six rigid chairs, no new rest places.
prism('D04SD_GroupTableTop',box(-81.95,-371.7,-78.65,-370.6).buffer(.15,quad_segs=6),17.22,17.3,role='warm_walnut',category='furniture')
for j,x in enumerate([-81.15,-79.45]):prism('D04SD_GroupTableBase_'+str(j),box(x-.35,-371.4,x+.35,-370.9).buffer(.1,quad_segs=3),16.5,16.56,category='furniture');cube('D04SD_GroupTableStem_'+str(j),[x-.08,16.56,-371.23],[x+.08,17.22,-371.07],category='furniture')
components=[]
for j,x in enumerate([-81.4,-80.3,-79.2]):
 for side,z,yaw in [('South',-372.4,0),('North',-369.9,math.pi)]:components.append({'catalogue_id':'AST-FUR-002','name':side+'Chair'+str(j),'position':[x,16.5,z],'yaw':yaw})
for j,z in enumerate([-373.6,-368.1]):components.append({'catalogue_id':'AST-FUR-001','name':'GardenEdgeBench'+str(j),'position':[-74.15,16.5,z],'yaw':math.pi/2})
feet=[]
for x in [-82.45,-77.4,-73.6]:
 for z in [-375.4,-369.95,-364.5]:
  j=len(feet);feet.append({'at':[x,-3.2,z],'owner':'HUL_KeelPan'});cube('D04SD_KeelShoe_'+str(j),[x-.45,-3.2,z-.45],[x+.45,-2.95,z+.45],category='keel_shoe');cube('D04SD_FoundationPier_'+str(j),[x-.25,-2.95,z-.25],[x+.25,15.4,z+.25],category='foundation_pier')
 for j,(a,b)in enumerate([(-375.4,-369.95),(-369.95,-364.5)]):segment('D04SD_Diagonal_'+str(x)+'_'+str(j),[x,-2.95,a],[x,15.4,b],.2,.2)
 cube('D04SD_LongTransfer_'+str(x),[x-.25,15.4,-375.9],[x+.25,16.26,-364],category='transfer_frame')
for j,z in enumerate([-375.4,-369.95,-364.5]):cube('D04SD_CrossTransfer_'+str(j),[-84.8,15.4,z-.25],[-73,16.26,z+.25],category='transfer_frame')
for j,x in enumerate([-84.7,-73.15]):
 for k,z in enumerate([-375.8,-364.15]):cube('D04SD_RoofPost_'+str(j)+'_'+str(k),[x-.05,16.5,z-.05],[x+.05,20.46,z+.05],category='roof_bearing')
 cube('D04SD_RoofBeam_'+str(j),[x-.05,20.22,-375.9],[x+.05,20.46,-364],category='roof_bearing')
lights=[]
for j,(x,z)in enumerate([(-78.5,-365.5),(-80.3,-371.15),(-74.6,-370.5)]):
 poly=box(x-.4,z-.25,x+.4,z+.25).buffer(.1,quad_segs=4);prism('D04SD_LampHousing_'+str(j),poly,20.12,20.25,category='light_source');prism('D04SD_LampLens_'+str(j),poly.buffer(-.05),20.08,20.12,role='opal_glow',category='light_source');parts[-1]['runtime_collision']=False;parts[-2]['runtime_collision']=False;lights.append({'name':'D04SD_Light_'+str(j),'at':[x,20.04,z]})
inputs=set(cs['source_pins']);inputs.update(['Game/data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json','Game/scripts/d04_port_forward_commons_service.gd','Game/data/architecture/D04_PORT_FORWARD_HORTICULTURAL_SERVICE.json','Game/scripts/d04_port_forward_horticultural_service.gd','Game/scripts/ship.gd','Game/data/programme_ledger.json','BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/immutable_revision.py','Game/data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json'])
for a in sources:inputs.update('BlenderCatalogue/'+a[k]for k in ['source','export','manifest'])
for f in cs['model_pins']:inputs.add('Game/assets/models/'+f)
reserve=box(-97,-384,-63,-356);cover=unary_union(existing).intersection(reserve);after=unary_union(existing+[floor]).intersection(reserve)
P={'schema':'astraea.d04.social_dayroom.v1','base_commit':'d915e3d7419c05dbc77366f19d962686616ee4fd','programme_key':'D04_directory_01','parts':parts,'components':components,'sources':sources,'lights':lights,'foundation_feet':feet,'floor_geometry':mapping(floor),'new_floor_m2':floor.area,'source_pins':{f:sha(R/f)for f in sorted(inputs)},'preimages':[pre],'successor_parts':successors,'preimage_sha256':hashlib.sha256(json.dumps(pre,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'open_gallery_connection':False,'units':old['units'],'new_units':0,'new_rest_places':0,'route':[[-78.5,16.5,-361.8],[-78.5,16.5,-366.5],[-76.1,16.5,-366.5],[-76.1,16.5,-374.1]],'floor_accounting':{'reservation_m2':952,'previous_floor_union_m2':cover.area,'after_floor_union_m2':after.area,'unallocated_reservation_m2':952-after.area,'no_duplicate_floor':True,'preserved_staff_stair_void_m2':reserve.intersection(box(-64.8,-381.3,-58.8,-370.8)).area,'remainder_is_not_a_solid_floor_requirement':True},'limits':['Garden privacy screen retained1.95m high: upper glazing standing view only; no seated garden-view acceptance','Furnished shared social room, no new activities/species/occupancy/save functionality','Geometric keel contact only, primary structural engineering held','Dedicated clean/used services, cart turns/docking/loaded vertical, full952reservation reconciliation pending','Native staff reach candidate remains inactive','Final normal-game/CRT/hardware held'],'integration_exceptions':['Game/scripts/ship.gd','Game/data/programme_ledger.json']}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'parts':len(parts),'pins':len(inputs),'floor':P['floor_accounting']}))
