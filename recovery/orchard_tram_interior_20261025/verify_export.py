"""Read-only GLB roundtrip checks. Does not import or launch an engine."""
from pathlib import Path
import json, struct, hashlib, sys
import numpy as np
R=Path(__file__).resolve().parents[2]
D=R/'Game/orchard_tram_interior_20261025/r002'

def load(path):
 raw=path.read_bytes(); n=struct.unpack_from('<I',raw,12)[0]
 doc=json.loads(raw[20:20+n]); binary=raw[28+n:]
 def acc(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
  assert 'sparse' not in a
  typ={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
  width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]; item=np.dtype(typ).itemsize
  return np.ndarray((a['count'],width),dtype=typ,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',item*width),item)).copy()
 def matrix(n):
  if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]); m=np.eye(4)
  m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 images=[]
 for im in doc.get('images',[]):
  v=doc['bufferViews'][im['bufferView']];b=v.get('byteOffset',0)
  images.append(hashlib.sha256(binary[b:b+v['byteLength']]).hexdigest())
 def material(i):
  m=json.loads(json.dumps(doc['materials'][i]));m.pop('name',None)
  def visit(v):
   if isinstance(v,dict):
    for k,x in list(v.items()):
     if k.endswith('Texture') and isinstance(x,dict) and 'index' in x:
      t=doc['textures'][x['index']];x['index']=images[t['source']]
      x['sampler']=doc.get('samplers',[])[t['sampler']] if 'sampler' in t else {}
     visit(x)
   elif isinstance(v,list):
    for x in v:visit(x)
  visit(m);return m
 out={}
 def walk(i,parent):
  node=doc['nodes'][i]; mat=parent@matrix(node)
  if 'mesh' in node:
   rows=[];materials=[]
   for p in doc['meshes'][node['mesh']]['primitives']:
    assert p.get('mode',4)==4
    at=p['attributes'];pos=acc(at['POSITION']).astype(float)@mat[:3,:3].T+mat[:3,3]
    norms=acc(at['NORMAL']).astype(float)@np.linalg.inv(mat[:3,:3]) if 'NORMAL' in at else np.zeros_like(pos)
    norms/=np.maximum(np.linalg.norm(norms,axis=1)[:,None],1e-30)
    uv=acc(at['TEXCOORD_0']) if 'TEXCOORD_0' in at else np.zeros((len(pos),2))
    idx=acc(p['indices']).ravel() if 'indices' in p else np.arange(len(pos))
    attrs=np.concatenate([pos,norms,uv],axis=1)
    # Cyclic rotations preserve winding, unlike sorting all three vertices.
    for tri in attrs[idx].reshape(-1,3,8):
     keys=[tuple(np.round(np.roll(tri,-j,axis=0).ravel(),5)) for j in range(3)]
     rows.append(min(keys))
    materials.append(material(p['material']) if 'material' in p else {})
   out[node['name']]={'triangles':sorted(rows),'materials':materials}
  for j in node.get('children',[]):walk(j,mat)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return out,doc

if __name__=='__main__':
 build=json.loads((D/'BUILD.json').read_text());result={'mode':'oriented triangle position/normal/UV comparison rounded to 5 decimal places; material semantic JSON comparison','passed':[],'failed':[]}
 for owner,filename in [('Orchard','AST-RTL-009.glb'),('Retail','AST-RTL-007.glb')]:
  old,_=load(R/'Game/assets/models'/filename);new,_=load(D/(owner+('_receiving_exact.glb' if '--exact' in sys.argv else '_receiving_successor.glb')))
  for key in build['unchanged_native_members']:
   if not key.startswith(owner+'/'):continue
   name=key.split('/',1)[1];a=old.get(name);b=new.get(name)
   errors=[]
   if a is None or b is None:errors.append('missing mesh')
   else:
    if a['triangles']!=b['triangles']:errors.append('triangle attributes differ')
    if a['materials']!=b['materials']:errors.append('material serialization differs; requires inspection')
   (result['failed'] if errors else result['passed']).append({'member':key,'issues':errors} if errors else key)
 _,doc=load(D/'OrchardInteriorReceiving.glb')
 result['new_glass_materials']=[m for m in doc.get('materials',[]) if 'glass' in m.get('name','').lower()]
 out=D/('EXACT_EXPORT_CHECK.json' if '--exact' in sys.argv else 'EXPORT_CHECK.json');assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':len(result['passed']),'failed':len(result['failed']),'first_failures':result['failed'][:6],'glass':result['new_glass_materials']}))
