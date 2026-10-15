from pathlib import Path
import json,struct,collections,hashlib,itertools
import numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');receipt=json.loads((D/'NATIVE_VERIFICATION.json').read_text())
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);assert all(k not in node for k in ['matrix','rotation','scale']);assert node.get('translation',[0,0,0])==[0,0,0];out=[]
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=accessor(j,b,p['attributes']['POSITION']);uv=accessor(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=accessor(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs))
  out += [[{'p':vs[i].astype(float),'uv':uv[i].astype(float)}for i in tri]for tri in ix.reshape(-1,3)]
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

def subtract(tri):
 pieces=[];inside=tri
 for axis,plane,less in[(0,-56.2,False),(0,-55.8,True),(1,0.,False),(1,3.2,True),(2,cut_range[0],False),(2,cut_range[1],True)]:
  p=clip(inside,axis,plane,not less)
  if len(p)>=3:pieces.append(p)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return [[poly[0],poly[i],poly[i+1]]for poly in pieces for i in range(1,len(poly)-1)]
def key(tri):return tuple(sorted(tuple(round(float(x),4)for x in np.r_[v['p'],v['uv']])for v in tri))
a,ab=load(G/'assets/models'/receipt['source_file']);n,nb=load(D/'import/Game/assets/synthesis_external_receiving_20261015/SYNTHESIS_EXTERNAL_LINKS_r001.glb');results=[]
for row in receipt['walls']:
 cut_range=(-28.7,-25.3)if '0185'in row['source_name']else(25.3,28.7)
 source=faces(a,ab,row['source_name']);new=faces(n,nb,row['replacement_name']);lo=np.array(row['input_bounds_local'][0]);hi=np.array(row['input_bounds_local'][1]);exterior=[tri for tri in new if any(all(abs(v['p'][axis]-bound)<.0001 for v in tri)for axis in range(3)for bound in[lo[axis],hi[axis]])];expected=[tri for old in source for tri in subtract(old)];e=collections.Counter(key(t)for t in expected);actual=collections.Counter(key(t)for t in exterior)
 unmatched=list(exterior);max_position=0.;max_uv=0.
 for tri in expected:
  match=None
  for i,other in enumerate(unmatched):
   for permutation in itertools.permutations(other):
    ep=max(float(np.linalg.norm(a['p']-b['p']))for a,b in zip(tri,permutation));eu=max(float(np.linalg.norm(a['uv']-b['uv']))for a,b in zip(tri,permutation))
    if ep<.0001 and eu<.0001:match=(i,ep,eu);break
   if match:break
  assert match is not None,(row['source_name'],'Unmatched triangle under unchanged fixed tolerance')
  unmatched.pop(match[0]);max_position=max(max_position,match[1]);max_uv=max(max_uv,match[2])
 assert not unmatched
 results.append({'node':row['source_name'],'exact_retained_clipped_triangles_with_uv':len(exterior),'new_reveal_triangles':len(new)-len(exterior),'maximum_position_error_m':max_position,'maximum_uv_error':max_uv})
report={'status':'PASS_EXACT_CLIPPED_SOURCE_TRIANGLES_AND_UV_OUTSIDE_SEPARATE_SYNTHESIS_LINKS','tolerance_m':.0001,'walls':results,'source_sha256':receipt['source_sha256'],'new_model_sha256':receipt['model_sha256'],'original_glb_unchanged':hashlib.sha256((G/'assets/models'/receipt['source_file']).read_bytes()).hexdigest()==receipt['source_sha256']};(D/'OUTSIDE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
