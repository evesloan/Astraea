"""Advisory same-facing overlap screen on axial and canted evaluated surfaces."""
from pathlib import Path
import sys,json,hashlib,collections,numpy as np
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'qa/batch12'
sys.path.insert(0,str(ROOT/'qa/batch08'))
from independent_collision_geometry import segment_triangles,inside_mesh
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def area(p):
 if len(p)<3:return 0.
 return .5*abs(sum(cross2(p[i]-p[0],p[i+1]-p[0])for i in range(1,len(p)-1)))
def clip(poly,tri):
 sign=np.sign(cross2(tri[1]-tri[0],tri[2]-tri[0]));result=poly
 for a,b in zip(tri,np.roll(tri,-1,axis=0)):
  old=result;result=[]
  if len(old)<3:return []
  for p,q in zip(old,np.roll(old,-1,axis=0)):
   u=sign*cross2(b-a,p-a);v=sign*cross2(b-a,q-a)
   if u>=-1e-10:result.append(p)
   if (u>=-1e-10)!=(v>=-1e-10):result.append(p+u/(u-v)*(q-p))
 return np.asarray(result)
selected=set(sys.argv[1:]);rows=[]
for p in sorted(OUT.glob('independent_source_AST-MED-*.json')):
 if selected and p.stem.removeprefix('independent_source_')not in selected:continue
 s=json.loads(p.read_text());assert sha(ROOT/s['path'])==s['sha256'];g=np.load(ROOT/s['geometry_cache']);tris=g['triangles'];names=g['object_names'];mats=g['material_names'];cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);norm=cross/np.maximum(np.linalg.norm(cross,axis=1),1e-30)[:,None];centres=tris.mean(axis=1)
 acc=collections.defaultdict(float);examples={};seps=collections.defaultdict(list)
 for i,(t,n)in enumerate(zip(tris,norm)):
  if np.linalg.norm(n)<.99:continue
  candidates=np.where((np.arange(len(tris))>i)&(names!=names[i])&(mats!=mats[i])&((norm@n)>.9999995)&(np.abs((centres-t[0])@n)<=.0020001))[0]
  if not len(candidates):continue
  ref=np.eye(3)[int(np.argmin(abs(n)))];u=np.cross(n,ref);u/=np.linalg.norm(u);v=np.cross(n,u);basis=np.asarray([u,v]);a=t@basis.T;lo=a.min(axis=0);hi=a.max(axis=0)
  for j in candidates:
   d=(tris[j]-t[0])@n
   if max(abs(d))>.0020001:continue
   b=tris[j]@basis.T
   if not ((lo<b.max(axis=0)-1e-8)&(hi>b.min(axis=0)+1e-8)).all():continue
   poly=clip(a,b);ar=area(poly)
   if ar<1e-7:continue
   plane=max(float(t[0]@n),float(tris[j].mean(axis=0)@n));point=np.asarray(poly).mean(axis=0)@basis+plane*n
   key=(str(min(names[i],names[j])),str(max(names[i],names[j])),tuple(np.round(n,5)))
   acc[key]+=ar;seps[key].append(abs(float(d.mean())))
   if key not in examples or ar>examples[key][0]:examples[key]=(ar,point,n)
 pairs=[]
 for key,ar in acc.items():
  if ar<1e-6:continue
  _,pt,n=examples[key];outward=pt+n*.0002;inside=[]
  for label in np.unique(names):
   t=tris[names==label];lo=t.reshape(-1,3).min(axis=0);hi=t.reshape(-1,3).max(axis=0)
   if ((outward>=lo)&(outward<=hi)).all()and inside_mesh([outward],t)[0]:inside.append(str(label))
  blocked=bool(segment_triangles(outward,pt+n*.025,tris));floor=bool(abs(n[2]+1)<1e-6 and abs(pt[2])<1e-6)
  pairs.append({'parts':list(key[:2]),'normal_source':n.tolist(),'canted_surface':float(np.max(abs(n)))<.999999,'overlap_area_m2':ar,'separation_range_m':[min(seps[key]),max(seps[key])],'sample_point_source_m':pt.tolist(),'outward_sample_inside_parts':inside,'normal_25mm_probe_blocked':blocked,'exposed_sample':not inside and not blocked,'floor_contact_plane':floor})
 row={'source':s['path'],'source_sha256':s['sha256'],'triangle_count':len(tris),'near_layer_candidates':sorted(pairs,key=lambda x:-x['overlap_area_m2'])};rows.append(row)
 print(Path(s['path']).stem,'pairs',len(pairs),'exposed',sum(x['exposed_sample']and not x['floor_contact_plane']for x in pairs))
 for x in pairs:
  if x['exposed_sample']and not x['floor_contact_plane']:print(json.dumps(x))
res={'executed_script_sha256':sha(Path(__file__)),'helper_sha256':sha(ROOT/'qa/batch08/independent_collision_geometry.py'),'max_same_facing_plane_separation_m':.002,'normal_cosine_threshold':.9999995,'assets':rows,'requires_review':any(x['exposed_sample']and not x['floor_contact_plane']for r in rows for x in r['near_layer_candidates']),'limits':'Advisory exact/near parallel different-material surfaces with <=2mm separation, including canted/sloped planes. Positive projected overlap and one outward visibility witness per part-pair/normal. Opposite-facing physical joins intentionally excluded. Finite visibility probes do not prove whole-surface visibility; final actual image review remains required.'}
(OUT/'independent_near_layer_screen.json').write_text(json.dumps(res,indent=2)+'\n')
