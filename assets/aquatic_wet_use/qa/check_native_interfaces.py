"""Native GLB node hierarchy, real transformed triangles, point/normal witnesses and structural compounds."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'qa'));import validate_glb as g

def nearest(p,tris):
 t=np.asarray(tris);a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;ap=p-a;n=np.cross(ab,ac);n=n/np.linalg.norm(n,axis=1)[:,None];signed=(ap*n).sum(1);proj=p-signed[:,None]*n;v=proj-a;d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1);d20=(v*ab).sum(1);d21=(v*ac).sum(1);den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/den;vv=(d00*d21-d01*d20)/den;valid=(u>=-1e-8)&(vv>=-1e-8)&(u+vv<=1+1e-8);ds=np.where(valid,abs(signed),np.inf)
 for x,y in[(a,b),(b,c),(c,a)]:
  e=y-x;q=x+np.clip(((p-x)*e).sum(1)/(e*e).sum(1),0,1)[:,None]*e;ds=np.minimum(ds,np.linalg.norm(q-p,axis=1))
 ix=ds.argmin();return float(ds[ix]),n[ix]

def hull_box(vertices,lo,hi):
 vs=np.array(vertices);hull=ConvexHull(vs);c=(np.array(lo)+hi)*.5;half=(np.array(hi)-lo)*.5;verts=vs-c;axes=[*np.eye(3),*hull.equations[:,:3]];edges=set()
 for f in hull.simplices:
  for a,b in[(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:edges.add(tuple(sorted((int(a),int(b)))))
 axes.extend(np.cross(vs[a]-vs[b],k)for a,b in edges for k in np.eye(3))
 for ax in axes:
  if np.linalg.norm(ax)<1e-9:continue
  dp=verts@ax;r=np.abs(ax)@half
  if dp.min()>r+1e-9 or dp.max()<-r-1e-9:return False
 return True
rows=[];coll=json.loads((BASE/'collision_proposals.json').read_text())
for rp in sorted(BASE.glob('AST-AQU-*.manifest.json')):
 r=json.loads(rp.read_text());path=BASE/r['export'];doc,blob=g.read(path);nodes={};geoms=[]
 def walk(ix,parent):
  nd=doc['nodes'][ix];m=parent@g.matrix(nd);nodes[nd.get('name','')]=(nd,m)
  if 'mesh'in nd:
   ts=[]
   for prim in doc['meshes'][nd['mesh']]['primitives']:
    v=g.accessor(doc,blob,prim['attributes']['POSITION']);v=(m@np.c_[v,np.ones(len(v))].T).T[:,:3];idx=g.accessor(doc,blob,prim['indices']).reshape(-1,3);ts.extend(v[idx])
   geoms.append((nd,np.array(ts)))
  for ch in nd.get('children',[]):walk(ch,m)
 for ix in doc['scenes'][doc.get('scene',0)]['nodes']:walk(ix,np.eye(4))
 markers=[]
 for mk in r['physical_and_proposal_markers']:
  nd,m=nodes[mk['name']];p=m[:3,3];row={'name':mk['name'],'native_node_position':p.tolist(),'expected':mk['gltf_m'],'position_error_m':float(np.linalg.norm(p-np.array(mk['gltf_m'])))}
  if mk['physical_part']:
   geo=next(ts for nd,ts in geoms if mk['physical_part']in json.loads(nd['extras']['semantic_parts']));dist,normal=nearest(p,geo);row.update(surface_distance_m=dist,normal_dot=float(normal@mk['surface_normal_gltf']),named_part=mk['physical_part']);wrong,_=nearest(np.array(mk['source_m']),geo);row['wrong_axis_distance_m']=wrong
  row['passes']=row['position_error_m']<1e-6 and row.get('surface_distance_m',0)<.00015 and row.get('normal_dot',1)>.99;markers.append(row)
 collisions=[]
 for v in r['receiver_voids']:
  hits=[s['name']for s in coll[r['catalogue_id']]['shapes']if hull_box(s['points_source_m'],np.array(v['min_source_m']),np.array(v['max_source_m']))];collisions.append({'name':v['name'],'hits':hits,'passes':not hits})
 motion=[]
 for root in r['independent_removable_roots']:
  ix=next(i for i,n in enumerate(doc['nodes'])if n.get('name')==root['name']);desc=set();todo=[ix]
  while todo:
   ni=todo.pop();desc.add(ni);todo.extend(doc['nodes'][ni].get('children',[]))
  members=[doc['nodes'][ni].get('name','')for ni in desc];marker=next(mk for mk in r['physical_and_proposal_markers']if mk['physical_part']==root['parts'][0]);expected=np.array(root['removal_vector_gltf_m']);marker_moves=marker['name']in members;body_nodes=[nd.get('name')for nd,ts in geoms if any(part in json.loads(nd['extras']['semantic_parts'])for part in root['parts'])];parts_move=all(n in members for n in body_nodes);zero=nodes[root['name']][1][:3,3];motion.append({'root':root['name'],'zero_pose_native_error_m':float(np.linalg.norm(zero-np.array(root['zero_pose_gltf_m']))),'native_children':members,'plate_mesh_nodes':body_nodes,'dependent_marker_moves':marker_moves,'all_plate_meshes_move':parts_move,'translation_native_m':expected.tolist(),'translated_marker_position':(nodes[marker['name']][1][:3,3]+expected).tolist(),'body_fixed':all(n not in members for n in [nd.get('name')for nd,ts in geoms if nd.get('name')not in body_nodes]),'passes':bool(marker_moves and parts_move and np.linalg.norm(zero-np.array(root['zero_pose_gltf_m']))<1e-6)})
 rows.append({'catalogue_id':r['catalogue_id'],'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_markers':markers,'native_removal_hierarchy_checks':motion,'collision_compounds':len(coll[r['catalogue_id']]['shapes']),'collision_clear_volume_checks':collisions,'collision_method':'Complete convex hull/AABB SAT using hull face normals, box axes and all hull edge cross box axes; positive occupied controls are in source checker','runtime_meshes':len(doc['meshes']),'native_nodes':len(doc['nodes']),'passes':all(x['passes']for x in markers+collisions+motion)})
(BASE/'qa/native_interface_collision_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(x['passes']for x in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes'],[x['name']for x in r['native_markers']+r['collision_clear_volume_checks']if not x['passes']])for r in rows])
