import pathlib,json,struct,math,collections
import numpy as np
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/crew-bank-receiving-20261019');src=R/'BlenderCatalogue/assets/group3_remaining_receiving_20261019/exports/AST-CRW-G3-003_current_columns_r001.glb';b=src.read_bytes();ln=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+ln]);binary=b[28+ln:]
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
out={'scope':'Triangle versus inward1mm protected source-column AABBs, positive surface penetration screening. Exact column profiles still require classification. Broad hull bands and nonarchitectural datum meshes excluded from this column screen.','hits':hits,'allocations':sorted(set(h['allocation']for h in hits))};(W/'SUCCESSOR_COLUMN_TRIANGLE_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n');print('hits',len(hits),'allocations',len(out['allocations']));print(collections.Counter(h['original_component']for h in hits));print(out['allocations'])
