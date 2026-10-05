"""Reconcile whole-ship layout scope without turning allocations into finished rooms.
Planning reservations never become floor cuts automatically.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def rect(r):return box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])
def build():
 paths=['data/design_contract.json','data/programme_ledger.json','data/reference/directory_allocations.json','data/reference/historical_guest_census.json','data/reference/historical_atlas_allocations.json','data/spatial_layout.json','data/hull_envelope.json']
 contract,ledger,allocation,census,atlas,layout,hull=map(read,paths)
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
 for side,x0,x1 in [('port',-90,-70),('starboard',70,90)]:
  for end,z0,z1 in [('forward',-380,-360),('aft',360,380)]:
   p=box(x0,z0,x1,z1);keys=[r['programme_key']for r in dest if 13<=r['deck']<=17 and p.intersection(rect(r)).area>1e-6]
   conflicts=[i for i,g in enumerate(guests)if 13<=g['deck']<=17 and p.intersection(rect(g)).area>1e-6]
   assert not conflicts and len(keys)==5
   courts.append({'id':f'{side}_{end}_residential_court','status':'Proposed vertical reservation; no slab cut or final architecture acceptance','x':[x0,x1],'z':[z0,z1],'floor_y':84,'upper_cover_y':106.5,'affected_programmes':keys,'purpose':'A five-level local residential court with arrival, terraces, resting edges, stairs and equivalent lift access; room views and house circulation must be composed around it','guest_envelope_conflicts':conflicts,'required_before_cut':['Resolve shaped gallery floor ownership for all five commons','Connect both guest and concealed service networks','Confirm protected D18 cover and source-derived support','Check all local room entries and views; preserve 1000 units']})
 cores=[]
 for name,z in [('forward',-432),('fore_midship',-216),('atrium_threshold',-72),('aft_midship',216),('aft',432)]:
  half=6 if z==-72 else 9
  p=box(-3,z-half,3,z+half)
  conflicts=[r.get('programme_key',r.get('stable_id'))for r in dest+guests+shops if p.intersection(rect(r)).area>1e-6]
  assert not conflicts
  cores.append({'id':name+'_vertical_core','status':'Plan-fit reservation only; existing spine requires authored bypasses before any shaft cut','x':[-3,3],'z':[z-half,z+half],'bypass_end_extension_m':2 if z==-72 else 3,'decks':list(elevations),'floor_y_range':[0,106.5],'programme_guest_shop_conflicts':conflicts,'guest_service_separation':'Separate screened landings and independently assigned cars; detailed layout pending','required_bypass_x_ranges':[[-7.8,-3.8],[3.8,7.8]],'purpose':'Longitudinal catchment access to all18decks without routing every journey through the central atrium','requirements':['Resolve landings and staff crosslinks on every deck','Keep public walking continuous around core','Tie into planned Townline catchments, without claiming tram implementation','Test physical doors, cabins and loaded cart transfers before use']})
 # A purpose-led fore aquatic section keeps the sports allocation below intact.
 pool_box=box(-44,-459,-18,-405)
 pool_keys={r['name']:r['programme_key']for r in dest if r['name']in ['The grand aquatic pool','Orchard market','The shared table / 240']}
 assert len(pool_keys)==3
 pool_conflicts=[i for i,g in enumerate(guests)if g['deck']in [8,9] and pool_box.intersection(rect(g)).area>1e-6]
 assert not pool_conflicts
 aquatic_reservation={'id':'fore_grand_pool_market_section','status':'Proposed coordinated volume; basin, ramps and market gallery not constructed','x':[-44,-18],'z':[-459,-405],'affected_programmes':pool_keys,'lower_arrival_y':44,'proposed_wet_deck_y':46.2,'proposed_basin_bottom_y':44.8,'market_gallery_y':52.5,'protected_dining_floor_y':61,'proposed_pool_water_length_m':50,'proposed_pool_water_width_m':18,'wet_deck_rise_m':2.2,'minimum_1_to_12_ramp_run_m':26.4,'guest_envelope_conflicts':pool_conflicts,'purpose':'A grand pool volume with environmentally separated market overlooks; raised wet deck protects the sports clear volume below instead of dropping a basin into it','requirements':['Fit accessible ramp landings and local lift at44/46.2/52.5','Retain all100 separate shop addresses and fit the large market programme around the opening','Protect D07 sports below and full D10 dining programme above','Resolve water structure, drainage, staff access and wet/dry environmental boundaries','Verify safety edges, pool use and actual species access before acceptance']}
 decks=[]
 for d in elevations:
  n=int(d[1:]);decks.append({'deck':d,'floor_y':elevations[d],'programme_keys':[r['programme_key']for r in programmes if r['deck']==d],'guest_envelope_count':sum(g['deck']==n for g in guests),'retail_envelope_count':sum(g['deck']==n for g in shops),'final_layout_accepted':False})
 stacks=[]
 catchments=[('forward',-432),('fore_midship',-216),('central',0),('aft_midship',216),('aft',432)]
 def district_for(r):
  z=sum(r['z'])/2;x=sum(r['x'])/2
  return ('port'if x<0 else'starboard')+'_'+min(catchments,key=lambda c:abs(z-c[1]))[0]
 for side in ['port','starboard']:
  for name,z in catchments:
   key=side+'_'+name
   stacks.append({'id':key,'status':'Geographic coordination group; final shapes and connections unresolved','programme_keys':[r['programme_key']for r in dest if district_for(r)==key],'guest_envelope_source_indices':[i for i,r in enumerate(guests)if district_for(r)==key],'retail_envelope_source_indices':[i for i,r in enumerate(shops)if district_for(r)==key],'purpose':'Coordinate vertically adjacent uses as a neighbourhood rather than treating each deck as an isolated flat layer','source_indices_are_persistent_room_ids':False})
 assert sum(len(s['programme_keys'])for s in stacks)==161
 assert sum(len(s['guest_envelope_source_indices'])for s in stacks)==1000
 assert sum(len(s['retail_envelope_source_indices'])for s in stacks)==100
 result={'schema':1,'scope':'Complete programme/accounting crosswalk and initial vertical reservations, not final construction or a substitute room registry','source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in paths},'decks':decks,'programmes':programmes,'neighbourhood_stacks':stacks,'residential_court_reservations':courts,'longitudinal_vertical_core_reservations':cores,'aquatic_section_reservations':[aquatic_reservation],'protected_totals':{'guest_units':1000,'retail_addresses':100,'directory_programmes':161,'crew_people_including_player':400,'luxury_replacements_within_guest_units':81},'unresolved_finalization_gates':['Resolved three-dimensional hull and roof clearances','All161 destination shapes, arrivals and service connections','100retail addresses assigned to designed courts/streets','1000unit identity/layout crosswalk including81luxury replacements','Royalty/Supreme multistorey and all-species provision','400crew berths and service support','Guest and service route connectivity including accessible vertical transport','Purpose, floor ownership and protection for every multi-level void','Normal-play route, visibility and performance acceptance'],'legacy_implementation_claims_are_current_evidence':False}
 return result
if __name__=='__main__':
 result=build();(ROOT/'data/whole_ship_layout.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'decks':len(result['decks']),'programmes':len(result['programmes']),'guest_units':1000,'shops':100,'proposed_residential_courts':4,'proposed_longitudinal_cores':5,'final_layout_accepted':False}))
