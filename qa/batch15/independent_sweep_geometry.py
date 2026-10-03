"""Continuous straight-line triangle sweep; no finite-pose clearance claim."""
import numpy as np

def triangle_sweep_contact(moving, fixed, delta, tolerance=1e-9):
 """Exact separating-axis time interval for two translated, nonrotating triangles.
 Includes coplanar in-plane edge normals. Degenerate triangles are unsupported.
 A result is a surface contact, not automatically material interpenetration.
 """
 a=np.asarray(moving,float);b=np.asarray(fixed,float);d=np.asarray(delta,float)
 ae=a[[1,2,0]]-a;be=b[[1,2,0]]-b
 an=np.cross(ae[0],ae[1]);bn=np.cross(be[0],be[1])
 axes=[an,bn]+[np.cross(x,y)for x in ae for y in be]+[np.cross(an,x)for x in ae]+[np.cross(bn,x)for x in be]
 axes=np.asarray([x/np.linalg.norm(x)for x in axes if np.linalg.norm(x)>1e-12])
 if not len(axes):raise ValueError('Degenerate triangle')
 ap=a@axes.T;bp=b@axes.T;velocity=axes@d
 low=bp.min(0)-ap.max(0)-tolerance;high=bp.max(0)-ap.min(0)+tolerance
 stationary=np.abs(velocity)<1e-12
 if np.any(stationary&((low>0)|(high<0))):return None
 lo=0.;hi=1.
 for l,h,v in zip(low[~stationary],high[~stationary],velocity[~stationary]):
  t1=l/v;t2=h/v;lo=max(lo,min(t1,t2));hi=min(hi,max(t1,t2))
  if lo>hi:return None
 return [float(lo),float(hi)]

def sweep_contacts(moving, fixed, delta, moving_labels=None, fixed_labels=None, tolerance=1e-8):
 """Full triangle broad phase followed by continuous SAT, not sampled poses."""
 moving=np.asarray(moving);fixed=np.asarray(fixed);delta=np.asarray(delta)
 ml=np.minimum(moving.min(1),moving.min(1)+delta);mh=np.maximum(moving.max(1),moving.max(1)+delta);fl=fixed.min(1);fh=fixed.max(1)
 rows=[]
 for i,t in enumerate(moving):
  candidates=np.where(((ml[i]<=fh+tolerance)&(mh[i]>=fl-tolerance)).all(1))[0]
  for j in candidates:
   hit=triangle_sweep_contact(t,fixed[j],delta,tolerance)
   if hit is not None:
    row={'moving_triangle':i,'fixed_triangle':int(j),'translation_fraction_interval':hit}
    if moving_labels is not None:row['moving_part']=str(moving_labels[i])
    if fixed_labels is not None:row['fixed_part']=str(fixed_labels[j])
    rows.append(row)
 return rows

if __name__=='__main__':
 a=np.array([[0,0,0],[1,0,0],[0,1,0]],float)
 assert triangle_sweep_contact(a,a+[0,0,1],[0,0,2]) is not None
 assert triangle_sweep_contact(a,a+[0,0,1],[1,0,0]) is None
 assert triangle_sweep_contact(a,a+[3,0,0],[4,0,0]) is not None
 assert triangle_sweep_contact(a,a+[3,0,0],[0,0,1]) is None
 print('Continuous SAT controls passed')
