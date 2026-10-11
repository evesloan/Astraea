from pathlib import Path
import bpy,json,hashlib,sys,math,bmesh
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'))
if (W/'PLAN.json').exists() and json.load(open(W/'PLAN.json')).get('aquatic_circulation_refinement'):
 raise SystemExit('Refined PLAN.json is retained; use build_refined_aquatic.py. Initial whole-pair generator remains historical.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
assert json.load(open(W/'PREIMAGE_SUPPORT.json'))['status']=='PASS'
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy,preview_only
palette={'champagne_metal':(.46,.4,.27,1),'warm_stone':(.58,.54,.45,1),'ivory_enamel':(.78,.73,.63,1),'warm_walnut':(.25,.12,.065,1),'hospitality_glass':(.22,.4,.44,.4),'opal_glow':(1,.87,.65,1),'foliage':(.11,.25,.14,1),'water':(.08,.34,.38,.6)}
def start():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;return{}
def add_parts(parts,mats):
 for p in parts:
  role=p['role']
  if role not in mats:
   mat=bpy.data.materials.new('D04Homes_'+role);mat.diffuse_color=palette[role];mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=palette[role];bs.inputs['Roughness'].default_value=.7 if role!='water'else .22;bs.inputs['Metallic'].default_value=.45 if role=='champagne_metal'else 0
   tex=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
   if tex.exists():im=bpy.data.images.load(str(tex),check_existing=True);im.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;node.interpolation='Closest';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
   if role in ['hospitality_glass','water']:bs.inputs['Alpha'].default_value=palette[role][3];mat.surface_render_method='DITHERED'
   if role=='hospitality_glass':bs.inputs['Alpha'].default_value=.12;bs.inputs['Roughness'].default_value=.16;bs.inputs['Transmission Weight'].default_value=.65
   if role=='opal_glow':bs.inputs['Emission Color'].default_value=palette[role];bs.inputs['Emission Strength'].default_value=1.2
   mats[role]=mat
  points=[];lookup={};indices=[]
  for v in p['verts']:
   key=tuple(round(float(c),9)for c in B(v))
   if key not in lookup:lookup[key]=len(points);points.append(key)
   indices.append(lookup[key])
  me=bpy.data.meshes.new(p['name']);me.from_pydata(points,[],[[indices[i]for i in f]for f in p['faces']]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)and bm.calc_volume(signed=True)>0,p['name'];bm.to_mesh(me);bm.free();me.update();me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled')
  for f in me.polygons:
   n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
   for li in f.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
  ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob)
  for k in ['role','category','runtime_collision']:ob[k]=p[k]
  ob['source_plan_sha256']=sha(W/'PLAN.json')

def components(bindings,prefix):
 records=[]
 for binding in bindings:
  a=next(a for a in P['sources']if a['catalogue_id']==binding['catalogue_id']);source=R/'BlenderCatalogue'/a['source'];assert sha(source)==P['source_pins'][str(source.relative_to(R))]
  with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
  obs=[o for o in dst.objects if o];worlds={}
  for o in obs:bpy.context.collection.objects.link(o)
  bpy.context.view_layer.update()
  for o in obs:worlds[o]=o.matrix_world.copy()
  root=bpy.data.objects.new(prefix+binding['name'],None);bpy.context.collection.objects.link(root);T=Matrix.Translation(Vector(B(binding['position'])))@Matrix.Rotation(binding['yaw'],4,'Z');root.matrix_world=T;count=0;excluded=[]
  for o in obs:
   oldname=o.name
   if o.type not in['MESH','EMPTY']or preview_only(oldname,{k:o.get(k,False)for k in ['preview_only','presentation_only','exclude_from_production']}):excluded.append(oldname);bpy.data.objects.remove(o,do_unlink=True);continue
   o.parent=root;o.matrix_world=T@worlds[o];o.name=prefix+binding['name']+'__'+oldname
   if o.type=='MESH':
    policy=str(o.get('collision_policy',''));o['runtime_collision']='NO_SOLID_COLLISION'not in policy and policy!='no_collision_detail'and not any(t in oldname for t in['WaterSurface_VisualOnly','Ripple']);o['category']='source_fitting';o['source_catalogue_id']=a['catalogue_id'];o['source_file_sha256']=sha(source);count+=1
  records.append({'binding':binding['name'],'catalogue_id':a['catalogue_id'],'source':a['source'],'source_sha256':sha(source),'origin':binding['position'],'yaw':binding['yaw'],'rigid_instance_no_rescaling':True,'mesh_count':count,'excluded_presentation':excluded})
 return records

