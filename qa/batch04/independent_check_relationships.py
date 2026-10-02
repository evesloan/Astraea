"""Actual evaluated source geometry, read-only BVH contact and topology inspection."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch04'
def geometry(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 vs=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];edges={}
 weldmap={};weld=[]
 for v in vs:
  key=tuple(round(c,6) for c in v);weld.append(weldmap.setdefault(key,len(weldmap)))
 for face in fs:
  f=tuple(weld[k] for k in face)
  for a,b in zip(f,f[1:]+f[:1]):
   key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
 result={'verts':vs,'faces':fs,'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=True),'boundary':sum(n==1 for n in edges.values()),'nonmanifold':sum(n>2 for n in edges.values()),'lo':[min(v[i] for v in vs) for i in range(3)],'hi':[max(v[i] for v in vs) for i in range(3)]}
 ev.to_mesh_clear();return result
def point_info(g,p):
 p=Vector(p);co,n,idx,dist=g['bvh'].find_nearest(p)
 return {'surface_distance_m':dist,'nearest_normal_signed_distance_m':(p-co).dot(n),'inside_or_on':dist<2e-6 or (p-co).dot(n)<0}
def interface(a,b):
 candidates=a['verts']+[sum((a['verts'][k] for k in f),Vector())/3 for f in a['faces']]
 dist=min(b['bvh'].find_nearest(p)[3] for p in candidates)
 return {'sampled_vertex_face_center_min_surface_distance_m':dist,'contact_within_10um':dist<1e-5,'a_bounds':[a['lo'],a['hi']],'b_bounds':[b['lo'],b['hi']]}
reports=[]
for family in ['botanical_canopy','botanical_understory','botanical_planter']:
 for path in sorted((ROOT/'assets'/family).rglob('*.blend')):
  if not path.stem.startswith('AST-BOT-'):continue
  bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);obs={o.name:o for o in bpy.context.scene.objects if o.type in ['MESH','CURVE']};geo={n:geometry(o) for n,o in obs.items()}
  r={'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'topology':[],'contacts':[],'issues':[]}
  for n,g in geo.items():
   kind=obs[n].get('semantic_kind',obs[n].get('surface_kind',''))
   r['topology'].append({'part':n,'kind':kind,'boundary_edges':g['boundary'],'nonmanifold_edges':g['nonmanifold'],'min_xyz':g['lo'],'max_xyz':g['hi']})
   if ('closed' in kind or family=='botanical_planter') and (g['boundary'] or g['nonmanifold']):r['issues'].append(n+': unexpectedly open or nonmanifold source solid')
  if family=='botanical_canopy':
   for n,o in obs.items():
    parent=o.get('parent_branch')
    if parent and parent!='soil_plane':
     start=list(o.data.splines[0].points[0].co)[:3];info=point_info(geo[parent],start);rec={'child':n,'parent':parent,'child_actual_curve_start_m':start,'parent_actual_surface_test':info};r['contacts'].append(rec)
     if not info['inside_or_on']:r['issues'].append(n+': curve root outside parent solid')
    if 'leaf_attachment_records' in o:
     for leaf in json.loads(o['leaf_attachment_records']):
      pet=obs[leaf['petiole']];end=list(pet.data.splines[0].points[-1].co)[:3];d=geo[n]['bvh'].find_nearest(Vector(end))[3]
      r['contacts'].append({'leaf_group':n,'petiole':pet.name,'actual_endpoint_to_actual_leaf_surface_m':d})
      if d>2e-6:r['issues'].append(pet.name+': actual leaf attachment gap')
  elif family=='botanical_understory':
   manifest=json.loads((ROOT/'assets'/family/(path.stem+'.manifest.json')).read_text())
   for j in manifest['support_joints']:
    p=j['child_attachment_m'];a=point_info(geo[j['child']],p);b=point_info(geo[j['parent']],p)
    r['contacts'].append({'child':j['child'],'parent':j['parent'],'attachment_m':p,'child_actual_surface_test':a,'parent_actual_surface_test':b})
    if not a['inside_or_on'] or not b['inside_or_on']:r['issues'].append(j['child']+': recorded joint point not on/in both actual meshes')
  else:
   pairs=[]
   brackets=sorted(n for n in obs if n.startswith('seat_load_bracket'))
   ribbons=sorted(n for n in obs if n.startswith('timber_sitting_ribbon'))
   rails=sorted(n for n in obs if n.startswith('timber_underseat'))
   for n in brackets:
    shoe=n.replace('seat_load_bracket','floor_contact_bracket_shoe');pairs.append((shoe,n))
    pairs.extend((n,rib) for rib in ribbons)
   for n,rib in zip(rails,[ribbons[0],ribbons[2]]):pairs.append((n,rib))
   pairs.extend([('soil_volume_with_usable_planting_surface','recessed_cavity_bottom'),('soil_volume_with_usable_planting_surface','sculpted_front_basin_wall'),('soil_volume_with_usable_planting_surface','sloped_rear_basin_wall')])
   for a,b in pairs:
    q=interface(geo[a],geo[b]);q.update(a=a,b=b);r['contacts'].append(q)
    if not q['contact_within_10um']:r['issues'].append(a+' -> '+b+': no sampled direct surface contact; inspect overlap/support extent')
  reports.append(r)
(OUT/'independent_actual_support_relationships.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps([{'source':r['source'],'contacts_checked':len(r['contacts']),'issues':r['issues']} for r in reports],indent=2))
