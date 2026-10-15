from pathlib import Path
import numpy as np,json,struct,hashlib,collections
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');helper=Path('/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/verify_rigid_r010.py').read_text();exec(helper[helper.index('def load('):helper.index('verified=0;')]);r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());o,ob=load(G/'assets/models/G8_CROWN_INTERIORS_r006.glb');n,nb=load(D/'import/Game/assets/fitted_upper_horizon_20261015'/r['file'])
for row in r['batches']:assert faces(o,ob,row['name'])==faces(n,nb,row['name']),row['name']
assert images(n,nb)<=images(o,ob)
# Independentlycompare world triangles/UV fromthe320 editable objects againstthe70 optimized batches.
def world_faces(j,b):
 parents={c:i for i,node in enumerate(j['nodes'])for c in node.get('children',[])};cache={}
 def matrix(i):
  if i in cache:return cache[i]
  node=j['nodes'][i]
  if'matrix'in node:M=np.array(node['matrix']).reshape((4,4),order='F')
  else:
   M=np.eye(4);x,y,z,w=node.get('rotation',[0,0,0,1]);M[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(node.get('scale',[1,1,1]));M[:3,3]=node.get('translation',[0,0,0])
  cache[i]=(matrix(parents[i])if i in parents else np.eye(4))@M;return cache[i]
 out=[]
 for i,node in enumerate(j['nodes']):
  if'mesh'not in node:continue
  for p in j['meshes'][node['mesh']]['primitives']:
   vs=acc(j,b,p['attributes']['POSITION']);uv=acc(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));world=(np.c_[vs,np.ones(len(vs))]@matrix(i).T)[:,:3];ix=acc(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs))
   for tri in ix.reshape(-1,3):out.append(tuple(sorted(tuple(float(v)for v in np.r_[world[k],uv[k]])for k in tri)))
 return np.array(out)
a,ab=load(D/'FITTED_UPPER_HORIZON_r001_authoring.glb');A=world_faces(a,ab);N=world_faces(n,nb)
from scipy.spatial import cKDTree
from itertools import permutations
assert A.shape==N.shape;tree=cKDTree(N.mean(axis=1));used=set();max_position=0.;max_uv=0.;perms=list(permutations(range(3)))
for tri in A:
 matched=False
 for index in tree.query_ball_point(tri.mean(axis=0),.00023):
  if index in used:continue
  for perm in perms:
   delta=np.abs(tri-N[index,list(perm)])
   if np.max(delta[:,:3])<=.0001 and np.max(delta[:,3:])<=.0001:
    used.add(index);max_position=max(max_position,float(np.max(delta[:,:3])));max_uv=max(max_uv,float(np.max(delta[:,3:])));matched=True;break
  if matched:break
 assert matched,('Actual coordinate/UV discrepancy exceeds0.1mm tolerance',tri.tolist())
assert len(used)==len(N)
report={'status':'PASS_70_SOURCE_BATCH_LOCAL_TRIANGLES_UV_IMAGE_BYTES_AND_320_AUTHORING_WORLD_GEOMETRY','rigid_source_runtime_batches':70,'editable_individual_authoring_meshes':320,'world_triangles_with_uv':len(A),'actual_position_uv_tolerance':.0001,'maximum_world_position_difference_m':max_position,'maximum_uv_difference':max_uv,'comparison':'One-to-one numeric triangle-corner matching;initial decimal-bucket comparison rejected1552 bucket-edge entries despite sub-tolerance float differences. Exact failed verifier retained.','embedded_source_image_bytes':len(images(n,nb)),'new_capacity_or_source_overwrite':False};(D/'SOURCE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
