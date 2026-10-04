"""Reload editable source and measure real support/stack contacts, no render."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def evaluated(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();v=[o.matrix_world@p.co for p in me.vertices];f=[list(p.vertices)for p in me.polygons];e.to_mesh_clear();return v,f
def closest(a,b):
 v,f=evaluated(a);vv,ff=evaluated(b);tree=BVHTree.FromPolygons(vv,ff,all_triangles=False);values=[tree.find_nearest(p)[3]for p in v];return min(x for x in values if x is not None)
def bounds(o):
 v,f=evaluated(o);return [[min(p[k]for p in v)for k in range(3)],[max(p[k]for p in v)for k in range(3)]]
rows=[]
for aid in['AST-HSP-005','AST-HSP-006']:
 path=BASE/'source'/(aid+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];tests=[]
 if aid.endswith('005'):
  for kind,num,pieces in[('tray',3,2),('plate',2,4)]:
   for i in range(num):
    group='005_'+kind+'_stock_'+str(i);first=bpy.data.objects[group+'_piece_0'];shelf=bpy.data.objects['005_'+kind+'_shelf_'+str(i)];gap=closest(first,shelf);tests.append({'parts':[first.name,shelf.name],'kind':'initial_stock_on_shelf','surface_gap_m':gap,'passed':gap<2e-6})
    for k in range(1,pieces):
     a=bpy.data.objects[group+'_piece_'+str(k)];b=bpy.data.objects[group+'_piece_'+str(k-1)];gap=closest(a,b);tests.append({'parts':[a.name,b.name],'kind':'nested_stock_contact','surface_gap_m':gap,'passed':gap<2e-6})
    for k in range(2):
     cleat=bpy.data.objects['005_'+kind+'_shelf_'+str(i)+'_folded_cleat_'+str(k)];gap=closest(shelf,cleat);tests.append({'parts':[shelf.name,cleat.name],'kind':'folded_cleat_support','surface_gap_m':gap,'passed':gap<2e-6})
 floor=[o for o in obs if'leveling_foot'in o.name or'rubber_wheel'in o.name]
 for o in floor:
  lo,hi=bounds(o);tests.append({'part':o.name,'kind':'actual_floor_bottom','bottom_source_z_m':lo[2],'passed':abs(lo[2])<2e-6})
 packed=[]
 roles=set()
 for o in obs:
  for mat in o.data.materials:
   roles.add(mat.get('astraea_material_role',mat.name))
   for node in mat.node_tree.nodes:
    if node.type=='TEX_IMAGE':packed.append({'image':node.image.name,'packed':bool(node.image.packed_file),'size':list(node.image.size)})
 row={'catalogue_id':aid,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reloaded':True,'semantic_mesh_parts':len(obs),'unit_scale':bpy.context.scene.unit_settings.scale_length,'unit_system':bpy.context.scene.unit_settings.system,'retained_modifier_count':sum(len(o.modifiers)for o in obs),'material_roles':sorted(roles),'all_referenced_images_packed':all(x['packed']for x in packed),'nonpositive_object_scale': [o.name for o in obs if any(s<=0 for s in o.scale)],'all_parts_have_metric_uv':all(o.data.uv_layers.active and o.data.uv_layers.active.name=='metric_material_uv'for o in obs),'support_and_stack_tests':tests,'passed':all(x['passed']for x in tests)and all(x['packed']for x in packed)};rows.append(row)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(x['passed']for x in rows)},indent=2)+'\n');print(json.dumps(rows,indent=2));assert all(x['passed']for x in rows)
