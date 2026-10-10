import math
def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))/2 if len(poly)>2 else 0
def clip(poly,axis,value,gt):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  aa=(a[axis]>=value-1e-10) if gt else (a[axis]<=value+1e-10);bb=(b[axis]>=value-1e-10) if gt else (b[axis]<=value+1e-10)
  if aa:out.append(a)
  if aa!=bb:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
 return out
