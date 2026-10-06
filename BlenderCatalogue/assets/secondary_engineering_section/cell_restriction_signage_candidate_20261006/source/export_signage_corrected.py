from pathlib import Path
import bpy,bmesh,json,hashlib,resource,numpy as np
R=Path(__file__).resolve().parents[1];P=json.loads((R/'source/sign_plan.json').read_text());OUT=R/'source/AST-ENG-008_cell_restriction_signage.blend';EXPORT=R/'exports/AST-ENG-008_cell_restriction_signage_002.glb';assert not EXPORT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(p):return [p.x,p.z,-p.y]
def uv(mesh):
 layer=mesh.uv_layers.new(name='MetreScaled')
 for f in mesh.polygons:
  axes=[k for k in range(3)if k!=max(range(3),key=lambda k:abs(f.normal[k]))]
  for li in f.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;layer.data[li].uv=(v[axes[0]],v[axes[1]])
assert sha(OUT)=='b32bb9111ef9e1b944634e67af32bd3186a0480d9b5f618c5d063573a65d4100'
bpy.ops.wm.open_mainfile(filepath=str(OUT));objects=list(bpy.context.scene.objects);l=P['leaf_print'];textrows=json.loads((R/'qa/BUILD.json').read_text())['text_rows']
# Export duplicates only. Editable fonts and original role graphs remain saved untouched.
dg=bpy.context.evaluated_depsgraph_get();groups={};tri=[];material_ids=[];material_names=[];degenerate=[]
for o in objects:
 me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));me.transform(o.matrix_world);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));zero=[f for f in bm.faces if f.calc_area()==0.0];degenerate.extend([{'object':o.name,'vertices_blender_xyz':[list(v.co)for v in f.verts]}for f in zero]);bmesh.ops.delete(bm,geom=zero,context='FACES_ONLY');bm.to_mesh(me);bm.free();me.calc_loop_triangles()
 if not me.uv_layers:uv(me)
 for t in me.loop_triangles:
  tri.append([xyz(me.vertices[i].co)for i in t.vertices]);mat=me.materials[t.material_index].name
  if mat not in material_names:material_names.append(mat)
  material_ids.append(material_names.index(mat))
 e=bpy.data.objects.new('Export_'+o.name,me);bpy.context.scene.collection.objects.link(e);groups.setdefault(o['sign_group'],[]).append(e)
exportobs=[]
for group,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 o=obs[0];o.name=group;o['collision_contract']='none';o['catalogue_id']='AST-ENG-008';o['source_backing_model_sha256']=P['model_sha256'];o['bind_source_owner']='LEAF_WORKBAY_CELL'if group==l['name']else'SectionStatic_0_WORKBAY';o['moving_with_existing_leaf']=group==l['name'];exportobs.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in exportobs:o.select_set(True)
bpy.context.view_layer.objects.active=exportobs[0];bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
np.savez_compressed(R/'qa/expected_export_triangles_002.npz',triangles=np.array(tri),material_ids=np.array(material_ids),material_names=np.array(material_names),source_sha256=np.array(sha(OUT)))
for p,h in P['immutable_inputs'].items():assert sha(p)==h
report={'source_sha256':sha(OUT),'export_sha256':sha(EXPORT),'editable_fonts':4,'editable_backing_plates':1,'mesh_groups':len(exportobs),'triangles':len(tri),'removed_exact_zero_area_font_triangles':degenerate,'text_rows':textrows,'materials':material_names,'all_new_collision_contracts':'none','old_source_unchanged':True,'new_lights':0,'new_emission_or_shader_graphs':0,'runtime_adopted':False,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/EXPORT_CORRECTION_002.json').write_text(json.dumps(report,indent=2)+'\n');print('SIGN_SOURCE_BUILT',json.dumps(report),flush=True)

assert len(degenerate)==8 and len(tri)==6672
