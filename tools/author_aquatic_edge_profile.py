from pathlib import Path
import json
from shapely.geometry import Polygon,Point
from shapely.ops import nearest_points
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');D=json.load(open(R/'data/aquatic_section.json'));L=json.load(open(R/'data/spatial_layout.json'));records=[]
for deck,y,below,label in [('D09',52.5,44,'D08_gentle_waters_floor'),('D10',61,52.5,'D09_living_gifts_floor')]:
 opening=Polygon(D['openings'][deck]);path=opening.buffer(.14,join_style=2);r=next(v for v in L['regions']if v['id']==label);safe=Polygon(r['boundary'],r.get('holes',[])).buffer(-2.0);ring=[list(v)for v in path.exterior.coords[:-1]];lights=[]
 for i in [0,2,4,6]:
  a=ring[i];b=ring[(i+1)%len(ring)];mid=((a[0]+b[0])/2,(a[1]+b[1])/2);target=nearest_points(Point(mid),safe)[1];lights.append({'source_xyz':[mid[0],y-.62,mid[1]],'receiver_xyz':[target.x,below+.04,target.y]})
 records.append({'deck':deck,'floor_y':y,'boundary':ring,'lights':lights})
result={'id':'aquatic_balcony_edges','status':'Construction and contact review pending','origin_xyz':[8,44,182],'decks':records,'guard_height_m':1.15,'design':'Continuous supported plinth, tinted infill and profiled handrail; local underside receivers, no new floor cuts'};p=R/'data/architecture/D09_D10_aquatic_edges.json';p.write_text(json.dumps(result,indent=2)+'\n');r=C/'assets/aquatic_balcony_edges';(r/'source').mkdir(parents=True,exist_ok=True);(r/'exports').mkdir(exist_ok=True);(r/'source/edge_contract.json').write_text(p.read_text());print([(r['deck'],r['lights'])for r in records])
