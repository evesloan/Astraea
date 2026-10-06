import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.load(open(R/'contracts/surface_manifest.json'));parts=[]
for f in d['surfaces']:
 for i,p in enumerate(f['parts']):
  q=p['boundary_xz'];parts.append((f['deck'],f['region_id'],i,q,[min(v[0] for v in q),min(v[1] for v in q),max(v[0] for v in q),max(v[1] for v in q)]))
def sat(a,b):
 for q in [a,b]:
  for p,r in zip(q,q[1:]+q[:1]):
   ax,az=r[1]-p[1],p[0]-r[0];aa=[v[0]*ax+v[1]*az for v in a];bb=[v[0]*ax+v[1]*az for v in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-7:return False
 return True
hits=[];candidates=0
for i,(deck,region,ix,a,ab) in enumerate(parts):
 for nd,nr,ni,b,bb in parts[i+1:]:
  if deck!=nd or ab[0]>=bb[2]-1e-8 or bb[0]>=ab[2]-1e-8 or ab[1]>=bb[3]-1e-8 or bb[1]>=ab[3]-1e-8:continue
  candidates+=1
  if sat(a,b):hits.append(dict(a=[region,ix],b=[nr,ni]))
(R/'qa/surface_partition_screen.json').write_text(json.dumps(dict(named_surfaces=len(d['surfaces']),source_parts=len(parts),candidate_comparisons=candidates,positive_area_XZ_overlaps=hits,scope='All eight static named surface polygons, including sloped ramps and fixed thresholds; separate stair-flight assembly is inside explicit excluded stairwell. No compiler/engine claim.'),indent=2)+'\n');print('Surface parts',len(parts),'AABB candidates',candidates,'overlaps',len(hits))
