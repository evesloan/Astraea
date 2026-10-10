from pathlib import Path
import json,copy,hashlib,math
from shapely.geometry import box,shape,mapping
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';assert not W.exists();W.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();ns={'R':R,'W':W};exec(s[:s.index('from shapely import affinity')].replace('R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent',''),ns);parts=ns['parts'];cube=ns['cube'];prism=ns['prism'];segment=ns['segment']
old=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'));first=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/PLAN.json'));fifth=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_fifth_20261010/PLAN.json'));catalogue=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));sources=[next(a for a in catalogue['assets'] if a['catalogue_id']==i)for i in ['AST-FUR-001','AST-FUR-002','AST-FUR-003','AST-STF-007']]
floor=box(-85,-364,-63.1,-356.2);assert floor.intersection(shape(old['floor_geometry'])).area<1e-7
all1000=json.load(open(R/'BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json'))['records']
for a in all1000:assert floor.intersection(box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1])).area<1e-7
prism('D04CS_Floor',floor,16.26,16.5);prism('D04CS_Roof',floor,20.46,20.66,role='ivory_enamel',category='roof')
feet=[]
for x in [-83.1,-77.4,-70.5,-63.6]:
 for z in [-363.5,-360.1,-356.7]:
  i=len(feet);feet.append({'at':[x,-3.2,z],'owner':'HUL_KeelPan'})
  cube(f'D04CS_KeelShoe_{i}',[x-.45,-3.2,z-.45],[x+.45,-2.95,z+.45],category='keel_shoe');cube(f'D04CS_Pier_{i}',[x-.25,-2.95,z-.25],[x+.25,15.4,z+.25],category='foundation_pier')
 for j,(a,b)in enumerate([(-363.5,-360.1),(-360.1,-356.7)]):segment(f'D04CS_LowerBrace_{x}_{j}',[x,-2.95,a],[x,15.4,b],.2,.2,category='lower_diagonal_brace')
 cube('D04CS_LongTransfer_'+str(x),[x-.25,15.4,-364],[x+.25,16.26,-356.2],category='transfer_frame')
for j,z in enumerate([-363.5,-360.1,-356.7]):cube(f'D04CS_CrossTransfer_{j}',[-85,15.4,z-.25],[-63.1,16.26,z+.25],category='transfer_frame')
# Entire new band is enclosed; each boundary has mass, datum and roof support.
for side,x in [('West',-85),('East',-63.1)]:cube('D04CS_'+side+'Wall',[x if side=='West'else x-.18,16.5,-364],[x+.18 if side=='West'else x,20.46,-356.2],role='ivory_enamel',category='shell')
cube('D04CS_NorthWall',[-85,16.5,-356.38],[-63.1,20.46,-356.2],role='ivory_enamel',category='shell')
# New south boundary has one exact3.6m receiving opening; old north enclosure remains sealed until its gate.
for j,(a,b)in enumerate([(-85,-73.0)]):cube(f'D04CS_SouthWall_{j}',[a,16.5,-364],[b,20.46,-363.82],role='ivory_enamel',category='shell')
# Existing contained successor head receives this aperture; do not duplicate it.
# Quiet activity room, screened from two distinct service cells. The3.7m gallery remains open and cart-clear.
for j,x in enumerate([-79.8,-74.8,-69.8]):cube(f'D04CS_CellPartition_{j}',[x-.09,16.5,-360.1],[x+.09,20.46,-356.38],role='ivory_enamel',category='privacy_screen')
# Fronts: separate contained3.6m entrances; splayed stub screens prevent direct views into shelf/returns.
for label,a,b,c in [('Quiet',-84.82,-79.89,-82.2),('Clean',-79.71,-74.89,-77.3),('Return',-74.71,-69.89,-72.3)]:
 for j,(l,h)in enumerate([(a,c-1.8),(c+1.8,b)]):
  if h>l:cube('D04CS_'+label+f'Front_{j}',[l,16.5,-360.19],[h,20.46,-360.01],role='warm_walnut'if label=='Quiet'else'ivory_enamel',category='shell')
 cube('D04CS_'+label+'Head',[c-1.8,19.16,-360.19],[c+1.8,20.46,-360.01],role='ivory_enamel',category='shell')
