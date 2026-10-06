"""Independent pure GLB geometry queries; no engine/imports or production writes."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
PRISMS={'north_cart_strip':[20,6,-454.6,53.7,8.7,-451],'south_cart_strip':[20,6,-413,53.7,8.7,-409.4],'east_cart_strip':[48.3,6,-465.7,53.7,9.6,-398.3],'control_turn':[28.2,6,-460.8,31.8,8.7,-457.2],'workbay_turn':[28.2,6,-406.8,31.8,8.7,-403.2],'control_operating_face':[21.9,6,-462.4,30.1,8.4,-460.9]}
def glb(path):
 b=Path(path).read_bytes();magic,version,total=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and total==len(b)
 chunks={};offset=12
 while offset<len(b):
  size,kind=struct.unpack_from('<II',b,offset);chunks[kind]=b[offset+8:offset+8+size];offset+=8+size
 doc=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
 def accessor(index):
  a=doc['accessors'][index];assert 'sparse' not in a
  bv=doc['bufferViews'][a['bufferView']];dtype={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
  k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=np.dtype(dtype).itemsize;off=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',k*size)
  return np.ndarray((a['count'],k),dtype=dtype,buffer=blob,offset=off,strides=(stride,size)).astype(float)
 nodes=[];meshes=[]
 def walk(index,parent):
  n=doc['nodes'][index]
  if 'matrix'in n:m=np.array(n['matrix']).reshape(4,4).T
  else:
   x,y,z,w=n.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
   m=np.eye(4);m[:3,:3]=rot@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
  m=parent@m;name=n.get('name',str(index));nodes.append({'name':name,'node_index':index,'world_matrix':m,'extras':n.get('extras',{})})
  if 'mesh'in n:
   for pi,p in enumerate(doc['meshes'][n['mesh']]['primitives']):
    assert p.get('mode',4)==4
    v=accessor(p['attributes']['POSITION']);idx=accessor(p['indices']).ravel().astype(int).reshape(-1,3) if 'indices'in p else np.arange(len(v)).reshape(-1,3);world=(np.c_[v,np.ones(len(v))]@m.T)[:,:3]
    meshes.append({'node':name,'primitive':pi,'triangles':world[idx],'material':doc.get('materials',[])[p['material']].get('name','') if 'material'in p else None,'extras':n.get('extras',{}),'indices':idx,'normals':accessor(p['attributes']['NORMAL']) if 'NORMAL'in p['attributes'] else None,'uv':accessor(p['attributes']['TEXCOORD_0']) if 'TEXCOORD_0'in p['attributes'] else None})
  for c in n.get('children',[]):walk(c,m)
 for index in doc['scenes'][doc.get('scene',0)]['nodes']:walk(index,np.eye(4))
 return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'doc':doc,'meshes':meshes,'nodes':nodes}
class Query:
 def __init__(self,meshes):
  self.meshes=meshes;self.tri=np.concatenate([m['triangles'] for m in meshes]);self.owner=np.concatenate([np.full(len(m['triangles']),i) for i,m in enumerate(meshes)]);self.e1=self.tri[:,1]-self.tri[:,0];self.e2=self.tri[:,2]-self.tri[:,0]
 def rays(self,a,b,minimum=1e-6):
  a=np.array(a,dtype=float);d=np.array(b,dtype=float)-a;length=np.linalg.norm(d);assert length>0;d/=length
  h=np.cross(d,self.e2);det=np.einsum('ij,ij->i',self.e1,h);good=abs(det)>1e-11;inv=np.zeros(len(det));inv[good]=1/det[good];s=a-self.tri[:,0];u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,self.e1);v=q@d*inv;t=np.einsum('ij,ij->i',self.e2,q)*inv
  indices=np.flatnonzero(good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=minimum)&(t<=length+1e-7));indices=indices[np.argsort(t[indices])]
  return [{'node':self.meshes[int(self.owner[i])]['node'],'primitive':self.meshes[int(self.owner[i])]['primitive'],'distance_m':float(t[i]),'position_xyz':(a+t[i]*d).tolist(),'triangle_index':int(i),'triangle_xyz':self.tri[i].tolist()} for i in indices]
 def prism_hits(self,box,tolerance=1e-5):
  lo=np.array(box[:3])+tolerance;hi=np.array(box[3:])-tolerance
  # A planar triangle strictly inside a prism MUST remain a candidate.
  candidates=np.flatnonzero(np.all(self.tri.max(1)>lo,axis=1)&np.all(self.tri.min(1)<hi,axis=1));hits=[]
  for i in candidates:
   polygon=list(self.tri[i])
   for axis,edge,sign in [(axis,edge,sign) for axis in range(3) for edge,sign in [(lo[axis],1),(hi[axis],-1)]]:
    clipped=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
     ia=sign*(a[axis]-edge)>=0;ib=sign*(b[axis]-edge)>=0
     if ia:clipped.append(a)
     if ia!=ib:clipped.append(a+(b-a)*(edge-a[axis])/(b[axis]-a[axis]))
    polygon=clipped
    if len(polygon)<3:break
   if len(polygon)>=3:
    area=sum(np.linalg.norm(np.cross(polygon[j]-polygon[0],polygon[j+1]-polygon[0])) for j in range(1,len(polygon)-1))
    if area>1e-12:hits.append({'triangle_index':int(i),'node':self.meshes[int(self.owner[i])]['node']})
  return hits
if __name__=='__main__':
 # Unit witnesses: axis-aligned triangle inside counts; boundary/outside does not.
 inside=np.array([[[.5,.2,.2],[.5,.8,.2],[.5,.2,.8]]]);q=Query([{'triangles':inside,'node':'inside','primitive':0}]);assert len(q.prism_hits([0,0,0,1,1,1]))==1
 for x in [0,1,1.1]:
  t=inside.copy();t[:,:,0]=x;assert not Query([{'triangles':t,'node':'boundary','primitive':0}]).prism_hits([0,0,0,1,1,1])
 print('Independent geometry-query unit witnesses pass.')
