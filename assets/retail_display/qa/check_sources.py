"""Reload actual saved sources; convex profiles, metric UVs, support patches, normals and joins."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def planes(v,t):
 q=v[t];n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);a=np.linalg.norm(n,axis=1);n/=a[:,None];return n,-np.sum(n*q[:,0],axis=1),a
rows=[];dump={}
for f in sorted(BASE.glob('AST-RTL-*.manifest.json')):
 rec=json.loads(f.read_text());bpy.ops.wm.open_mainfile(filepath=str(BASE/rec['source']));bpy.context.view_layer.update();parts=[];shapes={};checks=[]
 for ob in[o for o in bpy.context.scene.objects if o.type=='MESH']:
  me=ob.data;me.calc_loop_triangles();v=np.array([list(ob.matrix_world@q.co)for q in me.vertices]);t=np.array([list(q.vertices)for q in me.loop_triangles]);n,d,a=planes(v,t);shapes[ob.name]=(v,n,d);conv=float(np.max(n@v.T+d[:,None]));uv=me.uv_layers.active;ua=[]
  for tr in me.loop_triangles:
   q=np.array([list(uv.data[i].uv)for i in tr.loops]);ua.append(abs(float(np.linalg.det(np.array([q[1]-q[0],q[2]-q[0]])))))
  packed=all(node.image.packed_file for mat in ob.data.materials for node in mat.node_tree.nodes if node.type=='TEX_IMAGE'and node.image)
  checks.append({'part':ob.name,'whole_convex_profile_violation_m':conv,'minimum_triangle_double_area_m2':float(min(a)),'minimum_uv_double_area':float(min(ua)),'packed':packed,'passes':bool(conv<3e-6 and min(a)>1e-9 and min(ua)>1e-12 and packed)})
  parts.append({'name':ob.name,'parent':ob.parent.name,'vertices':v.tolist(),'triangles':t.tolist(),'material_role':ob['material_role'],'body_candidate_keep':ob['body_candidate_keep']})
 marks=[]
 for m in rec['physical_and_proposal_markers']:
  ob=bpy.data.objects[m['name']];p=np.array(list(ob.matrix_world.translation));err=float(np.linalg.norm(p-m['source_m']));row={'name':m['name'],'position_error_m':err};ok=err<2e-6
  if m['physical_part']:
   v,n,d=shapes[m['physical_part']];val=n@p+d;active=n[np.abs(val)<3e-6];dot=float(max(active@np.array(m.get('direction_source',[0,0,0]))))if len(active)else -1;row.update(surface_max_signed_m=float(max(val)),normal_dot=dot);ok=ok and abs(max(val))<3e-6 and dot>.999
  row['passes']=bool(ok);marks.append(row)
 joins=[]
 for j in rec['joins']:
  p=np.array(j['probe_source_m']);err=[float(max(shapes[k][1]@p+shapes[k][2]))for k in j['parts']];joins.append({'name':j['name'],'parts':j['parts'],'maximum_signed_distances_m':err,'passes':bool(max(err)<3e-6)})
 patches=[]
 for p in rec['support_patches']:
  v,n,d=shapes[p['physical_part']];pts=np.array(p['polygon_source_m']);vals=n@pts.T+d[:,None];maxs=np.max(vals,axis=0);tops=[n[i,2]for i in range(len(n))if np.all(np.abs(vals[i])<3e-6)];okay=float(max(maxs))<3e-6 and any(x>.999 for x in tops);patches.append({'name':p['name'],'whole_polygon_vertex_max_outside_m':float(max(maxs)),'all_vertices_on_same_up_face':any(x>.999 for x in tops),'passes':bool(okay)})
 row={'catalogue_id':rec['catalogue_id'],'source_sha256':sha(BASE/rec['source']),'parts':checks,'markers':marks,'joins':joins,'support_patches':patches,'all_passed':all(x['passes']for x in checks+marks+joins+patches)};rows.append(row);dump[rec['catalogue_id']]={'parts':parts,'markers':rec['physical_and_proposal_markers'],'voids':rec['useful_voids'],'joins':rec['joins'],'support_patches':rec['support_patches']}
 print(rec['catalogue_id'],row['all_passed'],[x.get('part',x.get('name'))for x in checks+marks+joins+patches if not x['passes']])
(BASE/'qa/source_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['all_passed']for r in rows)},indent=2)+'\n');(BASE/'qa/evaluated_source_geometry.json').write_text(json.dumps(dump)+'\n')
