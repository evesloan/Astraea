import json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import build_geometry as g
original=json.load(open('/workspace/shared/astraea-godot-production-20261003/data/architecture/packages/theater/CHAIR_FOOTPRINT_SCREENING.json'))
objects=json.load(open(R/'source/geometry.json'))['objects'];places=json.load(open(R/'contracts/place_instances.json'))['places']
def sat(a,b):
 for q in [a,b]:
  for p,r in zip(q,q[1:]+q[:1]):
   ax,az=r[1]-p[1],p[0]-r[0];aa=[v[0]*ax+v[1]*az for v in a];bb=[v[0]*ax+v[1]*az for v in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-8:return False
 return True
routes=[]
for q in original['aisle_reservations']:
 if q['clear_width_m']!=3.4:continue
 y={'stalls':69.5,'first_gallery':78,'crown_gallery':84}[q['tier']]
 high=y+(1 if 'rear_transverse' in q['id'] and q['tier']!='stalls' else 0)
 routes.append(dict(**q,floor_y_range=[y,high],provisional_headroom=3))
routes += [dict(id='D11_backstage_staff_cart',tier='stalls',clear_width_m=3.4,boundary=g.rect([-116,-258.7,-36,-255.3]),floor_y_range=[69.5,69.5],provisional_headroom=3),dict(id='D11_front_audience_crossroute',tier='stalls',clear_width_m=3.4,boundary=g.rect([-98,-229.95,-35,-226.55]),floor_y_range=[69.5,69.5],provisional_headroom=3)]
static=[]
for o in objects:
 if o['role'] in ['preview_only','walkable_authored','stair_flight']:continue
 vs=o['vertices_world'];lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)];p=[[v[0],v[2]] for v in vs[:len(vs)//2]]
 if len(p)<3 or g.area(p)<1e-9:p=g.rect([lo[0],lo[2],hi[0],hi[2]])
 static.append((o['name'],lo,hi,p))
contacts=[];margins=[];slope=8.9/4.5;nn=math.hypot(1,slope)
for q in routes:
 fy,high=q['floor_y_range'];top=high+3
 m=min(min(x+118.5-.8,(x+118.5-slope*(top-87.5))/nn-.8) for x,z in q['boundary'])
 liner=min(min(x+117.4,(x+117.65-slope*(top-87))/nn-.12) for x,z in q['boundary'])
 margins.append(dict(id=q['id'],pressure_reservation_margin=m,interior_liner_conservative_margin=liner,actual_floor_y_range=[fy,high],volume_top_y=top))
 for name,lo,hi,p in static:
  if lo[1]>=top-1e-7 or hi[1]<=fy+1e-7:continue
  if name=='west_acoustic_tapered_return' and liner>0:continue
  if sat(q['boundary'],p):contacts.append(dict(route=q['id'],structure=name))
front=next(q for q in routes if q['id']=='D11_front_audience_crossroute');chair_contacts=[]
for p in places:
 if p['tier']!='stalls':continue
 x,y,z=p['position'];a=p['orientation_yaw_radians'];poly=[[x+u*math.cos(a)+v*math.sin(a),z-u*math.sin(a)+v*math.cos(a)] for u,v in [(-.344,-.325),(.344,-.325),(.344,.460),(-.344,.460)]]
 if sat(front['boundary'],poly):chair_contacts.append(p['id'])
report=dict(routes=routes,static_route_contacts=contacts,front_crossroute_chair_contacts=chair_contacts,normal_margins=margins,minimum_pressure_margin=min(q['pressure_reservation_margin'] for q in margins),minimum_interior_liner_margin=min(q['interior_liner_conservative_margin'] for q in margins),floor_scope='D11 flat portions compiler conditional. Upper cart crossing has real raised plateau and transverse slopes, not a step. Cart/species/live capsule remains gated.',D11_front_access='3.4m transverse approach plus level front apron radius18.1–19.5; D11 compiler floor must connect to source apron once')
(R/'qa/cart_route_screen.json').write_text(json.dumps(report,indent=2)+'\n');print('Static route contacts',len(contacts),'front chair contacts',len(chair_contacts),'minimum pressure',report['minimum_pressure_margin'],'minimum liner',report['minimum_interior_liner_margin'])