def export(native,file,exclude_structure=False):
 assert not (W/native).exists()and not(W/file).exists()and not(R/'Game/assets/models'/file).exists(),(native,file)
 bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/native),compress=True)
 def write():
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.data.objects:
   if o.type in['MESH','EMPTY']and not(exclude_structure and o.get('category','')in['floor','frame','truss_brace']):o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',export_extras=True,use_selection=True,export_apply=True)
 write();h=sha(W/file);bpy.ops.wm.open_mainfile(filepath=str(W/native));write();assert sha(W/file)==h;validate_and_copy(W/file,R/'Game/assets/models'/file)
 # Exact exported collision policy, with Godot-safe name normalization.
 import struct
 raw=(W/file).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);policy={q['name'].replace('.','_'):{'collide':q.get('extras',{}).get('runtime_collision',True),'opaque':q.get('extras',{}).get('role','')not in['water','hospitality_glass'],'role':q.get('extras',{}).get('role',''),'category':q.get('extras',{}).get('category','')}for q in doc['nodes']if 'mesh'in q}
 return {'native':native,'native_sha256':sha(W/native),'export':file,'export_sha256':h,'mesh_count':len(policy),'collision_policy':policy,'fresh_native_repeat_identical':True}
catalogue=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));source=next(a for a in catalogue['assets']if a['catalogue_id']=='AST-HSK-006');P['sources'].append(source);pins={str(Path('BlenderCatalogue')/source[k]):sha(R/'BlenderCatalogue'/source[k])for k in ['source','export','manifest']};P['source_pins'].update(pins)
meta=json.load(open(R/'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.manifest.json'));assert meta['storage_openings']['right_open_bays_m'][1]['min'][2]==.525
bindings=[{'catalogue_id':'AST-HSK-006','name':'ClosedStockBottle_'+str(i),'position':[-77.3-x,17.009,-357.0],'yaw':0}for i,x in enumerate([.1,.3,.5,.7])]
mats=start();instances=components(bindings,'D04CS_');record=export('D04CommonsClosedStockProducts_r002.blend','D04_PORT_FORWARD_COMMONS_STOCK_r002.glb');record['source_instances']=instances
addendum={'status':'PASS','scope':'Four rigid original capped product bottles in original cabinet upper-right shelf','source_pins':pins,'bindings':bindings,'source_support_catalogue_id':'AST-STF-007','source_support_shelf_top_y':17.009,'source_rolled_rim_y':17.025,'actual_source_interior_deck_z':.509,'runtime_diagnostic':'STOCK_CONTACT_DIAGNOSIS.json','source_bottle_bottom_offset_m':0.0,'product_identity_chemistry_consumption_operation_accepted':False,'record':record}
(W/'PRODUCT_STAGING_ADDENDUM.json').write_text(json.dumps(addendum,indent=2)+'\n');q=json.load(open(W/'RUNTIME_PLAN.json'));q['source_pins'].update(pins);q['stock_products']={'model_file':record['export'],'model_sha256':record['export_sha256'],'mesh_count':record['mesh_count'],'collision_policy':record['collision_policy']};q['native_export_records'].append(record);q['model_pins'].pop('D04_PORT_FORWARD_COMMONS_STOCK_r001.glb');q['model_pins'][record['export']]=record['export_sha256'];q['stock_product_support_contacts']=bindings;(W/'RUNTIME_PLAN.json').write_text(json.dumps(q,indent=2)+'\n');n=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));n['records'].append(record);n['source_pins_unchanged']=len(q['source_pins']);(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(n,indent=2)+'\n');print('ORIGINAL_CLOSED_PRODUCT_STAGING',4)
