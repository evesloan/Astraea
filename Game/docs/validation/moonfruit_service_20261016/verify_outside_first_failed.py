from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/Astraea/Game');receipt=json.loads((D/'NATIVE_VERIFICATION.json').read_text())
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);assert all(k not in node for k in ['matrix','rotation','scale']);out=[]
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=accessor(j,b,p['attributes']['POSITION']);uv=accessor(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=accessor(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs))
  out += [[{'p':vs[i].astype(float)+np.array([-22.75,3.700000047683716,0]),'uv':uv[i].astype(float)}for i in tri]for tri in ix.reshape(-1,3)]
 return out

def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k]+(e[k]-s[k])*t for k in ['p','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out

def cut(poly,z):
 pieces=[];inside=poly
 for axis,plane,less in[(1,0.,False),(1,3.2,True),(2,z-1.2,False),(2,z+1.2,True)]:
  p=clip(inside,axis,plane,not less)
  if len(p)>=3:pieces.append(p)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
def subtract(tri):
 polys=[tri]
 for z in [-25.,16.]:polys=[part for poly in polys for part in cut(poly,z)]
 return [[poly[0],poly[i],poly[i+1]]for poly in polys for i in range(1,len(poly)-1)]
def key(tri):return tuple(sorted(tuple(round(float(x),4)for x in np.r_[v['p'],v['uv']])for v in tri))
a,ab=load(G/'assets/models'/'SOL_D10_directory_09_remaining_batch.glb');n,nb=load(D/'exports/MOONFRUIT_SERVICE_RECEIVER_r001.glb');results=[]
for row in receipt['walls']:
 source=faces(a,ab,row['source_name']);new=faces(n,nb,row['replacement_name']);lo=np.array([-23,0,-34]);hi=np.array([-22.5,7.4,34]);exterior=[tri for tri in new if any(all(abs(v['p'][axis]-bound)<.0001 for v in tri)for axis in range(3)for bound in[lo[axis],hi[axis]])];expected=[tri for old in source for tri in subtract(old)];e=collections.Counter(key(t)for t in expected);actual=collections.Counter(key(t)for t in exterior)
 assert e==actual,(row['source_name'],'Retained outside triangle/UV mismatch',len(e-actual),len(actual-e))
 results.append({'node':row['source_name'],'exact_retained_clipped_triangles_with_uv':len(exterior),'new_reveal_triangles':len(new)-len(exterior)})
report={'status':'PASS_EXACT_CLIPPED_SOURCE_TRIANGLES_AND_UV_OUTSIDE_MOONFRUIT_SERVICE_GATEWAY','tolerance_m':.0001,'walls':results,'source_sha256':receipt['source_pins']['assets/models/SOL_D10_directory_09_remaining_batch.glb'],'new_model_sha256':receipt['model_sha256'],'original_glb_unchanged':hashlib.sha256((G/'assets/models'/'SOL_D10_directory_09_remaining_batch.glb').read_bytes()).hexdigest()==receipt['source_pins']['assets/models/SOL_D10_directory_09_remaining_batch.glb']};(D/'OUTSIDE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
