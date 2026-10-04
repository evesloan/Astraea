"""Derived arrangements only: reuse exactly the authored book/endstop meshes.
Source is AST-LIB-006_upright_book_group.blend. No unique new artistic assets.
"""
from pathlib import Path
import bpy,json,math,sys,hashlib,copy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent
(ROOT/'qa').mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT));import build_library_contents as lib
BASE=ROOT/'AST-LIB-006_upright_book_group.blend'
BASE_INFO=json.loads(BASE.with_suffix('.manifest.json').read_text())
W=[.042,.029,.052,.038,.034,.062,.026,.048,.036,.047]
H=[.278,.233,.263,.251,.226,.271,.238,.257,.246,.269]
D=[.214,.191,.207,.220,.184,.215,.202,.220,.193,.210]
recipes=[];audits=[]
def group(n):return bpy.data.objects['STOCK_volume_%02d_editable_volume'%n]
def stats(parts):return lib.point_bounds(parts)
def run(kind):
 bpy.ops.wm.open_mainfile(filepath=str(BASE));omitted=[];contact=[]
 if kind=='reordered':
  order=[1,6,2,9,4,10,5,3,8,7];cursor=-.195
  for n in order:
   group(n).matrix_world=Matrix.Translation((cursor+W[n-1]/2,(.220-D[n-1])/2,0));cursor+=W[n-1]
  description='All eleven original volumes retained. Tall first binding and supported lean remain together; remaining ten-volume order is deliberately changed.'
  contact=[{'book':'STOCK_volume_%02d'%n,'base_z_m':0,'support':'Shelf surface at asset pivot Z0','side_support':'Previous adjacent cover touching at X %.6f'%(group(n).matrix_world.translation.x-W[n-1]/2) if i else 'Original leaning crown touches left cover at X -.195'} for i,n in enumerate(order)]
  contact.append(copy.deepcopy(BASE_INFO['support_contact_proposal']['book_base_contacts'][-1]))
 else:
  order=[1,2,5,7,9];cursor=-.235
  for n in order:
   group(n).matrix_world=Matrix.Translation((cursor+W[n-1]/2,(.220-D[n-1])/2,0));cursor+=W[n-1]
  for ob in [bpy.data.objects['STOCK_volume_11_supported_lean_editable_volume'],bpy.data.objects['STOCK_L_weighted_champagne_heel']]:ob.location.x-=.040
  bpy.data.objects['STOCK_R_weighted_champagne_endstop'].location.x+=(cursor-.219)
  for n,z in [(8,0),(4,W[7])]:
   group(n).matrix_world=Matrix.Translation((.152-H[n-1]/2,0,z+W[n-1]/2))@Matrix.Rotation(math.pi/2,4,'Y')
  omitted=[3,6,10]
  description='Five upright original volumes plus the original supported lean at left; two existing volumes laid flat at right with full cover support. Three existing volumes intentionally omitted, leaving a quiet gap. All source meshes are unchanged.'
  contact=[{'members':['volume_11_supported_lean','volume_01'],'contact_m':[-.235,.005,.246*math.cos(math.radians(8))],'intent':'Original contact pair rigidly translated -.040m on X'},
           {'book':'volume_08','base_z_m':0,'support':'Shelf contact via horizontal lower cover','actual_contact_bounds_xy_m':[[.0235,-.11],[.2805,.11]]},
           {'book':'volume_04','base_z_m':.048,'support':'Upper cover of volume08 at Z .048, wholly inside lower book cover footprint','actual_contact_bounds_xy_m':[[.0265,-.11],[.2775,.11]]},
           {'books':['volume_%02d'%n for n in order],'base_z_m':0,'support':'Shelf surface, adjacent covers mutually touching'}]
 omit_groups={group(n) for n in omitted}
 parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.parent not in omit_groups]
 ss=stats(parts);books=[]
 for ob in bpy.context.scene.objects:
  if ob.type=='EMPTY' and 'editable_volume' in ob.name and ob not in omit_groups:
   bb=stats([p for p in parts if p.parent==ob]);books.append({'name':ob.name,'bounds_min_m':bb['bounds_min_m'],'bounds_max_m':bb['bounds_max_m'],'base_contact_z_m':bb['bounds_min_m'][2]})
 recipe={'variant':kind,'catalogue_id':'AST-LIB-006','derivative_not_unique_artistic_asset':True,'base_source':BASE.name,'base_source_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'description':description,'book_order':order,'omitted_book_numbers':omitted,'transforms_blender_world_row_major':{o.name:[list(row) for row in o.matrix_world] for o in bpy.context.scene.objects if o.type=='EMPTY' and 'editable_volume' in o.name or 'weighted_champagne' in o.name},'book_contacts':contact,'actual_book_bounds':books,'bounds_min_m':ss['bounds_min_m'],'bounds_max_m':ss['bounds_max_m'],'triangles':ss['triangles_evaluated']}
 slug='AST-LIB-006_upright_book_group_'+kind;recipe['export']=slug+'.glb';recipes.append(recipe)
 info={k:copy.deepcopy(v) for k,v in BASE_INFO.items() if k not in ['blend_sha256','book_parts','parts','support_contact_proposal','contact_joins']};info.update(ss);info['name']+=' — '+kind+' assembly';info['assembly_variant']=recipe;info['source_generator']='build_stock_variants.py';info['source_generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();info['book_parts']=books;info['support_contact_proposal']={'pivot_m':[0,0,0],'stock_base_z_m':0,'stock_top_z_m':ss['bounds_max_m'][2],'book_base_contacts':contact,'stock_envelope_max_m':[.68,.24,.29]}
 bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
 for source in parts:
  me=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);uv=me.uv_layers.active;assert uv
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='UV_Metric_Metres';uv.active_render=True
  ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=source.matrix_world.copy();ob.select_set(True);copies.append(ob)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='AST-LIB-006_'+kind+'_static_visual';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 ob['catalogue_id']='AST-LIB-006';ob['assembly_variant']=kind;ob['unique_artistic_asset']=False;ob['base_source']=BASE.name
 bpy.ops.export_scene.gltf(filepath=str(ROOT/(slug+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_extras=True)
 info['glb_sha256']=hashlib.sha256((ROOT/(slug+'.glb')).read_bytes()).hexdigest();info['export']['source_semantic_part_count']=len(parts);info['resource_api']['load_glb']=slug+'.glb'
 (ROOT/(slug+'.manifest.json')).write_text(json.dumps(info,indent=2))
 boxes=[]
 if kind=='reordered':
  lo=ss['bounds_min_m'];hi=ss['bounds_max_m'];boxes=[{'type':'box','center_m':[(lo[0]+hi[0])/2,0,hi[2]/2],'size_m':[hi[0]-lo[0],.222,hi[2]]}]
 else:boxes=[{'type':'box','center_m':[(-.3338668-.039)/2,0,.139],'size_m':[.2948668,.222,.278]},{'type':'box','center_m':[.152,0,.043],'size_m':[.257,.22136,.086]}]
 (ROOT/(slug+'.collision_proposal.json')).write_text(json.dumps({'catalogue_id':'AST-LIB-006','variant':kind,'status':'Static grouping proposal only; optional shelf obstruction. Separate shapes preserve gap. No engine behavior validated.','proposed_static_shapes':boxes},indent=2))
 # Reimport this actual export and independently compare to the source arrangement.
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/(slug+'.glb')))
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.evaluated_get(dg).to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(tuple(o.matrix_world@v.co) for v in me.vertices);o.evaluated_get(dg).to_mesh_clear()
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 assert tri==ss['triangles_evaluated'];assert max(abs(lo[i]-ss['bounds_min_m'][i])+abs(hi[i]-ss['bounds_max_m'][i]) for i in range(3))<1e-5
 audits.append({'variant':kind,'source_is_reloaded_base_plus_recorded_recipe':True,'imported_glb_triangle_match':True,'imported_glb_bounds_match':True,'triangles':tri,'min_m':lo,'max_m':hi})
for kind in ['reordered','short_flat']:run(kind)
(ROOT/'stock_assembly_recipes.json').write_text(json.dumps({'unique_artistic_assets':1,'base':'AST-LIB-006','derived_assemblies':recipes,'layout_hint':'Alternate base/reordered/short_flat with offset by shelf level; avoid perfectly repeated publisher height sequence'},indent=2))
(ROOT/'qa/variant_source_import_audit.json').write_text(json.dumps(audits,indent=2));print('DERIVED_ASSEMBLIES_PASS',audits)
