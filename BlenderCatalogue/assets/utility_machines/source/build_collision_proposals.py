"""Conservative separate convex-piece proposals preserving ports and work space.
No automatic whole-machine hull; no engine/runtime collision verification.
Run with ordinary Python after build_utility_machines.py.
"""
import math,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def ex(p):return [p[0],p[2],-p[1]]
def wedge(name,axis,a,b,ri,ra,rb,center=(0,0,0),segments=12,omit=None):
 out=[];inner=ri/math.cos(math.pi/segments)
 for i in range(segments):
  t0=2*math.pi*i/segments;t1=2*math.pi*(i+1)/segments;mid=(t0+t1)/2
  if omit and omit(mid):continue
  pts=[]
  for s,ro in[(a,ra),(b,rb)]:
   for r,t in[(inner,t0),(ro,t0),(ro,t1),(inner,t1)]:
    xyz=(s,r*math.cos(t),r*math.sin(t)) if axis=='X' else(r*math.cos(t),r*math.sin(t),s)
    pts.append([v+c for v,c in zip(xyz,center)])
  out.append({'name':name+f'_sector_{i:02d}','type':'convex_hull_points','points_blender_source_m':pts,'points_gltf_yup_m':[ex(p) for p in pts]})
 return out

def box(name,lo,hi):
 pts=[[x,y,z] for x in(lo[0],hi[0]) for y in(lo[1],hi[1]) for z in(lo[2],hi[2])]
 return {'name':name,'type':'convex_hull_points','points_blender_source_m':pts,'points_gltf_yup_m':[ex(p) for p in pts]}
def generate(ident,rec):
 out=[]
 if ident=='AST-ENG-001':
  for side in(-1,1):out.append(box('skid_rail_'+str(side),[side*.56-.10,-.41,0],[side*.56+.10,1.10,.165]))
  for y in(-.12,.16,.354,.54,.88):out.append(box('load_crossbar_'+str(y),[-.575,y-.046,.113],[.575,y+.046,.163]))
  for a,b,ra,rb in[(-.33,-.26,.10,.11),(-.26,-.21,.11,.255),(-.21,-.18,.255,.28),(-.18,-.14,.28,.28),(-.14,.14,.28,.28),(.14,.18,.28,.28),(.18,.21,.28,.255),(.21,.26,.255,.11),(.26,.33,.11,.10)]:out+=wedge('pump_open_case_'+str(a),'X',a,b,.08,ra,rb,(0,0,.60),omit=(lambda t: math.cos(t)<0) if a==-.14 else None)
  out += [box('drive_housing',[-.203,.442,.399],[.203,1.01,.90]),box('coupling_guard',[-.154,.264,.582],[.154,.445,.728])]
  # Front removable cover is a separate solid obstruction only outside the X bore.
  out += [box('front_service_cover',[-.176,-.322,.424],[.176,-.275,.776])]
  for s in(-1,1):
   a,b=sorted((s*.33,s*.85));out+=wedge('pump_open_nozzle_'+str(s),'X',a,b,.08,.10,.10,(0,0,.60))
   a,b=sorted((s*.815,s*.85));out+=wedge('pump_open_flange_'+str(s),'X',a,b,.08,.16,.16,(0,0,.60))
 else:
  out.append(box('closed_belly',[-.203,-.203,.338],[.203,.203,.405]))
  # Deliberately leave wider collision windows around the actual ±X circular apertures.
  for a,b in[(.45,.50),(.50,.70),(.70,1.378)]:
   omit=(lambda t:abs(math.sin(t))<.42) if a==.50 else None
   out+=wedge('filter_shell_'+str(a),'Z',a,b,.252,.282,.282,omit=omit)
  out.append(box('removable_lid',[-.308,-.308,1.386],[.308,.308,1.569]))
  for i,a in enumerate(map(math.radians,(90,210,330))):
   x,y=.37*math.cos(a),.37*math.sin(a);tx,ty=.267*math.cos(a),.267*math.sin(a)
   # Separate slender leg proposals; empty space between them stays open.
   out.append(box('leg_'+str(i),[min(x,tx)-.04,min(y,ty)-.04,.055],[max(x,tx)+.04,max(y,ty)+.04,.48]))
   out.append(box('foot_'+str(i),[x-.10,y-.105,0],[x+.10,y+.105,.072]))
  for s in(-1,1):
   a,b=sorted((s*.235,s*.64));out+=wedge('filter_open_nozzle_'+str(s),'X',a,b,.08,.10,.10,(0,0,.60))
   a,b=sorted((s*.605,s*.64));out+=wedge('filter_open_flange_'+str(s),'X',a,b,.08,.16,.16,(0,0,.60))
 return {'status':'offline simplified collision proposal; no active engine physics','source_frame':'Blender asset local Z-up metres','exchange_frame':'GLB Y-up (x,z,-y)','primitives':out,'cylindrical_bore_preserved_radius_m':.08,'inner_polygon_rule':'Inner wedge radius is divided by cos(pi/12), so the inner chord stays outside the .08 bore or .252 cavity radius','floor_contacts':rec['floor_contacts'],'excluded_work_reservations':rec['maintenance_clearances'],'pump_service_aperture_collision_omission':'The front semicircle sectors (90 to270 degrees in YZ) are deliberately omitted only over X[-.14,.14]m, preserving the service opening after the separate cover collider is removed. This is a deliberately coarse open-space-preserving simplification around the circular aperture; it under-covers part of the front shell and is not an active collision shape.','open_space_policy':'No whole-machine convex hull. Pipe mouths are annular wedges. Front work space, inter-leg floor openings and overhead lid reservation remain outside geometry. Filter middle shell sectors omitted around nozzle holes rather than capped.','limitations':['Collision pieces are conservative proposals, not exact mechanical shapes','Separate cover/guard/lid colliders require runtime movement handling','No dynamic contact, actor reach, actual installed route or safety verification']}
def main():
 records={ident:json.loads((BASE/f'{ident}.manifest.json').read_text()) for ident in('AST-ENG-001','AST-ENG-002')}
 result={k:generate(k,r) for k,r in records.items()};(BASE/'collision_proposals.json').write_text(json.dumps(result,indent=2)+'\n');print('OPEN_COLLISION_PROPOSALS',[(k,len(r['primitives'])) for k,r in result.items()])
if __name__=='__main__':main()
