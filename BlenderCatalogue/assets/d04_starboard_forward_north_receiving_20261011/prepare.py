from pathlib import Path
import ast,json,hashlib,math
from shapely.geometry import box,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
source=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text();tree=ast.parse(source)
for n in tree.body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism','segment']:exec(compile(ast.get_source_segment(source,n),'<vetted local receiving geometry helper>','exec'))
C='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';allunits=json.load(open(R/C))['records'];units=[u for u in allunits if u['house']=='starboard_forward_lower_habitat_house'];assert len(units)==20 and sum(u['proposed_rest_place_count']for u in units)==25
selected=[u for u in units if min(u['allocation_z'])>-335];assert len(selected)==10
street=box(41.95,-334,46.05,-286.6);arrival=box(4,-290.8,41.95,-286.6);service=box(46.05,-294.6,59,-286.6);floor=unary_union([street,arrival,service]);assert floor.is_valid
for u in allunits:
 if u['deck']=='D04':assert floor.intersection(box(*[u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1]])).area<1e-8,u['source_envelope_index']
prism('D04SF_NorthReceivingFloor',floor,16.26,16.5);prism('D04SF_NorthReceivingRoof',floor,20.48,20.70,role='ivory_enamel',category='roof')
feet=json.load(open(W/'SUPPORT_PREFLIGHT.json'))['results'];assert all(f['original_keel_bearing']and not f['new_column_volume_blockers']for f in feet)
for i,f in enumerate(feet):
 x,y,z=f['foot'];cube(f'D04SF_KeelBearingShoe_{i:02d}',[x-.2,y,z-.2],[x+.2,y+.12,z+.2]);cube(f'D04SF_KeelBearingPier_{i:02d}',[x-.12,y+.08,z-.12],[x+.12,16.3,z+.12])
# True continuous geometric load path: keel shoes -> posts -> transfer/longitudinal beams -> slab. Engineering remains held.
for z in [-333.7,-324.3,-316.9,-309.5,-302.1,-294.6]:cube('D04SF_StreetTransfer_'+str(z),[26.38,15.98,z-.14],[61.52,16.3,z+.14])
for x in [42.2,45.8]:cube('D04SF_StreetLong_'+str(x),[x-.14,15.98,-334],[x+.14,16.3,-286.6])
for z in [-290.65,-286.75]:cube('D04SF_ArrivalLong_'+str(z),[4,15.98,z-.14],[44,16.3,z+.14])
for x in [8.5,20,32,43.7]:cube('D04SF_ArrivalCross_'+str(x),[x-.14,15.98,-290.8],[x+.14,16.3,-286.6])
for z in [-294.4,-286.8]:cube('D04SF_ServiceTransfer_'+str(z),[41.95,15.98,z-.14],[59,16.3,z+.14])
for x in [47.3,58.6]:cube('D04SF_ServiceLong_'+str(x),[x-.14,15.98,-294.6],[x+.14,16.3,-286.6])
# Street edge bays are separately named preimages for future room thresholds; all remain physically guarded while rooms are unbuilt.
guards=[]
def guard(name,a,b):
 if a[0]==b[0]:lo=[a[0]-.04,16.62,min(a[1],b[1])];hi=[a[0]+.04,17.62,max(a[1],b[1])]
 else:lo=[min(a[0],b[0]),16.62,a[1]-.04];hi=[max(a[0],b[0]),17.62,a[1]+.04]
 cube(name,lo,hi,role='hospitality_glass',category='guard');cube(name+'_Base',[lo[0],16.5,lo[2]],[hi[0],16.64,hi[2]],category='guard');cube(name+'_Cap',[lo[0],17.6,lo[2]],[hi[0],17.68,hi[2]],category='guard');guards.append(name)
for i,(a,b)in enumerate(zip(floor.exterior.coords,list(floor.exterior.coords)[1:])):
 if abs(a[0]-4)<1e-6 and abs(b[0]-4)<1e-6:continue
 # Service cell enclosure replaces these outer guards.
 if min(a[0],b[0])>=46.05-1e-6 and (abs(a[1]+294.6)<1e-6 or abs(a[1]+286.6)<1e-6 or abs(a[0]-59)<1e-6):continue
 guard(f'D04SF_OuterGuard_{i:02d}',a,b)
