"""Read-only geometry planning tests; writes reports only inside this package, no mesh/engine work."""
from pathlib import Path
import json, math, hashlib
P=Path(__file__).resolve().parent;R=P.parents[3]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/auditorium_use')
D=json.loads((P/'THEATER_SECTION_PROPOSAL.json').read_text());M=json.loads((C/'AST-CUL-003.manifest.json').read_text())
B=M['bounds_gltf_y_up'];lo,hi=B['min_m'],B['max_m']
def rot(x,z,a):return (x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a))
def chair(s):
 x,y,z=s['position'];a=math.pi+math.atan2(x+76,z+238) if s['kind']!='rear_transfer_replaceable_place' else math.pi
 s['orientation_yaw_radians']=a
 return [(x+rot(u,v,a)[0],z+rot(u,v,a)[1])for u,v in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]]
def aabb(q):return(min(v[0]for v in q),min(v[1]for v in q),max(v[0]for v in q),max(v[1]for v in q))
def sat(a,b):
 for q in [a,b]:
  for p0,p1 in zip(q,q[1:]+q[:1]):
   ax,az=p1[1]-p0[1],p0[0]-p1[0];aa=[p[0]*ax+p[1]*az for p in a];bb=[p[0]*ax+p[1]*az for p in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-9:return False
 return True
polys=[chair(s)for s in D['seat_proposals']];boxes=[aabb(p)for p in polys];pairs=[];comparisons=0
for i,a in enumerate(polys):
 for j in range(i+1,len(polys)):
  if D['seat_proposals'][i]['tier']!=D['seat_proposals'][j]['tier']:continue
  comparisons+=1;aa,bb=boxes[i],boxes[j]
  if aa[2]<=bb[0]or bb[2]<=aa[0]or aa[3]<=bb[1]or bb[3]<=aa[1]:continue
  if sat(a,polys[j]):pairs.append([D['seat_proposals'][i]['id'],D['seat_proposals'][j]['id']])
aisles=[]
for t in ['stalls','first_gallery','crown_gallery']:
 for side,x in [('port',(-117,-113.6)),('starboard',(-38.4,-35))]:aisles.append({'id':t+'_'+side+'_cart_return','tier':t,'clear_width_m':3.4,'boundary':[(x[0],-236),(x[1],-236),(x[1],-153),(x[0],-153)]})
 aisles.append({'id':t+'_rear_transverse','tier':t,'clear_width_m':3.4,'boundary':[(-113.6,-180.5),(-38.4,-180.5),(-38.4,-177.1),(-113.6,-177.1)]})
 for deg in [-28,0,28]:
  # Radial audience route, not a cart or anatomical access assertion
  a=math.radians(deg);q=[]
  for u,v in [(-.7,19),(.7,19),(.7,49),(-.7,49)]:q.append((-76+u*math.cos(a)+v*math.sin(a),-238-u*math.sin(a)+v*math.cos(a)))
  aisles.append({'id':t+'_radial_'+str(deg),'tier':t,'clear_width_m':1.4,'boundary':q})
blocked=[]
for s,p in zip(D['seat_proposals'],polys):
 for a in aisles:
  if s['tier']==a['tier']and sat(p,a['boundary']):blocked.append({'seat':s['id'],'aisle':a['id']})
outside=[s['id']for s,p in zip(D['seat_proposals'],polys)if any(not(-118<=x<=-34 and -265<=z<=-115)for x,z in p)]
result={'status':'Existing whole closed-chair oriented bounding-footprint planning test; not live collision/anatomy acceptance','method':'Exact manifest asymmetric closed-state XZ bounding rectangle, yaw aimed at stage centre; conservative separating-axis positive-area overlap test; separate tiers vertically disjoint','source_sha256':{str(C/'AST-CUL-003.manifest.json'):hashlib.sha256((C/'AST-CUL-003.manifest.json').read_bytes()).hexdigest(),'tools/compile_layout.py':hashlib.sha256((R/'tools/compile_layout.py').read_bytes()).hexdigest()},'chair_bounds_local_gltf_m':B,'count':len(polys),'same_tier_pair_comparisons':comparisons,'chair_pair_positive_area_overlaps':pairs,'chair_aisle_positive_area_overlaps':blocked,'chair_footprints_outside_allocation':outside,'aisle_reservations':aisles,'unclosed':['Six-species anatomical fit','Occupied legs/arms/transfer envelope','Folded/moving seat pan sweep','Doors/guards/supports not authored','True sightlines and crowd/evacuation behavior','Continuous travel path collision and elevation handling']}
(P/'CHAIR_FOOTPRINT_SCREENING.json').write_text(json.dumps(result,indent=2)+'\n')
D['chair_footprint_planning']=dict(count=len(polys),chair_overlaps=len(pairs),aisle_overlaps=len(blocked),outside=len(outside),report='CHAIR_FOOTPRINT_SCREENING.json');(P/'THEATER_SECTION_PROPOSAL.json').write_text(json.dumps(D,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['aisle_reservations','source_sha256']},indent=2))
