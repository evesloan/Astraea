"""Compare actual final overhead GLB cap vertices after declared placement."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.spatial.distance import cdist
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa/batch02'))
from geometry_checks import triangles
A=ROOT/'assets/staff_overhead/exports/AST-STF-004.glb';B=A.with_name('AST-STF-005.glb')
a={r['role']:r['triangles'].reshape(-1,3) for r in triangles(A)};b={r['role']:r['triangles'].reshape(-1,3) for r in triangles(B)};out=[]
for role in sorted(set(a)|set(b)):
 p=a.get(role,np.zeros((0,3)));q=b.get(role,np.zeros((0,3)))
 for join in ['straight_exit_to_turn_entry','turn_exit_to_rotated_straight_entry']:
  if join.startswith('straight'):
   u=np.unique(p[np.abs(p[:,0]-1.199)<1e-7][:,1:],axis=0);v=np.unique(q[np.abs(q[:,0]-.001)<1e-7][:,1:],axis=0)
  else:
   u=np.unique(q[np.abs(q[:,1]-.599)<1e-7][:,[0,2]],axis=0);u[:,0]=.6-u[:,0];v=np.unique(p[np.abs(p[:,0]-.001)<1e-7][:,1:],axis=0)
  if len(u)==len(v)==0:continue
  dist=cdist(u,v);h=float(max(dist.min(0).max(),dist.min(1).max())) if len(u) and len(v) else None
  out.append({'join':join,'material':role,'source_cap_vertices':len(u),'target_cap_vertices':len(v),'profile_hausdorff_m':h,'body_gap_m':.002,'passes':h is not None and h<1e-6})
report={'export_hashes':{A.name:hashlib.sha256(A.read_bytes()).hexdigest(),B.name:hashlib.sha256(B.read_bytes()).hexdigest()},'checks':out,'passes':all(r['passes'] for r in out),'scope':'Actual capped service/rail end profiles match in transformed depth-height space. Two millimetre body seam is intentionally spanned by external exit collars and hollow pipe sleeves; not utility, structural, or engine acceptance.'}
(ROOT/'qa/batch03/independent_overhead_joins.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
