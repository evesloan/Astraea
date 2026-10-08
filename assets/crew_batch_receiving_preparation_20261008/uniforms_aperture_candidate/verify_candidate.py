"""Read-only independent proof. No Blender/Godot, no file writes."""
from pathlib import Path
import struct,json,hashlib,itertools
import numpy as np
R=Path(__file__).resolve().parent
proof=json.loads((R/'RUNTIME_PROOF.json').read_text());source=json.loads((R/'SOURCE_PROOF.json').read_text())
def parse(raw):
 n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);size,tag=struct.unpack_from('<II',raw,20+n);assert tag==0x004e4942;return d,raw[28+n:28+n+size]
def arr(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dtype={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];c={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']];s=np.dtype(dtype).itemsize
 return np.ndarray((a['count'],c),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',c*s),s))
raw=(R/'AST-CIR-005_aft_uniforms_d03.glb').read_bytes();assert hashlib.sha256(raw).hexdigest()==proof['successor_glb_sha256'];d,b=parse(raw)
inverse=(R/'inverse_original_header.bin').read_bytes()+b[:proof['original_binary_length']]
assert hashlib.sha256(inverse).hexdigest()==proof['original_glb_sha256'];old,ob=parse(inverse)
assert hashlib.sha256(Path(proof['original_glb_path']).read_bytes()).hexdigest()==proof['original_glb_sha256']
assert hashlib.sha256(Path(source['original_path']).read_bytes()).hexdigest()==source['original_sha256']
assert hashlib.sha256((R/'AST-CIR-005_aft_uniforms_d03.blend').read_bytes()).hexdigest()==source['successor_sha256']
for k in ['materials','images','textures','samplers']:assert old.get(k)==d.get(k)
assert d['nodes'][:len(old['nodes'])]==old['nodes']
for m,om in enumerate(old['meshes']):
 op=om['primitives'][0];np_=d['meshes'][m]['primitives'][0]
 assert op['attributes']==np_['attributes'] and op['material']==np_['material']
 for k,i in op['attributes'].items():assert np.array_equal(arr(old,ob,i),arr(d,b,i))
 indices=arr(old,ob,op['indices']).reshape(-1,3);changed=next((q for q in proof['removed']if q['mesh']==m),None)
 if changed:indices=np.delete(indices,changed['removed_triangle_ordinals'],axis=0)
 assert np.array_equal(indices,arr(d,b,np_['indices']).reshape(-1,3))
boxes=[]
for node in d['nodes'][len(old['nodes']):]:
 assert not any(k in node for k in ['translation','rotation','scale','matrix']);p=d['meshes'][node['mesh']]['primitives'][0];v=arr(d,b,p['attributes']['POSITION']);ix=arr(d,b,p['indices']).ravel();t=v[ix].reshape(-1,3,3).astype(float);lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));assert len(t)==12
 # For each of six box faces, prove its two triangles exactly cover the rectangle.
 face_counts=[]
 for axis in range(3):
  other=[a for a in range(3)if a!=axis]
  for side in [0,1]:
   val=[lo,hi][side][axis];ts=t[np.all(t[:,:,axis]==val,axis=1)];assert len(ts)==2
   assert len(np.unique(ts.reshape(-1,3),axis=0))==4
   area=np.linalg.norm(np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]),axis=1).sum()/2
   assert abs(area-np.prod((hi-lo)[other]))<1e-9
   cross=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);assert (cross[:,axis]*(1 if side else -1)>0).all()
   face_counts.append(len(ts))
 boxes.append((d['materials'][p['material']]['name'],lo,hi))
for q in proof['removed']:
 lo,hi=np.array(q['actual_bounds']);material=old['materials'][old['meshes'][q['mesh']]['primitives'][0]['material']]['name'];parts=[(a,z) for m,a,z in boxes if m==material]
 assert all((a>=lo).all()and(z<=hi).all() for a,z in parts)
 planes=[sorted(set([lo[i],hi[i]]+[v[i] for part in parts for v in part])) for i in range(3)]
 for cell in itertools.product(*[list(zip(p[:-1],p[1:])) for p in planes]):
  centre=np.array([sum(p)/2 for p in cell]);count=sum(int(((centre>a)&(centre<z)).all()) for a,z in parts)
  void=-2<centre[2]<2 and 12<=centre[1]<float(np.float32(14.65));assert count==(0 if void else 1)
assert all(source['successor_object_fingerprints'][k]==v for k,v in source['original_object_fingerprints'].items()if k not in source['removed_objects'])
print('PASS: inverse original byte hash, originals untouched, retained geometry and material exact, six-face replacement cuboids, outside-aperture solid partition, source888-object fingerprints.')
