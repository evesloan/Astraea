"""Reload .blend files; physical markers, real voids and editable material audit."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];ps=[list(p.vertices)for p in me.polygons];t=BVHTree.FromPolygons(vs,ps);ev.to_mesh_clear();return t
def inside(t,p):
 p=Vector(p);near=t.find_nearest(p)
 if near[3] is not None and near[3]<.00003:return True
 d=Vector((.937,.287,.199)).normalized();count=0;start=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(start,d,100)
  if co is None:break
  count+=1;start=co+d*.000001
 return count%2==1
rows=[]
for recpath in sorted(BASE.glob('AST-LND-*.manifest.json')):
 rec=json.loads(recpath.read_text());path=BASE/rec['source'];bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];trees={o.name:tree(o)for o in obs};contacts=[];joins=[];voids=[]
 for m in rec['physical_and_proposal_markers']:
  o=bpy.data.objects[m['name']];p=o.matrix_world.translation;row={'name':m['name'],'source_node_position_m':list(p),'expected_m':m['source_m'],'position_matches':(p-Vector(m['source_m'])).length<1e-6}
  if m['physical_part']:
   near=trees[m['physical_part']].find_nearest(p);row.update(part=m['physical_part'],surface_distance_m=near[3],surface_matches=near[3]<.00015)
   if 'direction_source'in m:
    alignment=Vector(m['direction_source']).normalized().dot(near[1]);row['physical_normal_dot']=alignment;row['normal_matches']=alignment>.99
  row['passes']=row['position_matches']and row.get('surface_matches',True)and row.get('normal_matches',True);contacts.append(row)
 for j in rec['joins']:
  p=Vector(j['probe_source_m']);ds=[trees[n].find_nearest(p)[3]for n in j['parts']];ins=[inside(trees[n],p)for n in j['parts']];joins.append({'name':j['name'],'parts':j['parts'],'probe_source_m':list(p),'boundary_distances_m':ds,'probe_inside_or_on_both':ins,'passes':all(ins)})
 for v in rec['receiver_voids']:
  lo,hi=v['min_source_m'],v['max_source_m'];hits=[]
  # Dense cross-front ray grid through the proposed empty box, against all real meshes.
  for ix in range(7):
   for iz in range(7):
    x=lo[0]+(hi[0]-lo[0])*(ix+.5)/7;z=lo[2]+(hi[2]-lo[2])*(iz+.5)/7;a=Vector((x,lo[1],z));d=Vector((0,1,0))
    for name,t in trees.items():
     co,no,i,dist=t.ray_cast(a,d,hi[1]-lo[1])
     if co is not None:hits.append({'part':name,'point':list(co)})
  voids.append({'name':v['name'],'rays':49,'hits':hits,'passes':not hits})
 mats=[]
 for mat in set(s.material for ob in obs for s in ob.material_slots if s.material):
  images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mats.append({'role':mat.name,'images_packed':bool(images)and all(i.packed_file for i in images),'emission_strength':float(bs.inputs['Emission Strength'].default_value)})
 rows.append({'catalogue_id':rec['catalogue_id'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'editable_meshes':len(obs),'editable_modifiers':sum(len(o.modifiers)for o in obs),'physical_marker_checks':contacts,'joint_checks':joins,'void_checks':voids,'material_checks':mats,'no_light_objects':not any(o.type=='LIGHT'for o in bpy.context.scene.objects),'passes':all(x['passes']for x in contacts+joins+voids)and all(x['images_packed']for x in mats)})
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n')
print([(r['catalogue_id'],r['passes'],[x['name']for x in r['physical_marker_checks']+r['joint_checks']+r['void_checks']if not x['passes']])for r in rows])
