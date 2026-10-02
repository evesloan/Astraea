"""Reload actual editable sources; test support pixels geometrically, real cavities and packed textures."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def tree(ob):
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));t=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);bpy.data.meshes.remove(me);return t
rows=[]
for ident in ('AST-HSP-003','AST-HSP-004'):
 path=BASE/'source'/f'{ident}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];trees={o.name:tree(o) for o in obs};contacts=[];cavities=[]
 for ob in obs:
  if ob.name.startswith(('counter_contact_pad_','floor_pad_')):
   z=min((ob.matrix_world@v.co).z for v in ob.data.vertices);contacts.append({'part':ob.name,'min_source_z_m':z,'passes':abs(z)<1e-7})
 def near(marker,part):
  p=bpy.data.objects[marker].matrix_world.translation;co,no,i,d=trees[part].find_nearest(p);contacts.append({'marker':marker,'part':part,'point_source_m':list(p),'nearest_surface_distance_m':d,'tolerance_m':.000025,'passes':d<.000025})
 def ray(name,start,end):
  d=Vector(end)-Vector(start);length=d.length;d.normalize();hits=[]
  for n,t in trees.items():
   co,no,ix,dist=t.ray_cast(Vector(start),d,length)
   if co is not None:hits.append({'part':n,'distance_m':dist})
  cavities.append({'name':name,'start_source_m':start,'end_source_m':end,'hits':hits,'passes':not hits})
 if ident.endswith('003'):
  near('DRIP_BASE_BEARING','drip_catch_floor');near('DRIP_BASE_BEARING','weighted_rounded_base')
  for i,x in enumerate((-.14,.14)):
   for j in range(4):near('CUP_BASE_RING_CONTACT_'+str(i)+'_'+str(j),'cup_base_annular_rest_'+str(i))
   for dx,dy in[(0,0),(.004,0),(0,.004)]:ray('real_spout_bore_'+str((i,dx,dy)),[x+dx,-.095+dy,.373],[x+dx,-.095+dy,.426])
   for dx in(-.05,0,.05):ray('cup_access_'+str((i,dx)),[x+dx,-.23,.22],[x+dx,-.029,.22])
 else:
  near('DISH_TRAY_RECEIVING_SURFACE','receiving_caddy_floor')
  for x in(-.421,.421):near('CADDY_RAIL_BEARING_'+str(x),'caddy_runner_'+str(x))
  for x in(-.35,-.225,0,.225,.35):ray('pass_through_receiving_opening_'+str(x),[x,-.425,1.04],[x,.42,1.04])
  for x in(-.25,0,.25):ray('lower_staff_compartment_'+str(x),[x,.405,.55],[x,-.25,.55])
 used=[]
 for mat in set(s.material for ob in obs for s in ob.material_slots if s.material):
  images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image];used.append({'material':mat.name,'has_images':bool(images),'all_packed':all(i.packed_file is not None for i in images)})
 rows.append({'catalogue_id':ident,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mesh_objects':len(obs),'editable_modifiers':sum(len(o.modifiers)for o in obs),'contacts':contacts,'cavity_ray_checks':cavities,'materials':used,'passes':all(r['passes']for r in contacts+cavities)and all(x['has_images']and x['all_packed']for x in used)})
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes'])for r in rows])
