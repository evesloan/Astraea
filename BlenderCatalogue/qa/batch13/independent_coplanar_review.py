"""Advisory screen for different-material, same-facing axial faces sharing positive area."""
from pathlib import Path
import json,hashlib,collections,itertools,sys,numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"batch08"));from independent_collision_geometry import segment_triangles,inside_mesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13'
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def area(p):return .5*abs(sum(cross2(b-a,c-a)for a,b,c in [(p[0],p[i],p[i+1])for i in range(1,len(p)-1)])) if len(p)>=3 else 0.
def clip(poly,triangle):
 sign=np.sign(cross2(triangle[1]-triangle[0],triangle[2]-triangle[0]));result=poly
 for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
  old=result;result=[]
  if len(old)<3:return []
  for p,q in zip(old,np.roll(old,-1,axis=0)):
   u=sign*cross2(b-a,p-a);v=sign*cross2(b-a,q-a)
   if u>=-1e-10:result.append(p)
   if (u>=-1e-10)!=(v>=-1e-10):result.append(p+u/(u-v)*(q-p))
 return np.asarray(result)
rows=[]
for p in sorted(OUT.glob('independent_source_AST-BOT-010.json')):
 s=json.loads(p.read_text());a=np.load(ROOT/s['geometry_cache']);tris=a['triangles'];names=a['object_names'];roles={x['name']:x.get('materials',[])for x in s['objects']};groups=collections.defaultdict(list);acc=collections.defaultdict(float);examples={}
 cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);norm=cross/np.maximum(np.linalg.norm(cross,axis=1),1e-20)[:,None]
 for i,(t,n)in enumerate(zip(tris,norm)):
  axis=int(np.argmax(abs(n)))
  if abs(n[axis])<.999999 or np.ptp(t[:,axis])>1e-6:continue
  groups[(axis,int(np.sign(n[axis])),round(float(t[:,axis].mean()),5))].append(i)
 for (axis,sign,plane),ids in groups.items():
  dims=[x for x in range(3)if x!=axis];ts=tris[ids][:,:,dims];lo=ts.min(axis=1);hi=ts.max(axis=1)
  for k,i in enumerate(ids):
   for l in np.where(((lo[k]<hi[k+1:]-1e-8)&(hi[k]>lo[k+1:]+1e-8)).all(axis=1))[0]+k+1:
    j=ids[l]
    if names[i]==names[j]or roles[names[i]]==roles[names[j]]:continue
    poly=clip(ts[k],ts[l]);overlap=area(poly)
    if overlap>1e-7:
     key=(str(min(names[i],names[j])),str(max(names[i],names[j])),axis,sign,plane);acc[key]+=float(overlap)
     pt=np.zeros(3);pt[axis]=plane;pt[dims]=np.asarray(poly).mean(axis=0)
     if key not in examples or overlap>examples[key][0]:examples[key]=(float(overlap),pt)
 suspect=[{'parts':[a,b],'axis':axis,'normal_sign':sign,'plane_source_m':plane,'overlap_area_m2':v}for(a,b,axis,sign,plane),v in acc.items()if v>1e-6]
 for x in suspect:
  key=(*x['parts'],x['axis'],x['normal_sign'],x['plane_source_m']);pt=examples[key][1];direction=np.zeros(3);direction[x['axis']]=x['normal_sign'];x['sample_point_source_m']=pt.tolist();x['outward_probe_inside_solid']=bool(inside_mesh([pt+direction*.0002],tris)[0]);x['normal_25mm_probe_unoccluded']=not x['outward_probe_inside_solid'] and not bool(segment_triangles(pt+direction*.0002,pt+direction*.025,tris));x['floor_contact_plane']=x['axis']==2 and abs(x['plane_source_m'])<1e-6;x['inherited_start_mating_profile']=x['axis']==0 and x['normal_sign']==-1 and abs(x['plane_source_m']-.001)<1e-6
 row={'source':s['path'],'source_sha256':s['sha256'],'suspected_same_facing_overlaps':sorted(suspect,key=lambda x:-x['overlap_area_m2'])};rows.append(row);print(Path(s['path']).stem,len(suspect),json.dumps(row['suspected_same_facing_overlaps'][:10]))
(OUT/'independent_coplanar_screen.json').write_text(json.dumps({'scope':'Inherited X0.001 negative-X mating-profile end slices retain the accepted004 section; they are disclosed and not counted as a new exposed terminal finish. All other exposed candidates remain failures. Advisory same-facing axial triangle/material overlap screen, not automatic visibility rejection. Opposite-facing physical joins and nonaxial contacts are excluded.','assets':rows,'passed':not any(x['normal_25mm_probe_unoccluded']and not x['floor_contact_plane']and not x['inherited_start_mating_profile']for a in rows for x in a['suspected_same_facing_overlaps']),'exposed_same_facing_pair_count':sum(x['normal_25mm_probe_unoccluded']and not x['floor_contact_plane']and not x['inherited_start_mating_profile']for a in rows for x in a['suspected_same_facing_overlaps'])},indent=2)+'\n')
