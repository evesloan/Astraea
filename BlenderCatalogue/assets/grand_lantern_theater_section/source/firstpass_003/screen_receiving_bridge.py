"""Pure proposal screen. Does not authorize an added floor or alter Game."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
G=Path('/workspace/shared/astraea-godot-production-20261003');R=Path(__file__).resolve().parent
paths=['data/spatial_layout.json','data/whole_ship_layout.json','data/programme_ledger.json','data/reference/historical_guest_census.json','data/reference/historical_atlas_allocations.json','data/hull_envelope.json']
data={p:json.loads((G/p).read_text())for p in paths};shapes=data['data/spatial_layout.json'];whole=data['data/whole_ship_layout.json'];guest=data['data/reference/historical_guest_census.json']['guest_envelopes'];ledger=data['data/programme_ledger.json']['destinations'];hull=Polygon(data['data/hull_envelope.json']['plan_xz_m']);rows=[]
for deck in ['D11','D12','D13']:
 floor=box(-34,-129.05,-4,-122.95);route=box(-34,-128.6,-4,-123.4);conflicts=[];contacts=[]
 def check(kind,id,shape):
  a=floor.intersection(shape).area
  if a>1e-8:conflicts.append({'kind':kind,'id':id,'area_m2':a})
  elif floor.intersects(shape):contacts.append({'kind':kind,'id':id,'length_m':floor.intersection(shape).length})
 for row in ledger:
  if row['historical_deck']==deck:
   e=row['historical_envelope'];check('programme',row['programme_key'],box(e['x'][0],e['z'][0],e['x'][1],e['z'][1]))
 for i,row in enumerate(guest):
  if row['deck']==int(deck[1:]):check('guest_allocation',i,box(row['x'][0],row['z'][0],row['x'][1],row['z'][1]))
 for i,row in enumerate(data['data/reference/historical_atlas_allocations.json']):
  if row['deck']==int(deck[1:]):check('historical_atlas_allocation',i,box(row['x'][0],row['z'][0],row['x'][1],row['z'][1]))
 for row in shapes['regions']:
  if row['deck']==deck:check('retained_floor_region',row['id'],Polygon(row['boundary'],row.get('holes',[])))
 for row in shapes['voids']:
  if deck in row['decks']:check('protected_void',row['id'],Polygon(row['boundary']))
 for key in ['longitudinal_vertical_core_reservations','staff_riser_reservations']:
  for row in whole[key]:
   if deck in row['decks']:
    x=row.get('lobby_x',row.get('x'));z=row.get('lobby_z',row.get('z'));check(key,row['id'],box(x[0],z[0],x[1],z[1]))
 for row in whole['residential_court_reservations']:
  # Full x/z exclusion is conservative even before these upper court cuts exist.
  check('residential_court_plan',row['id'],Polygon(row['boundary']))
 assert hull.covers(floor)
 rows.append({'deck':deck,'proposed_floor_polygon':list(floor.exterior.coords)[:-1],'clear_route_polygon':list(route.exterior.coords)[:-1],'floor_area_m2':floor.area,'clear_width_m':5.2,'side_bearing_allowance_m':.45,'floor_to_plan_hull_boundary_min_m':floor.distance(hull.boundary),'positive_area_conflicts':conflicts,'boundary_contacts':contacts})
report={'status':'Proposed receiving bridge plan only; parent review and actual world/source contact checks required','source_sha256':{p:hashlib.sha256((G/p).read_bytes()).hexdigest()for p in paths},'proposal':rows,'first_stage_recommendation':'Author D11 only first: 30m span, 6.1m slab width, 5.2m clear route, 183m2 new floor. Existing internal theater stair reaches D12/D13; their external thresholds stay closed until separate receiving bridges pass.','required_before_adoption':['Parent reservation approval','Actual runtime neighbour census and exact retained triangles/hull at every relevant height','Source-backed fitted bearings/guardrails and head clearance; no floating deck or fabricated capacity certification','Imported strict floor/collision fidelity and continuous capsule/cart route','D11 main door open-pose/contact proof and deliberately locked safe state or tested controller','Closed secondary/staff exits and lift landings with physical source-derived collision'],'no_runtime_or_compiler_change':True}
out=R/'RECEIVING_BRIDGE_PLAN_SCREEN.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'decks':[(r['deck'],r['positive_area_conflicts'],r['boundary_contacts'])for r in rows],'first_stage_area':rows[0]['floor_area_m2']},indent=2))
