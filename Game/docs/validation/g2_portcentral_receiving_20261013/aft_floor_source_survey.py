from pathlib import Path
import json,struct,hashlib,numpy as np
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');result=[]
for key,model,sign,batches in [('port_aft_upper_house','SUNSET_ARCHITECTURE_lift_r003.glb',-1,['SC_Batch_56','SC_Batch_76']),('starboard_aft_upper_house','FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb',1,['FT_Batch_99','FT_Batch_138'])]:
 raw=(G/'assets/models'/model).read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);binstart=20+n+8;buf=raw[binstart:];triangles={}
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'VEC3':3,'SCALAR':1}[a['type']];return np.frombuffer(buf,dtype=dtype,count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],width)
 for node in j['nodes']:
  name=node.get('name','')
  if name not in batches:continue
  assert not node.get('translation')and not node.get('rotation')and not node.get('scale')
  tri=[]
  for p in j['meshes'][node['mesh']]['primitives']:
   vs=acc(p['attributes']['POSITION']);ix=acc(p['indices']).ravel()if 'indices'in p else np.arange(len(vs));tri.extend(vs[ix].reshape(-1,3,3))
  triangles[name]=np.array(tri)
 rows=[]
 for xabs in [63.5,65,67,69,71,73]:
  for z in [326.5,330,334,338,342,344.5,346,349,352,355.5,356.5]:
   x=sign*xabs;hits=[]
   for batch,ts in triangles.items():
    for t in ts:
     a,b,c=t[:,[0,2]];v0=b-a;v1=c-a;q=np.array([x,z])-a;det=np.linalg.det(np.array([v0,v1]));
     if abs(det)<1e-7:continue
     u,v=np.linalg.solve(np.array([v0,v1]).T,q)
     if u>=-1e-6 and v>=-1e-6 and u+v<=1+1e-6:
      y=float(t[0,1]+u*(t[1,1]-t[0,1])+v*(t[2,1]-t[0,1]));
      if abs(y-97.5)<.002 or abs(y-102)<.002:hits.append({'batch':batch,'y':round(y,4)})
   rows.append({'x':x,'z':z,'hits':list({(h['batch'],h['y']):h for h in hits}.values())})
 result.append({'key':key,'model':model,'sha256':hashlib.sha256(raw).hexdigest(),'rows':rows})
(P/'AFT_EXACT_SOURCE_FLOOR_GRID.json').write_text(json.dumps({'status':'STATIC_NATIVE_TRIANGLE_SURVEY_NOT_PHYSICS_ACCEPTANCE','sites':result},indent=2)+'\n')
for r in result:
 print(r['key'],'lower_hits',sum(any(h['y']==97.5 for h in a['hits'])for a in r['rows']),'upper_hits',sum(any(h['y']==102 for h in a['hits'])for a in r['rows']),'samples',len(r['rows']))
