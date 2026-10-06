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
 if not o.get('ramp_part_kind'):continue
 vs=o['vertices_world']
 for f in o['faces'][:2]:
  foot=[vs[i] for i in f];p=[[v[0],v[2]] for v in foot];pb=bounds(p);a,b,c=foot
  det=(b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2]);fx=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/det;fz=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/det;fo=a[1]-fx*a[0]-fz*a[2];minfy=min(v[1] for v in foot)
  minimum=1e9;witness=None
  for name,q,qb,ax,az,off,maxy in triangles:
   if name==o['name'] or maxy<=minfy+1e-6 or not overlap(pb,qb):continue
   inter=intersect(p,q)
   if not inter or g.area(inter)<1e-8:continue
   values=[((ax-fx)*x+(az-fz)*z+off-fo,[x,fx*x+fz*z+fo,z]) for x,z in inter]
   lo,pt=min(values)
   if lo<=1e-6:
    if max(v[0] for v in values)>1e-5:collisions.append(dict(floor=o['name'],structure=name,minimum=lo))
    continue
   if lo<minimum:minimum=lo;witness=dict(overhead=name,point=pt)
  if minimum<1e8:witnesses.append(dict(floor=o['name'],face=f,minimum_clearance_m=minimum,witness=witness))
report=dict(status='Pure source triangle-plane intersections, not runtime acceptance',minimum_actual_ramp_ceiling_clearance=min(w['minimum_clearance_m'] for w in witnesses),below_3m=[w for w in witnesses if w['minimum_clearance_m']<3-1e-6],walking_top_crossing_candidates=collisions,witnesses=witnesses,limits='Only modelled ceilings; canonical roof remains separate. Guards are boundaries, not overhead surfaces. Source ramp/source floors are partitioned; no claim of NPC/capsule/cart certification.')
(R/'qa/ramp_headroom_screen.json').write_text(json.dumps(report,indent=2)+'\n');print('Minimum ramp source ceiling clearance:',report['minimum_actual_ramp_ceiling_clearance'],'Below3m:',len(report['below_3m']),'Crossings:',len(collisions))
