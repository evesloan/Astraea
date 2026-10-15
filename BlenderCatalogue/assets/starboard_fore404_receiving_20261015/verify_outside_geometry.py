from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');receipt=json.loads((D/'NATIVE_VERIFICATION.json').read_text())
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);assert not any(k in node for k in ['matrix','rotation','scale']);out=[]
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
 for axis,plane,less in[(0,43.7,False),(0,44.3,True),(1,0.,False),(1,3.55,True),(2,50.3,False),(2,53.7,True)]:
  p=clip(inside,axis,plane,not less)
  if len(p)>=3:pieces.append(p)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return [[poly[0],poly[i],poly[i+1]]for poly in pieces for i in range(1,len(poly)-1)]
def key(tri):return tuple(sorted(tuple(round(float(x),4)for x in np.r_[v['p'],v['uv']])for v in tri))
a,ab=load(G/'assets/models'/receipt['source_file']);n,nb=load(D/'import/Game/assets/starboard_fore404_receiving_20261015'/receipt['file']);results=[]
for row in receipt['walls']:
 source=faces(a,ab,row['source_name']);new=faces(n,nb,row['replacement_name']);expected=[t for old in source for t in subtract(old)];buckets=collections.defaultdict(list)
 def bucket(tri):return tuple(sorted(tuple(round(float(x),2)for x in v['p'])for v in tri))
 for i,tri in enumerate(new):buckets[bucket(tri)].append((i,tri))
 used=set();max_position=0.;max_uv=0.
 for tri in expected:
  found=None
  for i,candidate in buckets[bucket(tri)]:
   if i in used:continue
   for shift in range(3):
    other=candidate[shift:]+candidate[:shift];pe=max(np.linalg.norm(x['p']-y['p'])for x,y in zip(tri,other));ue=max(np.linalg.norm(x['uv']-y['uv'])for x,y in zip(tri,other))
    if pe<.0001 and ue<.00001:found=(i,pe,ue);break
   if found:break
  assert found is not None,('Missing retained source triangle/UV',tri)
  used.add(found[0]);max_position=max(max_position,found[1]);max_uv=max(max_uv,found[2])
 extra=[tri for i,tri in enumerate(new)if i not in used]
 for tri in extra:
  planes=[all(abs(v['p'][2]-z)<.0001 for v in tri)for z in[50.3,53.7]]+[all(abs(v['p'][1]-3.55)<.0001 for v in tri)];assert any(planes),'Unexplained added wall surface'
  assert all(43.7-.0001<=v['p'][0]<=44.3+.0001 and -.0001<=v['p'][1]<=3.5501 and 50.2999<=v['p'][2]<=53.7001 for v in tri)
 results.append({'wall':row['source_name'],'retained_clipped_triangles':len(expected),'new_declared_reveal_triangles':len(extra),'max_position_error_m':max_position,'max_uv_error':max_uv})
report={'status':'PASS_RETAINED_SOURCE_SKIN_AND_UV_OUTSIDE_FINITE_GATEWAY','walls':results,'position_tolerance_m':.0001,'uv_tolerance':.00001,'original_glb_unchanged':hashlib.sha256((G/'assets/models'/receipt['source_file']).read_bytes()).hexdigest()==receipt['source_sha256']};assert report['original_glb_unchanged'];(D/'OUTSIDE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
