"""Independent proposal geometry checks against native GLB data. No physics claim."""
import json,importlib.util,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native',BASE/'qa/validate_glb.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
COL=json.loads((BASE/'collision_proposals.json').read_text())['assets'];API=json.loads((BASE/'interface_api.json').read_text())['assets']
def vertices(shape):
 if shape['type']=='box':
  a,b=shape['min_source_m'],shape['max_source_m'];return np.array([[x,y,z] for x in(a[0],b[0]) for y in(a[1],b[1]) for z in(a[2],b[2])])
 return np.array(shape['vertices_source_m'])
def points(path):
 doc,blob=native.read(path);vs=[];tri=[]
 def walk(idx,parent):
  node=doc['nodes'][idx];m=parent@native.matrix(node)
  if 'mesh' in node:
   for p in doc['meshes'][node['mesh']]['primitives']:
    a=native.accessor(doc,blob,p['attributes']['POSITION']);v=(m@np.column_stack([a,np.ones(len(a))]).T).T[:,:3];v=v[:,[0,2,1]]*np.array([1,-1,1]);ids=native.accessor(doc,blob,p['indices']).reshape(-1,3);vs.extend(v);tri.extend(v[ids])
  for i in node.get('children',[]):walk(i,m)
 for n in doc['scenes'][doc.get('scene',0)]['nodes']:walk(n,np.eye(4))
 return np.array(vs),np.array(tri)
def inside(P,shapes):
 out=np.zeros(len(P),bool)
 for s in shapes:
  h=ConvexHull(vertices(s));out|=np.all(P@h.equations[:,:3].T+h.equations[:,3]<=2e-6,axis=1)
 return out
def distances(P,tri):
 best=np.full(len(P),np.inf)
 for A,B,C in tri:
  u=B-A;v=C-A;n=np.cross(u,v);ln=np.linalg.norm(n)
  if ln<1e-12:continue
  n/=ln;dist=(P-A)@n;Q=P-dist[:,None]*n;w=Q-A
  uu=u@u;uv=u@v;vv=v@v;wu=w@u;wv=w@v;den=uu*vv-uv*uv
  if abs(den)<1e-18:continue
  beta=(wu*vv-wv*uv)/den;gamma=(wv*uu-wu*uv)/den;within=(beta>=0)&(gamma>=0)&(beta+gamma<=1)
  dd=np.full(len(P),np.inf);dd[within]=np.abs(dist[within])
  for X,Y in[(A,B),(B,C),(C,A)]:
   line=Y-X;t=np.clip((P-X)@line/(line@line),0,1);dd=np.minimum(dd,np.linalg.norm(P-X-t[:,None]*line,axis=1))
  best=np.minimum(best,dd)
 return best
def ray_inside(P,T):
 # Non-axis direction avoids regular construction edges. Parity of closed native triangles.
 D=np.array([1,.137,.073]);D/=np.linalg.norm(D);out=[];A=T[:,0];E1=T[:,1]-A;E2=T[:,2]-A;H=np.cross(np.tile(D,(len(T),1)),E2);det=np.einsum('ij,ij->i',E1,H);valid=np.abs(det)>1e-10;inv=np.zeros(len(T));inv[valid]=1/det[valid]
 for p in P:
  S=p-A;u=inv*np.einsum('ij,ij->i',S,H);Q=np.cross(S,E1);v=inv*(Q@D);t=inv*np.einsum('ij,ij->i',E2,Q);hits=t[valid&(u>1e-8)&(v>1e-8)&(u+v<1-1e-8)&(t>1e-8)];out.append(len(np.unique(np.round(hits,7)))%2==1)
 return np.array(out)
rows=[]
for ident,data in COL.items():
 shapes=data['shapes'];V,T=points(BASE/'exports'/f'{ident}.glb');P=np.vstack([V,T.mean(1)]);covered=inside(P,shapes);cs=[]
 for s in shapes:
  v=vertices(s);h=ConvexHull(v);cs.extend(v[h.simplices])
 outside=P[~covered];d=distances(outside,np.array(cs)) if len(outside) else np.array([0]);voids=[]
 for r in API[ident]['reserved_voids']:
  lo,hi=np.array(r['min_source_m']),np.array(r['max_source_m']);pv=np.array([[x,y,z] for x in np.linspace(lo[0],hi[0],7) for y in np.linspace(lo[1],hi[1],7) for z in np.linspace(lo[2],hi[2],7)]);a=inside(pv,shapes);b=ray_inside(pv,T);voids.append({'name':r['name'],'sample_count':len(pv),'proposal_intrusions':int(a.sum()),'native_visual_intrusions':int(b.sum()),'passed':not a.any() and not b.any()})
 centers=np.array([vertices(s).mean(0) for s in shapes]);positive=inside(centers,shapes)
 wrong_point=[0,.4,.50] if ident.endswith('004') else [0,-.4,1.0]
 wholelo=V.min(0);wholehi=V.max(0);inside_wrong=all(wholelo[i]<=wrong_point[i]<=wholehi[i] for i in range(3));correct_inside=bool(inside(np.array([wrong_point]),shapes)[0])
 if ident.endswith('003'):wrong_point=[0,.19,1.0];inside_wrong=all(wholelo[i]<=wrong_point[i]<=wholehi[i] for i in range(3));correct_inside=bool(inside(np.array([wrong_point]),shapes)[0])
 row={'id':ident,'glb_sha256':hashlib.sha256((BASE/'exports'/f'{ident}.glb').read_bytes()).hexdigest(),'structural_shape_count':len(shapes),'convexity_checked':all(ConvexHull(vertices(s)).volume>0 for s in shapes),'positive_collider_centers_tested':len(centers),'positive_centers_passed':bool(positive.all()),'void_probes':voids,'wrong_whole_aabb_negative_control':{'point_source_m':wrong_point,'incorrect_whole_box_fills_void':inside_wrong,'correct_compound_fills_void':correct_inside,'rejects_whole_box':inside_wrong and not correct_inside},'measured_visual_vertex_and_triangle_centroid_count':len(P),'outside_structural_proposal_samples':int((~covered).sum()),'maximum_sampled_visual_undercapture_distance_m':float(d.max()),'undercapture_scope':'Small replaceable rubber corner covers, bolt heads, tags and raised controls intentionally excluded from structural collision; evaluated bevel deviations are bounded. Sampled distance is not a continuous surface Hausdorff proof.','largest_declared_shape_corner_inflation_m':max(s['conservative_empty_corner_limit_m'] for s in shapes),'movement':'None; no moving tray or full-box collision','passed':all(r['passed'] for r in voids) and positive.all() and inside_wrong and not correct_inside}
 row['passed']=bool(row['passed']);rows.append(row)
result={'method':'Native GLB hierarchy parsed independently; convex halfspaces and nonaxis native triangle ray parity; collision proposals remain structural only','results':rows,'all_passed':all(r['passed'] for r in rows)}
(BASE/'qa/collision_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
