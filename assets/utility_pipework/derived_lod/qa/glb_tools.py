"""Small read-only glTF 2.0 accessor/node parser, plus new-file GLB writer."""
import json,struct,copy
from pathlib import Path
import numpy as np
COMP={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
WIDTH={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def read(path):
 raw=Path(path).read_bytes();magic,ver,total=struct.unpack_from('<4sII',raw);assert magic==b'glTF' and ver==2 and total==len(raw)
 n,k=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);off=20+n;bn,bk=struct.unpack_from('<II',raw,off);assert bk==0x004e4942;return d,raw[off+8:off+8+bn]
def accessor(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];code,size=COMP[a['componentType']];w=WIDTH[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',w*size)
 return np.array([struct.unpack_from('<'+code*w,b,off+j*stride)for j in range(a['count'])])
def matrix(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
 m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
def worlds(d):
 out={}
 def walk(i,p):
  out[i]=p@matrix(d['nodes'][i])
  for j in d['nodes'][i].get('children',[]):walk(j,out[i])
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return out
def primitives(d,b):
 for i,m in worlds(d).items():
  n=d['nodes'][i]
  if 'mesh'not in n:continue
  for p in d['meshes'][n['mesh']]['primitives']:
   v=accessor(d,b,p['attributes']['POSITION']);ix=accessor(d,b,p['indices']).reshape(-1,3).astype(int);world=(m@np.c_[v,np.ones(len(v))].T).T[:,:3]
   yield i,p,v,ix,world,m
class Writer:
 def __init__(self,source=None,blob=None):
  self.d={'asset':{'version':'2.0','generator':'ASTRAEA bounded actual-GLB geometry extraction'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[]};self.b=bytearray()
  if source:
   for key in('materials','textures','samplers','extensionsUsed','extensionsRequired'): 
    if key in source:self.d[key]=copy.deepcopy(source[key])
   self.d['images']=[]
   for im in source.get('images',[]):
    x=copy.deepcopy(im);bv=source['bufferViews'][x['bufferView']];start=bv.get('byteOffset',0);x['bufferView']=self.view(blob[start:start+bv['byteLength']]);self.d['images'].append(x)
 def view(self,raw):
  self.b.extend(b'\0'*((-len(self.b))%4));i=len(self.d['bufferViews']);self.d['bufferViews'].append({'buffer':0,'byteOffset':len(self.b),'byteLength':len(raw)});self.b.extend(raw);return i
 def attr(self,a,kind,component=5126):
  a=np.asarray(a);dtype='<f4' if component==5126 else '<u4';idx=len(self.d['accessors']);r={'bufferView':self.view(a.astype(dtype).tobytes()),'componentType':component,'count':len(a),'type':kind}
  if kind=='VEC3':r.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  self.d['accessors'].append(r);return idx
 def write(self,path):
  self.d['buffers']=[{'byteLength':len(self.b)}];j=json.dumps(self.d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);bb=bytes(self.b)+b'\0'*((-len(self.b))%4);raw=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(bb))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(bb),0x004e4942)+bb;Path(path).write_bytes(raw)
