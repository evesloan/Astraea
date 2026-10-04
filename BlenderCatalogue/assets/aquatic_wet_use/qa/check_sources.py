"""Actual reloaded evaluated source: contacts, complete support graph, entire AABB voids and rearward plate sweeps."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def geom(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];ts=[[vs[i]for i in tr.vertices]for tr in me.loop_triangles];tree=BVHTree.FromPolygons(vs,[list(t.vertices)for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear();return tree,ts

def inside(t,p):
 p=Vector(p);near=t.find_nearest(p)
 if near[3] is not None and near[3]<.00003:return True
 d=Vector((.937,.287,.199)).normalized();count=0;start=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(start,d,100)
  if co is None:break
  count+=1;start=co+d*.000001
 return count%2==1

def tri_box(tri,lo,hi):
 c=(Vector(lo)+Vector(hi))*.5;h=(Vector(hi)-Vector(lo))*.5;v=[p-c for p in tri];edges=[v[1]-v[0],v[2]-v[1],v[0]-v[2]];basis=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))];axes=basis+[edges[0].cross(edges[1])]+[e.cross(b)for e in edges for b in basis]
 for a in axes:
  if a.length_squared<1e-18:continue
  dots=[p.dot(a)for p in v];r=sum(abs(a[i])*h[i]for i in range(3))
  if min(dots)>r+1e-9 or max(dots)<-r-1e-9:return False
 return True

def clear_volume(v,trees,tris,exclude=()):
 lo,hi=v['min_source_m'],v['max_source_m'];hits=[];center=(Vector(lo)+Vector(hi))*.5
 for name,t in trees.items():
  if name in exclude:continue
  n=sum(tri_box(tri,lo,hi)for tri in tris[name]);enc=inside(t,center)
  if n or enc:hits.append({'part':name,'triangle_intersections':n,'box_center_in_solid':enc})
 return {'name':v.get('name','removal sweep'),'method':'Complete triangle/AABB separating-axis intersection plus center containment; boundary inclusive; all evaluated triangles','hits':hits,'passes':not hits}
rows=[]
for recpath in sorted(BASE.glob('AST-AQU-*.manifest.json')):
 rec=json.loads(recpath.read_text());path=BASE/rec['source'];bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];data={o.name:geom(o)for o in obs};trees={k:v[0]for k,v in data.items()};tris={k:v[1]for k,v in data.items()};contacts=[];joins=[]
 for m in rec['physical_and_proposal_markers']:
  o=bpy.data.objects[m['name']];p=o.matrix_world.translation;row={'name':m['name'],'source_node_position_m':list(p),'position_matches':(p-Vector(m['source_m'])).length<1e-6}
  if m['physical_part']:
   near=trees[m['physical_part']].find_nearest(p);row.update(part=m['physical_part'],surface_distance_m=near[3],surface_matches=near[3]<.00015)
   if 'surface_normal_source'in m:alignment=Vector(m['surface_normal_source']).normalized().dot(near[1]);row.update(physical_normal_dot=alignment,normal_matches=alignment>.99)
  row['passes']=row['position_matches']and row.get('surface_matches',True)and row.get('normal_matches',True);contacts.append(row)
 for ix,j in enumerate(rec['joins']):
  p=Vector(j['probe_source_m']);ds=[trees[n].find_nearest(p)[3]for n in j['parts']];ins=[inside(trees[n],p)for n in j['parts']];joins.append({'name':'join_'+str(ix),'kind':j['kind'],'parts':j['parts'],'probe_source_m':list(p),'boundary_distances_m':ds,'probe_inside_or_on_both':ins,'passes':all(ins)})
 adj={o.name:set()for o in obs}
 for j in joins:
  if j['passes']:a,b=j['parts'];adj[a].add(b);adj[b].add(a)
 connected=set();todo=[m['physical_part']for m in rec['physical_and_proposal_markers']if m['name']=='FLOOR_CONTACT']
 while todo:
  n=todo.pop()
  if n in connected:continue
  connected.add(n);todo.extend(adj[n]-connected)
 voids=[clear_volume(v,trees,tris)for v in rec['receiver_voids']];removal=[dict(clear_volume(dict(r['reserve'],name=r['name']),trees,tris,r['parts']),translation_source_m=r['translation_source_m'])for r in rec['removal_proposals']]
 # Positive solid control establishes that full-volume intersections actually reject occupied air.
 control=clear_volume({'name':'positive_plinth_control','min_source_m':[-.03,-.03,.04],'max_source_m':[.03,.03,.07]},trees,tris)
 mats=[]
 for mat in set(s.material for ob in obs for s in ob.material_slots if s.material):
  images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mats.append({'role':mat.name,'images_packed':bool(images)and all(i.packed_file for i in images),'emission_strength':float(bs.inputs['Emission Strength'].default_value)})
 row={'catalogue_id':rec['catalogue_id'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'editable_meshes':len(obs),'editable_modifiers':sum(len(o.modifiers)for o in obs),'physical_marker_checks':contacts,'joint_checks':joins,'complete_support_graph':{'root':'FLOOR_CONTACT','connected_count':len(connected),'all_semantic_parts':len(obs),'unsupported':sorted(set(trees)-connected),'passes':len(connected)==len(obs)},'void_checks':voids,'removal_checks':removal,'positive_solid_control_detected':not control['passes'],'material_checks':mats,'passes':all(x['passes']for x in contacts+joins+voids+removal)and len(connected)==len(obs)and all(x['images_packed']for x in mats)and not control['passes']};rows.append(row)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes'],r['complete_support_graph']['unsupported'],[x['name']for x in r['physical_marker_checks']+r['joint_checks']+r['void_checks']+r['removal_checks']if not x['passes']])for r in rows])