# Two local receiving cells: physically distinct destinations, sharing the arrival gallery. No full segregation claim.
cube('D04SF_ServiceSouthWall',[46.05,16.5,-294.6],[59,20.48,-294.42],role='ivory_enamel',category='wall');cube('D04SF_ServiceNorthWall',[46.05,16.5,-286.78],[59,20.48,-286.6],role='ivory_enamel',category='wall');cube('D04SF_ServiceEastWall',[58.82,16.5,-294.6],[59,20.48,-286.6],role='ivory_enamel',category='wall')
# Partition leaves a real1.8m enclosed closed-used doorway; clean room has its own1.8m gallery doorway.
for name,x,z0,z1 in [('CleanWest',46.05,-294.6,-292.5),('CleanWestNorth',46.05,-290.7,-286.6),('UsedPartitionSouth',52.45,-294.6,-292.5),('UsedPartitionNorth',52.45,-290.7,-286.6)]:cube('D04SF_'+name,[x,16.5,z0],[x+.18,20.48,z1],role='ivory_enamel',category='wall')
for label,x in [('Clean',46.05),('ClosedUsed',52.45)]:
 cube('D04SF_'+label+'_PortalHead',[x,19.15,-292.5],[x+.18,20.48,-290.7],role='ivory_enamel',category='wall')
 # Layered reveal/posts keep the portal legible rather than flat colored frames.
 for z in [-292.56,-290.64]:cube('D04SF_'+label+'_Reveal_'+str(z),[x-.08,16.5,z-.065],[x+.26,19.25,z+.065],category='portal')
 cube('D04SF_'+label+'_RevealHead',[x-.08,19.15,-292.63],[x+.26,19.30,-290.57],category='portal')
# Closed-used receives from a separate north gallery stub rather than through clean stock.
# Replace partition opening with a solid division, and put its1.8m threshold in its own north boundary.
parts=[p for p in parts if not p['name'].startswith(('D04SF_UsedPartition','D04SF_ClosedUsed'))]
cube('D04SF_ServicePartition',[52.45,16.5,-294.6],[52.63,20.48,-287.9],role='ivory_enamel',category='wall')
# North approach stub runs behind both cells in the existing service floor, connecting both cells directly to shared gallery.
parts=[p for p in parts if p['name']not in ['D04SF_CleanWestNorth']]
cube('D04SF_CleanWestNorth',[46.05,16.5,-290.7],[46.23,20.48,-288.1],role='ivory_enamel',category='wall')
for label,x0,x1 in [('Clean',46.23,52.45),('ClosedUsed',52.63,58.82)]:
 # North cell wall has its own contained service threshold at the east side.
 door_x=(x0+x1)/2
 for side,lo,hi in [('L',x0,door_x-.9),('R',door_x+.9,x1)]:cube('D04SF_'+label+'_CellNorth_'+side,[lo,16.5,-288.08],[hi,20.48,-287.9],role='ivory_enamel',category='wall')
 cube('D04SF_'+label+'_CellNorthHead',[door_x-.9,19.15,-288.08],[door_x+.9,20.48,-287.9],role='ivory_enamel',category='wall')
 # Static assembly leaves real supported apertures; existing door controllers can be connected in a later permissions phase.
lights=[]
for i,(x,z)in enumerate([(10,-288.7),(22,-288.7),(34,-288.7),(44,-328),(44,-316),(44,-304),(44,-289),(49.2,-291.6),(55.7,-291.6)]):
 cube(f'D04SF_LampHousing_{i}',[x-.32,20.18,z-.26],[x+.32,20.48,z+.26],category='fitting');cube(f'D04SF_LampLens_{i}',[x-.27,20.15,z-.21],[x+.27,20.18,z+.21],role='opal_glow',category='fitting');lights.append({'name':f'D04SF_LampLens_{i}','position':[x,20.12,z]})
for x in [42.10,45.90]:
 for z in [-333.7,-324.3,-316.9,-309.5,-302.1,-294.6]:cube('D04SF_RoofPost_'+str(x)+'_'+str(z),[x-.08,16.3,z-.1],[x+.08,20.50,z+.1]);cube('D04SF_RoofPostPlinth_'+str(x)+'_'+str(z),[x-.11,16.5,z-.13],[x+.11,16.69,z+.13])
