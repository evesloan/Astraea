"""Read-only shape adapters. Concave extruded polygons are never convexified whole."""
from pathlib import Path
import sys,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull

def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def triangulate(poly):
 p=np.asarray(poly,float);ids=list(range(len(p)));area=sum(cross(p[i],p[(i+1)%len(p)])for i in range(len(p)))/2
 assert abs(area)>1e-12;sign=np.sign(area);ts=[]
 while len(ids)>3:
  found=False
  for k in range(len(ids)):
   a,b,c=ids[k-1],ids[k],ids[(k+1)%len(ids)]
   if sign*cross(p[b]-p[a],p[c]-p[b])<=1e-12:continue
   other=[i for i in ids if i not in [a,b,c]]
   def inside(i):return min(sign*cross(p[b]-p[a],p[i]-p[a]),sign*cross(p[c]-p[b],p[i]-p[b]),sign*cross(p[a]-p[c],p[i]-p[c]))>=-1e-12
   if any(inside(i)for i in other):continue
   ts.append(p[[a,b,c]]);ids.pop(k);found=True;break
  assert found,'Profile is not a simple triangulatable polygon'
 ts.append(p[ids]);assert abs(sum(abs(cross(t[1]-t[0],t[2]-t[0]))/2 for t in ts)-abs(area))<1e-10
 return ts

def expand(record,gather=0):
 typ=record['type']
 if typ in ['visual_detail_exclusion','flexible_surface_no_independent_collision']:return []
 if typ=='box':return [Hull(list(itertools.product(*zip(record['min_source_m'],record['max_source_m']))),record)]
 if typ=='convex_hull':return [Hull(record['vertices_source_m'],record)]
 if typ=='capsule':
  a=np.asarray(record['a_source_m']);b=np.asarray(record['b_source_m']);r=record['radius_m'];n=16;rr=r/np.cos(np.pi/n);vs=[]
  for c in [a,b]:
   for phi in np.arange(n+1)*np.pi/n:
    for theta in np.arange(n*2)*np.pi/n:vs.append(c+rr*np.array([np.sin(phi)*np.cos(theta),np.sin(phi)*np.sin(theta),np.cos(phi)]))
  return [Hull(np.unique(np.round(vs,12),axis=0),{**record,'review_approximation':'Conservative spherical-grid hull, radius inflated by sec(pi/16); sphere grid angular coverage is below pi/16','review_radial_inflation_bound_m':rr-r})]
 if typ=='per_pose_thin_convex_pleat_panels':
  f=record['parameter_formula'];n=record['segments'];span=2.16-1.8*gather;lead=.02+1.8*gather;length=f['segment_developed_length_m'];amp=np.sqrt(length**2-(span/n)**2)/2;thick=record['half_thickness_m'];out=[]
  for i in range(n):
   a=np.array([.68+(-1 if i%2==0 else 1)*amp,lead+span*i/n,.28]);b=np.array([.68+(-1 if (i+1)%2==0 else 1)*amp,lead+span*(i+1)/n,.28]);d=b-a;normal=np.array([d[1],-d[0],0])/np.linalg.norm(d);vs=[p+z*np.array([0,0,1])+sign*thick*normal for p in [a,b]for z in [0,f['fabric_height_m']]for sign in [-1,1]];out.append(Hull(vs,{**record,'review_subshape_index':i,'review_gather':gather}))
  return out
 if typ=='convex_hull_points':return [Hull(record['points_source_m'],record)]
 if typ=='aabb':return [Hull(list(itertools.product(*zip(record['min_m'],record['max_m']))),record)]
 axis='xyz'.index(record['axis']);other=[k for k in range(3)if k!=axis]
 if typ=='extruded_polygon':
  out=[]
  for n,t in enumerate(triangulate(record['profile_2d_m'])):
   vs=[]
   for v in record['interval_m']:
    for q in t:
     p=np.zeros(3);p[axis]=v;p[other]=q;vs.append(p)
   out.append(Hull(vs,{**record,'review_subshape_index':n}))
  return out
 if typ=='cylinder':
  c=np.asarray(record['center_m']);r=record['radius_m'];depth=record['depth_m'];n=64;vs=[]
  # Circumscribed64-gon is conservative by at most0.0603mm for a50mm-radius wheel.
  for x in [-depth/2,depth/2]:
   for theta in np.arange(n)*2*np.pi/n:
    p=c.copy();p[axis]+=x;p[other]+=r/np.cos(np.pi/n)*np.array([np.cos(theta),np.sin(theta)]);vs.append(p)
  return [Hull(vs,{**record,'review_cylinder_approximation':'circumscribed64-gon; conservative radial overreach r*(sec(pi/64)-1)'})]
 raise ValueError(typ)
