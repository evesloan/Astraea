"""All-part connectivity and advisory coplanar finish termination screen, read-only."""
from pathlib import Path
import sys,json,hashlib,collections,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18'
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import contact_graph
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def area(p):return .5*abs(sum(cross2(p[i]-p[0],p[i+1]-p[0])for i in range(1,len(p)-1)))if len(p)>=3 else 0.
def clip(poly,t):
 sign=np.sign(cross2(t[1]-t[0],t[2]-t[0]));result=poly
 for a,b in zip(t,np.roll(t,-1,axis=0)):
  old=result;result=[]
  if len(old)<3:return []
  for p,q in zip(old,np.roll(old,-1,axis=0)):
   u=sign*cross2(b-a,p-a);v=sign*cross2(b-a,q-a)
   if u>=-1e-10:result.append(p)
   if (u>=-1e-10)!=(v>=-1e-10):result.append(p+u/(u-v)*(q-p))
 return np.asarray(result)
rows=[]
paths=[OUT/f'independent_source_{x}.json'for x in sys.argv[1:]]if len(sys.argv)>1 else sorted(OUT.glob('independent_source_AST-RTL-*.json'))
for p in paths:
 s=json.loads(p.read_text());assert sha(ROOT/s['path'])==s['sha256'];a=np.load(ROOT/s['geometry_cache']);t=a['triangles'];labels=a['object_names'];materials=a['material_names'];parts={str(n):t[labels==n]for n in np.unique(labels)};roots=[name for name,tt in parts.items()if abs(tt[:,:,2].min())<.00002];graph=contact_graph(t,labels,roots)
 cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);norm=cross/np.maximum(np.linalg.norm(cross,axis=1),1e-20)[:,None];groups=collections.defaultdict(list);acc=collections.defaultdict(float);examples={}
 for i,(tt,n)in enumerate(zip(t,norm)):
  if np.linalg.norm(cross[i])<1e-14:continue
  groups[tuple(np.round(n,5))+(round(float(n@tt[0]),5),)].append(i)
 for key,ids in groups.items():
  n=np.asarray(key[:3]);axis=int(np.argmax(abs(n)));dims=[i for i in range(3)if i!=axis];ts=t[ids][:,:,dims];lo=ts.min(1);hi=ts.max(1)
  for k,i in enumerate(ids):
   for l in np.where(((lo[k]<hi[k+1:]-1e-8)&(hi[k]>lo[k+1:]+1e-8)).all(1))[0]+k+1:
    j=ids[l]
    if labels[i]==labels[j]:continue
    if np.max(abs((t[j]-t[i,0])@norm[i]))>1e-6 or norm[i]@norm[j]<.999999:continue
    poly=clip(ts[k],ts[l]);overlap=area(poly)/abs(norm[i,axis])
    if overlap<=1e-7:continue
    pair=tuple(sorted([str(labels[i]),str(labels[j])]));ak=pair+key;acc[ak]+=float(overlap);point=np.zeros(3);point[dims]=np.asarray(poly).mean(0);point[axis]=(norm[i]@t[i,0]-point[dims]@norm[i,dims])/norm[i,axis]
    if ak not in examples or overlap>examples[ak][0]:examples[ak]=(overlap,point,norm[i],str(materials[i]),str(materials[j]))
 suspects=[]
 for ak,overlap in acc.items():
  if overlap<1e-6:continue
  _,point,n,ma,mb=examples[ak];outer=point+n*.0002;containing=[name for name,tt in parts.items()if ((outer>=tt.min((0,1))-1e-6)&(outer<=tt.max((0,1))+1e-6)).all()and inside_mesh([outer],tt)[0]];blocked=bool(segment_triangles(outer,point+n*.025,t));floor=abs(point[2])<1e-6 and n[2]<-.9999
  suspects.append({'parts':list(ak[:2]),'materials':[ma,mb],'same_material':ma==mb,'overlap_area_m2':overlap,'sample_point_source_m':point.tolist(),'outward_normal_source':n.tolist(),'outward_probe_inside_parts':containing,'normal_25mm_probe_unoccluded':not containing and not blocked,'floor_contact_plane':floor,'exposed_candidate':not containing and not blocked and not floor})
 row={'catalogue_id':Path(s['path']).stem,'source':s['path'],'source_sha256':s['sha256'],'all_part_contact_graph':graph,'suspected_same_facing_overlaps':sorted(suspects,key=lambda x:-x['overlap_area_m2']),'exposed_candidate_count':sum(x['exposed_candidate']for x in suspects),'passed':graph['passed']and not any(x['exposed_candidate']for x in suspects)};rows.append(row);print(row['catalogue_id'],'support',graph['passed'],'isolated',graph['isolated_parts'],'exposed',row['exposed_candidate_count'],flush=True)
 (OUT/f"independent_support_finish_{row['catalogue_id']}.json").write_text(json.dumps(row,indent=2,default=lambda x:x.item())+'\n')
report={'passed':all(x['passed']for x in rows),'assets':rows,'limits':['All planar triangle orientations screened, including sloped finish faces. Coplanar grouping is tolerance limited; advisory exposure probe is not full visibility proof.','Opposite-facing butt contacts are excluded. Floor boundaries are not exposed finish failures.','Connectivity is actual geometry, not structural strength, load or installation acceptance.'],'helper_bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in [ROOT/'qa/batch15/independent_contact_graph.py',ROOT/'qa/batch08/independent_collision_geometry.py']],'executed_script_sha256':sha(Path(__file__))};(OUT/'independent_support_finish_review.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item())+'\n')
