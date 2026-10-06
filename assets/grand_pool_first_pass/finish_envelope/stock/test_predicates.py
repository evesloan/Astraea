"""Adversarial sanity checks of the source-only collision/support predicates."""
from geometry import *
from pathlib import Path
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
raw=json.loads((C/'assets/retail_display/qa/evaluated_source_geometry.json').read_text())['AST-RTL-001']['parts'];parts={}
for p in raw:
 v=[(x,z,-y)for x,y,z in p['vertices']];parts[p['name']]={'vertices':v,'triangles':[tuple(v[i]for i in t)for t in p['triangles']],'bounds':bounds(v)}
floor=parts['lower_storage_tactile_floor'];y=floor['bounds'][1][1]
assert not convex_box_overlap(floor,[[-1,y,-.1],[-.6,y+.316,.2]])
assert convex_box_overlap(floor,[[-1,y-.001,-.1],[-.6,y+.316,.2]])
assert all(not any(abs(yy-.235)<EPS for yy,_,_ in horizontal_hits((x,.235,z),floor['triangles']))for x,z in ((-.8,-.1),(-.6,.2)))
plant=read_glb(C/'assets/botanical_understory/exports/AST-BOT-003.glb');yaw=math.radians(297);pos=(.8,2.06,-.105)
assert convex_box_overlap(parts['dark_inset_display_back'],bounds([transform(v,pos,yaw)for v in plant['vertices']]))
pos=(.8,2.06,-.05)
assert not convex_box_overlap(parts['dark_inset_display_back'],bounds([transform(v,pos,yaw)for v in plant['vertices']]))
a=((0,0,0),(1,0,0),(0,1,0));b=((.1,.1,-1),(.1,.1,1),(.5,.1,0));c=((2,0,0),(3,0,0),(2,1,0));d=((.2,.2,0),(.3,.2,0),(.2,.3,0))
assert triangle_intersects(a,b);assert not triangle_intersects(a,c);assert triangle_intersects(a,d)
print('PASS: contact accepted; 1 mm penetration, floating nominal lower-floor height and centered foliage rejected; disjoint, crossing and coplanar triangle cases verified.')
