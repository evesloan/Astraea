from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'))
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
   if role=='opal_glow':bs.inputs['Emission Color'].default_value=palette[role];bs.inputs['Emission Strength'].default_value=1.2
   mats[role]=mat
  me=bpy.data.meshes.new(p['name']);me.from_pydata([B(v)for v in p['verts']],[],p['faces']);me.update();me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled')
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
records=[];structure=[]
for room in P['rooms']:
 idx=room['source_index'];mats=start();add_parts(room['parts'],mats);inst=components(room['components'],'D04H'+str(idx)+'_');record=export(f'D04Home_{idx}.blend',room['model_file'],True);record.update(source_index=idx,source_instances=inst);records.append(record);room.update(model_sha256=record['export_sha256'],mesh_count=record['mesh_count'],collision_policy=record['collision_policy']);structure.extend(p for p in room['parts']if p['category']in['floor','frame','truss_brace']);print('EXPORTED_HOME',idx,record['mesh_count'],flush=True)
mats=start();add_parts(structure+P['commons_parts'],mats);inst=components(P['commons_components'],'D04Commons_');rec=export('D04ThirdHomesReceivingAndCourts.blend','D04_PORT_FORWARD_HOMES_THIRD_RECEIVING_r001.glb');rec['source_instances']=inst;records.append(rec);P['structure']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']}
mats=start();add_parts(P['guard_successor_parts'],mats);rec=export('D04ThirdHomeEntryGuardSuccessors.blend','D04_PORT_FORWARD_HOMES_THIRD_GUARDS_r001.glb');records.append(rec);P['entry_guard_successor']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']}
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
P['native_export_records']=records;P['open_room_entries']=False;(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':records,'source_pins_unchanged':len(P['source_pins']),'source_models_modified':False,'new_units':0,'new_rest_places':0,'entries_sealed_at_build':True,'rooms_adopted':0,'species_ready':0,'primary_load_accepted':False},indent=2)+'\n');print('NATIVE_EXPORT_PASS',len(records))
