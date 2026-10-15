from pathlib import Path
import json,struct,hashlib,itertools,numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');out=[]
def local(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape((4,4),order='F')
 M=np.eye(4);x,y,z,w=n.get('rotation',[0,0,0,1]);M[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];M[:3,:3]=M[:3,:3]@np.diag(n.get('scale',[1,1,1]));M[:3,3]=n.get('translation',[0,0,0]);return M
for key in['01','02','03']:
 file=G/'assets/models'/f'SOL_D10_directory_{key}_remaining_batch.glb';b=file.read_bytes();size=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+size]);parents={c:i for i,n in enumerate(j['nodes'])for c in n.get('children',[])};cache={}
 def world(i):
  if i not in cache:cache[i]=(world(parents[i])if i in parents else np.eye(4))@local(j['nodes'][i])
  return cache[i]
 rows=[]
 for i,node in enumerate(j['nodes']):
  name=node.get('name','')
  if 'mesh'not in node or not any(t in name for t in ['service_boundary','service_screen','C_fore','C_aft','arrival']):continue
  points=[]
  for p in j['meshes'][node['mesh']]['primitives']:
   a=j['accessors'][p['attributes']['POSITION']];points +=[(*v,1)for v in itertools.product(*zip(a['min'],a['max']))]
  ps=np.array(points)@world(i).T;rows.append({'name':name,'min':ps[:,:3].min(0).tolist(),'max':ps[:,:3].max(0).tolist()})
 out.append({'programme_key':'D10_directory_'+key,'file':file.name,'sha256':hashlib.sha256(b).hexdigest(),'parts':rows});print(key,[(x['name'],np.round(x['min'],2).tolist(),np.round(x['max'],2).tolist())for x in rows])
(D/'EXACT_DINING_SERVICE_BOUNDARIES.json').write_text(json.dumps(out,indent=2)+'\n')
