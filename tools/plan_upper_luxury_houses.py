"""Reversible81-unit luxury replacement study; no source IDs, floors or rooms changed."""
from pathlib import Path
import json,hashlib
from collections import Counter
from shapely.geometry import Polygon,box
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def rect(r):return box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])
g=read('data/reference/historical_guest_census.json')['guest_envelopes'];whole=read('data/whole_ship_layout.json');programmes=read('data/reference/directory_allocations.json')['records'];hull=Polygon(read('data/hull_envelope.json')['plan_xz_m'])
# This is compatibility/capacity reservation, not a population or habitat assignment.
schedules={
 'port_forward_upper_house':{'deluxe':10,'premium':6,'royalty':1},
 'port_central_upper_house':{'deluxe':4,'premium':2,'supreme':1},
 'port_aft_upper_house':{'deluxe':11,'premium':5,'royalty':1},
 'starboard_forward_upper_house':{'deluxe':10,'premium':6,'royalty':1},
 'starboard_central_upper_house':{'deluxe':5,'premium':1,'royalty':1},
 'starboard_aft_upper_house':{'deluxe':10,'premium':5,'royalty':1},
}
frontage={'deluxe':10,'premium':14,'royalty':22,'supreme':32};sleepers={'deluxe':4,'premium':6,'royalty':8,'supreme':10}
bands={'forward':[-478,-250],'central':[-90,90],'aft':[250,460]}
rooms=[];retained=[];houses=[];standard_replans=[]
for house in whole['residential_houses']:
 key=house['id']
 if key not in schedules:continue
 side,district=key.split('_')[:2];indices=[i for i in house['guest_envelope_source_indices']if g[i]['deck']==17];schedule=schedules[key]
 keep_count=len(indices)-sum(schedule.values());assert keep_count>=0
 # Retain inner-bank rooms first; any additional outer ones are at the ends,
 # away from the deeper central Supreme allocation.
 kept=sorted(indices,key=lambda i:(abs(sum(g[i]['x'])/2),-abs(sum(g[i]['z'])/2),i))[:keep_count]
 retained.extend(kept);replace=sorted(set(indices)-set(kept),key=lambda i:sum(g[i]['z']))
 types=[]
 for tier,n in schedule.items():types += [tier]*n
 # Centre the unique multilevel home; alternate the smaller sizes around it.
 ordinary=[];counts={k:v for k,v in schedule.items()if k not in ['royalty','supreme']}
 while sum(counts.values()):
  for tier in ['deluxe','premium']:
   if counts.get(tier,0):ordinary.append(tier);counts[tier]-=1
 special=[k for k in ['royalty','supreme']if schedule.get(k)]
 types=ordinary[:len(ordinary)//2]+special+ordinary[len(ordinary)//2:]
 span=sum(frontage[t]for t in types);z0,z1=bands[district]
 if district=='central':
  split=len(kept)//2
  for segment,assigned in [((-80,-20),kept[:split]),((20,80),kept[split:])]:
   cursor=(sum(segment)-len(assigned)*7.2)/2
   for index in assigned:
    shape=box(-76,cursor,-63,cursor+7.2)if side=='port'else box(63,cursor,76,cursor+7.2)
    standard_replans.append({'source_envelope_index':index,'house':key,'kind':'Retained standard unit in a replanned central house','floor_y':102,'proposed_floor_boundary':[list(q)for q in list(shape.exterior.coords)[:-1]],'source_allocation':{'x':g[index]['x'],'z':g[index]['z']},'historical_stable_id':g[index]['stable_id'],'status':'Unbuilt spatial proposal; no new unit, historical identity or bed created'})
    cursor+=7.2
 groups={}
 for category in ['court','space']:
  groups[category]=[tier for tier in types if (tier=='deluxe')==(category=='court')]
 placements={}
 if district in ['forward','central','aft']:
  gap=(-390,-350)if district=='forward'else(350,390)if district=='aft'else(-20,20)
  for category,tiers in groups.items():
   if district=='central'and category=='court':continue
   if district=='central':tiers=types
   split=len(tiers)//2
   for segment,segment_types in [((z0,gap[0]),tiers[:split]),((gap[1],z1),tiers[split:])]:
    length=sum(frontage[t]for t in segment_types);assert length<=segment[1]-segment[0]
    cursor=(sum(segment)-length)/2
    for tier in segment_types:
     placements.setdefault(tier,[]).append((cursor,cursor+frontage[tier]));cursor+=frontage[tier]
 for number,(index,tier)in enumerate(zip(replace,types),1):
  shape=None
  if district in ['forward','central','aft']:
   cursor,znext=placements[tier].pop(0)
   if district=='central':
    shape=box(-118,cursor,-94,znext)if side=='port'else box(94,cursor,118,znext)
   elif tier=='deluxe':
    inner,outer=(37,55)if district=='aft'else(43,61)
    shape=box(-outer,cursor,-inner,znext)if side=='port'else box(inner,cursor,outer,znext)
   else:
    ring=hull.buffer(-2).difference(hull.buffer(-20))
    clip=box(-130,cursor,-1,znext)if side=='port'else box(1,cursor,130,znext)
    shape=ring.intersection(clip)
   assert shape.geom_type=='Polygon'and shape.is_valid
   assert all(shape.intersection(rect(r)).area<1e-6 for r in programmes if r['deck']==17),(key,tier,'programme')
   assert all(shape.intersection(Polygon(r['proposed_floor_boundary'])).area<1e-6 for r in standard_replans),(key,tier,'replanned standard')
  boundary=None if shape is None else [[round(x,6),round(z,6)]for x,z in list(shape.exterior.coords)[:-1]]
  rooms.append({'proposal_key':f'{key}_luxury_{number:02}','house':key,'source_envelope_index':index,'historical_stable_id':g[index]['stable_id'],'source_allocation':{'x':g[index]['x'],'z':g[index]['z']},'tier':tier,'maximum_sleepers':sleepers[tier],'floor_y':102,'proposed_floor_boundary':boundary,'floor_area_m2':None if shape is None else round(shape.area,3),'frontage_m':frontage[tier],'nominal_depth_m':24 if district=='central'else 18,'upper_floor_y':106.5 if tier in ['royalty','supreme']else None,'upper_level_is_new_unit':False,'proposed_external_roof_limit_y':114.5 if tier=='supreme'else 112.0 if tier=='royalty'else 106.5,'view_intent':('Central homes combine hull-facing windows with their replanned house courts. No public gallery across bedroom windows; actual views and private entry geometry remain to fit.'if district=='central'else'Deluxe homes face the designed house court; premium and multilevel outer homes have a hull-facing space side and inward court side. Not every luxury room is a space-view room. Actual glazing/privacy remain to fit.'),'entry_intent':'Quiet house approaches with recessed entries; keep public circulation away from bedroom windows','status':'Central-house placement unresolved; protect fitted commons and retained standard rooms'if shape is None else'Spatial replacement proposal only; no room geometry, registry identity or actual beds authored'})
 houses.append({'house':key,'source_D17_units':len(indices),'retained_standard_source_indices':kept,'luxury_replacements':schedule,'band_z':[z0,z1],'occupied_frontage_m':span,'remaining_band_length_m':None if district=='central'else z1-z0-max(sum(frontage[t]for t in groups['court']),sum(frontage[t]for t in groups['space']))-40,'remaining_space_purpose':'Reserve house arrivals, screened entry courts and end conditions; exact access routes unresolved'})
assert len(rooms)==81 and len(retained)==19
assert Counter(r['tier']for r in rooms)=={'deluxe':50,'premium':25,'royalty':5,'supreme':1}
assert len({r['source_envelope_index']for r in rooms}|set(retained))==100
for i,a in enumerate(rooms):
 for b in rooms[i+1:]:
  if a['proposed_floor_boundary']and b['proposed_floor_boundary']:assert Polygon(a['proposed_floor_boundary']).intersection(Polygon(b['proposed_floor_boundary'])).area<1e-6
d18_crown=read('data/architecture/D18_COMMAND_CROWN_PROPOSAL.json')
upper_conflicts=[]
for room in rooms:
 if room['upper_floor_y']is None:continue
 shape=Polygon(room['proposed_floor_boundary'])
 assert all(shape.intersection(Polygon(r['proposed_floor_boundary'])).area<1e-6 for r in d18_crown['programmes'])
 for source_room in programmes:
  if source_room['deck']==18 and shape.intersection(rect(source_room)).area>1e-6:upper_conflicts.append({'luxury_proposal_key':room['proposal_key'],'historical_D18_programme':source_room['programme_key'],'overlap_m2':round(shape.intersection(rect(source_room)).area,3),'resolution_dependency':'Requires adopting the coordinated D18 programme relocation; original source allocations remain unchanged until then'})
source_paths=['data/architecture/D18_COMMAND_CROWN_PROPOSAL.json','data/reference/historical_guest_census.json','data/whole_ship_layout.json','data/hull_envelope.json','data/reference/directory_allocations.json']
result={'schema':1,'scope':'Reversible geometric proposal for replacing81 of the100 D17units, within the existing1000guest-unit total. Original source envelopes, persistent IDs and runtime geometry remain unchanged. This is not a recovered historical luxury allocation.','source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in source_paths},'houses':houses,'historical_D18_overlap_dependencies':upper_conflicts,'replacements':rooms,'retained_D17_standard_source_indices':retained,'replanned_standard_units':standard_replans,'counts':{'unchanged_other_deck_units':900,'retained_D17_standard_units':19,'D17_luxury_replacements':81,'geometrically_reserved_replacements':81,'unlocated_central_house_replacements':0,'total_guest_units':1000,'deluxe':50,'premium':25,'royalty':5,'supreme':1,'multilevel_units':6,'proposed_D17_standard_replans':19,'maximum_luxury_sleepers':sum(r['maximum_sleepers']for r in rooms),'admission_cap_unchanged':2000},'section_intent':{'single_level_floor_y':102,'local_upper_floor_y':106.5,'six_private_upper_pavilions':'Royalty/Supreme upper levels are parts of their existing units, not six new rooms. Reserve local roofs below118m and independent accessible internal circulation.','aft_court_privacy':'Set the aft court-facing band6m farther inboard to preserve approximately10m or more at the narrowest facing window pair. This is a stepped D17 garden/roof edge, not permission to cut D13-D16 guest rooms.','lower_house_courts':'Adapt the proposed D17 court opening at the inhabited outer rim; never cut these new suite floors or silently turn an entire court into a slab. D13-D16 volumes and room counts remain protected.'},'remaining_gates':['Fit the two central houses around their preserved commons and18m-wide court bands;19standard units retain their source identities but have proposed new footprints','Coordinate actual lower-roof and six private pavilion sections with the D18 command-crown proposal','Resolve foundations, hull skin/windows and transfer supports rather than claiming that plan fit establishes3D fit','Fit all six house entries, quiet galleries, privacy screens and service approaches','Fit private accessible vertical access for Royalty/Supreme, kitchens, conversation pits, multiple viewing levels and real rest/storage places','Assign5-10luxury provisions per required habitat/species need without inventing new canon or double-counting units','Fit all-species Supreme accommodation and actual room/bed compatibility','Reconcile category/physical sleeper ledger with admission cap; maxima are not actual bed anchors','Review normal player views and physical access before adopting the plan']}
(ROOT/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['counts']))
