"""Reload real sources; inspect all actual joins, surfaces, packed material graphs and profiles."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices)for p in ob.data.polygons])
def inside(t,p):
 p=Vector(p);near=t.find_nearest(p)
 if near[3]is not None and near[3]<.000025:return True
 d=Vector((.937,.287,.199)).normalized();count=0;start=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(start,d,100)
  if co is None:break
  count+=1;start=co+d*.000001
 return count%2==1

def clip(poly,axis,limit,keep_high):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=p[axis]>=limit if keep_high else p[axis]<=limit;b=q[axis]>=limit if keep_high else q[axis]<=limit
  if a:out.append(p)
  if a!=b:out.append(p.lerp(q,(limit-p[axis])/(q[axis]-p[axis])))
 return out
rows=[]
for rp in sorted(BASE.glob('AST-BOT-*.manifest.json')):
 rec=json.loads(rp.read_text());path=BASE/rec['source'];bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ts={o.name:tree(o)for o in obs};by={o.name:o for o in obs};contacts=[];joins=[];geo=[];mats=[];triangles={};duplicates=[]
 for m in rec['physical_and_proposal_markers']:
  o=bpy.data.objects[m['name']];p=o.matrix_world.translation;r={'name':m['name'],'source_node_m':list(p),'position_matches':(p-Vector(m['source_m'])).length<1e-6}
  if m['physical_part']:
   near=ts[m['physical_part']].find_nearest(p);r.update(surface_distance_m=near[3],surface_matches=near[3]<.00015)
   if 'normal_source'in m:r.update(normal_dot=near[1].dot(Vector(m['normal_source'])),normal_matches=near[1].dot(Vector(m['normal_source']))>.999)
  r['passes']=r['position_matches']and r.get('surface_matches',True)and r.get('normal_matches',True);contacts.append(r)
 for j in rec['joins']:
  p=Vector(j['probe_source_m']);child,parent=j['parts'];cd=ts[child].find_nearest(p)[3];pd=ts[parent].find_nearest(p)[3]
  ci=(cd<.000025)or(by[child]['surface_kind']=='closed_support'and inside(ts[child],p));pi=inside(ts[parent],p)
  joins.append({'name':j['name'],'parts':[child,parent],'probe_source_m':list(p),'child_distance_m':cd,'parent_distance_m':pd,'child_boundary_or_inside':ci,'parent_boundary_or_inside':pi,'passes':ci and pi})
 reached=set(rec.get('root_graph_parts',[rec['root_graph_part']]));edges=[j['parts']for j in rec['joins']if next(x for x in joins if x['name']==j['name'])['passes']]
 while True:
  old=len(reached)
  for a,b in edges:
   if a in reached or b in reached:reached.update([a,b])
  if len(reached)==old:break
 for ob in obs:
  me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);closed=ob['surface_kind']=='closed_support';boundary=sum(e.is_boundary for e in bm.edges);bad=sum(not e.is_manifold for e in bm.edges)if closed else 0;vol=bm.calc_volume(signed=True)if closed else None;bm.free();uv=me.uv_layers.active
  row={'name':ob.name,'closed_support':closed,'boundary_edges':boundary,'nonmanifold_closed_edges':bad,'signed_volume_m3':vol,'unit_object_scale':all(abs(x-1)<1e-8 for x in ob.scale),'finite_uv':bool(uv)and all(math.isfinite(c)for l in uv.data for c in l.uv),'vertices':len(me.vertices),'triangles':len(me.loop_triangles)};row['passes']=bad==0 and (vol is None or vol>0)and row['finite_uv']and row['unit_object_scale'];geo.append(row)
  for tr in me.loop_triangles:
   key=tuple(sorted(tuple(round(v,7)for v in me.vertices[i].co)for i in tr.vertices))
   if key in triangles:duplicates.append([ob.name,triangles[key]])
   else:triangles[key]=ob.name
 for mat in set(s.material for ob in obs for s in ob.material_slots if s.material):
  ims=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mats.append({'name':mat.name,'packed':bool(ims)and all(i.packed_file for i in ims),'alpha':bs.inputs['Alpha'].default_value,'two_sided':not mat.use_backface_culling})
 root_points=[]
 for m in rec['physical_and_proposal_markers']:
  if m['physical_part']:
   root_points.extend([ob.matrix_world@v.co for ob in [by[m['physical_part']]]for v in ob.data.vertices if abs((ob.matrix_world@v.co).z)<1e-6])
 root_bounds={'min_xy_m':[min(p[k]for p in root_points)for k in range(2)],'max_xy_m':[max(p[k]for p in root_points)for k in range(2)]}
 crossing=None
 if rec['catalogue_id']=='AST-BOT-008':
  clipped=[]
  for ob in obs:
   me=ob.data;me.calc_loop_triangles()
   for tr in me.loop_triangles:
    po=[ob.matrix_world@me.vertices[i].co for i in tr.vertices];po=clip(po,1,.164,True)
    if po:po=clip(po,1,.347,False)
    if po:clipped.extend((p,ob.name)for p in po)
  lowest=min(clipped,key=lambda x:x[0].z);crossing={'actual_coping_band_local_y_m':[.164,.347],'coping_top_above_soil_m':.04,'minimum_actual_mesh_z_in_band_m':lowest[0].z,'limiting_part':lowest[1],'vertical_clearance_m':lowest[0].z-.04,'checked':'All actual triangles geometrically clipped against both band boundaries, all foliage included','passes':lowest[0].z>.10}
 source_dump={o.name:{'vertices':[list(o.matrix_world@v.co)for v in o.data.vertices],'triangles':[list(tr.vertices)for tr in o.data.loop_triangles],'triangle_corners':[[{'position':list(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co),'uv':list(o.data.uv_layers.active.data[li].uv),'normal':list(o.data.corner_normals[li].vector)}for li in tr.loops]for tr in o.data.loop_triangles],'kind':o['surface_kind'],'material_role':o['material_role']}for o in obs}
 (BASE/'qa'/(rec['catalogue_id']+'_source_geometry.json')).write_text(json.dumps(source_dump))
 r={'catalogue_id':rec['catalogue_id'],'source_sha256':sha(path),'physical_marker_checks':contacts,'joint_checks':joins,'connected_semantic_parts':len(reached),'semantic_part_count':len(obs),'unconnected_parts':sorted(set(by)-reached),'root_contact_geometry_xy':root_bounds,'coping_crossing':crossing,'geometry':geo,'material_checks':mats,'identical_triangle_candidates':duplicates,'no_lights_or_cameras':not any(o.type in ('LIGHT','CAMERA')for o in bpy.context.scene.objects),'passes':all(x['passes']for x in contacts+joins+geo)and not(set(by)-reached)and not duplicates and all(x['packed']and x['alpha']==1 for x in mats)and(crossing is None or crossing['passes'])};rows.append(r)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n')
print([(r['catalogue_id'],r['passes'],r['unconnected_parts'],[j['name']for j in r['joint_checks']if not j['passes']],r['coping_crossing'])for r in rows])
