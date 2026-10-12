"""Boundary-following fitted construction with rigid retained furniture frames.
Profile coordinates author new fitted shapes; they never shear an imported asset.
"""
import math
class PremiumFrame:
 def __init__(self,polygon,floor=102):
  self.poly=polygon;self.floor=floor;self.star=min(x[0] for x in polygon)>0
  self.out=1 if self.star else -1;self.vsign=-1 if self.star else 1
  self.zmin=min(x[1] for x in polygon);self.zmax=max(x[1] for x in polygon)
  self.start=self.zmax if self.star else self.zmin;self.length=self.zmax-self.zmin
 def limits(self,v):
  z=self.start+self.vsign*max(0,min(self.length,v));values=[]
  for a,b in zip(self.poly,self.poly[1:]+self.poly[:1]):
   if abs(a[1]-b[1])<1e-8:
    if abs(z-a[1])<1e-7:values.extend([a[0],b[0]])
   elif min(a[1],b[1])-1e-7<=z<=max(a[1],b[1])+1e-7:
    t=(z-a[1])/(b[1]-a[1]);values.append(a[0]+t*(b[0]-a[0]))
  assert len(values)>=2,(v,z,values)
  return (min(values),max(values)) if self.star else (max(values),min(values))
 def inner(self,v):return self.limits(v)[0]
 def depth(self,v):return abs(self.limits(v)[1]-self.limits(v)[0])
 def world(self,u,v,h=0):return [self.inner(v)+self.out*u,self.floor+h,self.start+self.vsign*v]
 def blender(self,u,v,h=0):
  x,y,z=self.world(u,v,h);return(x,-z,y)
 def inverse(self,p):
  v=(-p[1]-self.start)/self.vsign;return((p[0]-self.inner(v))/self.out,v,p[2]-self.floor)
 def angle(self,v):
  a=max(.001,v-.05);b=min(self.length-.001,v+.05);s=(self.inner(b)-self.inner(a))/(b-a)
  return (0 if self.star else math.pi)+(-1 if self.star else 1)*math.atan(s)
 def rigid(self,u,v,du,dv,h=0):
  x,y,z=self.blender(u,v,h);a=self.angle(v);return(x+du*math.cos(a)-dv*math.sin(a),y+du*math.sin(a)+dv*math.cos(a),z)
