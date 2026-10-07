"""Decode retained GLB bytes and measure only; no engine, import or authoring."""
from pathlib import Path
import json, struct, hashlib, math
import numpy as np

OUT=Path(__file__).parent
ROOT=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x')
CIN=OUT/'WP13_FULL/WP13_D11_directory_02'
LIB=OUT/'WP06_FULL/WP06_D12_directory_02'
def glb(path, offset):
 b=path.read_bytes(); magic,ver,total=struct.unpack_from('<III',b);assert magic==0x46546c67 and ver==2 and total==len(b)
 pos=12;chunks={}
 while pos<len(b):
  n,k=struct.unpack_from('<II',b,pos);pos+=8;chunks[k]=b[pos:pos+n];pos+=n
 d=json.loads(chunks[0x4e4f534a]);raw=chunks[0x004e4942]
 types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
 cache={}
 def acc(i):
  if i in cache:return cache[i]
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];t=np.dtype(types[a['componentType']]);c=counts[a['type']];n=a['count'];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',t.itemsize*c)
  assert not a.get('sparse')
  q=np.ndarray((n,c),dtype=t,buffer=raw,offset=start,strides=(stride,t.itemsize)).copy();cache[i]=q;return q
 def matrix(n):
  if 'matrix'in n:return np.array(n['matrix']).reshape(4,4,order='F')
  x,y,z,w=n.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
  m=np.eye(4);m[:3,:3]=rot@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 meshes=[];nodes=[]
 def walk(i,parent):
  n=d['nodes'][i];m=parent@matrix(n);name=n.get('name',str(i));nodes.append({'name':name,'extras':n.get('extras',{}),'origin':(m[:3,3]+offset).tolist()})
  if 'mesh'in n:
   vv=[];ff=[];base=0
   for p in d['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4
    v=acc(p['attributes']['POSITION']).astype(float);v=(v@m[:3,:3].T)+m[:3,3]+offset
    f=acc(p['indices']).reshape(-1,3).astype(int) if 'indices'in p else np.arange(len(v)).reshape(-1,3)
    vv.append(v);ff.append(f+base);base+=len(v)
   v=np.concatenate(vv);f=np.concatenate(ff)
   meshes.append({'name':name,'extras':n.get('extras',{}),'vertices':v,'faces':f,'min':v.min(axis=0),'max':v.max(axis=0)})
  for j in n.get('children',[]):walk(j,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return meshes,nodes
def bounds(m):return {'name':m['name'],'min_xyz':m['min'].tolist(),'max_xyz':m['max'].tolist(),'vertices':len(m['vertices']),'triangles':len(m['faces'])}
def rayhits(meshes, a,b, ignored=()):
 a=np.array(a);b=np.array(b);dr=b-a;L=np.linalg.norm(dr);dr/=L;res=[]
 for m in meshes:
  if any(m['name'].startswith(i) for i in ignored):continue
  # Segment-AABB rejection, then exact Moller-Trumbore triangle intersection.
  safe=np.where(abs(dr)>1e-14,dr,1e-14);t0=(m['min']-a)/safe;t1=(m['max']-a)/safe
  if max(0,np.minimum(t0,t1).max())>min(L,np.maximum(t0,t1).min()):continue
  t=m['vertices'][m['faces']];e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(dr,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-9
  inv=np.zeros_like(det);inv[good]=1/det[good];s=a-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=(q@dr)*inv;tt=np.einsum('ij,ij->i',e2,q)*inv
  valid=good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(tt>1e-4)&(tt<L-1e-4)
  if valid.any():
   dist=float(tt[valid].min());res.append({'name':m['name'],'distance':dist,'point_xyz':(a+dist*dr).tolist()})
 return sorted(res,key=lambda x:x['distance'])
if __name__=='__main__':
 cm,cn=glb(CIN/'exports/WP13_cinema1.glb',np.array([11,69.5,-468]));lm,ln=glb(LIB/'exports/WP06_long_library.glb',np.array([8,78,-466]))
 (OUT/'CINEMA_MESH_BOUNDS.json').write_text(json.dumps([bounds(m)for m in cm],indent=2))
 (OUT/'LIBRARY_MESH_BOUNDS.json').write_text(json.dumps([bounds(m)for m in lm],indent=2))
 roles=[n for n in cn if n['extras'].get('place_id')]
 optical=[];lens=np.array([36,73.68,-416.025])
 for x in [23,36,49]:
  for y in [70.7,73.2,75.7]:
   end=[x,y,-459.47];optical.append({'origin_xyz':lens.tolist(),'screen_xyz':end,'hits':rayhits(cm,lens,end,ignored=('PROJECTOR_','BOOTH_projection_glass','SCREEN_original_'))})
 r={'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in[CIN/'exports/WP13_cinema1.glb',CIN/'source/WP13_cinema1.blend',LIB/'exports/WP06_long_library.glb']},'cinema_mesh_count':len(cm),'cinema_triangles':sum(len(m['faces'])for m in cm),'library_mesh_count':len(lm),'library_triangles':sum(len(m['faces'])for m in lm),'role_count':len(roles),'roles':roles,'projection_nine_ray_sample':optical,'bounds':{'cinema':[np.min([m['min']for m in cm],axis=0).tolist(),np.max([m['max']for m in cm],axis=0).tolist()],'library':[np.min([m['min']for m in lm],axis=0).tolist(),np.max([m['max']for m in lm],axis=0).tolist()]}}
 (OUT/'DECODED_GEOMETRY_EVIDENCE.json').write_text(json.dumps(r,indent=2))
 print(json.dumps({k:v for k,v in r.items()if k!='roles'},indent=2))
