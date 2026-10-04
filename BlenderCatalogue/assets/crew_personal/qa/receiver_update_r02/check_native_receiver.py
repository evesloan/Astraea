"""Actual changed native receiver vs unchanged module: hierarchy, surfaces and full envelopes."""
from pathlib import Path
import json,numpy as np,hashlib
BASE=Path(__file__).resolve().parents[2];CAT=BASE.parents[1];OUT=Path(__file__).resolve().parent
ns={'__file__':str(BASE/'qa/validate_glb.py')};code=(BASE/'qa/validate_glb.py').read_text();exec(code[:code.index('\nrecords=')],ns)
read,accessor,matrix=ns['read'],ns['accessor'],ns['matrix']
def closest(tr,p):
 a,b,c=tr[:,0],tr[:,1],tr[:,2];ab=b-a;ac=c-a;ap=p-a;n=np.cross(ab,ac);project=p-n*(np.sum(ap*n,axis=1)/np.sum(n*n,axis=1))[:,None];v=project-a;d00=np.sum(ab*ab,1);d01=np.sum(ab*ac,1);d11=np.sum(ac*ac,1);d20=np.sum(v*ab,1);d21=np.sum(v*ac,1);den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;inside=(u>=-1e-9)&(w>=-1e-9)&(u+w<=1+1e-9);candidates=[]
 for aa,bb in[(a,b),(b,c),(c,a)]:
  e=bb-aa;t=np.clip(np.sum((p-aa)*e,1)/np.sum(e*e,1),0,1);candidates.append(aa+t[:,None]*e)
 can=np.stack(candidates,1);dist=np.sum((can-p)**2,2);best=can[np.arange(len(tr)),dist.argmin(1)];best[inside]=project[inside];d=np.linalg.norm(best-p,axis=1);i=int(d.argmin());normal=n[i]/np.linalg.norm(n[i]);return {'distance_m':float(d[i]),'normal':normal,'point':best[i]}
def parse(path,offset):
 doc,blob=read(path);groups=[];nodes={}
 def walk(ix,parent):
  n=doc['nodes'][ix];w=parent@matrix(n);name=n.get('name','');nodes[name]=w[:3,3]+offset
  if'mesh'in n:
   vv=[];tt=[]
   for pr in doc['meshes'][n['mesh']]['primitives']:
    v=accessor(doc,blob,pr['attributes']['POSITION']);v=(w@np.column_stack((v,np.ones(len(v)))).T).T[:,:3]+offset;i=accessor(doc,blob,pr['indices']).reshape(-1,3);vv.extend(v);tt.extend(v[i])
   groups.append({'name':name,'parts':json.loads(n.get('extras',{}).get('semantic_parts','[]')),'vertices':np.array(vv),'triangles':np.array(tt)})
  for child in n.get('children',[]):walk(child,w)
 for ix in doc['scenes'][doc.get('scene',0)]['nodes']:walk(ix,np.eye(4))
 return groups,nodes
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bb(v):return np.array(v).min(0),np.array(v).max(0)
def sep(a,b):return np.maximum(b[0]-a[1],a[0]-b[1])
rp=CAT/'assets/crew_rest/exports/AST-CRW-001.glb';mp=BASE/'exports/AST-CRW-004.glb';rg,rnodes=parse(rp,np.zeros(3));mg,mnodes=parse(mp,np.array([-.26,.88,-2.14]));rhead=next(g for g in rg if'001_flat_headboard'in g['parts']);mb=next(g for g in mg if'headboard_mount_backplate'in g['parts']);checks=[]
for name,p in mnodes.items():
 if not name.startswith('HEADBOARD_CONTACT_'):continue
 a=closest(mb['triangles'],p);b=closest(rhead['triangles'],p);dot=float(a['normal']@b['normal']);checks.append({'native_marker':name,'native_world_position_m':p.tolist(),'module_surface_distance_m':a['distance_m'],'receiver_surface_distance_m':b['distance_m'],'module_physical_normal_gltf':a['normal'].tolist(),'receiver_physical_normal_gltf':b['normal'].tolist(),'opposing_normal_dot':dot,'passes':a['distance_m']<1e-6 and b['distance_m']<1e-6 and dot<-.999})
mbounds=bb(np.concatenate([g['vertices']for g in mg]));clearances=[]
for g in rg:
 if not any(p in g['parts']for p in ['001_shaped_head_pillow','001_shaped_single_mattress','001_draped_folded_blanket']):continue
 bounds=bb(g['vertices']);gaps=sep(mbounds,bounds);clearances.append({'native_material_group':g['name'],'included_semantic_parts':g['parts'],'full_native_group_min_m':bounds[0].tolist(),'full_native_group_max_m':bounds[1].tolist(),'complete_module_axis_separation_m':gaps.tolist(),'passes':bool(gaps.max()>0)})
use=(np.array([-.40,.565,-1.52]),np.array([.40,1.10,-.30]));gaps=sep(mbounds,use);record={'revision':'receiver-update-r02','frame':'actual native GLB Y-up hierarchy','module_to_receiver_translation_gltf_m':[-.26,.88,-2.14],'export_hashes':{'receiver_AST-CRW-001':sha(rp),'module_AST-CRW-004':sha(mp)},'native_mount_surface_checks':checks,'native_complete_module_bounds':{'min_m':mbounds[0].tolist(),'max_m':mbounds[1].tolist()},'native_complete_bedding_group_separation':clearances,'native_central_rest_use_volume':{'min_m':use[0].tolist(),'max_m':use[1].tolist(),'full_module_axis_separation_m':gaps.tolist(),'passes':bool(gaps.max()>0)},'limits':'Exact current native surfaces and full bounded geometry separation only. No actor/species head movement, anatomy, load or host-room certification. Material consolidation groups both pillow and mattress; the complete native group is conservatively tested.','all_passed':all(q['passes']for q in checks+clearances)and bool(gaps.max()>0)};(OUT/'native_mount_and_clearance.json').write_text(json.dumps(record,indent=2)+'\n');print('NATIVE_RECEIVER_R02',record['all_passed'])
