"""Exact evaluated source export. Preview/compiler floors and retained context are excluded."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector,Matrix

def export_package(R,source,removed):
 def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
 def xyz(p):return [p.x,p.z,-p.y]
 dg=bpy.context.evaluated_depsgraph_get();selected=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or (ob.hide_render and not ob.get('contact_only')):continue
  if not (ob.get('catalogue_derivative')=='AST-ENG-008_dense_bays' or ob.get('section_proposal_only') or ob.get('section_study')):continue
  if str(ob.get('kind','')).startswith('compiler_'):continue
  selected.append(ob)
 # Save canonical evaluated triangles from the closed-rest source, with per-part/material IDs.
 rows=[];tris=[];partids=[];matids=[];partnames=[];matnames=[];groups={}
 for source_index,ob in enumerate(selected):
  if source_index%100==0:print('EXPORT_SOURCE_PROGRESS',source_index,len(selected),ob.name,flush=True)
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));me.calc_loop_triangles();tt=list(me.loop_triangles);wv=[xyz(ob.matrix_world@v.co) for v in me.vertices];pid=len(partnames);partnames.append(ob.name);bounds=[min(v[i] for v in wv) for i in range(3)]+[max(v[i] for v in wv) for i in range(3)]
  rows.append({'name':ob.name,'bounds_xyz':bounds,'triangles':len(tt),'kind':ob.get('kind','equipment'),'control_id':ob.get('control_id'),'door_leaf_id':ob.get('door_leaf_id'),'collision':ob.get('collision_contract','static_surface')})
  out=bpy.data.meshes.new('ExactExport_'+ob.name);out.from_pydata([v.co[:] for v in me.vertices],[],[tuple(t.vertices) for t in tt]);out.update()
  for m in me.materials:out.materials.append(m)
  normals=[]
  for face,tr in zip(out.polygons,tt):
   face.material_index=tr.material_index;face.use_smooth=me.polygons[tr.polygon_index].use_smooth;material=me.materials[tr.material_index].name
   if material not in matnames:matnames.append(material)
   tris.append([wv[i] for i in tr.vertices]);partids.append(pid);matids.append(matnames.index(material));normals.extend([me.corner_normals[i].vector[:] for i in tr.loops])
  out.normals_split_custom_set(normals)
  # Custom-normal creation can reallocate mesh CustomData. Create/reacquire UV
  # only afterwards, matching the already-verified equipment exporter order.
  uv=out.uv_layers.new(name='MetreScaled')
  for face,tr in zip(out.polygons,tt):
   for dest,src in zip(face.loop_indices,tr.loops):uv.data[dest].uv=me.uv_layers.active.data[src].uv
  # Repair only numeric-collapse UVs, retaining source geometry and material identity.
  for face in out.polygons:
   a,b,c=[uv.data[i].uv for i in face.loop_indices]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-11:
    axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
    for li in face.loop_indices:
     v=out.vertices[out.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
  export_matrix=ob.matrix_world.copy()
  if not ob.get('control_id') and not ob.get('door_leaf_id'):
   assert max(abs(export_matrix[i][j]-(1 if i==j else 0)) for i in range(3) for j in range(3))<1e-8,'Unexpected static rotation needs normal transform review'
   for vertex in out.vertices:vertex.co=export_matrix@vertex.co
   out.update();export_matrix=Matrix.Identity(4)
  e=bpy.data.objects.new('TMP_EXPORT_'+ob.name,out);bpy.context.collection.objects.link(e);e.matrix_world=export_matrix;e.hide_render=True
  for prop in ['pivot_xyz','travel_axis_xyz','travel_type','travel_limits','travel_units','bay']:
   if prop in ob:
    value=ob[prop];e[prop]=list(value) if hasattr(value,'to_list') else value
  if ob.get('contact_only'):key=('proxy',ob.name,ob.get('collision_contract','static_surface'))
  elif ob.get('kind')=='real_door_control':key=('door_control',ob.name)
  elif ob.get('control_id'):key=('actuator',ob['control_id'])
  elif ob.get('door_leaf_id'):key=('door',ob['door_leaf_id'])
  else:key=('static',ob.get('bay','WORKBAY'),tuple(m.name for m in me.materials),ob.get('collision_contract','static_surface'))
  groups.setdefault(key,[]).append(e) # Retain evaluated temporary mesh until process exit; avoid Blender RNA cleanup crash.
 # Rename source mesh nodes in-memory only, after the editable source has been saved.
 for ob in selected:ob.name='SAVED_SOURCE_'+ob.name
 outobs=[]
 for i,(key,obs) in enumerate(groups.items()):
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  ob=obs[0]
  if key[0]=='proxy':ob.name=key[1];ob['collision_contract']=key[2];ob['visible_at_runtime']=False
  elif key[0]=='door_control':ob.name=key[1];ob['collision_contract']='door_control_only'
  elif key[0]=='actuator':ob.name='ACT_'+key[1];ob['control_id']=key[1];ob['collision_contract']='actuator_no_body_contact'
  elif key[0]=='door':ob.name='LEAF_WORKBAY_CELL';ob['door_leaf_id']=key[1];ob['collision_contract']='moving_door_leaf'
  else:ob.name='SectionStatic_'+str(i)+'_'+key[1];ob['collision_contract']=key[3]
  ob['catalogue_id']='AST-ENG-008';ob['catalogue_derivative']='dense_bays_section';outobs.append(ob)
 markers=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type!='EMPTY' or not ob.get('kind') or ob.get('assembly') in removed:continue
  row={'name':ob.name,'position_xyz':xyz(ob.matrix_world.translation),'kind':ob['kind']};markers.append(row);e=bpy.data.objects.new('TMP_'+ob.name,None);bpy.context.collection.objects.link(e);e.matrix_world=ob.matrix_world.copy()
  for k in ob.keys():
   if k!='_RNA_UI':e[k]=ob[k]
  name=ob.name;ob.name='SAVED_SOURCE_'+name;e.name=name;outobs.append(e)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in outobs:ob.select_set(True)
 bpy.context.view_layer.objects.active=outobs[0];dest=R/'exports/AST-ENG-008_workbay_section.glb';assert not dest.exists()
 bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
 np.savez_compressed(R/'qa/section_source_triangles.npz',triangles=np.array(tris),part_ids=np.array(partids),material_ids=np.array(matids),part_names=np.array(partnames),material_names=np.array(matnames),source_sha256=np.array(sha(source)),coordinate_system=np.array('world Godot XYZ metres'))
 report={'source_sha256':sha(source),'export_sha256':sha(dest),'parts':rows,'triangles':len(tris),'actuators':len([k for k in groups if k[0]=='actuator']),'door_leaves':len([k for k in groups if k[0]=='door']),'groups':len(groups),'markers':markers,'all_preview_floors_excluded':True,'retained_context_excluded':True,'selected_equipment_replaces_unadopted_dense_bays_glb':True,'runtime_installed':False}
 assert report['actuators']==120 and report['door_leaves']==1
 (R/'qa/section_export_build.json').write_text(json.dumps(report,indent=2)+'\n')
 for ob in outobs:ob.hide_render=True
 return report
