"""Exact finite segment-to-triangle distance for a bounded geometric capsule passage."""
import numpy as np
from independent_collision_adapters import Hull
from independent_collision_geometry import nearest_distances,segment_triangles

def segment_segment_distances(a,b,c,d):
 a=np.asarray(a);b=np.asarray(b);c=np.asarray(c);d=np.asarray(d);u=b-a;v=d-c;w=a-c
 def pseg(p,x,y):
  e=y-x;t=np.clip(np.sum((p-x)*e,axis=-1)/np.maximum(np.sum(e*e,axis=-1),1e-30),0,1);return np.linalg.norm(p-(x+t[...,None]*e),axis=-1)
 minimum=np.minimum.reduce([pseg(a,c,d),pseg(b,c,d),pseg(c,a,b),pseg(d,a,b)])
 aa=float(u@u);bb=v@u;cc=np.sum(v*v,axis=1);dd=w@u;ee=np.sum(v*w,axis=1);den=aa*cc-bb*bb
 s=(bb*ee-cc*dd)/np.where(abs(den)>1e-20,den,1);t=(aa*ee-bb*dd)/np.where(abs(den)>1e-20,den,1);valid=(abs(den)>1e-20)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
 dist=np.linalg.norm(w+s[:,None]*u-t[:,None]*v,axis=1);return np.minimum(minimum,np.where(valid,dist,np.inf))

def segment_triangle_distance(a,b,tris):
 t=np.asarray(tris)
 if segment_triangles(a,b,t):return 0.
 ends=nearest_distances([a,b],t);minimum=float(ends.min())
 for i,j in [(0,1),(1,2),(2,0)]:minimum=min(minimum,float(segment_segment_distances(a,b,t[:,i],t[:,j]).min()))
 return minimum

if __name__=='__main__':
 tri=np.array([[[0,0,0],[1,0,0],[0,1,0]]],float)
 assert abs(segment_triangle_distance([.1,.1,1],[.2,.2,1],tri)-1)<1e-9
 assert segment_triangle_distance([.1,.1,1],[.1,.1,-1],tri)==0
 assert abs(segment_triangle_distance([2,0,0],[2,0,1],tri)-1)<1e-9
 print('Segment-triangle capsule controls passed')
