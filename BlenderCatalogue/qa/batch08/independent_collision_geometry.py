"""Independent source-solid/convex-compound utilities, no author generator imports."""
import numpy as np
from scipy.spatial import ConvexHull

TOL=2e-7
class Hull:
 def __init__(self,points,record=None):
  self.points=np.asarray(points,float);self.hull=ConvexHull(self.points);self.planes=self.hull.equations;self.record=record or {}
  self.tris=self.points[self.hull.simplices]
  self.lo=self.points.min(axis=0);self.hi=self.points.max(axis=0)
 def inside(self,points,tol=TOL):
  points=np.asarray(points);return np.max(points@self.planes[:,:3].T+self.planes[:,3],axis=-1)<=tol
 def segment(self,a,b):
  a=np.asarray(a);b=np.asarray(b);d=b-a;p=self.planes
  v=p[:,:3]@a+p[:,3];w=p[:,:3]@d
  if np.any((np.abs(w)<1e-12)&(v>TOL)):return None
  lo=max(0,float(np.max(-v[w< -1e-12]/w[w< -1e-12])) if np.any(w< -1e-12) else 0)
  hi=min(1,float(np.min(-v[w>1e-12]/w[w>1e-12])) if np.any(w>1e-12) else 1)
  return [lo,hi] if lo<=hi+TOL else None
 def covers_triangles(self,tris):
  flat=np.asarray(tris).reshape(-1,3)
  return self.inside(flat).reshape(-1,3).all(axis=1)

def nearest_distances(points,tris,batch=64):
 """Exact Euclidean point-to-triangle distance, bounded-memory vectorized batches."""
 tris=np.asarray(tris);a,b,c=tris[:,0],tris[:,1],tris[:,2];ab=b-a;ac=c-a
 n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n);d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);den=d00*d11-d01*d01
 out=[]
 for start in range(0,len(points),batch):
  p=np.asarray(points[start:start+batch]);pa=p[:,None,:]-a
  projection=pa-n[None,:,:]*(np.einsum('pti,ti->pt',pa,n)/np.maximum(nn,1e-30))[...,None]
  d20=np.einsum('pti,ti->pt',projection,ab);d21=np.einsum('pti,ti->pt',projection,ac)
  u=(d11*d20-d01*d21)/np.maximum(den,1e-30);v=(d00*d21-d01*d20)/np.maximum(den,1e-30)
  ds=np.where((u>=0)&(v>=0)&(u+v<=1)&(nn>1e-20),np.sum((pa-projection)**2,axis=2),np.inf)
  for x,y in [(a,b),(b,c),(c,a)]:
   e=y-x;px=p[:,None,:]-x;t=np.clip(np.einsum('pti,ti->pt',px,e)/np.maximum(np.sum(e*e,axis=1),1e-30),0,1)
   ds=np.minimum(ds,np.sum((px-t[...,None]*e)**2,axis=2))
  out.extend(np.sqrt(np.min(ds,axis=1)))
 return np.asarray(out)

def inside_mesh(points,tris,batch=64):
 """Generalized winding number on each closed named solid; robust at shared edges."""
 points=np.asarray(points);tri=np.asarray(tris);out=[]
 for start in range(0,len(points),batch):
  p=points[start:start+batch];a=tri[None,:,0]-p[:,None,:];b=tri[None,:,1]-p[:,None,:];c=tri[None,:,2]-p[:,None,:]
  la=np.linalg.norm(a,axis=2);lb=np.linalg.norm(b,axis=2);lc=np.linalg.norm(c,axis=2)
  num=np.einsum('pti,pti->pt',a,np.cross(b,c));den=la*lb*lc+np.einsum('pti,pti->pt',a,b)*lc+np.einsum('pti,pti->pt',b,c)*la+np.einsum('pti,pti->pt',c,a)*lb
  w=np.sum(2*np.arctan2(num,den),axis=1)/(4*np.pi);out.extend(np.abs(w)>.5)
 return np.asarray(out)

def sample_triangles(tris,spacing=.04):
 """Barycentric surface grid; grid edge <= spacing, not just vertices or rays."""
 points=[];maximum_step=0
 for t in tris:
  longest=max(np.linalg.norm(t[i]-t[j]) for i,j in [(0,1),(1,2),(2,0)])
  n=max(1,int(np.ceil(longest/spacing)));maximum_step=max(maximum_step,longest/n)
  for i in range(n+1):
   for j in range(n+1-i):points.append(t[0]+(t[1]-t[0])*i/n+(t[2]-t[0])*j/n)
 return np.unique(np.round(points,9),axis=0),maximum_step

def segment_triangles(a,b,tris,eps=1e-10):
 a=np.asarray(a);b=np.asarray(b);d=b-a;tr=np.asarray(tris)
 # Axis-aligned segment/triangle broad-phase is conservative.
 mask=((tr.max(axis=1)>=np.minimum(a,b)-eps)&(tr.min(axis=1)<=np.maximum(a,b)+eps)).all(axis=1);t=tr[mask]
 if not len(t):return []
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);good=np.abs(det)>eps
 f=np.zeros(len(t));f[good]=1/det[good];s=a-t[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*(q@d);r=f*np.einsum('ij,ij->i',e2,q)
 good&=(u>=-eps)&(v>=-eps)&(u+v<=1+eps)&(r>=-eps)&(r<=1+eps)
 return sorted(set(np.round(r[good],10)))

def polygon_area(poly):
 if len(poly)<3:return 0.
 p=np.asarray(poly);return float(np.linalg.norm(np.sum(np.cross(p,np.roll(p,-1,axis=0)),axis=0))*.5)

def clip_polygon(poly,plane,keep_inside=True,tol=2e-7):
 """3D planar Sutherland-Hodgman clipping against a convex halfspace."""
 out=[];normal=plane[:3];offset=plane[3]-tol
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  va=float(a@normal+offset);vb=float(b@normal+offset);ia=va<=0 if keep_inside else va>=0;ib=vb<=0 if keep_inside else vb>=0
  if ia:out.append(a)
  if ia!=ib:
   frac=va/(va-vb);out.append(a+frac*(b-a))
 return np.asarray(out)

def triangle_uncovered_area(triangle,hulls):
 """Subtract convex hulls from a source triangle; remaining polygon areas expose gaps.

Each hull subtraction emits disjoint outside polygons while clipping the inside
remainder successively against every face. This checks continuous union coverage,
including triangles spanning intentional convex decomposition boundaries.
"""
 residual=[np.asarray(triangle)]
 for h in hulls:
  nxt=[]
  for polygon in residual:
   if ((polygon.max(axis=0)<h.lo-2e-7)|(polygon.min(axis=0)>h.hi+2e-7)).any():nxt.append(polygon);continue
   inner=polygon
   for plane in h.planes:
    if len(inner)<3:break
    outside=clip_polygon(inner,plane,False)
    if len(outside)>=3 and polygon_area(outside)>1e-13:nxt.append(outside)
    inner=clip_polygon(inner,plane,True)
   # Anything inside every hull halfspace is covered and therefore omitted.
  residual=nxt
  if not residual:break
 return sum(polygon_area(p) for p in residual)
