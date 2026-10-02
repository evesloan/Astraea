"""Exact triangle/box SAT plus convex feasibility for declared empty source boxes."""
import numpy as np
from scipy.optimize import linprog

def triangle_box_mask(tris,lo,hi,tol=1e-10):
 tris=np.asarray(tris,float);lo=np.asarray(lo,float);hi=np.asarray(hi,float);centre=(lo+hi)/2;half=(hi-lo)/2;t=tris-centre
 mask=((tris.max(axis=1)>=lo-tol)&(tris.min(axis=1)<=hi+tol)).all(axis=1)
 indices=np.where(mask)[0]
 if not len(indices):return mask
 q=t[indices];edges=q[:,[1,2,0]]-q[:,[0,1,2]]
 axes=[np.cross(edges[:,0],edges[:,1])]
 for k in range(3):
  unit=np.zeros(3);unit[k]=1
  axes.extend(np.cross(edges[:,j],unit)for j in range(3))
 alive=np.ones(len(q),bool)
 for a in axes:
  projections=np.einsum('tvi,ti->tv',q,a);radius=np.abs(a)@half
  alive&=(projections.min(axis=1)<=radius+tol)&(projections.max(axis=1)>=-radius-tol)
 mask[indices]=alive;return mask

def hull_box_overlap(hull,lo,hi):
 lo=np.asarray(lo);hi=np.asarray(hi)
 if ((hull.hi<lo)|(hull.lo>hi)).any():return {'overlaps':False}
 res=linprog(np.zeros(3),A_ub=hull.planes[:,:3],b_ub=-hull.planes[:,3],bounds=list(zip(lo,hi)),method='highs')
 return {'overlaps':bool(res.success),'point_source_m':res.x.tolist() if res.success else None,'solver_status':res.message}
