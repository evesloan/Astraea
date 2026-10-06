"""Read-only GLB/source-contract study. Writes reports only alongside this script."""
import json, struct, hashlib, math, pathlib, collections
import numpy as np
R=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/workspace/shared/astraea-catalogue-continuation-20261002')
G=pathlib.Path('/workspace/shared/astraea-godot-production-20261003')
S=C/'assets/grand_pool_orchard_section'
A=C/'assets/grand_pool_first_pass/architectural_composition'
P=pathlib.Path('/workspace/scratch/375c2e438292/pool-feature-installed-capture001')
inputs={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):
 inputs[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
 return p
def read(p):return json.loads(pin(p).read_text())
def write(fn,obj):(R/fn).write_text(json.dumps(obj,indent=2)+'\n')
def bounds(v):return [np.min(v,axis=0).tolist(),np.max(v,axis=0).tolist()]
def glb(p):
 b=pin(p).read_bytes();magic,version,size=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and size==len(b)
 off=12;chunks={}
 while off<len(b):
  n,t=struct.unpack_from('<II',b,off);chunks[t]=b[off+8:off+8+n];off+=8+n
 d=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
 def acc(i):
  x=d['accessors'][i];bv=d['bufferViews'][x['bufferView']];dt={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[x['componentType']];sz={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[x['type']];stride=bv.get('byteStride',np.dtype(dt).itemsize*sz);assert 'sparse' not in x
  return np.ndarray((x['count'],sz),dtype=dt,buffer=blob,offset=bv.get('byteOffset',0)+x.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
 def mat(n):
  if 'matrix'in n:return np.array(n['matrix']).reshape((4,4),order='F')
  x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 records=[]
 def visit(i,parent):
  n=d['nodes'][i];m=parent@mat(n)
  if 'mesh'in n:
   me=d['meshes'][n['mesh']]
   for pi,pr in enumerate(me['primitives']):
    assert pr.get('mode',4)==4
    v=acc(pr['attributes']['POSITION']).astype(float);v=v@m[:3,:3].T+m[:3,3];ix=acc(pr['indices']).ravel()if 'indices'in pr else np.arange(len(v));ts=v[ix.reshape((-1,3))]
    records.append({'node':n['name'],'mesh':me.get('name'),'node_index':i,'mesh_index':n['mesh'],'primitive_index':pi,'material':d['materials'][pr['material']]['name'],'bounds_xyz':bounds(v),'triangles':ts,'extras':n.get('extras',{})})
  for c in n.get('children',[]):visit(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return records
contract=read(S/'source/connected_contract.json');runtime=read(G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json');manifest=read(S/'AST-AQU-016.manifest.json')
for p in [S/'HANDOFF.md',S/'source/build_connected_section.py',S/'source/AST-AQU-016.blend',S/'qa/source_export_verification.json',S/'qa/plan_route_verification.json',S/'qa/check_plan_routes.py',S/'qa/lift_source_sweeps.json',G/'scripts/grand_pool_section.gd',G/'scripts/ship.gd',G/'assets/models/AST-AQU-016.glb.import',P/'output/long_view_installed_effects_off.png',P/'output/RESULT.json']:pin(p)
original=glb(S/'exports/AST-AQU-016.glb');installed=glb(G/'assets/models/AST-AQU-016.glb')
assert sha(S/'exports/AST-AQU-016.glb')==sha(G/'assets/models/AST-AQU-016.glb')==manifest['export_sha256']
assert sha(S/'source/AST-AQU-016.blend')==manifest['source_sha256'];assert sha(S/'source/connected_contract.json')==manifest['contract_sha256'];assert contract==runtime
T=np.concatenate([r['triangles']for r in installed]); node_idx=np.concatenate([np.full(len(r['triangles']),i)for i,r in enumerate(installed)]);tmin=T.min(axis=1);tmax=T.max(axis=1);tri_owners=[[]for _ in T];part_rows=[]
for p in contract['source_parts']:
 if p['export_excluded']:continue
 v=np.array(p['world_vertices']);lo,hi=v.min(axis=0),v.max(axis=0);indices=np.where(((tmin>=lo-5e-5)&(tmax<=hi+5e-5)).all(axis=1))[0]
 mt={'glass':'circulation_glass','lens':'GardenOpalLens'}.get(p['role'],'ASTRAEA_'+p['role']);good=[];max_error=0
 for i in indices:
  if installed[node_idx[i]]['material']!=mt:continue
  err=np.linalg.norm(T[i,:,None,:]-v[None,:,:],axis=2).min(axis=1).max()
  if err<5e-5:good.append(int(i));tri_owners[i].append(p['name']);max_error=max(max_error,float(err))
 assert good,p['name']
 part_rows.append({'source_name':p['name'],'design_owner':p['parent_design_id'],'assembly_owner':'AST-AQU-016','material_role':p['role'],'collision_contract':p['collision_contract'],'source_bounds_xyz':[lo.tolist(),hi.tolist()],'verified_installed_triangle_bounds_xyz':bounds(T[good].reshape((-1,3))),'matched_triangle_count':len(good),'max_source_vertex_delta_m':max_error,'installed_nodes':sorted({installed[node_idx[i]]['node']for i in good}),'global_triangle_indices':good})
write('RETAINED_PART_BOUNDS.json',{'coordinate_frame':'Godot world XYZ metres, all roots identity','method':'Source contract vertex sets cross-matched to actual installed GLB triangles at 0.00005 m. No Blender or Godot launched. Original freeze checks and source/runtime contracts exact. Vertex-set matching is not a fresh topology/UV/native-equivalence proof.','parts':part_rows})
write('INSTALLED_GLB_BATCH_BOUNDS.json',[{k:v for k,v in r.items()if k!='triangles'}for r in installed])
# Pure ray witness from actual retained camera to visible pixels.
cap=read(P/'output/long_view_installed_effects_off.png.caption.json');eye=np.array(cap['actual_eye']);fwd=np.array(cap['actual_camera_forward']);right=np.cross(fwd,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,fwd);fh=math.tan(math.radians(cap['fov'])/2);ww,hh=cap['image_resolution']
def ray(pixel):
 x,y=pixel;direction=fwd+right*((2*(x+.5)/ww-1)*(ww/hh)*fh)+up*((1-2*(y+.5)/hh)*fh);direction/=np.linalg.norm(direction)
 e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];h=np.cross(direction,e2);a=np.einsum('ij,ij->i',e1,h);mask=abs(a)>1e-10;f=np.zeros(len(a));f[mask]=1/a[mask];s=eye-T[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);vv=f*(q@direction);t=f*np.einsum('ij,ij->i',e2,q);hit=np.where(mask&(u>=0)&(vv>=0)&(u+vv<=1)&(t>0))[0];hit=sorted(hit,key=lambda i:t[i]);out=[]
 for i in hit[:8]:out.append({'distance_m':float(t[i]),'xyz':(eye+t[i]*direction).tolist(),'installed_node':installed[node_idx[i]]['node'],'material':installed[node_idx[i]]['material'],'source_parts':tri_owners[i]})
 return {'pixel':list(pixel),'retained_shell_intersections':out}
rays=[ray(p)for p in [(1280,550),(1600,600),(1500,750),(1100,450),(1100,250),(1070,550),(1030,480)]]
write('LONG_VIEW_IDENTITY_RAYS.json',{'camera':{k:cap[k]for k in ['actual_eye','actual_camera_forward','fov','image_resolution']},'method':'Pure ray/actual installed AST-AQU-016 GLB triangle intersections, KEEP_HEIGHT projection. Other assets and transparency not traced; these are shell identity witnesses, not rendered visibility proof.','rays':rays})
# Source root support paths; saved actual mesh-contact evidence, not generated anew.
cg=read(S/'qa/source_contact_graph.json');adj=collections.defaultdict(list)
for edge in cg['contacts']:adj[edge['a']].append(edge['b']);adj[edge['b']].append(edge['a'])
def bfs(start):
 q=collections.deque([(start,[start])]);seen={start}
 while q:
  x,path=q.popleft()
  if x==cg['root']:return path
  for y in adj[x]:
   if y not in seen:seen.add(y);q.append((y,path+[y]))
keys=['GP_LocalLiftRear','GP_LocalLiftSide.001','GP_LocalLiftCap','GP_GalleryFasciaBody_2','GP_GalleryFasciaLowerReturn_2','GP_GalleryFasciaBody_10','GP_SculptedPier_3','GP_SculptedPier_4','GP_SculptedPier_5','GP_UpperPier_3','GP_UpperPier_4','GP_UpperPier_5','GP_EastWall.002','GP_EastWall.003']
write('RETAINED_SUPPORT_PATHS.json',{'source':str(S/'qa/source_contact_graph.json'),'scope':cg['scope'],'paths':[{'source_name':k,'direct_contacts':adj[k],'path_to_retained_keel':bfs(k)}for k in keys]})
# Saved native-source snapshots for retained finish and architecture, plus actual GLB bounds.
finish=[]
for kind in ['envelope','roof','loggia','focal_end']:
 sp=A/'export_tooling003'/('envelope_snapshot001.json'if kind=='envelope'else kind+'_snapshot.json');d=read(sp)
 for o in d['objects']:
  if o['type']!='MESH':continue
  v=np.array(o['positions']).reshape((-1,3));b=bounds(v)
  finish.append({'source_snapshot':str(sp),'source_name':o['name'],'kind':kind,'bounds_xyz':b,'material':o['material'],'extras':o['extras']})
write('RETAINED_FINISH_BOUNDS.json',finish)
arch=read(G/'data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json');fin=read(G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json');first=read(G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json')
for d,kind in [(arch,'architecture'),(fin,'finish')]:
 for k,m in d['models'].items():
  if k not in ['roof','loggia','focal_end','envelope','wayfinding']:continue
  model=G/'assets/models'/m['file'];rr=glb(model);assert sha(model)==m['sha256'],m['file']
  write('INSTALLED_'+k.upper()+'_BOUNDS.json',[{x:y for x,y in r.items()if x!='triangles'}for r in rr])
write('PRESERVED_VIEWS.json',arch['preserved_view_probes'])
write('FLOOR_POLYGONS.json',{'owner':'existing floor_compiler; read-only, no new slab or void changes','floor_regions':contract['floor_regions']})
# Import cache is not parsed; existence/hash alone is not a geometry acceptance claim.
imp=G/'assets/models/AST-AQU-016.glb.import'
for line in imp.read_text().splitlines():
 if line.startswith('path="res://'):
  ip=G/line.split('"')[1][6:]
  if ip.exists():pin(ip)
write('INPUT_HASHES.json',inputs)
write('EXTRACTION_RESULT.json',{'pass':True,'source_parts':len(part_rows),'installed_mesh_primitives':len(installed),'installed_triangle_count':len(T),'triangles_with_no_source_owner':sum(not x for x in tri_owners),'triangles_with_multiple_source_owners':sum(len(x)>1 for x in tri_owners),'max_source_vertex_delta_m':max(x['max_source_vertex_delta_m']for x in part_rows),'source_and_installed_glb_sha256_equal':True,'source_runtime_contract_equal':True,'no_engine_or_import_run':True,'no_production_writes':True})
print(json.dumps(json.load(open(R/'EXTRACTION_RESULT.json')),indent=2))
for row in rays:
 print(row['pixel'],row['retained_shell_intersections'][:1])
