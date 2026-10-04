"""Actual all-part contact graph to physical floor shoes; no author join-list assumptions."""
from pathlib import Path
import json,hashlib,sys,itertools,collections,numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances,inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rp=OUT/'independent_source_AST-MED-002.json';r=json.loads(rp.read_text());assert sha(ROOT/r['path'])==r['sha256'];g=np.load(ROOT/r['geometry_cache']);labels=g['object_names'];tri=g['triangles'];names=sorted(np.unique(labels));part={n:tri[labels==n]for n in names};verts={n:np.unique(part[n].reshape(-1,3),axis=0)for n in names};bounds={n:(v.min(0),v.max(0))for n,v in verts.items()}
def edges(t):
 e=t[:,[[0,1],[1,2],[2,0]]].reshape(-1,2,3).copy();flip=np.asarray([tuple(x[0])>tuple(x[1])for x in e]);e[flip]=e[flip,::-1];return np.unique(np.round(e,9),axis=0)
def contact(a,b):
 av,bv=verts[a],verts[b];at,bt=part[a],part[b];da=nearest_distances(av,bt);db=nearest_distances(bv,at);d=float(min(da.min(),db.min()))
 if d<.00002:
  p=av[da.argmin()]if da.min()<=db.min()else bv[db.argmin()];return {'method':'Actual vertex-to-triangle boundary witness','point_source_m':p.tolist(),'distance_m':d}
 for p,t,lo,hi in [(av,bt,*bounds[b]),(bv,at,*bounds[a])]:
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
links=[];adj=collections.defaultdict(list)
for a,b in itertools.combinations(names,2):
 alo,ahi=bounds[a];blo,bhi=bounds[b]
 if ((alo>bhi+.00002)|(blo>ahi+.00002)).any():continue
 c=contact(a,b)
 if c:links.append({'parts':[str(a),str(b)],**c});adj[a].append(b);adj[b].append(a)
floor=[n for n in names if bounds[n][0][2]<.00002];parents={n:None for n in floor};queue=collections.deque(floor)
while queue:
 a=queue.popleft()
 for b in adj[a]:
  if b not in parents:parents[b]=a;queue.append(b)
gp=ROOT/'assets/clinical_architecture/exports/AST-MED-002.glb';native=Native(gp);native_labels=np.array([str(x).removeprefix('EXPORT_')for x in native.nodes]);nt=native.tris@C;rows=[]
for n in names:
 path=[];x=n
 while x in parents:
  path.append(str(x));x=parents[x]
  if x is None:break
 nv=nt[native_labels==n].reshape(-1,3);v=verts[n];err=float(max(cKDTree(v).query(nv)[0].max(),cKDTree(nv).query(v)[0].max()))if len(nv)else 1e9
 rows.append({'part':str(n),'actual_contact_neighbours':[str(x)for x in adj[n]],'contact_path_to_floor':path if n in parents else [],'source_native_named_part_vertex_hausdorff_m':err,'pass':n in parents and err<1e-6})
res={'passed':all(x['pass']for x in rows),'executed_script_sha256':sha(Path(__file__)),'source':r['path'],'source_sha256':r['sha256'],'export':str(gp.relative_to(ROOT)),'export_sha256':sha(gp),'source_audit_sha256':sha(rp),'tolerance_m':.00002,'floor_parts':[str(x)for x in floor],'all_semantic_parts':rows,'actual_source_contacts':links,'isolated_parts':[x['part']for x in rows if not x['contact_path_to_floor']],'limits':'Actual visual solid-contact connectivity and named native geometry correspondence. Contact is geometric, not fastening details, structural load or service-procedure certification. No extra mechanical clearances are silently exempted. Declared opposing-face mount normals are checked separately.'}
(OUT/'independent_wash_support_graph.json').write_text(json.dumps(res,indent=2)+'\n');print('wash all-part floor-contact graph',res['passed'],'parts',len(rows),'links',len(links),'isolated',res['isolated_parts'])
