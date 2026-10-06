"""Continuous translational triangle SAT over retained GLB surfaces; no engine/write to Game.
Intersections are reported, never waived. Tangent rolling/meeting contacts require classification.
"""
from pathlib import Path
import sys,json,numpy as np,hashlib,time
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sat_times(a,delta,b,tol=1e-8):
 # Triangle convex sets: face normals, all edge cross-products, plus coplanar in-plane axes.
 ae=np.roll(a,-1,axis=0)-a;be=np.roll(b,-1,axis=1)-b;an=np.cross(ae[0],ae[1]);bn=np.cross(be[:,0],be[:,1]);n=len(b)
 axes=[np.broadcast_to(an,(n,3)),bn]
 for x in ae:
  for k in range(3):axes.append(np.cross(np.broadcast_to(x,(n,3)),be[:,k]))
 for x in ae:axes.append(np.broadcast_to(np.cross(an,x),(n,3)))
 for k in range(3):axes.append(np.cross(bn,be[:,k]))
 lower=np.zeros(n);upper=np.ones(n);valid=np.ones(n,dtype=bool)
 origin=a[0];aa=a-origin;bb=b-origin
 for ax in axes:
  length=np.linalg.norm(ax,axis=1);use=length>1e-12;unit=np.zeros_like(ax);unit[use]=ax[use]/length[use,None]
  ap=aa@unit.T;bp=np.einsum('nij,nj->ni',bb,unit);lo=bp.min(1)-ap.max(0)-tol;hi=bp.max(1)-ap.min(0)+tol;speed=unit@delta;still=abs(speed)<1e-12
  valid&=~use|~still|((lo<=0)&(hi>=0))
  moving=use&~still;ta=np.zeros(n);tb=np.ones(n);ta[moving]=np.minimum(lo[moving]/speed[moving],hi[moving]/speed[moving]);tb[moving]=np.maximum(lo[moving]/speed[moving],hi[moving]/speed[moving]);lower=np.maximum(lower,ta);upper=np.minimum(upper,tb);valid&=lower<=upper
 return np.flatnonzero(valid),lower,upper
# Analytical witnesses: real crossing, separated, and tangent contact retained as a contact.
a=np.array([[0,0,0],[0,1,0],[0,0,1]],float);b=np.array([[[.5,.1,.1],[.5,.7,.1],[.5,.1,.7]],[[2,.1,.1],[2,.7,.1],[2,.1,.7]]]);ix,lo,hi=sat_times(a,np.array([1.,0,0]),b);assert list(ix)==[0]and abs(lo[0]-.5)<1e-6
moving=glb(G/'assets/models/AST-CUL-005_moving_003.glb');fixed=glb(G/'assets/models/AST-CUL-005_static_003.glb');bridge=glb(G/'assets/models/AST-CUL-005_bridge_002.glb');fixed_meshes=fixed['meshes']+bridge['meshes'];tri=np.concatenate([x['triangles']for x in fixed_meshes]);owner=np.concatenate([np.full(len(x['triangles']),i)for i,x in enumerate(fixed_meshes)]);tlo=tri.min(1);thi=tri.max(1);rows=[];start=time.monotonic();counts={}
for identity,direction in [('THEATER_D11_MAIN_LEAF_LEFT',-1),('THEATER_D11_MAIN_LEAF_RIGHT',1)]:
 meshlist=[x for x in moving['meshes']if x['extras'].get('source_owner')==identity];delta=np.array([0,0,2.65*direction]);hits=0
 for mesh in meshlist:
  for index,a in enumerate(mesh['triangles']):
   low=np.minimum(a.min(0),a.min(0)+delta)-1e-7;high=np.maximum(a.max(0),a.max(0)+delta)+1e-7;candidates=np.flatnonzero(np.all(thi>=low,1)&np.all(tlo<=high,1))
   if not len(candidates):continue
   ids,enter,leave=sat_times(a,delta,tri[candidates])
   for j in ids:
    si=int(candidates[j]);part=fixed_meshes[int(owner[si])];an=np.cross(a[1]-a[0],a[2]-a[0]);bn=np.cross(tri[si,1]-tri[si,0],tri[si,2]-tri[si,0]);an/=np.linalg.norm(an);bn/=np.linalg.norm(bn)
    parallel=abs(float(an@bn))>.999999;plane=float((tri[si,0]-a[0])@an);tangent=parallel and abs(float(delta@an))<1e-9 and abs(plane)<1e-7
    rows.append({'moving_group':identity,'moving_batch':mesh['node'],'moving_triangle':index,'fixed_batch':part['node'],'fixed_triangle_global':si,'fraction_enter':float(enter[j]),'fraction_leave':float(leave[j]),'tangent_coplanar':tangent,'plane_separation_m':plane if parallel else None,'moving_triangle_xyz':a.tolist(),'fixed_triangle_xyz':tri[si].tolist(),'possible_fixed_semantics':json.loads(part['extras'].get('source_semantic_ids','[]'))});hits+=1
 counts[identity]=hits
out=R/'SOURCE_CONTINUOUS_SWEEP_CONTACTS.json';assert not out.exists();out.write_text(json.dumps({'status':'CONTACTS_REPORTED_CLASSIFICATION_PENDING'if rows else'PASS_NO_SURFACE_INTERSECTION','source_moving_sha256':moving['sha256'],'source_static_sha256':fixed['sha256'],'bridge_sha256':bridge['sha256'],'method':'Continuous translated convex-triangle separating axes, including coplanar edge axes;1e-8m numerical projection tolerance. Contacts are reported, not implicitly ignored. This is source geometry, not imported physics margins.','counts':counts,'tangent_coplanar_count':sum(x['tangent_coplanar']for x in rows),'non_tangent_count':sum(not x['tangent_coplanar']for x in rows),'contacts':rows,'seconds':time.monotonic()-start},indent=2)+'\n');print('RESULT',counts,'tangent',sum(x['tangent_coplanar']for x in rows),'non-tangent',sum(not x['tangent_coplanar']for x in rows),'seconds',time.monotonic()-start)
