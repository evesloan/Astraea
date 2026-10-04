"""Reload editable sources; exact physical witnesses and complete geometry dump."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];tri=[list(t.vertices)for t in me.loop_triangles];t=BVHTree.FromPolygons(vs,tri,all_triangles=True);ev.to_mesh_clear();return t,vs,tri
def in_convex(part,p):
 vs=np.array(part['vertices'],dtype=float);tr=vs[np.array(part['triangles'])];ns=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);ns/=np.linalg.norm(ns,axis=1)[:,None];return bool(np.max(np.sum(ns*(np.array(p)-tr[:,0]),axis=1))<2e-6)
def inside(t,p):
 p=Vector(p);q=t.find_nearest(p)
 if q[3]is not None and q[3]<.000002:return True
 d=Vector((.937,.287,.199)).normalized();count=0;a=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(a,d,100)
  if co is None:break
  count+=1;a=co+d*.0000001
 return bool(count%2)
rows=[];dumps={}
for rp in sorted(BASE.glob('AST-CUL-*.manifest.json')):
 rec=json.loads(rp.read_text());p=BASE/rec['source'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];trees={};parts=[]
 for ob in obs:
  t,vs,ts=tree(ob);trees[ob.name]=t;parts.append({'name':ob.name,'parent':ob.parent.name,'movement_group':ob.get('movement_group'),'vertices':[list(v)for v in vs],'triangles':ts,'material_role':ob['material_role'],'source_uv_count':len(ob.data.uv_layers),'source_modifiers':[m.type for m in ob.modifiers]})
 contacts=[];joins=[]
 for m in rec['physical_and_proposal_markers']:
  ob=bpy.data.objects[m['name']];p=ob.matrix_world.translation;row={'name':m['name'],'source_position_m':list(p),'matches_declared_position':(p-Vector(m['source_m'])).length<1e-6,'parent_root':ob.parent.name,'parent_matches':ob.parent.name==m['parent_root']}
  if m['physical_part']:
   near=trees[m['physical_part']].find_nearest(p);row.update(part=m['physical_part'],surface_distance_m=near[3],surface_matches=near[3]<.00001)
   if 'direction_source'in m:row['normal_dot']=Vector(m['direction_source']).normalized().dot(near[1]);row['normal_matches']=row['normal_dot']>.99
  row['passes']=row['matches_declared_position']and row['parent_matches']and row.get('surface_matches',True)and row.get('normal_matches',True);contacts.append(row)
 for j in rec['joins']:
  p=Vector(j['probe_source_m']);ds=[trees[n].find_nearest(p)[3]for n in j['parts']];ins=[in_convex(next(pa for pa in parts if pa['name']==n),p)for n in j['parts']];row={'name':j['name'],'parts':j['parts'],'kind':j['kind'],'advisory_float_BVH_distances_m':ds,'contact_acceptance_method':'Double-precision evaluated triangle planes for complete convex parts, 2 micrometre tolerance','inside_or_on_both':ins,'passes':all(ins)}
  if 'normal_a_source'in j:
   nd=[Vector(j[key]).dot(trees[name].find_nearest(p)[1])for key,name in zip(('normal_a_source','normal_b_source'),j['parts'])];row['normal_dots']=nd;row['passes']=row['passes']and all(x>.99 for x in nd)
  joins.append(row)
 mats=[]
 for mat in set(s.material for ob in obs for s in ob.material_slots if s.material):
  ims=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mats.append({'role':mat.name,'packed':bool(ims)and all(i.packed_file for i in ims),'emission_strength':float(bs.inputs['Emission Strength'].default_value)})
 row={'catalogue_id':rec['catalogue_id'],'source_sha256':hashlib.sha256((BASE/rec['source']).read_bytes()).hexdigest(),'editable_meshes':len(obs),'physical_markers':contacts,'joins':joins,'materials':mats,'no_light_objects':not any(o.type=='LIGHT'for o in bpy.context.scene.objects),'passes':all(x['passes']for x in contacts+joins)and all(m['packed']for m in mats)};rows.append(row);dumps[rec['catalogue_id']]={'parts':parts,'markers':rec['physical_and_proposal_markers'],'voids':rec['receiver_voids'],'joins':rec['joins'],'motion_records':rec['motion_records']}
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');(BASE/'qa/evaluated_source_geometry.json').write_text(json.dumps(dumps))
print([(r['catalogue_id'],r['passes'],[x['name']for x in r['physical_markers']+r['joins']if not x['passes']])for r in rows])
