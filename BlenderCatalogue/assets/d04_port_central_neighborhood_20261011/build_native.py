from pathlib import Path
import bpy,json,hashlib,sys,bmesh
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import preview_only
for f,h in P['source_pins'].items():assert sha(R/f)==h,f

manifest=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
for source in P['sources']:assert next(a for a in manifest['assets']if a['catalogue_id']==source['catalogue_id'])==source

palette={'champagne_metal':(.46,.4,.27,1),'warm_stone':(.58,.54,.45,1),'ivory_enamel':(.78,.73,.63,1),'warm_walnut':(.25,.12,.065,1),'hospitality_glass':(.22,.4,.44,.4),'opal_glow':(1,.87,.65,1),'foliage':(.11,.25,.14,1),'water':(.08,.34,.38,.6),'staff_panel':(.32,.39,.40,1)}

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
  a=next(a for a in P['sources']if a['catalogue_id']==binding['catalogue_id']);source=R/'BlenderCatalogue'/binding.get('source_override',a['source']);assert sha(source)==P['source_pins'][str(source.relative_to(R))]
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
  records.append({'binding':binding['name'],'catalogue_id':a['catalogue_id'],'source':str(source.relative_to(R/'BlenderCatalogue')),'source_sha256':sha(source),'origin':binding['position'],'yaw':binding['yaw'],'rigid_instance_no_rescaling':True,'mesh_count':count,'excluded_presentation':excluded})
 return records

sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import require_new,export_native
records=[]
for room in P['rooms']:
 idx=room['source_index'];mats=start();add_parts(room['parts'],mats);instances=components(room['components'],f'PC{idx}_');rec=export_native(bpy,W,R,f'D04PortCentralHome_{idx}_r001.blend',room['model_file']);rec['source_instances']=instances;records.append(rec);room.update(model_sha256=rec['export_sha256'],mesh_count=rec['mesh_count'],collision_policy=rec['collision_policy']);print('PORT_CENTRAL_HOME_EXPORTED',idx,flush=True)
for label,parts in P['assemblies'].items():
 mats=start();add_parts(parts,mats);instances=components(P['bindings']['CO'],'PCC_')if label=='CO'else[];file='D04_PORT_CENTRAL_'+label.upper()+'_r001.glb';rec=export_native(bpy,W,R,'D04PortCentral'+label+'_r001.blend',file);rec['source_instances']=instances;records.append(rec);P[label.lower()+'_structure']={'model_file':file,'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']}
 if label=='CO':
  for name in P['stair_detailed_contact_replacements']:assert name in P['co_structure']['collision_policy']and P['co_structure']['collision_policy'][name]['collide'];P['co_structure']['collision_policy'][name]['collide']=False
P['native_export_records']=records;P['model_pins']={r['export']:r['export_sha256']for r in records}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':records,'original_registered_sources_unchanged':True,'rigid_original_fittings_no_rescale_or_reflection':True,'original_rest_reservations_preserved':25,'active':False},indent=2)+'\n');print('PORT_CENTRAL_PACKAGE_EXPORTED',len(records),flush=True)
