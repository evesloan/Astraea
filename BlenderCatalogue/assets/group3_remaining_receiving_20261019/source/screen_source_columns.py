import pathlib,json,struct,math,collections
import numpy as np
R=pathlib.Path(__file__).resolve().parents[4];W=pathlib.Path(__file__).resolve().parent/'receiving_inputs';src=R/'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_crew_bank_source_batch015/exports/AST-CRW-G3-003.glb';b=src.read_bytes();ln=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+ln]);binary=b[28+ln:]
def acc(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];dim={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];item=np.dtype(dt).itemsize;off=v.get('byteOffset',0)+a.get('byteOffset',0)
 return np.ndarray((a['count'],dim),dtype=dt,buffer=binary,offset=off,strides=(v.get('byteStride',item*dim),item)).copy()
def transform(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape((4,4),order='F')
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
parents={c:i for i,n in enumerate(g['nodes'])for c in n.get('children',[])};matrices={}
def world(i):
 if i not in matrices:matrices[i]=(world(parents[i]) if i in parents else np.eye(4))@transform(g['nodes'][i])
 return matrices[i]
def tri_box(t,lo,hi):
 center=(lo+hi)/2;half=(hi-lo)/2;v=t-center;e=np.roll(v,-1,axis=0)-v;axes=[*np.eye(3),np.cross(e[0],e[1]),*[np.cross(x,y)for x in e for y in np.eye(3)]]
 for a in axes:
  if np.dot(a,a)<1e-16:continue
  p=v@a;r=half@np.abs(a)
  if p.min()>r or p.max()<-r:return False
 return True
candidates=json.load(open(W/'ROOM_AABB_SCREEN.json'))['candidates'];by=collections.defaultdict(list)
for c in candidates:
 if 'LowerHullBody' not in c['path'] and 'All18Deck' not in c['path']:by[c['allocation']].append(c)
mesh_cache={};hits=[]
for i,n in enumerate(g['nodes']):
 if 'mesh'not in n:continue
 key=n.get('extras',{}).get('source_allocation_key');cs=by.get(key,[])
 if not cs:continue
 mi=n['mesh']
 if mi not in mesh_cache:
  mesh_cache[mi]=[(acc(p['attributes']['POSITION']),acc(p['indices']).ravel() if 'indices'in p else np.arange(g['accessors'][p['attributes']['POSITION']]['count']))for p in g['meshes'][mi]['primitives']]
 for verts,ids in mesh_cache[mi]:
  m=world(i);v=(np.c_[verts,np.ones(len(verts))]@m.T)[:,:3];tris=v[ids.reshape(-1,3)]
  for c in cs:
   a=c['bounds'];lo=np.array([a[0]+.001,max(12.005,a[1]+.001),a[2]+.001]);hi=np.array([a[3]-.001,min(15.25,a[4]-.001),a[5]-.001]);choose=np.all(tris.max(axis=1)>=lo,axis=1)&np.all(tris.min(axis=1)<=hi,axis=1);count=sum(tri_box(t,lo,hi) for t in tris[choose])
   if count:hits.append({'allocation':key,'source_node':n['name'],'original_component':n.get('extras',{}).get('original_component'),'protected_path':c['path'],'protected_bounds':a,'intersecting_source_triangles':count})
out={'scope':'Triangle versus inward1mm protected source-column AABBs, positive surface penetration screening. Exact column profiles still require classification. Broad hull bands and nonarchitectural datum meshes excluded from this column screen.','hits':hits,'allocations':sorted(set(h['allocation']for h in hits))};(W/'SOURCE_COLUMN_TRIANGLE_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n');print('hits',len(hits),'allocations',len(out['allocations']));print(collections.Counter(h['original_component']for h in hits));print(out['allocations'])
# Fit the whole existing rest/storage arrangement by one bounded rigid local-X shift.
# Relative bed/curtain/storage geometry and the central entry/wash/desk zone remain unchanged.
contract=json.load(open(R/'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_crew_bank_source_batch015/source/REMAINING_BANK_CONTRACT.json'));poses={q['allocation_key']:q for q in contract['instances']};plans=[]
for key in out['allocations']:
 tr=[];mins=[];maxs=[]
 for i,n in enumerate(g['nodes']):
  if 'mesh'not in n or n.get('extras',{}).get('source_allocation_key')!=key or n['name'].split('__')[1]=='Shell':continue
  mi=n['mesh']
  if mi not in mesh_cache:mesh_cache[mi]=[(acc(p['attributes']['POSITION']),acc(p['indices']).ravel())for p in g['meshes'][mi]['primitives']]
  for verts,ids in mesh_cache[mi]:
   m=world(i);v=(np.c_[verts,np.ones(len(verts))]@m.T)[:,:3];tr.extend(v[ids.reshape(-1,3)])
 tr=np.array(tr);pose=poses[key];yaw=pose['yaw'];chosen=None
 for step in range(15):
  dx=step*.1;delta=np.array([math.cos(yaw)*dx,0,-math.sin(yaw)*dx]);moved=tr+delta;bad=0
  for c in by[key]:
   a=c['bounds'];lo=np.array([a[0]-.03,max(12.001,a[1]),a[2]-.03]);hi=np.array([a[3]+.03,min(15.25,a[4]),a[5]+.03]);choose=np.all(moved.max(axis=1)>=lo,axis=1)&np.all(moved.min(axis=1)<=hi,axis=1)
   if any(tri_box(t,lo,hi)for t in moved[choose]):bad+=1;break
  if not bad:chosen={'allocation':key,'local_x_translation_m':round(dx,3),'world_translation':delta.tolist(),'all_rest_curtain_storage_groups_moved_together':True,'protected_column_clearance_m':.03};break
 plans.append(chosen or {'allocation':key,'status':'NO_BOUNDED_RIGID_FIT_FOUND'})
(W/'RIGID_FURNITURE_FIT_PLAN.json').write_text(json.dumps({'maximum_search_translation_m':1.4,'preserved':'Original geometry/UV/materials and relative rest/curtain/storage arrangement; shell fixtures, entry, wash and desk stay fixed. Physical unassigned rests only; no save keys.','plans':plans},indent=2)+'\n');print('fits',[(p['allocation'],p.get('local_x_translation_m',p.get('status')))for p in plans])
