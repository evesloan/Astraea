"""Author the connected stone walking loop; cached triangles are consumed by Blender."""
from pathlib import Path
import json,math
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
import shapely
root=Path(__file__).resolve().parent
room=Polygon([(0,-34),(37,-34),(43,-30),(46,-21),(46,21),(43,30),(37,34),(0,34)])
loop=LineString([(18+10.5*math.cos(2*math.pi*i/48),6.8*math.sin(2*math.pi*i/48))for i in range(49)]).buffer(1.2,quad_segs=3)
paths=[[(0,0),(8,0)],[(2.5,-31),(2.5,31)],[(2.5,-20),(14,-20)],[(2.5,15),(23,15)],[(28.5,0),(38,0)]]
finish=unary_union([loop]+[LineString(p).buffer(1.4,quad_segs=3,cap_style=2,join_style=2)for p in paths]).intersection(room)
tri=list(shapely.constrained_delaunay_triangles(finish).geoms)
assert finish.is_valid and abs(sum(t.area for t in tri)-finish.area)<.001
(root/'floor_finish.json').write_text(json.dumps({'purpose':'Connected entry, quiet viewing spine and planted-court walking loop','triangles':[[list(p)for p in t.exterior.coords[:3]]for t in tri],'area_m2':finish.area,'loop_points':[[18+10.5*math.cos(2*math.pi*i/48),6.8*math.sin(2*math.pi*i/48)]for i in range(49)]},separators=(',',':'))+'\n')
