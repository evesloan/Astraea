import json,struct
from pathlib import Path
import numpy as np
def decode(p):
 b=Path(p).read_bytes(); assert b[:4]==b'glTF' and struct.unpack_from('<II',b,4)==(2,len(b))
 o=12;chunks={}
 while o<len(b):
  n,t=struct.unpack_from('<II',b,o);o+=8;assert o+n<=len(b);chunks[t]=b[o:o+n];o+=n
 assert o==len(b)
 j=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];d=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]);assert 'sparse'not in a
  assert v.get('buffer',0)==0
  return np.ndarray((a['count'],c),dtype=d,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',d.itemsize*c),d.itemsize)).copy()
 marks={};triangles=[];materials=[]
 def visit(i,M,seen):
  assert i not in seen;seen=seen|{i};n=j['nodes'][i]
  if 'matrix'in n:m=np.array(n['matrix']).reshape(4,4,order='F')
  else:
   x,y,z,w=n.get('rotation',(0,0,0,1));m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',(1,1,1)));m[:3,3]=n.get('translation',(0,0,0))
  m=M@m;name=n.get('name','');assert np.isfinite(m).all()
  if name.startswith('DATUM_'):assert name not in marks;marks[name]=m[:3,3]
  if 'mesh'in n:
   for p in j['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4;v=acc(p['attributes']['POSITION']);q=(np.c_[v,np.ones(len(v))]@m.T)[:,:3];ix=acc(p['indices']).reshape(-1);assert len(ix)%3==0 and max(ix)<len(v);tr=q[ix].reshape(-1,3,3);assert np.isfinite(tr).all();triangles.append(tr);materials.extend([n.get('name','')+'|'+j.get('materials',[])[p['material']]['name']]*len(tr))
  for c in n.get('children',[]):visit(c,m,seen)
 for i in j['scenes'][j.get('scene',0)]['nodes']:visit(i,np.eye(4),set())
 return j,np.concatenate(triangles),marks,materials
