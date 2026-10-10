from pathlib import Path
import json, math, struct, hashlib, numpy as np
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
O=W
# Full-read exact-ID ownership assertion before assigning this new source family.
cat=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
ids=['AST-TRM-G4-018']
def entries(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and x in ids: raise AssertionError('ID already exists: '+x)
   entries(x)
 elif isinstance(v,list):
  for x in v:entries(x)
entries(cat)
PIN=[]
def read(p):
 PIN.append(p);return (R/p).read_bytes()
def accessor(d,b,n):
 a=d['accessors'][n];v=d['bufferViews'][a['bufferView']];dt={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 return np.ndarray((a['count'],width),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*width),np.dtype(dt).itemsize)).copy()
def triangles(file,at=(0,0,0),yaw=0):
 raw=read('Game/assets/models/'+file);ln=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+ln]);b=raw[28+ln:]
 def local(node):
  if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
  x,y,z,w=node.get('rotation',[0,0,0,1]);rr=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
  mat=np.eye(4);mat[:3,:3]=rr@np.diag(node.get('scale',[1,1,1]));mat[:3,3]=node.get('translation',[0,0,0]);return mat
 world={}
 def walk(i,parent):
  assert i not in world,'ambiguous multi-parent glTF node'
  world[i]=parent@local(d['nodes'][i])
  for ch in d['nodes'][i].get('children',[]):walk(ch,world[i])
 roots=d.get('scenes',[{'nodes':list(range(len(d['nodes'])))}])[d.get('scene',0)]['nodes']
 for i in roots:walk(i,np.eye(4))
 for ni,node in enumerate(d['nodes']):
  if 'mesh' not in node or ni not in world:continue
  for prim in d['meshes'][node['mesh']]['primitives']:
   pts=accessor(d,b,prim['attributes']['POSITION']).astype(float);pts=(np.column_stack([pts,np.ones(len(pts))])@world[ni].T)[:,:3];x=pts[:,0].copy();z=pts[:,2].copy();pts[:,0]=x*math.cos(yaw)+z*math.sin(yaw);pts[:,2]=-x*math.sin(yaw)+z*math.cos(yaw);pts+=np.array(at)
   ids=accessor(d,b,prim['indices']).reshape(-1) if 'indices' in prim else np.arange(len(pts))
   yield node.get('name','mesh'),pts[ids.reshape(-1,3)]
def contacts(tris,p,r,ylo,yhi):
 lo=tris.min(axis=1);hi=tris.max(axis=1);mask=(lo[:,1]<yhi)&(hi[:,1]>ylo);lo=lo[mask];hi=hi[mask];result=np.zeros(len(lo),dtype=bool)
 for a,b in zip(p,p[1:]):
  t0=np.zeros(len(lo));t1=np.ones(len(lo));valid=np.ones(len(lo),dtype=bool)
  for idx,axis in [(0,0),(1,2)]:
   delta=b[idx]-a[idx];mn=lo[:,axis]-r;mx=hi[:,axis]+r
   if abs(delta)<1e-12:valid&=(a[idx]>=mn)&(a[idx]<=mx)
   else:
    u=(mn-a[idx])/delta;v=(mx-a[idx])/delta;t0=np.maximum(t0,np.minimum(u,v));t1=np.minimum(t1,np.maximum(u,v));valid&=t0<=t1
  result|=valid
 return int(result.sum())
