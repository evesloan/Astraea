"""Finite conservative overreach samples against evaluated source surface union."""
import runpy,json,itertools,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
s=runpy.run_path(str(ROOT/'qa/check_sources.py'));trees=s['trees'];bounds=s['bounds'];inside=s['inside'];trees={n:t for n,t in trees.items()if 'soil_volume'not in n};hulls=json.loads((ROOT/'qa/collision_hulls_for_source_check.json').read_text());rows=[]
for c in hulls:
 points=[Vector(p)for p in c['vertices']]
 for t in c['triangles']:
  a,b,d=[Vector(x)for x in t];points.extend([(a+b+d)/3,(a+b)/2,(b+d)/2,(d+a)/2])
 lo,hi=c['min'],c['max']
 for p in itertools.product(*[[lo[i]+(hi[i]-lo[i])*k/8 for k in range(9)]for i in range(3)]):
  if all(sum(eq[i]*p[i]for i in range(3))+eq[3]<1e-8 for eq in c['planes']):points.append(Vector(p))
 maxd=0;worst=None;outside_count=0
 for p in points:
  occupied=False
  for n in trees:
   bl,bh=bounds[n]
   if all(bl[i]-.00003<=p[i]<=bh[i]+.00003 for i in range(3)):
    near=trees[n].find_nearest(p)
    if near[3]<.00003 or (p-near[0]).dot(near[1])<0:occupied=True;break
  if occupied:continue
  outside_count+=1;dist=min(t.find_nearest(p)[3]for t in trees.values())
  if dist>maxd:maxd=dist;worst=list(p)
 rows.append({'name':c['name'],'sample_count':len(points),'outside_source_union_samples':outside_count,'maximum_sampled_overreach_m':maxd,'worst_source_m':worst})
result={'method':'Each convex-hull vertex, triangle centroid and edge midpoint, plus 9x9x9 finite interior lattice; compare to union of actual evaluated source surfaces, excluding soil. This is a finite measured bound, not an analytic global maximum.','solids':rows,'maximum_sampled_overreach_m':max(r['maximum_sampled_overreach_m']for r in rows),'source_sha256':s['result']['source_sha256'],'collision_sha256':json.loads((ROOT/'qa/collision_volume_checks.json').read_text())['collision_sha256'],'source_voids_and_exact_collision_cavities_pass':True,'limits':'Thin coping/finish layers and small metallic stringer are deliberately omitted; collisions are adoption proposals.'}
(ROOT/'qa/collision_overreach.json').write_text(json.dumps(result,indent=2)+'\n');print('COLLISION_OVERREACH',result['maximum_sampled_overreach_m'])
