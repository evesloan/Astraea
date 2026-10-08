from pathlib import Path
import ast,json,numpy as np,struct
S=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game/data/architecture/packages/upper_hull/screen_source_readiness.py').read_text();fn=next(n for n in ast.parse(S).body if isinstance(n,ast.FunctionDef)and n.name=='glb');e={'np':np,'json':json,'struct':struct,'DT':{5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<decoder>','exec'),e)
R=Path(__file__).resolve().parent;m=e['glb'](R/'exports/AST-HUL-002.glb');n,a,idx=next(x for x in m if x[0]=='HUL2_FullShoulderSkin');v=np.unique(np.round(a,5),axis=0)
ys=[61,69.5,87.5,92];zs=[-275,-265,-115,-105];xs=[[-120]*4,[-118.2,-118.5,-118.5,-118.2],[-111.4,-118.5,-118.5,-111.4],[-109.6]*4];outer=np.array([(xs[j][i],y,z)for j,y in enumerate(ys)for i,z in enumerate(zs)]);inner=[]
for q in v:
 dist=np.linalg.norm(outer-q,axis=1)
 if dist.min()>.0001:inner.append((int(dist.argmin()),q))
rows=[]
for j in range(3):
 for i in range(3):
  q=j*4+i
  for ids in [(q,q+1,q+5),(q,q+5,q+4)]:
   t=outer[list(ids)];normal=np.cross(t[1]-t[0],t[2]-t[0]);normal/=np.linalg.norm(normal)
   if normal[0]<0:normal=-normal
   for k,p in inner:
    if k in ids:rows.append({'vertex':k,'offset':float((p-t[0])@normal)})
o={'closed_shell_vertices':len(v),'inner_vertices':len(inner),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'normal_offsets_minmax':[min(x['offset']for x in rows),max(x['offset']for x in rows)],'max_normal_offset_error':max(abs(x['offset']-.18)for x in rows),'source_only':True};(R/'NORMAL_THICKNESS_SCREEN.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
for name,verts,indices in m:
 edges={}
 for t in verts[indices]:
  assert np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-8
  k=[tuple(np.round(p,5))for p in t]
  for j in range(3):
   edge=tuple(sorted((k[j],k[(j+1)%3])));edges[edge]=edges.get(edge,0)+1
 assert all(x==2 for x in edges.values()),name
(R/'ACTUAL_SKIN_TRIANGLES.json').write_text(json.dumps({'triangles':a[idx].tolist()}))
