from pathlib import Path
import json,math,itertools,collections
import numpy as np
R=Path(__file__).resolve().parents[3];P=R/'Game/quiet_court_finish_20261022';data=json.loads(Path('/tmp/quiet-court-geometry-comparison.json').read_text());offsets=list(itertools.product([-1,0,1],repeat=3));perms=np.array(list(itertools.permutations(range(3))));rows=[];global_max=0
for row in data:
 a=np.array(row['source']).reshape(-1,3,3);b=np.array(row['batched']).reshape(-1,3,3);assert a.shape==b.shape
 grid=collections.defaultdict(list)
 for i,c in enumerate(a.mean(axis=1)):grid[tuple(np.floor(c/.01).astype(int))].append(i)
 unmatched=set(range(len(a)));peak=0.;bad=0
 for tri,c in zip(b,b.mean(axis=1)):
  key=tuple(np.floor(c/.01).astype(int));found=None
  for off in offsets:
   for j in grid.get(tuple(key[k]+off[k]for k in range(3)),[]):
    if j not in unmatched:continue
    error=float(np.linalg.norm(a[j][perms]-tri,axis=2).max(axis=1).min())
    if error<=.001:found=j;peak=max(peak,error);break
   if found is not None:break
  if found is None:bad+=1
  else:unmatched.remove(found)
 ok=not bad and not unmatched and row['pose_equal'];rows.append(dict(name=row['name'],pass_check=ok,triangles=len(a),max_vertex_difference_m=peak,unmatched=bad));global_max=max(global_max,peak)
 if len(rows)%25==0:print('VERIFIED',len(rows),flush=True)
result=dict(status='PASS'if all(r['pass_check']for r in rows)else'FAIL',placements=rows,max_vertex_difference_m=global_max,tolerance_m=.001,method='One-to-one complete triangle matching, allowing vertex permutation and submillimetre import/world-transform float rounding; equal poses and triangle counts required. No triangle removal.',fps_acceptance=False)
(P/'evidence/BATCHING_GEOMETRY.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],'max_vertex_difference_m',global_max);assert result['status']=='PASS'
