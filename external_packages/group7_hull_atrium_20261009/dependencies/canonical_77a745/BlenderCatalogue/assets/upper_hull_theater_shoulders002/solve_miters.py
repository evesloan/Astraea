from pathlib import Path
import numpy as np,json,itertools
R=Path(__file__).resolve().parent;ys=[61,69.5,87.5,92];zs=[-275,-265,-115,-105];xs=[[-120]*4,[-118.2,-118.5,-118.5,-118.2],[-111.4,-118.5,-118.5,-111.4],[-109.6]*4];v=np.array([(xs[j][i],y,z)for j,y in enumerate(ys)for i,z in enumerate(zs)]);faces=[];normals=[]
for j in range(3):
 for i in range(3):
  a=j*4+i
  for ids in [(a,a+1,a+5),(a,a+5,a+4)]:
   t=v[list(ids)];n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
   if n[0]<0:n=-n
   faces.append(ids);normals.append(n)
inner=[];offsets=[]
for k,p in enumerate(v):
 ns=np.array([n for f,n in zip(faces,normals)if k in f]);eq=[]
 if k//4 in [0,3]:eq.append([0,1,0])
 if k%4 in [0,3]:eq.append([0,0,1])
 best=None
 for count in range(1,4):
  for active in itertools.combinations(range(len(ns)),count):
   A=np.array([*eq,*ns[list(active)]]);b=np.array([0]*len(eq)+[.18]*count);d=np.linalg.lstsq(A,b,rcond=None)[0]
   if np.max(np.abs(A@d-b))>1e-8 or np.any(ns@d<.18-1e-8):continue
   if best is None or np.linalg.norm(d)<np.linalg.norm(best):best=d
 assert best is not None
 inner.append((p+best).tolist());offsets.extend((ns@best).tolist())
o={'outer_vertices_world':v.tolist(),'inner_vertices_world':inner,'outer_triangles':faces,'normal_skin_min':min(offsets),'normal_skin_max_at_miter':max(offsets),'boundary_planes_preserved':True,'all_inner_vertices_inside_0_4m_material_band':max(offsets)<.4,'interpretation':'Nominal0.18m skin with explicitly thickened miter junctions inside the existing0.4m skin/frame band. No change to0.8m total exclusion or routes.'};(R/'EXACT_MITER_VERTICES.json').write_text(json.dumps(o,indent=2)+'\n');print({k:v for k,v in o.items()if 'vertices'not in k and 'triangles'not in k})
