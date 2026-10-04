"""Advisory actual native axial same-facing/cross-material coplanar area screen."""
from pathlib import Path
import runpy,numpy as np,json,itertools
ROOT=Path(__file__).resolve().parents[1];g=runpy.run_path(str(ROOT/'qa/check_native.py'));roles=g['roles'];groups={}
for role,triangles in roles.items():
 for i,t in enumerate(triangles):
  n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n)
  if length<1e-14:continue
  n/=length;axis=int(np.argmax(abs(n)))
  if abs(n[axis])<.999999:continue
  plane=float(t[:,axis].mean());axes=[k for k in range(3)if k!=axis];key=(axis,1 if n[axis]>0 else -1,round(plane,6));groups.setdefault(key,[]).append((role,i,t[:,axes]))
def clip(subject,clipper):
 poly=[np.array(p)for p in subject];orientation=np.sign(np.cross(clipper[1]-clipper[0],clipper[2]-clipper[0]))
 for a,b in zip(clipper,np.roll(clipper,-1,axis=0)):
  out=[]
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=orientation*np.cross(b-a,p-a);dq=orientation*np.cross(b-a,q-a);ip=dp>=-1e-12;iq=dq>=-1e-12
   if ip:out.append(p)
   if ip!=iq:out.append(p+(q-p)*dp/(dp-dq))
  poly=out
  if len(poly)<3:return 0
 return abs(sum(np.cross(a,b)for a,b in zip(poly,poly[1:]+poly[:1])))/2
candidates=[]
for key,rows in groups.items():
 for a,b in itertools.combinations(rows,2):
  if a[0]==b[0]:continue
  if np.any(a[2].max(0)<b[2].min(0))or np.any(b[2].max(0)<a[2].min(0)):continue
  area=clip(a[2],b[2])
  if area>1e-9:candidates.append({'native_axis':key[0],'outward_sign':key[1],'plane_m':key[2],'roles':[a[0],b[0]],'triangle_indices':[a[1],b[1]],'overlap_area_m2':float(area)})
result={'scope':'Axial same-facing finite triangle screen; opposite-facing butt contacts excluded. Sloped coplanarity and visibility are not proved by this advisory screen.','candidates':candidates,'candidate_area_m2':sum(r['overlap_area_m2']for r in candidates),'glb_sha256':g['result']['glb_sha256']};(ROOT/'qa/finish_plane_screen.json').write_text(json.dumps(result,indent=2)+'\n');print('FINISH_PLANE',result['candidate_area_m2'],candidates)
