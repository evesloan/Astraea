from pathlib import Path
import numpy as np,json,struct,hashlib,collections
D=Path(__file__).resolve().parent
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);out=[]
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=acc(j,b,p['attributes']['POSITION']);uv=acc(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=acc(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs));out +=[tuple(sorted(tuple(round(float(x),4)for x in np.r_[vs[i],uv[i]])for i in tri))for tri in ix.reshape(-1,3)]
 return collections.Counter(out)
def images(j,b):
 out=[]
 for row in j.get('images',[]):
  v=j['bufferViews'][row['bufferView']];out.append(hashlib.sha256(b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest())
 return set(out)
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
r=json.loads((D/"NATIVE_RECEIVER_VERIFICATION.json").read_text());P=D/"native_import/Game/assets/dining_service_receiving_20261015"
a,ab=load(P/r["raw_authoring_file"]);n,nb=load(P/r["file"]);A=world_faces(a,ab);N=world_faces(n,nb)
assert images(a,ab)==images(n,nb)
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
report={'status':'PASS_ALL_2753_AUTHORING_MESHES_TO_39_RUNTIME_BATCHES_GEOMETRY_UV_AND_IMAGE_BYTES','authoring_meshes':r['authoring_meshes'],'runtime_batches':r['meshes'],'world_triangles_with_uv':len(A),'actual_position_uv_tolerance':.0001,'maximum_world_position_difference_m':max_position,'maximum_uv_difference':max_uv,'embedded_source_image_bytes':len(images(n,nb)),'source_clone_native_geometry_proof':'RIGID_SOURCE_GEOMETRY_VERIFICATION.json'}
(D/'BATCH_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
