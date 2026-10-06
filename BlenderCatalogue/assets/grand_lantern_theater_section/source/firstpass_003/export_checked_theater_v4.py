"""Three new scratch exports from the frozen complete source. No source save/Game write."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');SOURCE=R/'source_repair003/AST-CUL-005_firstpass_003.blend'
EXPECTED='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=R/'exports_run004';assert sha(SOURCE)==EXPECTED and not OUT.exists();OUT.mkdir()
sys.path.insert(0,'/workspace/scratch/375c2e438292/pool-comfort-greenery/greenery');from precise_normal_export import precise_normals
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));old_scene=bpy.context.scene;bpy.context.view_layer.update()
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));Ci=C.inverted()
def matrix_world(ob):return matrix_world(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis.copy()
def native_matrix(m):return [list(r)for r in C@m@Ci]
def nv(v):return [v[0],v[2],-v[1]]
source_meshes=[o for o in old_scene.objects if o.type=='MESH'];assert len(source_meshes)==1706
motion_specs={o.name:json.loads(o['mechanism_spec'])for o in old_scene.objects if o.get('mechanism_spec')};assert len(motion_specs)==39
mechanism=json.loads((P/'source/firstpass_001/mechanism_package_compact.json').read_text());names=json.loads((P/'qa/firstpass_001_build_report.json').read_text())['mechanisms']['object_names'];assert len(names)==len(set(names))==len(mechanism['objects'])==880
semantic_by_name={n:s['name']for n,s in zip(names,mechanism['objects'])};assert len(set(semantic_by_name.values()))==880
instances=[];definitions={}
for ob in old_scene.objects:
 if not ob.instance_collection:continue
 col=ob.instance_collection;definitions[col.name]=col
 instances.append({'id':ob.name,'definition':col.name,'native_matrix':native_matrix(matrix_world(ob)@Matrix.Translation(-col.instance_offset)),'audience_chair':ob.get('existing_family')=='AST-CUL-003','retained_family':ob.get('retained_family',ob.get('existing_family'))})
assert sum(i['audience_chair']for i in instances)==2200 and len(definitions)==19
# Preserve actual named source parts within consolidated original meshes.
def face_semantics(ob):
 if 'pure_part_ranges'not in ob:return [semantic_by_name.get(ob.name,ob.get('semantic_id',ob.name))]*len(ob.data.polygons)
 result=[None]*len(ob.data.polygons)
 for part in json.loads(ob['pure_part_ranges']):
  for i in range(part['face_start'],part['face_start']+part['face_count']):assert result[i]is None;result[i]=part['name']
 assert all(result);return result
# Evaluate complete retained definitions, including their actual source modifiers,
# in temporary scenes. Never discard a modifier or replace the visible form.
prototype_meshes={};prototype_evaluation=[]
for colname,col in definitions.items():
 eval_scene=bpy.data.scenes.new('EVALUATE_'+colname);eval_scene.collection.children.link(col);bpy.context.window.scene=eval_scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for ob in col.all_objects:
  if ob.type!='MESH':continue
  assert all(m.show_viewport==m.show_render for m in ob.modifiers),('Explicit render/viewport evaluation required',ob.name)
  ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg).copy();ev.to_mesh_clear();me.calc_loop_triangles();prototype_meshes[ob.as_pointer()]=me
  prototype_evaluation.append({'definition':colname,'object':ob.name,'source_modifiers':[{'type':m.type,'name':m.name,'show_render':m.show_render}for m in ob.modifiers],'evaluated_triangles':len(me.loop_triangles)})
expected_arrays={};batches=[];materials_used={};part_counts=Counter();export_records=[]
def emit_group(scene,label,objects,mode,definition=None):
 buckets={}
 for ob in objects:
  assert ob.type=='MESH' and (mode=='prototype' or not ob.modifiers),ob.name
  me=prototype_meshes[ob.as_pointer()] if mode=='prototype' else ob.data;me.calc_loop_triangles();world=matrix_world(ob);normal_mat=world.to_3x3().inverted().transposed();semantic=[definition+'::'+ob.get('firstpass_retained_source_object',ob.name)]*len(me.polygons) if mode=='prototype' else face_semantics(ob)
  assert me.uv_layers.active,ob.name
  group=ob.get('motion_group','') if mode=='moving' else ''
  if mode=='moving':assert group in motion_specs,(ob.name,group)
  for tri in me.loop_triangles:
   poly=me.polygons[tri.polygon_index];mat=me.materials[poly.material_index];assert mat,ob.name
   materials_used[mat.name]=mat
   coords=[world@me.vertices[i].co for i in tri.vertices];center=sum(coords,Vector())/3
   if mode=='static':cell=tuple(math.floor(center[i]/16)for i in range(3));origin=Vector(tuple(i*16 for i in cell));owner=ob.get('ownership_region','');role=ob.get('collision_role','unclassified');key=(role,owner,mat.name,cell)
   elif mode=='moving':origin=Vector((motion_specs[group]['closed_root_world'][0],-motion_specs[group]['closed_root_world'][2],motion_specs[group]['closed_root_world'][1]));key=(group,mat.name);role='moving_mechanism';owner=group
   else:origin=Vector();key=(definition,mat.name);role='retained_prototype';owner=definition
   if key not in buckets:buckets[key]={'origin':origin,'mat':mat,'coords':[],'normals':[],'uv':[],'semantic':[],'role':role,'owner':owner,'group':group}
   b=buckets[key]
   for li,p in zip(tri.loops,coords):
    b['coords'].append(p);b['normals'].append((normal_mat@me.corner_normals[li].vector).normalized());b['uv'].append(list(me.uv_layers.active.data[li].uv))
   b['semantic'].append(semantic[tri.polygon_index]);part_counts[(mode,definition or '',semantic[tri.polygon_index])]+=1
 roots={}
 if mode=='moving':
  for i,(ident,spec)in enumerate(motion_specs.items()):
   root=bpy.data.objects.new('C005_M%02d'%i,None);scene.collection.objects.link(root);root.location=Vector((spec['closed_root_world'][0],-spec['closed_root_world'][2],spec['closed_root_world'][1]));root['semantic_id']=ident;root['motion_contract']=json.dumps(spec,separators=(',',':'));roots[ident]=root
  for ident,spec in motion_specs.items():
   if spec['parent']:
    root=roots[ident];root.parent=roots[spec['parent']];a=spec['closed_root_world'];b=motion_specs[spec['parent']]['closed_root_world'];root.location=Vector((a[0]-b[0],-a[2]+b[2],a[1]-b[1]))
 elif mode=='prototype':
  root=bpy.data.objects.new('C005_P%02d'%list(definitions).index(definition),None);scene.collection.objects.link(root);root['definition_id']=definition;roots[definition]=root
 for key,b in sorted(buckets.items(),key=lambda kv:str(kv[0])):
  name='%s_%04d'%(label,len(batches));origin=b['origin'];coords=b['coords'];v=[p-origin for p in coords];faces=[(i,i+1,i+2)for i in range(0,len(v),3)]
  me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.materials.append(b['mat']);me.update();uv=me.uv_layers.new(name='source_metric_uv')
  for i,value in enumerate(b['uv']):uv.data[i].uv=value
  for poly in me.polygons:poly.use_smooth=True
  me.normals_split_custom_set([tuple(n)for n in b['normals']])
  ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob.location=origin
  if mode=='moving':ob.parent=roots[b['group']];ob.location=Vector()
  elif mode=='prototype':ob.parent=roots[definition]
  ob['source_role']=b['role'];ob['source_owner']=b['owner'];ob['source_semantic_ids']=json.dumps(sorted(set(b['semantic'])),separators=(',',':'));ob['unpowered_closed_preview']=mode=='moving';ob['source_sha256']=EXPECTED
  xyz=np.array([nv(p)for p in coords],dtype=np.float64).reshape(-1,3,3);uv_expected=np.array(b['uv'],dtype=np.float64).reshape(-1,3,2);uv_expected[:,:,1]=1-uv_expected[:,:,1];normal_expected=np.array([nv(p)for p in b['normals']],dtype=np.float64).reshape(-1,3,3)
  expected_arrays[name+'_xyz']=xyz;expected_arrays[name+'_uv']=uv_expected;expected_arrays[name+'_normal']=normal_expected
  batches.append({'name':name,'kind':mode,'definition':definition,'material':b['mat'].name,'triangles':len(faces),'role':b['role'],'owner':b['owner'],'motion_group':b['group'] or None,'semantic_ids':sorted(set(b['semantic'])),'semantic_triangle_runs':[[s,n]for s,n in Counter(b['semantic']).items()],'origin_native':nv(origin)})
 return roots
with precise_normals() as precision:
 for mode,objects in [('static',[o for o in source_meshes if not o.get('motion_group')]),('moving',[o for o in source_meshes if o.get('motion_group')]),('prototype',[])]:
  scene=bpy.data.scenes.new('EXPORT_THEATER_'+mode);bpy.context.window.scene=scene
  if mode=='prototype':
   for colname,col in definitions.items():emit_group(scene,'C005_P',[o for o in col.all_objects if o.type=='MESH'],mode,colname)
  else:emit_group(scene,'C005_'+mode[0].upper(),objects,mode)
  bpy.context.view_layer.update();filepath=OUT/('AST-CUL-005_'+mode+'_003.glb');assert not filepath.exists()
  bpy.ops.export_scene.gltf(filepath=str(filepath),export_format='GLB',use_active_scene=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False)
  export_records.append({'kind':mode,'path':str(filepath),'sha256':sha(filepath),'mesh_batches':len([b for b in batches if b['kind']==mode]),'triangles':sum(b['triangles']for b in batches if b['kind']==mode)})
assert sum(b['triangles']for b in batches if b['kind']!='prototype')==148950
np.savez_compressed(OUT/'source_triangle_attributes.npz',**expected_arrays)
images=[]
for mat in materials_used.values():
 assert mat.use_nodes
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:
   im=n.image;assert im.packed_file,(mat.name,im.name)
   images.append({'material':mat.name,'image':im.name,'size':list(im.size),'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest(),'color_space':im.colorspace_settings.name})
assert sha(SOURCE)==EXPECTED
report={'status':'Complete source split exported; independent binary equivalence and native import pending','source':str(SOURCE),'source_sha256':EXPECTED,'source_unchanged':True,'export_records':export_records,'instances':instances,'motion_groups':motion_specs,'batches':batches,'source_semantic_triangle_counts':[{'kind':k[0],'definition':k[1],'semantic_id':k[2],'triangles':v}for k,v in part_counts.items()],'prototype_evaluation':prototype_evaluation,'used_material_images':images,'normal_precision':precision,'source_attribute_archive_sha256':sha(OUT/'source_triangle_attributes.npz'),'pending':['Independent source/export attributes and embedded material texture checks','Closed-state source-derived collision contact classification','Actual imported geometry precision','D11 floor/foundation/receiving bridge and exact eight upper floor owners','Doors/lift loaded operation','Native eight-source lighting selection and visual review']}
(OUT/'EXPORT_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'exports':export_records,'instances':len(instances),'chairs':2200,'moving_groups':len(motion_specs),'source_sha256':EXPECTED},indent=2))
