import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
places=json.load(open(R/'contracts/place_instances.json'))['places']
def chair(s):
 x,y,z=s['position']; a=s['orientation_yaw_radians'];c,t=math.cos(a),math.sin(a)
 return [[x+u*c+v*t,z-u*t+v*c] for u,v in [(-.344,-.325),(.344,-.325),(.344,.460),(-.344,.460)]]
def sat(a,b):
 for q in [a,b]:
  for p,r in zip(q,q[1:]+q[:1]):
   ax,az=r[1]-p[1],p[0]-r[0];aa=[v[0]*ax+v[1]*az for v in a];bb=[v[0]*ax+v[1]*az for v in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-8:return False
 return True
polys={s['id']:chair(s) for s in places}; failures=[]; comparisons=0
revised=[s for s in places if 'planning_original_position' in s]
for a in revised:
 for b in places:
  if a['tier']!=b['tier'] or a['id']==b['id']:continue
  comparisons+=1
  if sat(polys[a['id']],polys[b['id']]):failures.append([a['id'],b['id']])
piers=[]
for x in [-105,-47]:
 for z in [-160,-149]:piers.append((f'pier_{x}_{z}',[[x-.55,z-.55],[x+.55,z-.55],[x+.55,z+.55],[x-.55,z+.55]]))
contacts=[dict(place=s['id'],pier=n) for s in places for n,p in piers if sat(polys[s['id']],p)]
report=dict(revised_places=len(revised),comparisons=comparisons,revised_chair_overlap_failures=failures,all_chair_pier_footprint_contacts=contacts,chair_bounds='Unchanged AST-CUL-003 closed asymmetric bounding rectangle; orientation retained',not_tested=['Species','Moving pan','guards','Door sweeps','Full bearing polygon','Runtime'])
(R/'qa/revised_place_screen.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
