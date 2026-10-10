from pathlib import Path
import bpy,bmesh,json,hashlib,sys,struct
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'BUILD_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
G=json.load(open(W/'PREIMAGE_SUPPORT.json'));assert G['status']=='PASS'and G['plan_sha256']==sha(W/'BUILD_PLAN.json')
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
assert not (W/P['native_file']).exists(),'Retained native exists; use an explicit owned successor rather than regenerate over it'
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy,preview_only
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
palette={'champagne_metal':(.46,.4,.27,1),'warm_stone':(.58,.54,.45,1),'ivory_enamel':(.78,.73,.63,1),'warm_walnut':(.25,.12,.065,1),'opal_glow':(1,.87,.65,1)};mats={}
for role,color in palette.items():
 m=bpy.data.materials.new('D04Northern_'+role);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.7;bs.inputs['Metallic'].default_value=.45 if role=='champagne_metal'else 0
 tex=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
 if tex.exists():im=bpy.data.images.load(str(tex),check_existing=True);im.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;node.interpolation='Closest';m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 if role=='opal_glow':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=1.2
 mats[role]=m
for p in P['parts']:
 me=bpy.data.meshes.new(p['name']);me.from_pydata([B(v)for v in p['verts']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mats[p['role']]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
 ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob)
 for key in['role','category','runtime_collision','runtime_visual']:ob[key]=p[key]
 ob['source_plan_sha256']=sha(W/'BUILD_PLAN.json')
instances=[]
for spec in P['source_fittings']:
 source=R/spec['source'];assert sha(source)==P['source_pins'][spec['source']]
 with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=a.objects
 obs=[o for o in b.objects if o]
 for o in obs:bpy.context.collection.objects.link(o)
 bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in obs};T=Matrix.Translation(Vector(B(spec['origin'])))@Matrix.Rotation(spec['yaw'],4,'Z');root=bpy.data.objects.new(spec['prefix'],None);bpy.context.collection.objects.link(root);root.matrix_world=T;excluded=[];count=0
 for o in obs:
  name=o.name
  if o.type not in['MESH','EMPTY']or preview_only(name,{k:o.get(k,False)for k in['preview_only','presentation_only','exclude_from_production']}):excluded.append(name);bpy.data.objects.remove(o,do_unlink=True);continue
  o.parent=root;o.matrix_world=T@worlds[o];o.name=spec['prefix']+'__'+name;o['source_file_sha256']=sha(source)
  if o.type=='MESH':o['category']='source_fitting';o['runtime_collision']=True;o['runtime_visual']=True;count+=1
 instances.append({**spec,'source_sha256':sha(source),'rigid_source_instance_no_rescaling':True,'mesh_count':count,'excluded_presentation':excluded})
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.;bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/P['native_file']),compress=True)
def write():bpy.ops.export_scene.gltf(filepath=str(W/P['model_file']),export_format='GLB',export_extras=True,export_apply=True)
write();h=sha(W/P['model_file']);bpy.ops.wm.open_mainfile(filepath=str(W/P['native_file']));write();assert sha(W/P['model_file'])==h;validate_and_copy(W/P['model_file'],R/'Game/assets/models'/P['model_file'])
raw=(W/P['model_file']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);policy={q['name'].replace('.','_'):{'collide':q.get('extras',{}).get('runtime_collision',True),'opaque':q.get('extras',{}).get('role','')!='hospitality_glass','role':q.get('extras',{}).get('role',''),'category':q.get('extras',{}).get('category','')}for q in doc['nodes']if'mesh'in q}
record={'native':P['native_file'],'native_sha256':sha(W/P['native_file']),'export':P['model_file'],'export_sha256':h,'mesh_count':len(policy),'fresh_native_repeat_identical':True,'collision_policy':policy,'source_instances':instances}
RT={**P,'model_sha256':h,'native_sha256':record['native_sha256'],'collision_policy':policy,'native_export_records':[record],'preimage_support_sha256':sha(W/'PREIMAGE_SUPPORT.json'),'new_runtime_installed':True,'connection_accepted':False}
(W/'RUNTIME_PLAN.json').write_text(json.dumps(RT,indent=2)+'\n');(R/'Game/data/architecture/D04_PORT_FORWARD_NORTHERN_RECEIVING.json').write_text(json.dumps(RT,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'record':record,'source_pins_unchanged':len(P['source_pins']),'owned_parts':len(P['parts']),'source_models_modified':False,'new_guest_units':0,'new_rest_places':0,'primary_load_accepted':False},indent=2)+'\n');print('D04_NORTHERN_NATIVE_PASS')
