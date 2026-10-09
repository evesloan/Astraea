"""Bounded independent binary checks of retained GLBs; no engine/import."""
import json,struct,sys,hashlib
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745'
def read(path):
 b=path.read_bytes();magic,ver,size=struct.unpack_from('<III',b)
 assert (magic,ver,size)==(0x46546c67,2,len(b))
 n,t=struct.unpack_from('<II',b,12);assert t==0x4e4f534a
 j=json.loads(b[20:20+n]);nb,t=struct.unpack_from('<II',b,20+n);assert t==0x004e4942
 return j,b[28+n:28+n+nb]
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']]
 dt=np.dtype({5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
 stride=v.get('byteStride',w*dt.itemsize);off=v.get('byteOffset',0)+a.get('byteOffset',0)
 assert off+(a['count']-1)*stride+w*dt.itemsize<=len(b)
 return np.ndarray((a['count'],w),dtype=dt,buffer=b,offset=off,strides=(stride,dt.itemsize)).copy()
def matrix(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.eye(4)
 r[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(n.get('scale',[1,1,1]));r[:3,3]=n.get('translation',[0,0,0]);return r
def nodes(d):
 def visit(i,m):
  n=d['nodes'][i];m=m@matrix(n)
  if 'mesh' in n:yield n,m
  for c in n.get('children',[]):yield from visit(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:yield from visit(i,np.eye(4))
rows=[]
for r in json.loads((P/'qa/retained_native_census.json').read_text())['natives']:
 source=D/r['source'];f=source.parents[1]/'exports'/source.with_suffix('.glb').name
 d,b=read(f);points=[];triangles=0;count=0;external=[]
 for im in d.get('images',[]):
  if 'uri' in im:external.append(im['uri'])
  else:assert 'bufferView' in im
 for n,m in nodes(d):
  count+=1
  for q in d['meshes'][n['mesh']]['primitives']:
   assert q.get('mode',4)==4
   a=acc(d,b,q['attributes']['POSITION']);assert np.isfinite(a).all();a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3];points.extend(a)
   idx=acc(d,b,q['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a);triangles+=len(idx)//3
   for k in ['NORMAL','TEXCOORD_0']:
    if k in q['attributes']:assert np.isfinite(acc(d,b,q['attributes'][k])).all()
 a=np.array(points);bounds=[a.min(axis=0).tolist(),a.max(axis=0).tolist()]
 delta=float(np.max(np.abs(np.array(bounds)-np.array(r['source_y_up_bounds']))))
 assert triangles==r['evaluated_triangles'] and delta<1e-4 and not external
 rows.append({'export':f.relative_to(D).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_nodes':count,'triangles':triangles,'local_y_up_bounds':bounds,'native_bound_max_error_m':delta,'external_image_dependencies':external})
out={'passed':True,'scope':'Seven retained native/export pairs: binary structure, indices, finite attributes, embedded images, evaluated triangle totals and transformed bounds. Bounds/count equivalence is not full vertex/physics or whole-ship overlap acceptance.','engine_import_run':False,'exports':rows}
(P/'qa/retained_export_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('RETAINED_EXPORT_CHECKS',len(rows),max(r['native_bound_max_error_m'] for r in rows))
