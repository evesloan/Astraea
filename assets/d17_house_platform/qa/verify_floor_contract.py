"""Read-only polygon and portal-seat checks; run with the existing geometry-deps PYTHONPATH."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());old=json.loads((C/'assets/starboard_house_upper/source/house_contract.json').read_text());record=next(a for a in old['floor_regions']if a['deck']=='D17');assert hashlib.sha256((C/'assets/starboard_house_upper/source/house_contract.json').read_bytes()).hexdigest()==D['source_inputs']['catalogue/assets/starboard_house_upper/source/house_contract.json'];floor=Polygon(record['boundary'],record['holes']);regions=[Polygon(r['compiler_candidate']['boundary'],r['compiler_candidate']['holes'])for r in D['units']]
assert all(p.is_valid and p.area>0 for p in regions)
assert all(p.intersection(floor).area<1e-8 for p in regions)
assert all(a.intersection(b).area<1e-8 for i,a in enumerate(regions)for b in regions[i+1:])
seats=[]
for side in[-1,1]:
 z0,z1=sorted([side*12.75,side*13.65])
 for x0,x1 in[(78.22,78.5),(81.5,81.78)]:
  seat=box(x0,z0,x1,z1);assert floor.covers(seat);seats.append({'xz':[x0,x1,z0,z1],'area_m2':seat.area,'owner':'D17_starboard_house_extension','contact_y':102})
assert all(u['compiler_candidate']['priority']==5 and u['compiler_candidate']['thickness']==.24 and u['compiler_candidate']['status'].startswith('HELD')for u in D['units'])
(R/'qa/floor_contract_verification.json').write_text(json.dumps({'pass':True,'held_floor_count':16,'candidate_area_m2':sum(p.area for p in regions),'disjoint_old_D17_floor':True,'mutually_disjoint_interiors':True,'existing_floor_contract_sha256':hashlib.sha256((C/'assets/starboard_house_upper/source/house_contract.json').read_bytes()).hexdigest(),'portal_jamb_seats':seats,'floor_adoption':False,'walkable_floor_geometry_in_source':0,'limit':'Polygon ownership and contact seats only; no16-unit support, route or engine acceptance'},indent=2)+'\n');print('Floor contract and four retained-floor portal seats pass')
