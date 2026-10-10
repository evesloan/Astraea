from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent
u={'__file__':str(W/'survey_d14.py')};exec((W/'survey_d14.py').read_text().replace("print(json.dumps({k:result[k]for k in ['collars','approach_existing_floor_overlap_m2','nearby_floor_owners','local_source_mesh_candidates']},indent=2))",''),u)
def clip(poly,axis,v,less):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]<=v if less else a[axis]>=v;ib=b[axis]<=v if less else b[axis]>=v
  if ia:out.append(a)
  if ia!=ib:
   t=(v-a[axis])/(b[axis]-a[axis]);out.append(a+(b-a)*t)
 return out
def exact_hit(t,lo,hi):
 mins=t.min(axis=1);maxs=t.max(axis=1);ts=t[np.all((maxs>lo+1e-5)&(mins<hi-1e-5),axis=1)];hits=0;area=0
 for tri in ts:
  poly=list(tri)
  for ax in range(3):
   if not poly:break
   poly=clip(poly,ax,lo[ax],False);poly=clip(poly,ax,hi[ax],True)if poly else[]
  a=sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0]))/2 for i in range(1,len(poly)-1))if len(poly)>2 else 0
  if a>1e-7:hits+=1;area+=a
 return hits,area
results=[]
for name,b in [('west_same_z_clean',[-63.34,-59.05,88.501,91.3,-494.8,-491.2]),('direct_east_clean',[-59.2,-46.05,88.501,91.3,-494.38,-491.62]),('direct_east_returns',[-59.2,-46.05,88.501,91.3,-488.38,-485.62]),('between_382_376',[-59.06,-45.95,88.501,91.3,-486.0,-482.6]),('south_street_end_missing_link',[-45.7,-42.3,88.501,91.3,-498.06,-493.50])]:
 lo=np.array([b[0],b[2],b[4]]);hi=np.array([b[1],b[3],b[5]]);hits=[]
 for n,t in u['allgeo'].items():
  c,area=exact_hit(t,lo,hi)
  if c:hits.append({'mesh':n,'clipped_triangles':c,'clipped_area_m2':round(area,8)})
 poly=u['box'](b[0],b[4],b[1],b[5]);results.append({'name':name,'bounds_xxyyzz':b,'actual_source_contacts':hits,'existing_floor_overlap_m2':poly.intersection(u['old']).area,'proposed_approach_overlap_m2':poly.intersection(u['request']).area,'missing_floor_m2':poly.difference(u['old'].union(u['request'])).area})
(W/'D14_BOUNDED_LOCAL_CANDIDATES.json').write_text(json.dumps({'schema':1,'scope':'five exact local boxes only, clipped actual source triangles; no route traversal','candidates':results},indent=2)+'\n');print(json.dumps(results,indent=2))
