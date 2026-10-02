"""Resolve actual native GLB hierarchy; check surfaces, seam, markers and positive/negative controls."""
from pathlib import Path
import json,numpy as np,hashlib,sys

ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
# This is a local read-only parser; importing no authoring geometry functions.
ns={'__file__':str(ROOT/'qa/validate_glb.py')};exec((ROOT/'qa/validate_glb.py').read_text().split('def validate(path):')[0],ns);read,accessor,matrix=ns['read'],ns['accessor'],ns['matrix']
def geometry(path):
 doc,blob=read(path);triangles=[];roles={};nodes={}
 def walk(i,parent):
  n=doc['nodes'][i];m=parent@matrix(n);nodes[n.get('name',str(i))]={'position':m[:3,3],'matrix':m,'extras':n.get('extras',{})}
  if 'mesh'in n:
   for p in doc['meshes'][n['mesh']]['primitives']:
    v=accessor(doc,blob,p['attributes']['POSITION']);v=(m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];ix=accessor(doc,blob,p['indices']).reshape(-1,3);ts=v[ix];triangles.extend(ts);role=doc['materials'][p['material']]['name'];roles.setdefault(role,[]).extend(ts)
  for child in n.get('children',[]):walk(child,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return np.array(triangles),{r:np.array(t)for r,t in roles.items()},nodes
tri,roles,nodes=geometry(ROOT/'exports/AST-BOT-010.glb');meta=json.loads((ROOT/'AST-BOT-010.manifest.json').read_text())
def nearest(p,ts):
 p=np.asarray(p);a,b,c=ts[:,0],ts[:,1],ts[:,2];ab=b-a;ac=c-a;nn=np.cross(ab,ac);n2=(nn*nn).sum(1);ap=p-a;proj=p-((ap*nn).sum(1)/n2)[:,None]*nn;v=proj-a
 d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1);d20=(v*ab).sum(1);d21=(v*ac).sum(1);den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;valid=(u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10)
 candidates=[proj]
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;t=np.clip(((p-x)*e).sum(1)/(e*e).sum(1),0,1);candidates.append(x+t[:,None]*e)
 qs=np.array(candidates);ds=np.linalg.norm(qs-p,axis=2);ds[0,~valid]=np.inf;ki,ti=np.unravel_index(ds.argmin(),ds.shape);normal=nn[ti]/np.sqrt(n2[ti]);return float(ds[ki,ti]),qs[ki,ti],normal
markers=[]
for r in meta['markers']:
 p=nodes[r['name']]['position'];expected=np.array(r['native_glb_m']);row={'name':r['name'],'actual_native_m':p.tolist(),'expected_native_m':expected.tolist(),'node_error_m':float(np.linalg.norm(p-expected)),'passed':np.linalg.norm(p-expected)<1e-6}
 if r['physical_normal_source']:
  d,q,n=nearest(p,tri);sn=r['physical_normal_source'];nn=np.array([sn[0],sn[2],-sn[1]]);row.update(surface_distance_m=d,actual_native_normal=n.tolist(),expected_native_normal=nn.tolist(),normal_dot=float(n@nn));row['passed'] &= d<.00015 and n@nn>.99
  bad=p+nn*.15;wrong,_,_=nearest(bad,tri);row['outward_offset_negative_control_distance_m']=wrong
 markers.append(row)
# Compare real start and original straight end triangles in the same plane.
old,oldroles,_=geometry(CAT/'assets/botanical_planter/AST-BOT-004.glb');seams=[]
for role in sorted(roles):
 a=roles[role];b=oldroles[role];a=a[np.max(np.abs(a[:,:,0]-.001),axis=1)<1e-6];b=b[np.max(np.abs(b[:,:,0]-2.399),axis=1)<1e-6]
 if not len(a) and not len(b):continue
 aa=a.copy();bb=b.copy();aa[:,:,0]=0;bb[:,:,0]=0;maxd=0
 for pts,ts in [(aa.reshape(-1,3),bb),(bb.reshape(-1,3),aa)]:
  if not len(ts):maxd=float('inf');break
  for p in pts:maxd=max(maxd,nearest(p,ts)[0])
 seams.append({'role':role,'new_start_triangles':len(a),'old_end_triangles':len(b),'max_bidirectional_sample_distance_m':maxd,'physical_joint_gap_m':float(a[:,:,0].mean()+2.4-b[:,:,0].mean()) if len(a)and len(b)else None,'passed':maxd<.00015})
# All expected source bounding values transformed, rather than raw local vertices.
lo=tri.min((0,1));hi=tri.max((0,1));expected_lo=[meta['min_m'][0],meta['min_m'][2],-meta['max_m'][1]];expected_hi=[meta['max_m'][0],meta['max_m'][2],-meta['min_m'][1]]
bounds_error=max(np.max(np.abs(lo-expected_lo)),np.max(np.abs(hi-expected_hi)))
result={'glb_sha256':hashlib.sha256((ROOT/'exports/AST-BOT-010.glb').read_bytes()).hexdigest(),'actual_native_bounds':{'min':lo.tolist(),'max':hi.tolist()},'source_native_bound_error_m':float(bounds_error),'actual_source_to_native_markers':markers,'unchanged_004_mating_face_checks':seams,'scope':'Actual native node and physical triangle evidence, not metadata-only transform agreement','passed':bounds_error<1e-6 and all(r['passed']for r in markers+seams)}
(ROOT/'qa/native_surface_checks.json').write_text(json.dumps(result,indent=2,default=lambda v: v.item())+'\n');print('NATIVE_PASS',result['passed']);print([(r['name'],r)for r in markers if not r['passed']]);print(seams);assert result['passed']
