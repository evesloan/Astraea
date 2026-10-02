"""Read actual GLB end-cap triangles at declared staff-wall seams."""
from pathlib import Path
import json,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'qa/batch02'))
from geometry_checks import triangles,contains_xy
DATA={s:triangles(ROOT/'assets/staff_wall'/f'AST-STF-00{s}.glb') for s in [1,2,3]}
def cap(which,axis,position,role,depth_axis=1,depth_sign=1):
 t=np.concatenate([r['triangles'] for r in DATA[which] if r['role'].endswith(role)])
 t=t[(np.abs(t[:,:,axis]-position)<2e-7).all(1)]
 q=t[:,:,[depth_axis,2,axis]].copy();q[:,:,0]*=depth_sign;q[:,:,2]=0
 return q
rows=[]
for name,other in [('corner_A',cap(2,0,.3,'staff_rubber')),('corner_B',cap(2,1,-.3,'staff_rubber',0,-1)),('terminal',cap(3,0,0,'staff_rubber'))]:
 a=cap(1,0,1.2,'staff_rubber');b=other
 yy,zz=np.meshgrid(np.arange(-.120+.00025,-.044,.0005),np.arange(.765+.00025,.935,.0005));points=np.column_stack([yy.ravel(),zz.ravel()])
 aa=contains_xy(points,a);bb=contains_xy(points,b)
 rows.append({'join':'bay_to_'+name,'profile':'closed_rubber_bumper','sample_spacing_m':.0005,'covered_samples':int(aa.sum()),'mismatched_samples':int((aa!=bb).sum()),'nominal_seam_gap_m':0,'a_cap_triangles':len(a),'b_cap_triangles':len(b)})
for part,ys,zs in [('formed_cove',[-.077,0],[0,.182]),('folded_top',[-.046,0],[2.575,2.6])]:
 a=cap(1,0,1.2,'staff_zinc')
 yy,zz=np.meshgrid(np.arange(ys[0]+.00025,ys[1],.0005),np.arange(zs[0]+.00025,zs[1],.0005));points=np.column_stack([yy.ravel(),zz.ravel()]);aa=contains_xy(points,a)
 for name,b in [('corner_A',cap(2,0,.3,'staff_zinc')),('corner_B',cap(2,1,-.3,'staff_zinc',0,-1)),('terminal',cap(3,0,0,'staff_zinc'))]:
  bb=contains_xy(points,b)
  # Backing carriers are intentionally solid in corner/terminal; only require
  # original bay cap coverage, not identity of hidden construction.
  rows.append({'join':'bay_to_'+name,'profile':part,'sample_spacing_m':.0005,'source_covered_samples':int(aa.sum()),'source_uncovered_by_target':int((aa&~bb).sum()),'extra_target_samples':int((~aa&bb).sum()),'nominal_seam_gap_m':0})
result={'measurement':'Actual coplanar end-cap triangles at exported seams; 0.5 mm area grid in depth/height planes. Corner B remapped by declared 90 degree bay rotation. Profile end caps demonstrate closure; support/load claims are excluded.','results':rows}
(ROOT/'qa/batch03/independent_wall_joins.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
