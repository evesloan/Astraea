"""Fit actual R070 and its connected approach without consuming other shops."""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box

r=Path(__file__).resolve().parents[1]
p=r/'data/architecture/D09_R070_profile.json';d=json.loads(p.read_text())
# The historic cross-street centre touches another shop's allocation. Bend the
# local approach through the actual inter-shop gap; preserve the existing public
# connection at the Living Gifts edge and R070's addressed east-facing entrance.
line=[[52,216],[60,222.5],[84,223],[84,236],[78,236]]
approach=LineString(line).buffer(2.0,cap_style='flat',join_style='round')
room=box(66,230,78,242)
allocations=json.loads((r/'data/reference/historical_atlas_allocations.json').read_text())
for a in allocations:
    if a['deck']!=9 or a['kind']!='unlabelled_shop_allocation':continue
    shape=box(a['x'][0],a['z'][0],a['x'][1],a['z'][1])
    if shape.equals(room):continue
    assert approach.intersection(shape).area<1e-5,('Approach consumes another shop',a)
shape=room.union(approach);assert shape.geom_type=='Polygon' and shape.is_valid
region={'id':'D09_R070_and_connected_approach','deck':'D09','boundary':[list(v)for v in shape.exterior.coords[:-1]],'holes':[],'priority':62,'thickness':.24,'status':'Actual R070 allocation with bent inter-shop approach; neighbouring shop interiors remain unfinished'}
layout_path=r/'data/spatial_layout.json';layout=json.loads(layout_path.read_text());layout['regions']=[v for v in layout['regions']if v['id']!=region['id']]+[region];layout_path.write_text(json.dumps(layout,indent=2)+'\n')
d['approach_centerline_xz']=line;d['approach_clear_width']=4.0;d['neighboring_shop_envelopes_preserved']=True
p.write_text(json.dumps(d,indent=2)+'\n')
print('R070 and supported public approach fit; neighbouring historical shop envelopes untouched')
