"""Exact projected polygon/triangle minimum ceiling check for authored stair tops."""
import json,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import build_geometry as g
objects=json.load(open(R/'source/geometry.json'))['objects']
def bounds(p):return [min(q[0] for q in p),min(q[1] for q in p),max(q[0] for q in p),max(q[1] for q in p)]
def overlap(a,b):return a[0]<b[2]-1e-8 and b[0]<a[2]-1e-8 and a[1]<b[3]-1e-8 and b[1]<a[3]-1e-8
def intersect(p,c):
 signed=sum(c[i][0]*c[(i+1)%len(c)][1]-c[(i+1)%len(c)][0]*c[i][1] for i in range(len(c)));sign=1 if signed>0 else -1
 for a,b in zip(c,c[1:]+c[:1]):
  p=g.split_line(p,a,b,sign,True)
  if not p:return []
 return p
triangles=[]
for o in objects:
 if o['role'] in ['preview_only','guard_proposal']:continue
 vs=o['vertices_world']
 for f in o['faces']:
  for i in range(1,len(f)-1):
   tri=[vs[j] for j in [f[0],f[i],f[i+1]]];p=[[v[0],v[2]] for v in tri]
   if g.area(p)<1e-9:continue
   a,b,c=tri;det=(b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2])
   ax=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/det
   az=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/det
   off=a[1]-ax*a[0]-az*a[2]
   triangles.append((o['name'],p,bounds(p),ax,az,off,max(v[1] for v in tri)))
witnesses=[];collisions=[]
for o in objects:
 if o['role']!='stair_flight':continue
 vs=o['vertices_world'];n=len(vs)//2;p=[[v[0],v[2]] for v in vs[:n]];pb=bounds(p);fy=vs[0][1];minimum=1e9;witness=None
 for name,q,qb,ax,az,off,maxy in triangles:
  if name==o['name'] or maxy<=fy+1e-6 or not overlap(pb,qb):continue
  inter=intersect(p,q)
  if not inter or g.area(inter)<1e-8:continue
  values=[(ax*x+az*z+off-fy,[x,fy,z]) for x,z in inter]
  lo,pt=min(values)
  if lo<=1e-6:
   # True crossing of a walking top is a separate contact candidate, not an overhead ceiling.
   if max(v[0] for v in values)>1e-5:collisions.append(dict(floor=o['name'],structure=name,minimum=lo))
   continue
  if lo<minimum:minimum=lo;witness=dict(overhead=name,point=pt)
 if minimum<1e8:witnesses.append(dict(floor=o['name'],minimum_clearance_m=minimum,witness=witness))
report=dict(status='Pure triangle projection, not runtime acceptance',stair_walkable_planes=sum(o['role']=='stair_flight' for o in objects),minimum_stair_clearance_m=min(w['minimum_clearance_m'] for w in witnesses),below_3m=[w for w in witnesses if w['minimum_clearance_m']<3-1e-6],walking_top_crossing_candidates=collisions,witnesses=witnesses,limits='Guards intentionally excluded as boundary elements; actual capsule species and fall behavior still gated. Only authored source ceilings are tested; canonical91.5 roof reservation remains separate.')
(R/'qa/stair_headroom_screen.json').write_text(json.dumps(report,indent=2)+'\n');print('Minimum stair headroom:',report['minimum_stair_clearance_m'],'Below3m:',len(report['below_3m']),'Crossings:',len(collisions))
