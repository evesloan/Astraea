"""Reload saved Blender sources and measure contacts, finish containment and bores."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def bvh(ob):
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);bpy.data.meshes.remove(me);return tree

def contained(tree,p):
 co,no,idx,d=tree.find_nearest(Vector(p));signed=(Vector(p)-co).dot(no)
 return {'point_source_m':list(p),'nearest_distance_m':d,'signed_distance_m':signed,'inside_closed_finish':signed<=.000002}

rows=[]
for ident in('AST-ENG-001','AST-ENG-002'):
 path=BASE/'source'/f'{ident}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));obs=[o for o in bpy.data.objects if o.type=='MESH'];contacts=[];support=[]
 for ob in obs:
  if ob.name.startswith(('floor_pad_','filter_floor_pad_')):
   zmin=min((ob.matrix_world@v.co).z for v in ob.data.vertices);contacts.append({'name':ob.name,'source_z_min_m':zmin,'passes':abs(zmin)<1e-7})
 if ident=='AST-ENG-001':
  cases=[('pump_cast_mount_web','cast_pump_chamber_with_open_X_bore'),('motor_saddle_web','drive_motor_cast_housing')]
 else:cases=[('filter_splayed_closed_leg','filter_hollow_formed_shell')]
 for prefix,target in cases:
  tree=bvh(bpy.data.objects[target])
  for ob in obs:
   if ob.name.startswith(prefix):
    if prefix=='filter_splayed_closed_leg':points=[ob.matrix_world@v.co for v in ob.data.vertices if v.index>=4]
    else:
     top=max(v.co.z for v in ob.data.vertices);points=[ob.matrix_world@v.co for v in ob.data.vertices if abs(v.co.z-top)<1e-6]
    checks=[contained(tree,p) for p in points];support.append({'support':ob.name,'finished_body':target,'top_cap_vertex_probes':checks,'passes':all(c['inside_closed_finish'] for c in checks)})
 if ident=='AST-ENG-001':
  for ob in obs:
   if ob.name.startswith('coupling_guard_standoff_'):
    x=ob.data.vertices[0].co.x+.011;side=-.134 if x<0 else .134
    for end,target,limit in [('top','coupling_guard_skirt_'+str(side),max(v.co.z for v in ob.data.vertices)),('bottom','load_crossmember_0.354',min(v.co.z for v in ob.data.vertices))]:
     tree=bvh(bpy.data.objects[target]);points=[ob.matrix_world@v.co for v in ob.data.vertices if abs(v.co.z-limit)<1e-6];checks=[contained(tree,p) for p in points]
     support.append({'support':ob.name+'_'+end,'finished_body':target,'cap_vertex_probes':checks,'passes':all(c['inside_closed_finish'] for c in checks)})
 bore=[]
 # Actual source ray proof of central unobstructed bore from each external face into body chamber.
 alltrees=[(o.name,bvh(o)) for o in obs]
 face=.85 if ident=='AST-ENG-001' else .64
 for sign in(-1,1):
  # Start at bare face and travel into chamber; slight radial offsets challenge fake caps.
  for y,zoff in[(0,0),(.055,0),(-.055,0),(0,.055),(0,-.055)]:
   start=Vector((sign*(face+.005),y,.60+zoff));direction=Vector((-sign,0,0));length=face+.005 if ident=='AST-ENG-002' else 2*face+.01
   hits=[]
   for name,tree in alltrees:
    loc,no,idx,dist=tree.ray_cast(start,direction,length)
    if loc is not None:hits.append({'part':name,'distance_m':dist,'point_m':list(loc)})
   bore.append({'side':sign,'offset_yz_m':[y,zoff],'tested_length_m':length,'hits':hits,'passes':not hits})
 used=[]
 for mat in set(slot.material for ob in obs for slot in ob.material_slots if slot.material):
  imgs=[node.image for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image]
  used.append({'material':mat.name,'images':[im.name for im in imgs],'packed':all(im.packed_file is not None for im in imgs),'has_used_image':bool(imgs)})
 row={'catalogue_id':ident,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'editable_mesh_objects':len(obs),'floor_contacts':contacts,'finished_surface_support_containment':support,'bore_ray_checks':bore,'used_material_images':used,'passes':all(c['passes'] for c in contacts+support+bore) and all(x['packed'] and x['has_used_image'] for x in used)};rows.append(row)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'scope':'Saved editable sources reloaded; explicit vertex containment and multi-offset bore ray tests. No operating behavior/rating verification.','assets':rows,'all_passed':all(r['passes'] for r in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes']) for r in rows])