# Arrival landmark: deep directory plinth and shaped canopy within owned receiving floor.
cube('D04SF_DirectoryPlinth',[39.7,16.5,-290.25],[41.45,16.72,-289.85],role='warm_walnut',category='fitting');cube('D04SF_DirectoryFrame',[39.72,16.70,-290.23],[41.43,18.80,-289.99],category='fitting');cube('D04SF_DirectoryFace',[39.84,16.82,-289.99],[41.31,18.67,-289.96],role='ivory_enamel',category='fitting')
# Native closed return vessels, supported in the receiving cell; no laundry machinery or task state invented.
for i,x in enumerate([54.2,57.2]):
 cube('D04SF_ClosedReturnFoot_'+str(i),[x-.43,16.5,-293.55],[x+.43,16.62,-292.65],category='fitting');cube('D04SF_ClosedReturnShell_'+str(i),[x-.40,16.62,-293.52],[x+.40,17.43,-292.68],role='ivory_enamel',category='closed_return');cube('D04SF_ClosedReturnLid_'+str(i),[x-.42,17.43,-293.54],[x+.42,17.52,-292.66],role='warm_walnut',category='closed_return')
manifest=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));cab=next(a for a in manifest['assets']if a['catalogue_id']=='AST-STF-007');assert cab['family']=='staff_work_cabinet';bindings=[{'catalogue_id':'AST-STF-007','name':'NorthCleanStockCabinet','position':[49.2,16.5,-293.95],'yaw':0}]
pins=json.load(open(R/'BlenderCatalogue/assets/d04_commons_transport_20261011/PLAN.json'))['source_pins'];paths=list(pins)+[C,'Game/data/whole_ship_layout.json','Game/data/reference/directory_allocations.json','Game/data/programme_ledger.json','Game/data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json','Game/scripts/structural_floor_builder.gd','Game/scripts/lower_hull_body.gd','BlenderCatalogue/'+cab['source'],'BlenderCatalogue/'+cab['export'],'BlenderCatalogue/references/landings/staff_corridor_services.png','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg'];paths=sorted(set(p for p in paths if (R/p).exists()));pins={p:sha(R/p)for p in paths}
P={'schema':'astraea.d04.starboard_forward.north_receiving.v1','status':'UNFINISHED_NATIVE_FRAME','base_commit':'4e26a6b0b3724c26c2936f045cad458e248be740','house_id':'starboard_forward_lower_habitat_house','commons_programme_key':'D04_directory_02','all20_units':units,'north10_units':selected,'preserved_units':20,'preserved_proposed_rests':25,'rooms_built':0,'new_units':0,'new_rest_places':0,'floor_y':16.5,'new_floor_m2':floor.area,'floor_geometry':mapping(floor),'parts':parts,'guards':guards,'foundation_feet':[f['foot']for f in feet],'foundation_owner':'LowerHullBody_WIP/HUL_KeelPan','foundation_y':-3.2,'source_pins':pins,'sources':[cab],'rigid_bindings':bindings,'lights':lights,'floor_compartments':{'street':mapping(street),'public_arrival':mapping(arrival),'local_receiving_service':mapping(service)},'reference_images_inspected':['BlenderCatalogue/references/landings/staff_corridor_services.png','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg'],'retained_forward_staff_D04_D07_blank':True,'new_lift_or_controller':False,'shared_public_service_approach':True,'dedicated_clean_used_segregation_accepted':False,'cart_vertical_accepted':False,'primary_load_accepted':False,'provider_save_biology_final_accepted':False,'active':False,'limits':['Northern receiving/package only: ten northern room thresholds guarded; all20room interiors/private courts/full commons/southern street remain unbuilt','Existing fore-midship public core/spine interface; no new vertical system or forward staff stop','Separate local clean-stock/closed-return cells with shared approach; full dedicated back-of-house route unresolved','Native shoes/posts/transfers/slab/roof are geometric continuity, not sized engineering','Source cabinet and closed vessels are physical fixtures only; stock/laundry/task/consumption/save/occupancy not accepted','No whole-house/neighborhood/all-eight-group or final normal-game/CRT/hardware acceptance']}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'parts':len(parts),'floor_m2':floor.area,'foundation_feet':len(feet),'preserved_units':20,'preserved_rests':25,'northern_thresholds':10,'source_pins':len(pins)}))
