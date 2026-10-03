"""Exact finite convex-hull/AABB feasibility for proposed voids, literal subset audit.
SciPy Qhull builds declared convex proposals; linprog tests entire volume intersection.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1];path=BASE/'collision_proposals.json';data=json.loads(path.read_text());rows=[]
for ident,d in data.items():
 shapes=d['precise_reference'];body=d['optional_body_candidate']['retained_shape_names'];name_map={r['name']:r for r in shapes};checks=[];equations={}
 for r in shapes:
  a=np.array(r['points_source_m']);eq=ConvexHull(a).equations;equations[r['name']]=eq
 for v in d['preserved_voids']:
  bounds=[(v['min_source_m'][i]+1e-6,v['max_source_m'][i]-1e-6)for i in range(3)];hits=[]
  for name,eq in equations.items():
   result=linprog(np.zeros(3),A_ub=eq[:,:3],b_ub=-eq[:,3],bounds=bounds,method='highs')
   if result.success:hits.append({'shape':name,'witness':result.x.tolist(),'body_retained':name in body})
  checks.append({'name':v['name'],'all_precise_reference_hulls_clear':not hits,'optional_body_hulls_clear':not any(h['body_retained']for h in hits),'hits':hits})
 # Positive obstruction control places a 20 mm cube at an actual retained part centroid.
 retained=name_map[body[0]];centre=np.array(retained['points_source_m']).mean(0);eq=equations[retained['name']];r=linprog(np.zeros(3),A_ub=eq[:,:3],b_ub=-eq[:,3],bounds=[(x-.01,x+.01)for x in centre],method='highs')
 rows.append({'id':ident,'precise_reference_count':len(shapes),'optional_body_count':len(body),'literal_subset':set(body).issubset(name_map),'new_enclosing_hull_count':0,'actual_voids':checks,'positive_control_detects_retained_solid':r.success,'maximum_edge_easing_allowance_m':max(p['edge_easing_max_m']for p in shapes),'passes':all(c['all_precise_reference_hulls_clear']and c['optional_body_hulls_clear']for c in checks)and r.success})
out={'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'ConvexHull halfspaces and HiGHS complete convex hull/axis-aligned-box feasibility; 1 micrometre box inset excludes boundary-only contact','results':rows,'all_passed':all(r['passes']for r in rows),'limits':'Geometric proposals only; no rigid-body stability, load, motion, engine physics or target-PC performance'};(BASE/'qa/collision_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
