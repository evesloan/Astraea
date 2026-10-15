from pathlib import Path
import json,struct,collections,hashlib,itertools
import numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');receipt={}
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);assert all(k not in node for k in ['matrix','rotation','scale']);assert node.get('translation',[0,0,0]) in [[0,0,0],[-31,0,-432]];out=[]
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


old=D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/exports/thread_stock/thread_stock_repair_r004.glb';new=D/'import/Game/assets/models/group5/thread_stock/thread_stock_repair_r005.glb';a,ab=load(old);n,nb=load(new);name='Group5VisualFinish_ThreadCeiling';source=faces(a,ab,name);actual=faces(n,nb,name);holes=[(31.63,32.37,-11.29,-10.71),(31.63,32.37,6.71,7.29)]
def subtract(poly,box):
 pieces=[];inside=poly
 for axis,plane,less in[(0,box[0],False),(0,box[1],True),(2,box[2],False),(2,box[3],True)]:
  q=clip(inside,axis,plane,not less)
  if len(q)>=3:pieces.append(q)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
polys=source
for hole in holes:polys=[p for old in polys for p in subtract(old,hole)]
expected=[[p[0],p[i],p[i+1]]for p in polys for i in range(1,len(p)-1)];lo=np.min([v['p']for p in source for v in p],axis=0);hi=np.max([v['p']for p in source for v in p],axis=0);exterior=[tri for tri in actual if any(all(abs(v['p'][axis]-bound)<.0001 for v in tri)for axis in range(3)for bound in[lo[axis],hi[axis]])];unmatched=list(exterior);maxp=0.;maxuv=0.
for tri in expected:
 match=None
 for i,other in enumerate(unmatched):
  for perm in itertools.permutations(other):
   ep=max(float(np.linalg.norm(x['p']-y['p']))for x,y in zip(tri,perm));eu=max(float(np.linalg.norm(x['uv']-y['uv']))for x,y in zip(tri,perm))
   if ep<.0001 and eu<.0001:match=(i,ep,eu);break
  if match:break
 
 if match is None:
  print('MISSING',tri,'EXPECTED_COUNT',len(expected),'ACTUAL',len(actual),'EXTERIOR',len(exterior));print('NEAR',sorted([(float(np.linalg.norm(np.mean([x["p"]for x in tri],axis=0)-np.mean([x["p"]for x in q],axis=0))),q)for q in unmatched],key=lambda x:x[0])[:2])
 assert match is not None,'No exact retained clipped ceiling triangle/UV match';unmatched.pop(match[0]);maxp=max(maxp,match[1]);maxuv=max(maxuv,match[2])
assert not unmatched
report={'status':'PASS_EXACT_CANDIDATE_CEILING_OUTSIDE_TWO_RETAINED_FIXTURE_HOUSING_CUTOUTS','retained_clipped_triangles':len(expected),'new_painted_cut_edge_triangles':len(actual)-len(exterior),'maximum_position_error_m':maxp,'maximum_uv_error':maxuv,'fixed_tolerance_m':.0001,'source_r004_model_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_r005_model_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'original_ship_geometry_changed':False};(D/'CEILING_OUTSIDE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(expected),maxp,maxuv)
