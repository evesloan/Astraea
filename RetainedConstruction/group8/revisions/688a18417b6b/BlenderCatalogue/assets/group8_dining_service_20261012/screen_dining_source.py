from pathlib import Path
import json,numpy as np,sys
from shapely.geometry import box,LineString,Point
W=Path(__file__).resolve().parent;p=json.load(open(W/'PLAN.json'));src={r['programme_key']:r['bounds']for r in json.load(open(W/'ACTUAL_DINING_NATIVE_BOUNDS.json'))};holds=[];checks=0;route_holds=[];rchecks=0
for row in p['meshes']:
 a=np.array(row['world_aabb']);old=src[row['programme_key']];oa=np.array([r['world_aabb']for r in old]);delta=np.minimum(a[[1,3,5]],oa[:,[1,3,5]])-np.maximum(a[[0,2,4]],oa[:,[0,2,4]]);checks+=len(old)
 for i in np.where(np.min(delta,axis=1)>.0005)[0]:
  if old[i]['name']not in row['permitted_retained_context']:holds.append({'new':row['name'],'old':old[i]['name'],'positive_overlap_m':delta[i].tolist()})
 if not row['collide']or a[2]>=62.82:continue
 key=row['programme_key'];num=int(key.rsplit('_',1)[1]);side=1 if num==2 else-1;z0=-250 if num==3 else-466;poly=box(a[0],a[4],a[1],a[5]);contract=p['retained_contracts'][key];oldplan=contract['source_routes'];rad=float(contract['source_cart_envelope']['test_radius_with_margin_m'])
 for index,route in enumerate(oldplan['routes']+[[v,v]for n,v in oldplan['cart_parking']]):
  points=[(side*(8+q[0]),z0+q[1])for q in route];curve=LineString(points)if len(set(points))>1 else Point(points[0]);distance=curve.distance(poly);rchecks+=1
  if distance<rad-.001:route_holds.append({'new':row['name'],'route':index,'distance_m':distance,'protected_radius_m':rad})
report={'status':'HOLD'if holds or route_holds else'PASS','source_context_pair_checks':checks,'protected_route_checks':rchecks,'undeclared_context_overlaps':holds,'protected_static_source_route_holds':route_holds,'scaled_moving_standard_door_and_cart_acceptance':'requires actual focused runtime'};(W/('SOURCE_SCREEN'+sys.argv[1]+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='scaled_moving_standard_door_and_cart_acceptance'}))
