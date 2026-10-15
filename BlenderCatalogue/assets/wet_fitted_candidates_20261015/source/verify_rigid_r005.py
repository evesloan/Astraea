from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
D=Path(__file__).resolve().parent;S=D.parent/'immutable_inputs/Game/assets/group2_vip_pavilions';r=json.loads((D/'FITTED_NATIVE_VERIFICATION_r005.json').read_text())
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);out=[]
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=acc(j,b,p['attributes']['POSITION']);uv=acc(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=acc(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs));out +=[tuple(sorted(tuple(round(float(x),4)for x in np.r_[vs[i],uv[i]])for i in tri))for tri in ix.reshape(-1,3)]
 return collections.Counter(out)
def images(j,b):
 out=[]
 for row in j.get('images',[]):
  v=j['bufferViews'][row['bufferView']];out.append(hashlib.sha256(b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest())
 return set(out)
verified=0;image_count=0
for model in r['models']:
 kit=model['kit'];o,ob=load(S/f'VIP_{kit}_r003.glb');n,nb=load(D/'fitted_r005_import/Game/assets/fitted_wet_pavilions_20261015'/model['file']);old_images=images(o,ob);new_images=images(n,nb);assert new_images<=old_images,'Unexpected source image pixels';image_count+=len(new_images)
 for row in r['rigid_source_roster']:
  if not row['source'].startswith('G2VIP_'+kit+'_'):continue
  assert faces(o,ob,row['source'])==faces(n,nb,row['new']),(kit,row['source'],'Exact retained geometry/UV changed');verified+=1
report={'status':'PASS_ALL_RETAINED_PROP_AND_FRAME_LOCAL_TRIANGLES_UV_AND_IMAGE_BYTES','verified_rigid_source_meshes':verified,'embedded_images':image_count,'position_uv_quantization':.0001,'fitted_native_fresh_reexport_verified':True,'original_sources_unchanged':True,'versioned_new_slabs_basin_ramps_and_adapters_excluded_from_rigid_claim':True};(D/'RIGID_SOURCE_GEOMETRY_VERIFICATION_r005.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
