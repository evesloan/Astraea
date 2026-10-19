from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box,shape
from shapely.ops import unary_union
R=Path('/workspace/Astraea');D=R/'BlenderCatalogue/assets/d17_starboard_standard_20261019';p=json.load(open(D/'PLAN.json'));checks=[]
for f,h in p['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h;checks.append('source:'+f)
streets=json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'))['regions']
for r in p['bearings']:
 reg=next(v for v in streets if v['id']==r['owner']);foot=box(r['at'][0]-.16,r['at'][2]-.16,r['at'][0]+.16,r['at'][2]+.16);slab=unary_union([Polygon(t)for t in reg['triangles']]);assert slab.covers(foot);checks.append('whole_footprint:'+r['name'])
polys=[];ids=[];reservations=[]
for r in p['rooms']:
 a=r['allocation'];polys.append(box(*[r['adopted_x'][0],r['adopted_z'][0],r['adopted_x'][1],r['adopted_z'][1]]));ids.append(a['proposed_runtime_id']);reservations+=a['proposed_rest_slot_ids'];assert a['proposed_rest_place_count']==2
assert len(set(ids))==9 and len(set(reservations))==18
for i,a in enumerate(polys):
 for b in polys[i+1:]:assert a.intersection(b).area<1e-7
premium=box(94.059997,-61.939999,117.940003,-48.060001);assert all(a.intersection(premium).area==0 for a in polys)
checks+=['unique_nine_source_ids','unique_eighteen_reservations','no_room_floor_overlap','premium808_geometry_separate']
reg=json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions'];existing=unary_union([Polygon(t)for r in reg if r['floor_y']==102 for t in r['triangles']]);assert shape(p['floor_geometry']).intersection(existing).area<1e-7;checks.append('missing_only_floor')
source=json.load(open(R/'Game/data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json'))
for r in source['source_parts']:
 if r['name']=='CR_EdgeHanger_00':
  vs=r['world_vertices'];lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)]
  for w in p['walls']:
   if w['owner']=='aft':assert not all(lo[i]<w['cut_max'][i]and hi[i]>w['cut_min'][i]for i in range(3))
checks.append('retained_Z18_hanger_outside_all_cuts')
(D/'CONTRACT_VERIFICATION.json').write_text(json.dumps({'status':'PASS','checks':checks,'source_pins_checked':len(p['source_pins']),'whole_permanent_street_footprints':len(p['bearings']),'new_floor_m2':shape(p['floor_geometry']).area,'engineering_or_art_accepted':False},indent=2)+'\n');print('PASS',len(checks))
