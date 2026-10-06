"""Bounded scratch-only Blender builder. Parent-allocated serial two-thread slot only."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S=json.loads((R/'source/dense_plan.json').read_text());assert S['derivative']=='dense_bays' and S['family']=='secondary_engineering_section';assert json.loads((R/'qa/pure_plan_check.json').read_text())['passed']
reg=json.loads((C/'catalogue_manifest.json').read_text());ids=[a['catalogue_id'] for a in reg['assets']];assert len(ids)==len(set(ids));assert next(a for a in reg['assets'] if a['catalogue_id']=='AST-ENG-008')['family']==S['family']
for p,h in S['input_hashes'].items():assert sha(p)==h,p
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials
M=staff_materials.materials();mat=bpy.data.materials.new('ASTRAEA_dense_instrument_pigment');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.84;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/dense_instruments.png'));tex.image.pack();tex.interpolation='Linear';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat['astraea_material_role']='dense_instrument_pigment';mat['meters_per_tile_uv']=[1,1];M['dense_instrument_pigment']=mat
roots={};parts=[];control_lookup={c['id']:c for c in S['controls']}
def cv(p):return Vector((p[0],-p[2],p[1]))
def xyz(p):return [p.x,p.z,-p.y]
def empty(name,parent=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;return o
root=empty('AST_ENG_008_dense_bays');root['catalogue_id']='AST-ENG-008';root['family']=S['family'];root['derivative']='dense_bays';root['runtime_adopted']=False
for bay in ['CONTROL','WORKBAY']:roots[bay]=empty(bay,root)
assemblies={}
for p in S['parts']:
 key=(p['bay'],p['assembly'])
 if key not in assemblies:assemblies[key]=empty(p['bay']+'_'+p['assembly'],roots[p['bay']])
 me=bpy.data.meshes.new(p['name']);pivot=cv(control_lookup[p['control_id']]['pivot_xyz']) if p.get('control_id') else Vector((0,0,0));me.from_pydata([cv(v)-pivot for v in p['vertices_xyz']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);ob.location=pivot;ob.parent=assemblies[key];me.materials.append(M[p['material_role']]);parts.append(ob)
 ob['material_role']=p['material_role'];ob['collision_contract']=p['collision'];ob['bay']=p['bay'];ob['assembly']=p['assembly'];ob['catalogue_derivative']='AST-ENG-008_dense_bays'
 if p.get('control_id'):
  c=control_lookup[p['control_id']];ob['control_id']=c['id'];ob['pivot_xyz']=c['pivot_xyz'];ob['travel_axis_xyz']=c['travel_axis_xyz'];ob['travel_type']=c['travel_type'];ob['travel_limits']=c['travel_limits'];ob['travel_units']=c['travel_units']
 uv=me.uv_layers.new(name='MetreScaled');tile=M[p['material_role']].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  if 'atlas_cell'in p:
   cell=p['atlas_cell'];col=cell%4;row=cell//4;front=p['faces'][0][0]==0
   for li in f.loop_indices:
    vi=me.loops[li].vertex_index;u,v=[(0,0),(1,0),(1,1),(0,1)][vi];u=u if front else 1-u;uv.data[li].uv=((col+(u*.984+.008))/4,(8-row-1+(v*.97+.015))/8)
  else:
   n=f.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
   for li in f.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
 if p['bevel']:
  mod=ob.modifiers.new('Editable formed edge','BEVEL');mod.width=min(p['bevel'],min(max(v[i] for v in p['vertices_xyz'])-min(v[i] for v in p['vertices_xyz']) for i in range(3))*.32);mod.segments=1;mod.limit_method='ANGLE';mod=ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
for row in S['markers']:
 o=empty(row['name'],roots[row['bay']]);o.location=cv(row['position_xyz']);o.empty_display_size=.045
 for k,v in row.items():
  if k not in ['name','position_xyz'] and v is not None:o[k]=v
bpy.context.view_layer.update();scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']=S['scope'];scene['controls_candidate_count']=120;scene['runtime_code']=False;scene['retained_context_in_export']=False
# Actual evaluated source records, used again by independent export comparison.
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in parts:
 eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();vs=[xyz(ob.matrix_world@v.co) for v in me.vertices];bounds=[min(v[i] for v in vs) for i in range(3)]+[max(v[i] for v in vs) for i in range(3)];rows.append({'name':ob.name,'bounds_xyz':bounds,'triangles':len(me.loop_triangles),'material_role':ob['material_role'],'bay':ob['bay'],'collision':ob['collision_contract'],'control_id':ob.get('control_id')});eo.to_mesh_clear()
for c in S['controls']:
 rr=[r for r in rows if r['control_id']==c['id']];c['actual_source_actuator_bounds_xyz']=[min(r['bounds_xyz'][i] for r in rr) for i in range(3)]+[max(r['bounds_xyz'][i+3] for r in rr) for i in range(3)]
# File exists check prevents unrecorded overwrite of an earlier build; caller archives failures first.
blend=R/'source/AST-ENG-008_dense_bays.blend';glb=R/'exports/AST-ENG-008_dense_bays.glb';assert not blend.exists() and not glb.exists(),'Preserve prior source/export before rebuilding'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
# Saved source retains semantic names. In-memory source objects are now renamed so
# exported actuator/marker IDs cannot acquire Blender .001 suffixes.
for ob in list(bpy.context.scene.objects):ob.name='SOURCE_ONLY_'+ob.name
# Static geometry is spatially/semantically batched; moving actuators remain 120 distinct nodes.
groups={};export=[]
for src in parts:
 me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.active
 if uv:
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='MetreScaled';uv.active_render=True
  for f in me.polygons:
   vs=[uv.data[li].uv for li in f.loop_indices];a,b,c=vs
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-10:
    axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
    for li in f.loop_indices:
     q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy()
 key=('ACT',src['control_id']) if src.get('control_id') else ('STATIC',src['bay'],src['material_role'],src['collision_contract']);groups.setdefault(key,[]).append(ob)
for key,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 ob=obs[0]
 if key[0]=='ACT':
  c=control_lookup[key[1]];ob.name='ACT_'+c['id'];ob['control_id']=c['id'];ob['collision_contract']='actuator_no_body_contact';ob['bay']=c['bay']
  for k in ['pivot_xyz','travel_axis_xyz','travel_type','travel_limits','travel_units']:ob[k]=c[k]
 else:ob.name='Dense_'+key[1]+'_'+key[2]+'_'+key[3];ob['collision_contract']=key[3];ob['bay']=key[1]
 ob['catalogue_derivative']='AST-ENG-008_dense_bays';export.append(ob)
# Detached export empties retain absolute marker transforms, avoiding selection of editable objects.
for row in S['markers']:
 o=empty(row['name']+'_EXPORT');o.name=row['name'];o.location=cv(row['position_xyz'])
 for k,v in row.items():
  if k not in ['name','position_xyz'] and v is not None:o[k]=v
 export.append(o)
# Source marker names conflict in this export scene unless original empties are renamed first.
for row in S['markers']:
 original=bpy.data.objects.get(row['name'])
 if original and original not in export:original.name='SOURCE_ONLY_'+row['name']
for ob,row in zip(export[-len(S['markers']):],S['markers']):ob.name=row['name']
bpy.ops.object.select_all(action='DESELECT')
for ob in export:ob.select_set(True)
bpy.context.view_layer.objects.active=export[0]
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
for p,h in S['input_hashes'].items():assert sha(p)==h,p
report={'scope':'Additive source-only derivative; source/export QA pending independent checks','source_sha256':sha(blend),'export_sha256':sha(glb),'plan_sha256':sha(R/'source/dense_plan.json'),'parts':rows,'controls':S['controls'],'markers':S['markers'],'cables':S['cables'],'contacts':S['contacts'],'prisms':S['prisms'],'input_hashes':S['input_hashes'],'export_mesh_groups':len(groups),'export_actuator_nodes':120,'export_static_groups':len(groups)-120,'source_parts':len(rows),'evaluated_triangles':sum(r['triangles'] for r in rows),'retained_inputs_unchanged':True,'no_runtime_code':True,'no_new_floor':True,'light_sources_exported':0}
(R/'qa/source_build.json').write_text(json.dumps(report,indent=2)+'\n');(R/'source/control_manifest.json').write_text(json.dumps({k:report[k] for k in ['controls','markers','cables','contacts','prisms']},indent=2)+'\n');print('DENSE_BAYS_BUILD_OK',len(rows),report['evaluated_triangles'],len(groups))
