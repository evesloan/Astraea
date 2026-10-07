"""Selective actual furniture/door-approach receiving checks, not runtime cart QA."""
from pathlib import Path
import json,sys,runpy,math
import numpy as np
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,Point,MultiPoint,shape,LineString,box
from shapely.ops import unary_union
p=json.loads((R/'outputs/house_r001/PLAN.json').read_text());C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');manifest={r['catalogue_id']:r for r in json.loads((C/'catalogue_manifest.json').read_text())['assets']};decode=runpy.run_path(str(W/'residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py'))['decode'];cache={};rows=[]
floors={y:unary_union([shape(r['geometry'])for r in p['floor_regions']if r['floor_y']==y])for y in p['upper_datums']}
for a in p['asset_instances']:
 if not a['catalogue_id'].startswith('AST-FUR'):continue
 m=manifest[a['catalogue_id']];f=C/m['export']
 if f not in cache:cache[f]=decode(f)[1].reshape(-1,3)
 v=cache[f];yaw=math.radians(a['yaw']);x,y,z=a['world_xyz'];xx=v[:,0]*math.cos(yaw)+v[:,2]*math.sin(yaw);zz=-v[:,0]*math.sin(yaw)+v[:,2]*math.cos(yaw);q=MultiPoint(np.c_[xx*a['scale']+x,zz*a['scale']+z]).convex_hull
 route=box(4,366,97,374);out=q.difference(floors[y]).area;cross=q.intersection(route).area
 rows.append({'name':a['name'],'catalogue_id':a['catalogue_id'],'floor_y':y,'footprint_without_owned_floor_m2':out,'main_cart_through_route_overlap_m2':cross,'pass':out<1e-5 and cross<1e-5})
# Door approaches run from each exact historical marker0.8m into the owned street.
entries=[]
for r in p['rooms']:
 x,z=r['historical_door_marker_xz'];endx=x+.8 if x<44 else x-.8;q=LineString([(x,z),(endx,z)]).buffer(.30,cap_style=2);area=q.difference(floors[r['floor_y']]).area;entries.append({'source_index':r['census_source_index'],'approach_area_without_new_floor_m2':area,'pass':area<1e-5})
report={'scope':'Actual catalogue furniture projected footprint support and clear8m route; exact entry approach floor. No running-door or cart validation.','furniture':rows,'door_floor_approaches':entries,'all_furniture_pass':all(r['pass']for r in rows),'all_door_approach_floors_pass':all(r['pass']for r in entries)};(R/'qa/PUBLIC_POCKET_AND_ENTRY_SCREEN.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['furniture','door_floor_approaches']},indent=2));print('FAILED FURNITURE',[r for r in rows if not r['pass']]);print('FAILED APPROACHES',[r for r in entries if not r['pass']]);assert report['all_furniture_pass']and report['all_door_approach_floors_pass']
