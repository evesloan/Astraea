"""Reconcile whole-ship layout scope without turning allocations into finished rooms.
Planning reservations never become floor cuts automatically.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def rect(r):return box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])
def build():
 paths=['data/design_contract.json','data/programme_ledger.json','data/reference/directory_allocations.json','data/reference/historical_guest_census.json','data/reference/historical_atlas_allocations.json','data/spatial_layout.json','data/hull_envelope.json','data/reference/D03_crew_envelopes.json']
 contract,ledger,allocation,census,atlas,layout,hull,crew_source=map(read,paths)
 crew=crew_source['records'];assert len(crew)==200
 guests=census['guest_envelopes'];shops=[r for r in atlas if r['kind']=='unlabelled_shop_allocation'];dest=allocation['records'];bykey={r['programme_key']:r for r in ledger['destinations']}
 assert len(dest)==len(bykey)==161 and len(guests)==1000 and len(shops)==100
 hull_plan=Polygon(hull['plan_xz_m'])
 elevations={d['deck_id']:d['floor_elevation_m']for d in contract['deck_datums']}
 floors={d:unary_union([Polygon(r['boundary'])for r in layout['regions']if r['deck']==d])for d in elevations}
 programmes=[]
 for r in dest:
  key=r['programme_key'];d=f"D{r['deck']:02}";p=rect(r);entry=bykey[key]
  programmes.append({'programme_key':key,'name':r['name'],'deck':d,'floor_y':elevations[d],'allocation_x':r['x'],'allocation_z':r['z'],'historical_room_id':entry.get('historical_room_id'),'geometry_owner':entry.get('current_geometry_owner'),'construction_status':entry['current_status'],'allocation_inside_plan_hull':hull_plan.buffer(1e-6).covers(p),'raw_structural_floor_overlap_m2':round(p.intersection(floors[d]).area,3),'allocation_area_m2':round(p.area,3),'overlap_scope':'Floor-plan overlap only; includes reservations/closures and ignores height, voids and route ownership; never finished-area credit','neighbours_above':[q['programme_key']for q in dest if q['deck']==r['deck']+1 and p.intersection(rect(q)).area>1e-6]})
 courts=[]
 for side,x0,x1 in [('port',-100,-63),('starboard',63,100)]:
  for end,z0,z1 in [('forward',-500,-250),('aft',250,500)]:
   p=box(x0,z0,x1,z1).intersection(hull_plan.buffer(-2))
   for protected in layout['voids']:
    if any(f'D{deck:02}'in protected['decks']for deck in range(13,18)):
     p=p.difference(Polygon(protected['boundary']).buffer(3))
   assert p.geom_type=='Polygon' and p.is_valid
   keys=[r['programme_key']for r in dest if 13<=r['deck']<=17 and p.intersection(rect(r)).area>1e-6]
   conflicts=[i for i,g in enumerate(guests)if 13<=g['deck']<=17 and p.intersection(rect(g)).area>1e-6]
   assert not conflicts and len(keys)==5
   candidates=[]
   direction=-1 if side=='port'else 1
   for i,g in enumerate(guests):
    if not 13<=g['deck']<=17:continue
    z=sum(g['z'])/2;edge=g['x'][0]if direction<0 else g['x'][1]
    ray=LineString([(edge+direction*.01,z),(edge+direction*10,z)])
    if not ray.intersects(p):continue
    blocked=any(j!=i and other['deck']==g['deck']and ray.intersection(rect(other)).length>1e-6 for j,other in enumerate(guests))
    if not blocked:candidates.append(i)
   focus_z=-370 if end=='forward' else 370
   focus_x=[-90,-70]if side=='port'else[70,90]
   courts.append({'id':f'{side}_{end}_residential_court','status':'Proposed landscaped house court; no slab cut or final architecture acceptance','x':[round(p.bounds[0],3),round(p.bounds[2],3)],'z':[round(p.bounds[1],3),round(p.bounds[3],3)],'boundary':[[round(x,3),round(z,3)]for x,z in list(p.exterior.coords)[:-1]],'area_m2':round(p.area,3),'floor_y':84,'upper_cover_y':106.5,'affected_programmes':keys,'arrival_focus_x':focus_x,'arrival_focus_z':[focus_z-10,focus_z+10],'arrival_focus_role':'Retain shaped lobbies, lift landings and inhabited terraces within the commons; not an uninterrupted slab opening','purpose':'A five-level landscaped court alongside real residential banks, with distinct local arrivals and private window edges','guest_envelope_conflicts':conflicts,'potential_outward_view_source_indices':candidates,'view_evidence_scope':'Short plan rays from source room outer edges reach the court without crossing another guest allocation. No installed window, finished view or privacy acceptance implied','guest_access_intent':'Use inward paired-bank corridor gaps and common arrivals; do not run a public gallery directly across every bedroom window','required_before_cut':['Resolve shaped gallery floor ownership for all five commons','Connect both guest and concealed service networks','Confirm protected D18 cover and source-derived support','Fit planted court base, offset bridges and preserved arrival islands','Check all local room entries and views; preserve1000units']})
 cores=[]
 obstacles=dest+guests+shops+crew
 for name,z,catchment in [('forward',-432,-432),('fore_midship',-216,-216),('atrium_threshold',-100,-72),('aft_midship',216,216),('aft',432,432)]:
  p=box(-3.3,z-9,3.3,z+15)
  conflicts=[r.get('programme_key',r.get('stable_id'))for r in obstacles if p.intersection(rect(r)).area>1e-6]
  assert not conflicts
  cores.append({'id':name+'_vertical_core','status':'Public lift/stair plan reservation; no shaft cuts or global access acceptance','x':[-3.3,3.3],'z':[z-9,z+15],'center_z':z,'transport_catchment_z':catchment,'apron_connector':{'x':[-7.8,7.8],'z':[-81,-80],'status':'Required authored bridge between lobby end and existing apron'}if name=='atrium_threshold'else None,'bypass_end_extension_m':4,'decks':list(elevations),'floor_y_range':[0,106.5],'programme_guest_shop_conflicts':conflicts,'guest_service_separation':'Public core only. Staff risers are separate to avoid forcing service through the arrivals crosslink','required_bypass_x_ranges':[[-7.8,-3.5],[3.5,7.8]],'lobby_x':[-7.8,7.8],'lobby_z':[z-13,z+19],'guest_lift_gate_local_xz':[-1.8,-6],'stair_reservation_local_x':[-3.1,3.1],'stair_reservation_local_z':[4,14.8],'preserved_crosslink_local_z':[-3,3],'purpose':'Public lift and stair catchment serving all18decks, with actual bypass floors and crosslinks','requirements':['Author both4.3m bypasses and4m end connections','Keep the D01/D02 existing arrivals crosslink open between lift and stair reservations','Fit differing4.5/6/8.5m stair pitches and equivalent lift access','Confirm pit below-0.18m and headroom above109.44m against resolved hull section','At the central threshold the core is shifted forward to avoid the hero atrium; the Townline catchment remains-72m','Test physical doors, cabins and loaded cart transfers before use']})
 staff_cores=[]
 positions={'port':[-490,-283,-90,290,490],'starboard':[-490,-323,-86,323,490]}
 for side,zs in positions.items():
  x=-25 if side=='port' else 25
  floor_x=[-27.4,-18.8]if side=='port'else[18.8,27.4]
  for index,z in enumerate(zs):
   half=5.8 if side=='starboard'and index==2 else 6
   p=box(floor_x[0],z-half,floor_x[1],z+half)
   conflicts=[r.get('programme_key',r.get('stable_id'))for r in obstacles if p.intersection(rect(r)).area>1e-6]
   assert not conflicts and hull_plan.buffer(-2).covers(p)
   staff_cores.append({'id':side+'_service_riser_'+str(index+1),'status':'Separate screened staff-riser/lobby reservation; routes and access logic not constructed','center_xz':[x,z],'lobby_x':floor_x,'lobby_z':[z-half,z+half],'shaft_x':[x-2.2,x+2.2],'shaft_z':[z-2.2,z+2.2],'decks':list(elevations),'allocation_conflicts':conflicts,'purpose':'Keep staff vertical movement on its own side of the ship and link into concealed district service routes','requirements':['Explicit floor-by-floor staff links; no open merging with guest spine','Opaque screened arrivals and service access logic','Maintain source guest, crew and programme allocations','Protect hull section, pit/headroom and all source-derived cabin contacts']})
 # Concrete lower-deck routing intent, outside the public arrivals room and axis.
 staff_arrivals_link={'decks':['D01','D02'],'riser':'port_service_riser_1','route_xz':[[-20,-490],[-20,-500],[-57,-500],[-57,-432],[-54,-432]],'width_m':3.6,'status':'Plan-fit link to the existing west service interface; floor, corners, enclosure and doors still require authoring','source_interface':'Arrivals/fusion service street atX-57, interfaceX-54','public_crossing_required':False}
 # A purpose-led fore aquatic section keeps the sports allocation below intact.
 pool_box=box(-44,-459,-18,-405)
 pool_keys={r['name']:r['programme_key']for r in dest if r['name']in ['The grand aquatic pool','Orchard market','The shared table / 240']}
 assert len(pool_keys)==3
 pool_conflicts=[i for i,g in enumerate(guests)if g['deck']in [8,9] and pool_box.intersection(rect(g)).area>1e-6]
 assert not pool_conflicts
 aquatic_reservation={'id':'fore_grand_pool_market_section','status':'Proposed coordinated volume; basin, ramps and market gallery not constructed','x':[-44,-18],'z':[-459,-405],'affected_programmes':pool_keys,'lower_arrival_y':44,'proposed_wet_deck_y':46.2,'proposed_basin_bottom_y':44.8,'market_gallery_y':52.5,'protected_dining_floor_y':61,'proposed_pool_water_length_m':50,'proposed_pool_water_width_m':18,'wet_deck_rise_m':2.2,'minimum_1_to_12_ramp_run_m':26.4,'guest_envelope_conflicts':pool_conflicts,'purpose':'A grand pool volume with environmentally separated market overlooks; raised wet deck protects the sports clear volume below instead of dropping a basin into it','requirements':['Fit accessible ramp landings and local lift at44/46.2/52.5','Retain all100 separate shop addresses and fit the large market programme around the opening','Protect D07 sports below and full D10 dining programme above','Resolve water structure, drainage, staff access and wet/dry environmental boundaries','Verify safety edges, pool use and actual species access before acceptance']}
 decks=[]
 for d in elevations:
  n=int(d[1:]);decks.append({'deck':d,'floor_y':elevations[d],'programme_keys':[r['programme_key']for r in programmes if r['deck']==d],'guest_envelope_count':sum(g['deck']==n for g in guests),'retail_envelope_count':sum(g['deck']==n for g in shops),'crew_bank_envelope_count':sum(g['deck']==n for g in crew),'final_layout_accepted':False})
 houses=[]
 for side in ['port','starboard']:
  direction=-1 if side=='port'else 1
  for district in ['forward','central','aft']:
   indices=[i for i,g in enumerate(guests)if g['deck']>=13 and sum(g['x'])*direction>0 and ('forward'if sum(g['z'])/2<-200 else'aft'if sum(g['z'])/2>200 else'central')==district]
   houses.append({'id':side+'_'+district+'_upper_house','guest_envelope_source_indices':indices,'decks':[f'D{n:02}'for n in range(13,18)],'court_reservation':side+'_'+district+'_residential_court'if district!='central'else None,'status':'House membership plan; room shapes, privacy, local routes and luxury replacements still require fitting','identity_scope':'Source-index crosswalk only; no recovered room IDs invented'})
  for district,center in [('forward',-370),('central',0),('aft',370)]:
   indices=[i for i,g in enumerate(guests)if g['deck']==4 and sum(g['x'])*direction>0 and min([-370,0,370],key=lambda z:abs(sum(g['z'])/2-z))==center]
   houses.append({'id':side+'_'+district+'_lower_habitat_house','guest_envelope_source_indices':indices,'decks':['D04'],'status':'Lower habitat-neighbourhood membership; environmental boundaries and species compatibility unresolved','identity_scope':'Habitat profiles are not species and source indices are not recovered room IDs'})
 assert sum(len(h['guest_envelope_source_indices'])for h in houses)==1000
 stacks=[]
 catchments=[('forward',-432),('fore_midship',-216),('central',0),('aft_midship',216),('aft',432)]
 def district_for(r):
  z=sum(r['z'])/2;x=sum(r['x'])/2
  return ('port'if x<0 else'starboard')+'_'+min(catchments,key=lambda c:abs(z-c[1]))[0]
 for side in ['port','starboard']:
  for name,z in catchments:
   key=side+'_'+name
   stacks.append({'id':key,'status':'Geographic coordination group; final shapes and connections unresolved','programme_keys':[r['programme_key']for r in dest if district_for(r)==key],'guest_envelope_source_indices':[i for i,r in enumerate(guests)if district_for(r)==key],'retail_envelope_source_indices':[i for i,r in enumerate(shops)if district_for(r)==key],'crew_envelope_source_indices':[i for i,r in enumerate(crew)if district_for(r)==key],'purpose':'Coordinate vertically adjacent uses as a neighbourhood rather than treating each deck as an isolated flat layer','source_indices_are_persistent_room_ids':False})
 assert sum(len(s['programme_keys'])for s in stacks)==161
 assert sum(len(s['guest_envelope_source_indices'])for s in stacks)==1000
 assert sum(len(s['retail_envelope_source_indices'])for s in stacks)==100
 result={'schema':1,'scope':'Complete programme/accounting crosswalk and initial vertical reservations, not final construction or a substitute room registry','source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in paths},'decks':decks,'programmes':programmes,'neighbourhood_stacks':stacks,'residential_houses':houses,'residential_court_reservations':courts,'longitudinal_vertical_core_reservations':cores,'staff_riser_reservations':staff_cores,'arrivals_service_link_reservation':staff_arrivals_link,'aquatic_section_reservations':[aquatic_reservation],'protected_totals':{'guest_units':1000,'retail_addresses':100,'directory_programmes':161,'crew_people_including_player':400,'historical_crew_bank_envelopes':200,'luxury_replacements_within_guest_units':81},'unresolved_finalization_gates':['Resolved three-dimensional hull and roof clearances','All161 destination shapes, arrivals and service connections','100retail addresses assigned to designed courts/streets','1000unit identity/layout crosswalk including81luxury replacements','Royalty/Supreme multistorey and all-species provision','400crew berths and service support','Guest and service route connectivity including accessible vertical transport','Purpose, floor ownership and protection for every multi-level void','Normal-play route, visibility and performance acceptance'],'crew_assignment_gate':crew_source['bed_assignment_status'],'legacy_implementation_claims_are_current_evidence':False}
 return result
if __name__=='__main__':
 result=build();(ROOT/'data/whole_ship_layout.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'decks':len(result['decks']),'programmes':len(result['programmes']),'guest_units':1000,'shops':100,'proposed_residential_courts':4,'proposed_longitudinal_cores':5,'final_layout_accepted':False}))
