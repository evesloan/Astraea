"""Reload saved sources; source surface/normals, convex-solid structure, UVs and packed roles."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def planes(v,t):
 tr=v[t];n=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(n,axis=1);n=n/area[:,None];return n,-np.sum(n*tr[:,0],axis=1),area
rows=[];dump={}
for file in sorted(BASE.glob('AST-HSK-*.manifest.json')):
 rec=json.loads(file.read_text());bpy.ops.wm.open_mainfile(filepath=str(BASE/rec['source']));bpy.context.view_layer.update();parts=[];shapes={};checks=[]
 for ob in [o for o in bpy.context.scene.objects if o.type=='MESH']:
  me=ob.data;me.calc_loop_triangles();v=np.array([list(ob.matrix_world@v.co)for v in me.vertices]);t=np.array([list(q.vertices)for q in me.loop_triangles]);n,d,a=planes(v,t);shapes[ob.name]=(v,n,d);conv=float(np.max(n@v.T+d[:,None]));uv=me.uv_layers.active;ua=[]
  for tr in me.loop_triangles:
   q=np.array([list(uv.data[i].uv)for i in tr.loops]);ua.append(abs(np.cross(q[1]-q[0],q[2]-q[0])))
  mats=[s.material for s in ob.material_slots if s.material];packed=all(all(n.image.packed_file for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image)for m in mats)
  checks.append({'part':ob.name,'max_convex_violation_m':conv,'minimum_triangle_double_area':float(min(a)),'minimum_uv_double_area':float(min(ua)),'packed':packed,'passes':conv<3e-6 and min(a)>1e-9 and min(ua)>1e-12 and packed});parts.append({'name':ob.name,'parent':ob.parent.name,'movement_group':ob['movement_group'],'vertices':v.tolist(),'triangles':t.tolist(),'material_role':ob['material_role'],'body_candidate_keep':ob['body_candidate_keep'],'body_omission_max_distance_m':ob['body_omission_max_distance_m']})
 contacts=[]
 for m in rec['physical_and_proposal_markers']:
  ob=bpy.data.objects[m['name']];p=np.array(list(ob.matrix_world.translation));row={'name':m['name'],'position_error_m':float(np.linalg.norm(p-m['source_m'])),'parent_matches':ob.parent.name==m['parent_root']};ok=row['position_error_m']<2e-6 and row['parent_matches']
  if m['physical_part']:
   v,n,d=shapes[m['physical_part']];values=n@p+d;active=n[np.abs(values)<3e-6];dot=float(np.max(active@np.array(m.get('direction_source',[0,0,0]))))if len(active)else-1;row.update(surface_max_signed_m=float(max(values)),normal_dot=dot);ok=ok and abs(max(values))<3e-6 and (dot>.999 if 'direction_source'in m else True)
  row['passes']=bool(ok);contacts.append(row)
 joins=[]
 for j in rec['joins']:
  p=np.array(j['probe_source_m']);err=[float(max(shapes[k][1]@p+shapes[k][2]))for k in j['parts']];joins.append({'name':j['name'],'parts':j['parts'],'maximum_signed_distances_m':err,'passes':max(err)<3e-6})
 row={'catalogue_id':rec['catalogue_id'],'source_sha256':sha(BASE/rec['source']),'parts':checks,'markers':contacts,'joins':joins,'all_passed':all(x['passes']for x in checks+contacts+joins)};rows.append(row);dump[rec['catalogue_id']]={'parts':parts,'markers':rec['physical_and_proposal_markers'],'voids':rec['receiver_voids'],'joins':rec['joins'],'motion_records':rec['motion_records']}
(BASE/'qa/source_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['all_passed']for r in rows)},indent=2)+'\n');(BASE/'qa/evaluated_source_geometry.json').write_text(json.dumps(dump));print([(r['catalogue_id'],r['all_passed'],[x.get('name',x.get('part'))for x in r['parts']+r['markers']+r['joins']if not x['passes']])for r in rows])
