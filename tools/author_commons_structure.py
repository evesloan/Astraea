"""Compile the reviewed pair of real commons allocations into existing ownership data."""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
r=Path(__file__).resolve().parents[1];d=json.loads((r/'data/architecture/D13_D14_starboard_commons.json').read_text());p=r/'data/spatial_layout.json';layout=json.loads(p.read_text())
outer=Polygon(d['envelope_xz_m']);void=unary_union([Polygon(d['upper_main_void_xz_m']),Polygon(d['upper_stair_void_xz_m'])]);hole=Polygon(d['lift']['floor_hole_xz_m'])
regions=[];records=[]
for i,deck in enumerate(['D13','D14']):
 arrival=LineString(d[('lower'if i==0 else'upper')+'_arrival_centerline_xz_m']).buffer(2.2,cap_style='flat',join_style='mitre')
 shape=unary_union([outer,arrival])
 if i==0:shape=shape.union(LineString(d['residential_street_connection_xz_m']).buffer(2.2,cap_style='flat'))
 shape=shape.difference(hole)
 if i==1:shape=shape.difference(void)
 assert shape.is_valid and shape.geom_type=='Polygon'
 boundary=[list(p)for p in shape.exterior.coords[:-1]];holes=[[list(p)for p in q.coords[:-1]]for q in shape.interiors]
 regions.append({'id':deck+'_starboard_commons_authored','deck':deck,'boundary':boundary,'holes':holes,'priority':65,'thickness':.24,'status':'Authored commons structure; lift/finishes/route validation pending'})
 records.append({'deck':deck,'floor_y':d['floors_y_m'][i],'boundary':boundary,'holes':holes})
layout['regions']=[x for x in layout['regions']if x['id']not in [q['id']for q in regions]]+regions
p.write_text(json.dumps(layout,indent=2)+'\n')
cat=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/vertical_commons')
(cat/'source').mkdir(parents=True,exist_ok=True);(cat/'exports').mkdir(exist_ok=True)
(cat/'source/architecture_contract.json').write_text(json.dumps({'contract':d,'floor_regions':records},indent=2)+'\n')
print('Two actual commons allocations compiled to ownership source; no extra guest units')
