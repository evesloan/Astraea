"""Prepared, engine-unrun Court-only exporter. Default inspection is pure Python.
Actual export requires a fresh parent gate and reserved Blender slot. No source
save, light, full theater, prototype placement baking, Game or Catalogue writes.
"""
from pathlib import Path
import argparse,collections,hashlib,importlib.util,json,math,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def inspect():
 plan=read(D/'EXPORT_PLAN.json')
 for p,h in plan['input_sha256'].items():assert sha(p)==h,('Changed immutable input',p)
 assert len(plan['authored_meshes'])==157 and len(plan['placements'])==24
 return plan

def export(gate_path):
 plan=inspect();gate=read(gate_path)
 for key in ['parent_authorized_export','source_engine_slot_granted','independent_retention_verified']:assert gate.get(key)is True,key
 assert gate['production_install_authorized']is False
 assert gate['source_sha256']==plan['source_sha256'] and gate['export_script_sha256']==sha(__file__)
 proof=Path(gate['independent_retention_receipt']);assert proof.is_file() and sha(proof)==gate['independent_retention_receipt_sha256']
 out=D/'raw_export001';assert not out.exists();out.mkdir(exist_ok=False)
 import bpy,numpy as np
 from mathutils import Vector,Matrix
 K=Path(plan['retained_package']);R=K/'court';S=R/'reopen_qa001/winding_repair001/authored_source001'
 F=K.parent/'firstpass_001';common=load('court_export_common',F/'firstpass_common.py')
 qa=load('court_export_qa',R/'reopen_qa001/reopen_court_A_evaluated_readonly.py')
 normal=load('court_precise_normals',K.parent/'firstpass_003/dependencies/precise_normal_export.py')
 build=read(S/'BUILD_REPORT.json');reopen=read(S/'REOPEN_REPORT.json')
 audit=read(R/'reopen_qa001/retained_state_audit001/RETAINED_STATE_EVALUATED_AUDIT_1791297242994592082.json')
 bpy.ops.wm.open_mainfile(filepath=plan['source'],use_scripts=False,load_ui=False)
 old_scene=bpy.context.scene;court=bpy.data.collections['A4_COMPLETED_COURT'];root=bpy.data.objects['A4_SOURCE_ONLY']
 specs={r['name']:r for r in plan['authored_meshes']};placements={r['id']:r for r in plan['placements']}
 assert {o.name for o in court.objects}==set(specs)|set(placements)|{root.name}
 assert {o.name for o in old_scene.objects}=={o.name for o in court.objects}
 assert not any(o.type in {'LIGHT','CAMERA'}or o.get('existing_family')=='AST-CUL-003' for o in bpy.data.objects)
 assert len([o for o in court.objects if o.type=='MESH'])==157
 for name,spec in specs.items():
  ob=court.objects[name];assert not ob.modifiers and not ob.constraints and ob.animation_data is None
  assert bool(ob.get('collides'))==spec['collides']
  assert common.digest(common.mesh_record(ob.data))==build['mesh_uv_fingerprints'][name]
 C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));Ci=C.inverted()
 def world(ob):return world(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis.copy()
 def nv(v):return [v[0],v[2],-v[1]]
 def bv(v):return Vector((v[0],-v[2],v[1]))
 anchor=Vector(plan['court_origin_native']);anchor_b=bv(anchor)
 defs={};instances=[];prior_matrices={r['id']:r for r in reopen['instance_matrices']}
 for name,spec in placements.items():
  ob=court.objects[name];col=ob.instance_collection;assert col and col.name==prior_matrices[name]['collection']
  assert np.max(abs(np.array(ob.matrix_basis)-np.array(prior_matrices[name]['matrix_basis'])))<=2e-7
  assert ob.get('retained_family')==spec['asset']
  defs[spec['asset']]=col;m=C@(world(ob)@Matrix.Translation(-col.instance_offset))@Ci
  local=Matrix.Translation(-anchor)@m
  assert np.max(abs(np.array(Matrix.Translation(anchor)@local)-np.array(m)))<=1e-7
  instances.append({'id':name,'definition':spec['asset'],'native_matrix':[list(r)for r in m],
   'court_local_matrix':[list(r)for r in local],'collides':spec['collides'],'root_receiver':spec.get('root_receiver')})
 assert sorted(defs)==plan['expected_definitions'] and len(instances)==len({r['id']for r in instances})==24
 for asset,col in defs.items():
  expected=next(r for r in build['retained_definitions']if r['asset']==asset)
  assert {o.get('firstpass_retained_source_object')for o in col.all_objects}==set(expected['source_objects'])
 assert sum(len(c.all_objects)for c in defs.values())==133
 # Evaluate each definition once at the exact audited frame, never per placement.
 evscene=bpy.data.scenes.new('COURT_ONLY_DEFINITION_EVALUATION')
 for col in defs.values():evscene.collection.children.link(col)
 bpy.context.window.scene=evscene;evscene.frame_set(audit['frame'],subframe=audit['subframe']);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 evaluated={};evaluation=[];qa_eval={(r['asset'],r['source_name']):r for r in audit['evaluated_geometry_rows']}
 for asset,col in sorted(defs.items()):
  for ob in col.all_objects:
   if ob.type!='MESH':assert ob.type=='EMPTY';continue
   assert all(m.show_viewport==m.show_render for m in ob.modifiers)
   ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
   record=qa.canonical_mesh(me,common.mesh_record);record['edges']=[list(e.vertices)for e in me.edges]
   record['polygon_normals']=[list(p.normal)for p in me.polygons];record['corner_normals']=[list(n.vector)for n in me.corner_normals]
   record['evaluated_matrix_world']=[list(r)for r in ev.matrix_world]
   source_name=ob['firstpass_retained_source_object'];h=common.digest(record)
   assert h==qa_eval[(asset,source_name)]['actual_sha256'],('Evaluated source drift',asset,source_name)
   copied=me.copy();evaluated[ob.as_pointer()]=(copied,ev.matrix_world.copy());ev.to_mesh_clear()
   evaluation.append({'asset':asset,'source_name':source_name,'evaluated_sha256':h,'modifiers':[(m.name,m.type)for m in ob.modifiers]})
 assert len(evaluated)==120
 # Exact source graphs first; glTF conversion is separately checked, never inferred.
 mats={m for ob in list(court.objects)+[o for c in defs.values()for o in c.all_objects]if ob.type=='MESH' for m in ob.data.materials if m}
 expected_graphs={r['material']:r['graph_sha256']for r in reopen['retained_material_graph_checks']+reopen['paper_material_graph_checks']}
 material_expectations={};images=[]
 for mat in sorted(mats,key=lambda m:m.name):
  graph=common.digest(qa.graph_record(mat,common.material_record));assert graph==expected_graphs[mat.name]
  nodes=list(mat.node_tree.nodes);bs=[n for n in nodes if n.type=='BSDF_PRINCIPLED'];outputs=[n for n in nodes if n.type=='OUTPUT_MATERIAL'];tex=[n for n in nodes if n.type=='TEX_IMAGE']
  assert len(bs)==len(outputs)==1 and len(tex)<=1 and len(nodes)==2+len(tex),('Unsupported shader conversion must be reviewed',mat.name)
  bs=bs[0];links={(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in mat.node_tree.links}
  required={(bs.name,'BSDF',outputs[0].name,'Surface')}
  image=None
  if tex:
   t=tex[0];required.add((t.name,'Color',bs.name,'Base Color'));im=t.image;assert im and im.packed_file
   image={'sha256':hashlib.sha256(im.packed_file.data).hexdigest(),'extension':t.extension,'interpolation':t.interpolation,'colorspace':im.colorspace_settings.name}
   assert image['colorspace']=='sRGB' and t.extension in {'REPEAT','EXTEND'} and t.interpolation=='Linear'
   images.append({'material':mat.name,'image':im.name,'packed_sha256':image['sha256']})
  assert links==required,('Unsupported shader links',mat.name)
  for socket in ['Transmission Weight','Coat Weight','Sheen Weight','Subsurface Weight','Anisotropic IOR Level','Emission Strength']:
   if socket in bs.inputs:assert bs.inputs[socket].default_value==0,(mat.name,socket)
  assert bs.inputs['Alpha'].default_value==1
  specular=float(bs.inputs['Specular IOR Level'].default_value)*2
  tint=list(bs.inputs['Specular Tint'].default_value)[:3]
  material_expectations[mat.name]={'graph_sha256':graph,'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),
   'base_color':[1.,1.,1.,1.]if tex else list(bs.inputs['Base Color'].default_value),
   'specular_factor':min(specular,1.),'specular_color':[v*max(1.,specular)for v in tint],'ior':float(bs.inputs['IOR'].default_value),
   'double_sided':not mat.use_backface_culling,'image':image}
 arrays={};batches=[];counts=collections.Counter();exports=[]
 def emit(scene,objects,kind,asset=None):
  buckets={}
  for ob in objects:
   me,m=evaluated[ob.as_pointer()]if kind=='prototype'else(ob.data,world(ob));me.calc_loop_triangles()
   assert me.uv_layers.active and m.to_3x3().determinant()>0
   nmat=m.to_3x3().inverted().transposed();semantic=(asset+'::'+ob['firstpass_retained_source_object'])if asset else specs[ob.name]['semantic_id']
   collides=not asset.startswith('AST-BOT')if asset else specs[ob.name]['collides'];role='retained_furniture'if asset and collides else'decorative_plant'if asset else specs[ob.name]['role']
   for tri in me.loop_triangles:
    mat=me.materials[me.polygons[tri.polygon_index].material_index];coords=[m@me.vertices[i].co for i in tri.vertices]
    if kind=='authored':
     center=Vector(nv(sum(coords,Vector())/3))-anchor;cell=tuple(math.floor(v/plan['local_cell_m'])for v in center)
     origin_b=bv([x*plan['local_cell_m']for x in cell]);key=(collides,role,mat.name,cell)
    else:origin_b=Vector();key=(asset,collides,role,mat.name)
    if key not in buckets:buckets[key]={'coords':[],'normals':[],'uv':[],'semantic':[],'mat':mat,'origin_b':origin_b,'collides':collides,'role':role}
    bucket=buckets[key]
    for li,p in zip(tri.loops,coords):
     bucket['coords'].append(p.copy());bucket['normals'].append((nmat@me.corner_normals[li].vector).normalized());bucket['uv'].append(list(me.uv_layers.active.data[li].uv))
    bucket['semantic'].append(semantic);counts[(kind,asset or'',semantic)]+=1
  proto_root=None
  if asset:
   proto_root=bpy.data.objects.new('A4_DEF_'+asset.replace('-','_'),None);scene.collection.objects.link(proto_root);proto_root['definition_id']=asset
  for key,b in sorted(buckets.items(),key=lambda kv:str(kv[0])):
   name=('A4_G'if kind=='authored'else'A4_P')+'_%04d'%len(batches);origin=b['origin_b'];offset=anchor_b if kind=='authored'else Vector()
   verts=[p-offset-origin for p in b['coords']];faces=[(i,i+1,i+2)for i in range(0,len(verts),3)]
   me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(b['mat']);me.update();uv=me.uv_layers.new(name='source_metric_uv')
   for i,value in enumerate(b['uv']):uv.data[i].uv=value
   for poly in me.polygons:poly.use_smooth=True
   me.normals_split_custom_set([tuple(n)for n in b['normals']])
   ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob.location=origin
   if proto_root:ob.parent=proto_root
   ob['collides']=b['collides'];ob['source_role']=b['role'];ob['source_sha256']=plan['source_sha256'];ob['source_semantic_ids']=json.dumps(sorted(set(b['semantic'])))
   arrays[name+'_xyz']=np.array([nv(p)for p in b['coords']],dtype=np.float64).reshape(-1,3,3)
   arrays[name+'_normal']=np.array([nv(p)for p in b['normals']],dtype=np.float64).reshape(-1,3,3)
   u=np.array(b['uv'],dtype=np.float64).reshape(-1,3,2);u[:,:,1]=1-u[:,:,1];arrays[name+'_uv']=u
   batches.append({'name':name,'kind':kind,'definition':asset,'material':b['mat'].name,'triangles':len(faces),'collides':b['collides'],'role':b['role'],
    'semantic_ids':sorted(set(b['semantic'])),'semantic_triangle_counts':dict(collections.Counter(b['semantic'])),'origin_native_local':nv(origin)})
 with normal.precise_normals()as precision:
  for kind in ['authored','prototype']:
   scene=bpy.data.scenes.new('COURT_EXPORT_'+kind);bpy.context.window.scene=scene
   if kind=='authored':emit(scene,[court.objects[n]for n in sorted(specs)],kind)
   else:
    for asset,col in sorted(defs.items()):emit(scene,[o for o in col.all_objects if o.type=='MESH'],kind,asset)
   assert not any(o.instance_collection for o in scene.objects)
   scene['court_origin_native_json']=json.dumps(plan['court_origin_native'])if kind=='authored'else'prototype-only-no-placements'
   path=out/plan['runtime_names']['authored_glb'if kind=='authored'else'prototype_glb'];assert not path.exists()
   bpy.context.view_layer.update();bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False)
   exports.append({'kind':kind,'path':str(path),'sha256':sha(path)})
 np.savez_compressed(out/'source_triangle_attributes.npz',**arrays)
 assert len([k for k in counts if k[0]=='authored'])==157 and len([k for k in counts if k[0]=='prototype'])==120
 for p,h in plan['input_sha256'].items():assert sha(p)==h,('Source input changed',p)
 receipt={'status':'RAW_COURT_EXPORT_UNVERIFIED_NOT_FOR_ADOPTION','source':plan['source'],'source_sha256':plan['source_sha256'],'source_unchanged':True,'source_authored_meshes':157,'definition_meshes':120,'definitions':sorted(defs),'instances':instances,
  'court_origin_native':plan['court_origin_native'],'batches':batches,'export_records':exports,'used_material_images':images,'material_expectations':material_expectations,'prototype_evaluation':evaluation,
  'source_semantic_triangle_counts':[{'kind':k[0],'definition':k[1],'semantic_id':k[2],'triangles':n}for k,n in counts.items()],
  'source_attribute_archive_sha256':sha(out/'source_triangle_attributes.npz'),'normal_precision':precision,'export_plan_sha256':sha(D/'EXPORT_PLAN.json'),'export_script_sha256':sha(__file__),
  'protected_input_sha256':plan['input_sha256'],'chairs_or_old_plants_or_usher_exported':False,'lights_exported':False,'runtime_installed':False,
  'pending':['Direct source-corner normal repack','Independent binary positions/UV/normals/winding/material/image equality','New-only compression-disabled Godot import and raw LOD0 comparison','Separate visual and collision precision/contact QA','Sibling-only integration and preservation verification','Native composition, six-species and reach review']}
 with(out/'EXPORT_RECEIPT.json').open('x')as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps({'status':receipt['status'],'exports':exports,'batches':len(batches),'placements':len(instances)}))

def main():
 p=argparse.ArgumentParser();p.add_argument('--export',action='store_true');p.add_argument('--gate',type=Path);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:])
 if args.export:
  assert args.gate is not None;export(args.gate)
 else:
  plan=inspect();print(json.dumps({'status':'PREPARED_NOT_ENGINE_TESTED','authored_meshes':157,'placements':24,'source_sha256':plan['source_sha256'],'origin_native':plan['court_origin_native'],'no_output_created':True}))
if __name__=='__main__':main()
