"""Native GLB transforms and marker-to-real-triangle checks independent of Blender."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import cKDTree
def closest_point(tr,points):
 a,b,c=tr[:,0],tr[:,1],tr[:,2];ab=b-a;ac=c-a;ap=points-a
 n=np.cross(ab,ac);proj=points-n*(np.sum(ap*n,axis=1)/np.sum(n*n,axis=1))[:,None]
 v=proj-a;d00=np.sum(ab*ab,axis=1);d01=np.sum(ab*ac,axis=1);d11=np.sum(ac*ac,axis=1);d20=np.sum(v*ab,axis=1);d21=np.sum(v*ac,axis=1);den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;inside=(u>=-1e-9)&(w>=-1e-9)&(u+w<=1+1e-9)
 candidates=[]
 for aa,bb in [(a,b),(b,c),(c,a)]:
  e=bb-aa;t=np.clip(np.sum((points-aa)*e,axis=1)/np.sum(e*e,axis=1),0,1);candidates.append(aa+t[:,None]*e)
 can=np.stack(candidates,axis=1);dist=np.sum((can-points[:,None,:])**2,axis=2);best=can[np.arange(len(tr)),dist.argmin(1)];best[inside]=proj[inside];return best
BASE=Path(__file__).resolve().parents[1]
ns={'__file__':str(BASE/'qa/validate_glb.py')};text=(BASE/'qa/validate_glb.py').read_text();exec(text[:text.index('\nrecords=')],ns)
read,accessor,matrix=ns['read'],ns['accessor'],ns['matrix'];source=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());rows=[]
for p in sorted((BASE/'exports').glob('*.glb')):
 ident=p.stem.replace('_open','');rec=json.loads((BASE/(ident+'.manifest.json')).read_text());doc,blob=read(p);nodes={};meshes=[]
 def walk(ix,mat,anc):
  no=doc['nodes'][ix];w=mat@matrix(no);name=no.get('name','');nodes[name]={'matrix':w,'ancestors':anc,'node':no}
  if 'mesh'in no:
   vv=[];tt=[]
   for pr in doc['meshes'][no['mesh']]['primitives']:
    v=accessor(doc,blob,pr['attributes']['POSITION']);v=(w@np.column_stack((v,np.ones(len(v)))).T).T[:,:3];i=accessor(doc,blob,pr['indices']).reshape(-1,3);vv.extend(v);tt.extend(v[i])
   meshes.append({'name':name,'vertices':np.array(vv),'triangles':np.array(tt),'semantic_parts':json.loads(no.get('extras',{}).get('semantic_parts','[]'))})
  for child in no.get('children',[]):walk(child,w,anc+[name])
 for ix in doc['scenes'][doc.get('scene',0)]['nodes']:walk(ix,np.eye(4),[])
 openstate='_open'in p.stem;delta=np.array([0,0,.24 if openstate else 0]);markers=[]
 for m in rec['physical_and_proposal_markers']:
  n=nodes[m['name']];point=n['matrix'][:3,3];expect=np.array(m['gltf_m'])+(delta if m['parent_root']=='DRAWER_TRANSLATE'else 0);row={'name':m['name'],'position_error_m':float(np.linalg.norm(point-expect)),'moving_parent_preserved':m['parent_root']!='DRAWER_TRANSLATE'or'DRAWER_TRANSLATE'in n['ancestors']}
  if m['physical_part']:
   candidates=[q for q in meshes if m['physical_part']in q['semantic_parts']];assert len(candidates)==1;tr=candidates[0]['triangles'];near=closest_point(tr,np.tile(point,(len(tr),1)));d=np.linalg.norm(near-point,axis=1);i=int(d.argmin());row['surface_distance_m']=float(d[i])
   if 'direction_gltf'in m:
    a,b,c=tr[i];normal=np.cross(b-a,c-a);normal/=np.linalg.norm(normal);row['normal_dot']=float(normal@np.array(m['direction_gltf']))
  row['passes']=row['position_error_m']<1e-6 and row['moving_parent_preserved']and row.get('surface_distance_m',0)<1e-6 and row.get('normal_dot',1)>.99;markers.append(row)
 comparisons=[]
 for part in source[ident]['parts']:
  v=np.array(part['vertices']);v=v[:,[0,2,1]]*np.array([1,1,-1]);v+=delta if part['movement_group']=='drawer'else 0;mat=next(q for q in meshes if part['name']in q['semantic_parts']);dist=cKDTree(mat['vertices']).query(v)[0];comparisons.append({'part':part['name'],'vertex_count':len(v),'source_to_native_max_error_m':float(dist.max()),'passes':bool(dist.max()<1e-6)})
 rows.append({'file':str(p.relative_to(BASE)),'physical_markers':markers,'source_to_native_geometry':comparisons,'moving_roots':[n for n in nodes if n=='DRAWER_TRANSLATE'],'all_passed':all(r['passes']for r in markers+comparisons)})
out={'scope':'Actual native node hierarchy transforms resolved, source evaluated vertices converted once, named part groups and physical triangle normals inspected, both drawer states','files':rows,'all_passed':all(r['all_passed']for r in rows)};(BASE/'qa/native_interface_checks.json').write_text(json.dumps(out,indent=2)+'\n');print([(r['file'],r['all_passed'],[m['name']for m in r['physical_markers']if not m['passes']])for r in rows])
