from pathlib import Path
import json,itertools,numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
D=Path(__file__).resolve().parent;out=[]
for row in json.load(open(D/'PATCH_TRIANGLES.json')):
 groups=[]
 for side in ['before','after']:
  for tri in row[side]:
   v=np.array([q['p']for q in tri]);n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n)
   if length<1e-10:continue
   n=n/length
   if n[np.argmax(abs(n))]<0:n=-n
   d=n@v[0];g=next((g for g in groups if abs(g['n']@n)>.999 and max(abs(v@g['n']-g['d']))<1e-4),None)
   if g is None:
    assert side=='before',(row['name'],'new plane',n,d)
    u=(v[1]-v[0]);u=u/np.linalg.norm(u);w=np.cross(n,u);g={'n':n,'d':d,'u':u,'w':w,'before':[],'after':[]};groups.append(g)
   g[side].append(Polygon([(q@g['u'],q@g['w'])for q in v]))
 err=0
 for g in groups:
  old=unary_union(g['before']);actual=unary_union(g['after']);lo=row['cut_min'];hi=row['cut_max'];corners=[np.array(q)for q in itertools.product(*zip(lo,hi))];pts=[]
  for a,b in itertools.combinations(corners,2):
   if sum(abs(a-b)>1e-9)!=1:continue
   da=a@g['n']-g['d'];db=b@g['n']-g['d']
   for v,dv in [(a,da),(b,db)]:
    if abs(dv)<1e-8:pts.append((v@g['u'],v@g['w']))
   if da*db<0:
    v=a+(b-a)*da/(da-db);pts.append((v@g['u'],v@g['w']))
  cut=MultiPoint(pts).convex_hull if pts else Polygon();expected=old.difference(cut);delta=expected.symmetric_difference(actual).area;assert delta<.0002,(row['name'],delta);err+=delta
 out.append({'name':row['name'],'source_planes':len(groups),'surface_difference_m2':err})
(D/'PATCH_VERIFICATION.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_PROJECTED_PLANE_SUBTRACTION','rows':out,'method':'Each retained source plane projected to 2D; cut is independent intersection of plane with twelve box edges; polygon union/difference compared to all successor triangles.','scope':'Geometry only; no engineering or art acceptance'},indent=2)+'\n');print(out)
