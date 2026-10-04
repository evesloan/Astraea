"""Author the D02 garden floor and shallow water pockets inside the reserved atrium base.
This is a named composition, not room generation or a new accommodation allocation.
"""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,box
from shapely.affinity import scale,translate
from shapely.ops import unary_union
root=Path(__file__).resolve().parents[1]
p=root/'data/spatial_layout.json';layout=json.loads(p.read_text())
terrace=next(r for r in layout['regions'] if r['id']=='D02_authored_atrium_terrace')
base=Polygon(terrace['holes'][0]);outer=scale(Point(0,0).buffer(1,quad_segs=16),27,42)
inner=translate(scale(Point(0,0).buffer(1,quad_segs=16),17,28),-3,-4)
# Four legible approaches connect the garden court to the perimeter, with offset arrivals.
routes=[[(0,-51),(-9,-35),(-7,-20)],[(0,51),(10,34),(5,20)],[(-35,-18),(-23,-13),(-13,-7)],[(35,18),(23,12),(11,5)]]
bridges=unary_union([LineString(q).buffer(3,cap_style='square',join_style='round') for q in routes])
water=outer.difference(inner).difference(bridges)
pools=sorted(water.geoms,key=lambda g:g.centroid.x+g.centroid.y*.01)
assert len(pools)==4
# A level dry floor surrounds four shallow basins. Above D01, no engineering cutouts.
new=[{'id':'D02_garden_dry_court','deck':'D02','boundary':list(base.exterior.coords)[:-1],'holes':[list(q.exterior.coords)[:-1] for q in pools],'kind':'atrium_garden_base','void_exemptions':['central_atrium'],'priority':14,'thickness':.24,'render_cell_m':16,'status':'Authored garden circulation; planting, lighting and use still under construction'}]
for i,q in enumerate(pools):new.append({'id':f'D02_garden_pool_{i+1}','deck':'D02','boundary':list(q.exterior.coords)[:-1],'offset_y':-.8,'kind':'atrium_garden_base','void_exemptions':['central_atrium'],'priority':14,'thickness':.24,'render_cell_m':16,'material_role':'pool_bed','status':'Shallow ornamental basin structure; no swimming simulation'})
layout['regions']=[r for r in layout['regions'] if not r['id'].startswith('D02_garden_')]+new
p.write_text(json.dumps(layout,indent=2)+'\n')
source={'version':1,'floor_y':6.0,'water_y':5.74,'basin_bed_y':5.2,'dry_boundary':list(base.exterior.coords)[:-1],'pools':[list(q.exterior.coords)[:-1] for q in pools],'approach_centerlines':routes,'plan_intent':'Offset four-way approaches gather on an inner grove court, separated from the perimeter promenade by four shallow reflective pockets. All paths are at D02; tall planting occupies already reserved atrium air.','central_planting':{'center':[-3,-4],'radii':[8,16]},'scope':'D02 botanical base only, no new passenger capacity or through-deck cuts'}
(root/'data/atrium_garden.json').write_text(json.dumps(source,indent=2)+'\n')
assert min(r['offset_y'] if 'offset_y'in r else 0 for r in new)==-.8
for route in routes:
 assert base.union(Polygon(terrace['boundary'])).covers(LineString(route).buffer(2.8))
print('D02 garden authored:',len(pools),'water pockets;',round(base.area-water.area,1),'m2 dry floor')
