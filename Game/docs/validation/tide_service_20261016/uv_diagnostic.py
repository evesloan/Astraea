from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
D=Path('/workspace/Astraea/BlenderCatalogue/assets/tide_service_20261016');G=Path('/workspace/Astraea/Game');receipt=json.loads((D/'NATIVE_VERIFICATION.json').read_text())
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);out=[]
 x,y,z,w=node.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 transform=np.eye(4);transform[:3,:3]=rot@np.diag(node.get('scale',[1,1,1]));transform[:3,3]=node.get('translation',[0,0,0])
 if 'matrix'in node:transform=np.array(node['matrix']).reshape(4,4).T
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=accessor(j,b,p['attributes']['POSITION']);uv=accessor(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=accessor(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs))
  out += [[{'p':(transform@np.r_[vs[i].astype(float),1])[:3],'uv':uv[i].astype(float)}for i in tri]for tri in ix.reshape(-1,3)]
 return out

def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k]+(e[k]-s[k])*t for k in ['p','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out

def cut(poly,z):
 pieces=[];inside=poly
 for axis,plane,less in[(1,61.,False),(1,64.2,True),(2,z-1.7,False),(2,z+1.7,True)]:
  p=clip(inside,axis,plane,not less)
  if len(p)>=3:pieces.append(p)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
def subtract(tri):
 polys=[tri]
 for z in [-12.,12.]:polys=[part for poly in polys for part in cut(poly,z)]
 return [[poly[0],poly[i],poly[i+1]]for poly in polys for i in range(1,len(poly)-1)]
def key(tri):return tuple(sorted(tuple(round(float(x),4)for x in np.r_[v['p'],v['uv']])for v in tri))
from shapely.geometry import Polygon
from shapely.ops import unary_union
a,ab=load(G/'assets/models/SOL_D10_directory_05_entry001.glb');n,nb=load(D/'exports/TIDE_SERVICE_RECEIVER_r001.glb');results=[]

row=receipt['walls'][0];source=faces(a,ab,row['source_name']);q={'p':np.array([-95.16683602,64.19999695,-23.98682125]),'uv':np.array([.51785737,1.])};best=[]
for old in source:
 v0,v1,v2=[v['p']for v in old];mat=np.column_stack((v1-v0,v2-v0));w=np.linalg.lstsq(mat,q['p']-v0,rcond=None)[0];weights=np.maximum(np.array([1-sum(w),w[0],w[1]]),0);weights/=sum(weights);closest=sum(weights[i]*old[i]['p']for i in range(3));uv=sum(weights[i]*old[i]['uv']for i in range(3));err=np.linalg.norm(closest-q['p']);ue=np.linalg.norm(uv-q['uv']);best.append((err,ue,str(w),str(uv),str(old)))
for row in sorted(best)[:3]:print(row)
