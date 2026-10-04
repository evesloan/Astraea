"""Read-only actual triangle contact graph used by independent Batch15 review."""
import sys, collections, itertools, numpy as np
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'qa/batch08'))
from independent_collision_geometry import nearest_distances,inside_mesh,segment_triangles
def contact_graph(tri,labels,root_parts):
 names=sorted(np.unique(labels));part={n:tri[labels==n]for n in names};verts={n:np.unique(part[n].reshape(-1,3),axis=0)for n in names};bounds={n:(v.min(0),v.max(0))for n,v in verts.items()}
 def edges(t):
  e=t[:,[[0,1],[1,2],[2,0]]].reshape(-1,2,3).copy();flip=np.asarray([tuple(x[0])>tuple(x[1])for x in e]);e[flip]=e[flip,::-1];return np.unique(np.round(e,9),axis=0)
 def contact(a,b):
  av,bv=verts[a],verts[b];at,bt=part[a],part[b];da=nearest_distances(av,bt);db=nearest_distances(bv,at);d=float(min(da.min(),db.min()))
  if d<.00002:
   p=av[da.argmin()]if da.min()<=db.min()else bv[db.argmin()];return {'method':'Actual vertex-to-triangle boundary witness','point_source_m':p.tolist(),'distance_m':d}
  for p,t,lo,hi,target in [(av,bt,*bounds[b],b),(bv,at,*bounds[a],a)]:
   if not closed[target]:continue
   selected=p[((p>=lo)&(p<=hi)).all(1)]
   if len(selected):
    good=inside_mesh(selected,t)
    if good.any():return {'method':'Actual vertex contained by adjacent closed solid','point_source_m':selected[good][0].tolist(),'boundary_distance_m':d}
  for es,t in [(edges(at),bt),(edges(bt),at)]:
   for x,y in es:
    hits=segment_triangles(x,y,t)
    if hits:return {'method':'Actual triangle edge intersects adjacent triangle','point_source_m':(x+hits[0]*(y-x)).tolist(),'boundary_distance_m':d}
  # Coplanar crossing edges need an explicit in-plane test when no endpoint lies on the other face.
  for ae in edges(at):
   u=ae[1]-ae[0]
   for be in edges(bt):
    if ((ae.max(0)<be.min(0)-.00002)|(be.max(0)<ae.min(0)-.00002)).any():continue
    v=be[1]-be[0];M=np.column_stack([u,-v]);st,_,rank,_=np.linalg.lstsq(M,be[0]-ae[0],rcond=None)
    if rank==2 and np.all(st>=-1e-7)and np.all(st<=1+1e-7)and np.linalg.norm(M@st-(be[0]-ae[0]))<.00002:return {'method':'Actual coplanar/nonparallel source edges share a point','point_source_m':(ae[0]+st[0]*u).tolist(),'boundary_distance_m':d}
  return None
 closed={}
 for name,t in part.items():
  es=t[:,[[0,1],[1,2],[2,0]]].reshape(-1,2,3).copy();flip=np.asarray([tuple(x[0])>tuple(x[1])for x in es]);es[flip]=es[flip,::-1];_,counts=np.unique(np.round(es,8),axis=0,return_counts=True);closed[name]=bool(np.all(counts==2))
 links=[];adj=collections.defaultdict(list)
 for a,b in itertools.combinations(names,2):
  alo,ahi=bounds[a];blo,bhi=bounds[b]
  if ((alo>bhi+.00002)|(blo>ahi+.00002)).any():continue
  c=contact(a,b)
  if c:links.append({'parts':[str(a),str(b)],**c});adj[a].append(b);adj[b].append(a)
 parents={n:None for n in root_parts};queue=collections.deque(root_parts)
 while queue:
  a=queue.popleft()
  for b in adj[a]:
   if b not in parents:parents[b]=a;queue.append(b)
 rows=[]
 for n in names:
  path=[];x=n
  while x in parents:
   path.append(str(x));x=parents[x]
   if x is None:break
  rows.append({'part':str(n),'actual_contact_neighbours':[str(x)for x in adj[n]],'contact_path_to_root_or_floor':path if n in parents else [],'pass':n in parents})
 return {'passed':all(x['pass']for x in rows),'tolerance_m':.00002,'root_or_floor_parts':list(root_parts),'all_semantic_parts':rows,'actual_source_contacts':links,'isolated_parts':[x['part']for x in rows if not x['pass']],'method':'Full semantic-part graph using actual vertex/triangle boundaries, enclosed points, edge/triangle and coplanar-edge intersections. AABB only rejects separated pairs; it never establishes contact.','limits':'Geometric connectivity, not structural design, attachment strength, irrigation, load, or simulation behavior. Open folded foliage is not treated as a closed support hull.'}

def normal_witness(p,tris,n):
 p=np.asarray(p);t=np.asarray(tris);a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;cross=np.cross(ab,ac);nn=np.einsum('ij,ij->i',cross,cross)
 proj=p-cross*(np.einsum('ij,ij->i',p-a,cross)/np.maximum(nn,1e-30))[:,None];v=proj-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);d20=np.einsum('ij,ij->i',v,ab);d21=np.einsum('ij,ij->i',v,ac);den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/np.maximum(den,1e-30);vv=(d00*d21-d01*d20)/np.maximum(den,1e-30);ds=np.where((u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-20),np.sum((proj-p)**2,axis=1),np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1);q=x+f[:,None]*e;ds=np.minimum(ds,np.sum((q-p)**2,axis=1))
 normal=cross/np.maximum(np.sqrt(nn),1e-30)[:,None];near=np.sqrt(ds)<=np.sqrt(ds.min())+.0002;cos=normal@np.asarray(n);best=int(np.argmax(np.where(near,cos,-np.inf)))
 return {'nearby_named_triangle_count':int(near.sum()),'best_declared_outward_normal_cosine':float(cos[best]),'actual_surface_normal_source':normal[best].tolist(),'pass':bool(cos[best]>.999)}

