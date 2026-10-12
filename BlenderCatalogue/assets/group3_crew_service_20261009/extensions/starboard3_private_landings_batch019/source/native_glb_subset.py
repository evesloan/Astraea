"""Read only named native GLB meshes; no whole-platform adoption or cache."""
from pathlib import Path
import json,struct
class GLB:
 def __init__(self,path):
  self.path=Path(path);self.raw=self.path.read_bytes();assert self.raw[:4]==b'glTF';n=struct.unpack_from('<I',self.raw,12)[0];self.doc=json.loads(self.raw[20:20+n]);self.bin=self.raw[28+n:];self.by_name={q['name']:q for q in self.doc['nodes']if'name'in q};self.parent_by_identity={id(self.doc['nodes'][i]):q for q in self.doc['nodes']for i in q.get('children',[])}
 def accessor(self,i):
  a=self.doc['accessors'][i];v=self.doc['bufferViews'][a['bufferView']];fmt={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=struct.calcsize(fmt)*n;offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
  return [struct.unpack_from('<'+fmt*n,self.bin,offset+k*stride)for k in range(a['count'])]
 def named(self,name):
  return self.by_name[name]
 def transform(self,q,p):
  if 'matrix' in q:
   m=q['matrix'];return tuple(sum(m[c*4+r]*p[c]for c in range(3))+m[12+r]for r in range(3))
  v=[p[i]*q.get('scale',[1,1,1])[i]for i in range(3)];x,y,z,w=q.get('rotation',[0,0,0,1]);a,b,c=v
  rotated=[(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*c,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*c,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*c]
  return tuple(rotated[i]+q.get('translation',[0,0,0])[i]for i in range(3))
 def global_transform(self,q,p):
  p=self.transform(q,p);parent=self.parent_by_identity.get(id(q))
  return self.global_transform(parent,p)if parent else p
 def geometry(self,name):
  q=self.named(name);vs,fs,uvs=[],[],[]
  for p in self.doc['meshes'][q['mesh']]['primitives']:
   assert p.get('mode',4)==4
   base=len(vs);v=self.accessor(p['attributes']['POSITION']);idx=[q[0]for q in self.accessor(p['indices'])];uv=self.accessor(p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else[(0,0)]*len(v);vs.extend(self.global_transform(q,r)for r in v)
   for i in range(0,len(idx),3):fs.append(tuple(base+k for k in idx[i:i+3]));uvs.extend(uv[k]for k in idx[i:i+3])
  return vs,fs,uvs,q.get('extras',{})
 def bounds(self,name,offset=(0,0,0)):
  v=self.geometry(name)[0];return [f(c[k]+offset[k]for c in v)for k in range(3)for f in [min,max]]
