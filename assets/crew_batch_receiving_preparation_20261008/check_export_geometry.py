from pathlib import Path
import json,struct,hashlib,numpy as np
R=Path(__file__).resolve().parent;reports=[]
for item in json.loads((R/'INTAKE.json').read_text()):
 raw=Path(item['glb']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['glb']['sha256'];ln=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+ln]);off=20+ln;bn,bt=struct.unpack_from('<II',raw,off);assert bt==0x004e4942;binary=raw[off+8:off+8+bn]
 def accessor(idx):
  a=d['accessors'][idx];assert 'sparse'not in a;v=d['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0;dt={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=np.dtype(dt).itemsize;stride=v.get('byteStride',nc*size);return np.ndarray((a['count'],nc),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,size)).copy()
 def matrix(n):
  if 'matrix'in n:return np.array(n['matrix'],dtype=float).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 lower=np.full(3,np.inf);upper=np.full(3,-np.inf);triangles=0;instances=0;preview=[];visited=set()
 def walk(i,parent):
  global lower,upper,triangles,instances
  assert i not in visited;visited.add(i);n=d['nodes'][i];m=parent@matrix(n)
  if 'mesh'in n:
   instances+=1
   if 'preview'in n.get('name','').lower():preview.append(n['name'])
   for p in d['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4;v=accessor(p['attributes']['POSITION']).astype(float);norm=accessor(p['attributes']['NORMAL']);uv=accessor(p['attributes']['TEXCOORD_0']);assert len(v)==len(norm)==len(uv);assert np.isfinite(v).all() and np.isfinite(norm).all() and np.isfinite(uv).all();assert (np.linalg.norm(norm,axis=1)>.9).all();w=(np.column_stack((v,np.ones(len(v))))@m.T)[:,:3];lower=np.minimum(lower,w.min(axis=0));upper=np.maximum(upper,w.max(axis=0));ids=accessor(p['indices']).ravel() if 'indices'in p else np.arange(len(v));assert len(ids)%3==0 and int(ids.max())<len(v);triangles+=len(ids)//3
  for ch in n.get('children',[]):walk(ch,m)
 for n in d['scenes'][d.get('scene',0)]['nodes']:walk(n,np.eye(4))
 x0,x1,z0,z1=item['placement']['boundary'];assert all(lower>=np.array([x0,12,z0])-.001) and all(upper<=np.array([x1,15.34,z1])+.001);assert not preview
 reports.append({'programme':item['programme'],'sha256':item['glb']['sha256'],'actual_instanced_triangles':triangles,'mesh_instances':instances,'world_bounds':[lower.tolist(),upper.tolist()],'finite_positions_normals_uvs':True,'preview_named_meshes':preview,'contained':True})
(R/'GLB_GEOMETRY_SCREEN.json').write_text(json.dumps({'scope':'Independent actual binary accessor and scene-transform checks; no Godot import or traversal claim','sections':reports},indent=2)+'\n');print(json.dumps(reports))
