"""Measure finite bore/pin/cap capture from actual evaluated geometry, independent of declared radii."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
BASE=Path(__file__).resolve().parents[1];data=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text())
def maxrad(v,p):return float(np.linalg.norm((v-p)[:,1:],axis=1).max())
def minrad(v,p):
 q=np.unique((v-p)[:,1:],axis=0);h=ConvexHull(q);q=q[h.vertices]
 if np.max(h.equations[:,:2]@np.zeros(2)+h.equations[:,2])<=0:return 0.
 ds=[]
 for i in range(len(q)):
  a=q[i];b=q[(i+1)%len(q)];d=b-a;t=np.clip(-a@d/(d@d),0,1);ds.append(np.linalg.norm(a+t*d))
 return float(min(ds))
rows=[]
for ident,pivot,key,pin_key,cap_key,obstacle in [('AST-CUL-003',[0,.1,.44],'moving_bearing_sector','retained_hinge_pin','inner_pin_retainer','folding_timber_pan'),('AST-CUL-004',[0,.115,1.54],'aim_bearing_sector','retained_aim_pin','aim_pin_inner_retainer','formed_light_hood')]:
 rec=json.loads((BASE/f'{ident}.manifest.json').read_text());p=np.array(pivot);parts={r['name']:r for r in data[ident]['parts']}
 for side in('left','right'):
  sectors=[r for n,r in parts.items()if n.startswith(side+'_'+key)];innerplanes=[];innervertices=[]
  for r in sectors:
   v=np.array(r['vertices']);ts=v[np.array(r['triangles'])];ns=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);ns/=np.linalg.norm(ns,axis=1)[:,None]
   for n,t in zip(ns,ts):
    # Bore-facing radial planes exclude both axial caps and radial sector joining faces, which pass through the axis.
    signed=n@(p-t[0])
    if abs(n[0])<1e-5 and signed>.005:
     innerplanes.append(signed);innervertices.extend(t)
  pin=np.array(parts[side+'_'+pin_key]['vertices']);cap=np.array(parts[side+'_'+cap_key]['vertices']);obs=np.array(parts[obstacle]['vertices']);bmin=float(min(innerplanes));bmax=maxrad(np.array(innervertices),p);pr=maxrad(pin,p);capmin=minrad(cap,p) # This volume contains the axis, so use lateral halfspaces for true perimeter inradius below.
  cap2=np.unique((cap-p)[:,1:],axis=0);ch=ConvexHull(cap2);capin=float(min(-ch.equations[:,2]));capr=maxrad(cap,p);obsmin=minrad(obs,p)
  # A full 1mm artificial pin offset in radial Y defeats the claimed margin, positive control only.
  shifted=pin+np.array([0,.001,0]);shiftedr=maxrad(shifted,p)
  row={'catalogue_id':ident,'side':side,'actual_convex_sleeve_sectors':len(sectors),'actual_bore_inradius_m':bmin,'actual_bore_circumradius_m':bmax,'actual_pin_circumradius_m':pr,'full_rotation_guaranteed_radial_clearance_m':bmin-pr,'actual_retainer_inradius_m':capin,'guaranteed_radial_retention_overlap_m':capin-bmax,'retainer_circumradius_m':capr,'obstacle_minimum_axis_radius_m':obsmin,'full_rotation_cap_obstacle_clearance_m':obsmin-capr,'one_mm_pin_offset_negative_control_detected':shiftedr>bmin,'source_sha256':rec['source_sha256'],'scope':'Finite polygonal geometry and exact coaxial X-axis rotations. Radial clearance and axial end-face capture are geometric proposals; no load, wear, tolerance-stack or operating mechanism certification','passes':bmin>pr and capin>bmax and obsmin>capr and shiftedr>bmin};rows.append(row)
out={'results':rows,'all_passed':all(r['passes']for r in rows)};(BASE/'qa/retained_bearing_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