# Quiet room planted lightwell, contained inside programme and opaque outer wall: no borrowed hull/window claim.
cube('D04CS_QuietGardenDado',[-84.82,16.5,-357.48],[-79.89,17.25,-357.3],role='warm_walnut',category='shell');cube('D04CS_QuietGardenGlass',[-84.82,17.25,-357.48],[-79.89,20.1,-357.3],role='hospitality_glass',category='window');cube('D04CS_QuietGardenHead',[-84.82,20.1,-357.48],[-79.89,20.46,-357.3],role='ivory_enamel',category='shell')
for j,x in enumerate([-84,-82.4,-80.8]):
 poly=box(x-.4,-357.14,x+.4,-356.58).buffer(.12,quad_segs=3);prism('D04CS_Planter_'+str(j),poly,16.5,16.95,role='warm_stone',category='planter')
 for k,h in enumerate([.6,1,.75]):prism(f'D04CS_Foliage_{j}_{k}',box(x-.22+k*.13,-357.1,x+.13+k*.13,-356.75).buffer(.1,quad_segs=2),16.95,16.95+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
# Purpose-built clean-linen shelf/closed return bins have meaningful volume; cleaner and molt handling parameters remain undecided.
for j,z in enumerate([-357.7,-358.25]):
 prism('D04CS_CleanLinenShelf_'+str(j),box(-79.3,z-.23,-78.7,z+.23).buffer(.07,quad_segs=2),17.0+j*.35,17.08+j*.35,role='warm_walnut',category='storage')
 for k in range(3):prism(f'D04CS_LinenFold_{j}_{k}',box(-79.24,z-.19+k*.1,-78.76,z-.11+k*.1).buffer(.04,quad_segs=2),17.08+j*.35,17.15+j*.35,role='ivory_enamel',category='storage')
for j,(x,label)in enumerate([(-73.8,'Textiles'),(-70.8,'OrdinaryWaste')]):
 poly=box(x-.37,-357.35,x+.37,-356.6).buffer(.12,quad_segs=3);prism('D04CS_Return'+label,poly,16.5,17.45,role='warm_walnut',category='closed_return_bin');prism('D04CS_Return'+label+'Lid',poly.buffer(.04),17.45,17.53,role='ivory_enamel',category='closed_return_bin')
# Visible bounded lights for every destination; contained fixture geometry only.
lights=[]
for j,(x,z)in enumerate([(-66.1,-361.7),(-72.3,-361.7),(-77.3,-361.7),(-82.2,-361.7),(-82.2,-358.8),(-77.3,-358.4),(-72.3,-358.4)]):
 poly=box(x-.32,z-.32,x+.32,z+.32).buffer(.12,quad_segs=3);prism(f'D04CS_LampHousing_{j}',poly,20.12,20.25,role='champagne_metal',category='light_source');prism(f'D04CS_LampLens_{j}',poly.buffer(-.06),20.08,20.12,role='opal_glow',category='light_source');parts[-1]['runtime_collision']=False;parts[-2]['runtime_collision']=False;lights.append({'name':f'D04CS_Lamp_{j}','at':[x,20.04,z]})
# Roof support posts sit inside boundary/cell volumes; they do not project into the gallery.
for j,x in enumerate([-84.91,-79.8,-74.8,-69.8,-63.19]):
 cube('D04CS_UpperPost_'+str(j),[x-.07,16.5,-356.52],[x+.07,20.46,-356.38],category='upper_pier');cube('D04CS_RoofBeam_'+str(j),[x-.07,20.22,-363.82],[x+.07,20.46,-356.38],category='roof_bearing')
components=[{'catalogue_id':'AST-FUR-002','name':'QuietChairWest','position':[-83.6,16.5,-358.65],'yaw':math.pi/2},{'catalogue_id':'AST-FUR-002','name':'QuietChairEast','position':[-80.9,16.5,-358.65],'yaw':-math.pi/2},{'catalogue_id':'AST-FUR-003','name':'QuietActivityTable','position':[-82.25,16.5,-358.65],'yaw':0},{'catalogue_id':'AST-STF-007','name':'CleanStockCabinet','position':[-77.3,16.5,-356.9],'yaw':math.pi}]
preimages=[copy.deepcopy(q)for q in old['parts']if q['name'].startswith('D04PF_UpperGuard_06')]+[copy.deepcopy(q)for q in first['commons_parts']if q['name']in['D04Commons_SouthDado','D04Commons_SouthGlass','D04Commons_SouthHead']]
successors=[]
for q in preimages:
 lo=[min(v[k]for v in q['verts'])for k in range(3)];hi=[max(v[k]for v in q['verts'])for k in range(3)]
 for j,(a,b)in enumerate([(lo[0],-67.9),(-64.3,hi[0])]):
  if b>a:
   n=len(parts);cube('D04CS_'+q['name']+'_Remaining_'+str(j),[a,lo[1],lo[2]],[b,hi[1],hi[2]],role=q['role'],category='contained_preimage_successor');successors.extend(parts[n:]);del parts[n:]
 # Preserve original above-aperture face only. Existing head entirely starts19.8, so its aperture interval remains.
 if hi[1]>19.16:
  n=len(parts);cube('D04CS_'+q['name']+'_RemainingHead',[-67.9,max(lo[1],19.16),lo[2]],[-64.3,hi[1],hi[2]],role=q['role'],category='contained_preimage_successor');successors.extend(parts[n:]);del parts[n:]
inputs=set(fifth['source_pins']);inputs.update(['Game/assets/models/AST-HUL-001.glb','BlenderCatalogue/assets/lower_hull_body/source/AST-HUL-001.blend','Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','BlenderCatalogue/references/intimate/image(20261002-000722).png','BlenderCatalogue/references/landings/staff_corridor_services.png','BlenderCatalogue/assets/d04_port_forward_homes_fifth_20261010/RUNTIME_PLAN.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_FIFTH.json','Game/scripts/d04_port_forward_homes_fifth.gd','Game/assets/models/D04_PORT_FORWARD_HOMES_FIFTH_RECEIVING_r001.glb','Game/assets/models/D04_PORT_FORWARD_HOMES_FIFTH_GUARDS_r001.glb'])
for q in sources:inputs.update('BlenderCatalogue/'+q[k]for k in ['source','export','manifest'])
P={'schema':'astraea.d04.commons_service.plan.v1','base_commit':'0f19276d3c7845c8583ad4ca1d874bce7a6f4f97','programme_key':'D04_directory_01','floor_geometry':mapping(floor),'new_floor_m2':floor.area,'parts':parts,'components':components,'sources':sources,'lights':lights,'foundation_feet':feet,'preimages':preimages,'successor_parts':successors,'source_pins':{f:sha(R/f)for f in sorted(inputs)},'all_twenty_allocations_unchanged':old['units'],'open_receiving_connection':False,'connection_accepted':False,'public_entry':[-66.1,16.5,-364.08],'gallery_route':[[-66.1,16.5,-361.8],[-72.3,16.5,-361.8],[-77.3,16.5,-361.8],[-82.2,16.5,-361.8]],'clean_stock_cart_station':[-77.3,16.5,-358.7],'soiled_return_cart_station':[-72.3,16.5,-358.7],'quiet_activity_approach':[-82.2,16.5,-359.75],'separate_clean_and_return_enclosures':True,'shared_gallery_clean_soiled_crossing_operation_held':True,'quiet_planted_lightwell_service_access_held':True,'outer_geometry_cantilever_from_pier_center_m':1.9,'limits':['Twenty homes are entry-connected; gameplay/species/operational acceptance remains held','New commons service/activity band only; full28m-deep/34m-wide programme remains unfinished','Separate clean-stock and closed soiled/ordinary-waste return bays; shared gallery crossing, stock/save/refill, laundry and guest/staff autonomous operation remain held','Mantelid quiet activity and Baelin distinct-cleaner accommodation grounded in species overlay; no new biology or cleaner efficacy parameters','Keel contact/transfer continuity are geometric evidence; primary load/cantilever/buckling engineering held','Existing staff stair is walking-only; cart-safe vertical access held','Final ordinary in-game/CRT/hardware acceptance held']}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'parts':len(parts),'preimages':len(preimages),'successors':len(successors),'feet':len(feet),'new_floor_m2':floor.area,'pins':len(inputs)}))
