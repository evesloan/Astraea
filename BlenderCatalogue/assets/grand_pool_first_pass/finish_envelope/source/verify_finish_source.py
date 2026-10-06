"""Independent Blender reopen QA for the NEW source; never saves the .blend."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
HERE=Path(__file__).resolve().parents[1];CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');D=json.loads((HERE/'source/finish_contract.json').read_text());SOURCE=HERE/'source/grand_pool_finish_envelope.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(SOURCE);bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();issues=[];records=[]
assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==len(D['parts'])
assert len([o for o in bpy.context.scene.objects if o.type=='EMPTY'])==14
assert not [o for o in bpy.context.scene.objects if o.type not in {'MESH','EMPTY'}]
for row in D['parts']:
 ob=bpy.data.objects.get(row['name']);assert ob is not None and ob.type=='MESH';eo=ob.evaluated_get(deps);me=eo.to_mesh();me.calc_loop_triangles();vv=[eo.matrix_world@v.co for v in me.vertices];actual=[Vector((v.x,v.z,-v.y)) for v in vv];expected=[Vector(v) for v in row['world_vertices']]
 tree=KDTree(len(actual))
 for i,v in enumerate(actual):tree.insert(v,i)
 tree.balance();error=max(tree.find(v)[2] for v in expected)
 tree2=KDTree(len(expected))
 for i,v in enumerate(expected):tree2.insert(v,i)
 tree2.balance();error=max(error,max(tree2.find(v)[2] for v in actual))
 if error>.00010:issues.append({'object':ob.name,'source_vertex_error_m':error})
 degenerate=[t.index for t in me.loop_triangles if t.area<1e-11]
 if degenerate:issues.append({'object':ob.name,'degenerate_triangles':degenerate})
 bm=bmesh.new();bm.from_mesh(me);bad_edges=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 if bad_edges:issues.append({'object':ob.name,'nonmanifold_edges':bad_edges})
 if volume<=0:issues.append({'object':ob.name,'nonpositive_volume':volume})
 if not me.uv_layers or len(me.uv_layers.active.data)!=len(me.loops):issues.append({'object':ob.name,'uv_coverage':'missing'})
 if str(ob.get('material_role'))!=row['material_role'] or len(me.materials)!=1:issues.append({'object':ob.name,'wrong_material_assignment':True})
 if ob.get('collision_contract')!=row['collision_contract']:issues.append({'object':ob.name,'collision_contract_changed':True})
 records.append({'part':ob.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'max_source_vertex_error_m':error,'closed':not bad_edges,'signed_volume_m3':volume,'material':me.materials[0].name if me.materials else None})
 eo.to_mesh_clear()
for f in D['fixtures']:
 ob=bpy.data.objects.get(f['name']);assert ob is not None and ob.type=='EMPTY';actual=Vector((ob.matrix_world.translation.x,ob.matrix_world.translation.z,-ob.matrix_world.translation.y));err=(actual-Vector(f['position_xyz'])).length
 if err>.0001:issues.append({'marker':ob.name,'position_error_m':err})
 if (Vector(ob['direction_godot_xyz'])-Vector(f['direction_xyz'])).length>1e-6:issues.append({'marker':ob.name,'direction_changed':True})
 for field in ['physical_housing','physical_lens']:
  if ob[field]!=f[field] or bpy.data.objects.get(f[field]) is None:issues.append({'marker':ob.name,'missing_physical_part':field})
# Compare full source material graphs and embedded image content to the actual
# retained exemplars, instead of treating a familiar material name as proof.
def mat_signature(mat):
 nodes=[]
 for node in mat.node_tree.nodes:
  inputs={}
  for socket in node.inputs:
   if not hasattr(socket,'default_value'):continue
   value=socket.default_value
   if isinstance(value,(float,int,str,bool)):inputs[socket.name]=value
   else:
    try:inputs[socket.name]=list(value)
    except TypeError:continue
  info={'name':node.name,'type':node.bl_idname,'inputs':inputs}
  if node.type=='TEX_IMAGE' and node.image:
   im=node.image;packed=im.packed_file or (im.packed_files[0].packed_file if im.packed_files else None);info['image']={'size':list(im.size),'packed_sha256':hashlib.sha256(bytes(packed.data)).hexdigest() if packed else None,'interpolation':node.interpolation}
  nodes.append(info)
 links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links)
 return {'nodes':sorted(nodes,key=lambda x:x['name']),'links':links,'metric_tile_m':list(mat.get('meters_per_tile_uv',[1,1]))}
exemplars={'ivory_enamel':'GP_WestWallBand','warm_stone':'GP_SculptedPier_0','warm_walnut':'GP_VaultLamp_-433_-36_Recess','champagne_metal':'GP_GlazingMullion','aquatic_edge_tile':'GP_BasinWall_Port','lens':'GP_VaultLamp_-433_-36_Lens'}
actual_mats={r['material_role']:bpy.data.objects[r['name']].data.materials[0] for r in D['parts']};material_checks=[]
with bpy.data.libraries.load(str(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend'),link=False) as(src,dst):dst.objects=list(exemplars.values())
refs={ob.name:ob for ob in dst.objects}
for role,name in exemplars.items():
 equal=mat_signature(actual_mats[role])==mat_signature(refs[name].data.materials[0]);material_checks.append({'role':role,'exact_original_graph_and_packed_images':equal})
 if not equal:issues.append({'material_role':role,'retained_graph_or_image_changed':True})
for im in bpy.data.images:
 if im.source not in {'FILE','GENERATED'}:continue
 if min(im.size)<=0 or (im.source=='FILE' and not(im.packed_file or im.packed_files)):issues.append({'image':im.name,'empty_or_unpacked':True})
assert sha(SOURCE)==before,'Reopen QA must never rewrite source'
assert sha(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend')==D['original_inputs']['original_blend_sha256']
report={'status':'source_checks_pass' if not issues else 'source_checks_failed','source_sha256':before,'contract_sha256':sha(HERE/'source/finish_contract.json'),'mesh_parts':len(records),'fixture_markers':14,'triangles':sum(r['triangles'] for r in records),'max_vertex_error_m':max(r['max_source_vertex_error_m'] for r in records),'parts':records,'material_checks':material_checks,'issues':issues,'limits':['Source-only evaluated geometry/material/mount marker verification','Independent pure triangle geometry/contact/route/cone review is separate and must match this exact contract','No export/import/runtime/lighting-selection/normal-view/sign-legibility or final-art acceptance']}
(HERE/'qa/editable_source_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['parts','material_checks']},indent=2));assert not issues,'New editable source QA failed'
