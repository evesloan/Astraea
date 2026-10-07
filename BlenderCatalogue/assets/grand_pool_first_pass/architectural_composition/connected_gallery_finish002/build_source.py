from pathlib import Path
import bpy,bmesh,json,hashlib,sys,importlib.util,gzip
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True;B=Path(__file__).parent;S=B.parent;OUT=B/'source_build001'
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load_module('retained_connected_source',S/'pool-connected-gallery-curved001/build_source.py');core=m.core;sha=m.sha

def stock_snapshot(collection):
 out=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in sorted(collection.all_objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();out.append({'name':o.name,'instance':o.get('programme_instance'),'source':o.get('retained_source_file'),'source_name':o.get('retained_source_object'),'vertices_xyz':[core.G(ev.matrix_world@v.co)for v in me.vertices],'evaluated_triangles':[list(t.vertices)for t in me.loop_triangles],'fingerprint':m.retained.fingerprint(o)});ev.to_mesh_clear()
 return out

def project_uv(o,part,mat):
 me=o.data;uv=me.uv_layers.active
 if uv is None:uv=me.uv_layers.new(name='MetreScaled_SourceRole')
 tile=mat.get('meters_per_tile_uv',[1,1]);axis=core.B(part.get('grain_axis_xyz',[1,0,0]))
 for face in me.polygons:
  n=face.normal.normalized();u=axis-n*axis.dot(n)
  if u.length<.01:a=Vector((0,0,1))if abs(n.z)<.9 else Vector((0,1,0));u=a-n*a.dot(n)
  u.normalize();v=n.cross(u).normalized()
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/tile[0],p.dot(v)/tile[1])

def main():
 pins=json.loads((B/'SOURCE_JOB_PINS.json').read_text())['inputs']
 for p,h in pins.items():assert sha(p)==h,p
 plan=json.loads((B/'CORE_PLAN.json').read_text());fit=json.loads((B/'FIXTURE_FIT_REVIEW.json').read_text());stock=json.loads((B/'STOCK_PLAN.json').read_text());tri=json.loads((B/'SOURCE_TRIANGLES.json').read_text());assert fit['status']=='PASS_PURE_FIXTURE_AND_FINISH_FIT'and fit['plan_sha256']==sha(B/'CORE_PLAN.json')and tri['plan_sha256']==sha(B/'CORE_PLAN.json');assert stock['status']=='PASS_SUPPORTED_RETAINED_RECEIVING_STOCK'and stock['instance_count']<=12
 assert not OUT.exists();OUT.mkdir();(OUT/'qa').mkdir();(OUT/'source').mkdir();assert sha(plan['source_base'])==plan['source_base_sha256'];bpy.ops.wm.open_mainfile(filepath=plan['source_base']);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
 before={o.name:m.retained.fingerprint(o)for o in scene.objects};materials={}
 for o in scene.objects:
  if o.type=='MESH':
   for mat in o.data.materials:
    role=mat.get('astraea_material_role')
    if role and role not in materials:materials[role]=mat
 materials['lens']=bpy.data.objects['EAST_Bay_OpalLens_0'].data.materials[0]
 for r in json.loads((B/'MATERIALS.json').read_text())['materials']:
  image=bpy.data.images.load(r['path'],check_existing=False);image.pack();mat=bpy.data.materials.new('ASTRAEA_CG_'+r['role']);mat.use_nodes=True;mat.use_backface_culling=True;mat['astraea_material_role']=r['role'];mat['meters_per_tile_uv']=r['meters_per_tile_uv'];mat['source_scope']='connected_gallery_finish002_local_only';mat['original_texture_sha256']=r['sha256'];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=r['roughness'];bs.inputs['Metallic'].default_value=0;texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Closest';texture.extension='REPEAT';mat.node_tree.links.new(texture.outputs['Color'],bs.inputs['Base Color']);materials[r['role']]=mat
 collection=bpy.data.collections.new('FIN_CONNECTED_GALLERY_FINISH002');scene.collection.children.link(collection);changed=set(plan['modified_existing_parts']);new=set(plan['new_parts']);geometry=set(tri['parts']);marker_names={f['name']for f in plan['fixture_reservations']}
 for r in plan['parts']:
  n=r['name']
  if n not in changed|new:continue
  if n in geometry:
   me=bpy.data.meshes.new(n+'_finish002');me.from_pydata([core.B(v)for v in r['vertices_xyz']],[],tri['parts'][n]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
   if n in new:o=bpy.data.objects.new(n,me);collection.objects.link(o)
   else:o=bpy.data.objects[n];o.data=me
  else:
   o=bpy.data.objects[n]
   if o.data.users>1:o.data=o.data.copy()
  assert o.matrix_world==Matrix.Identity(4),n
  mat=materials[r['material_role']];o.data.materials.clear();o.data.materials.append(mat);project_uv(o,r,mat)
  o['parent_design_id']=r.get('parent_family','AST-AQU-016');o['source_group']=r['group'];o['material_role']=r['material_role'];o['support_json']=json.dumps(r['support']);o['collision_contract']=r['collision'];o['source_plan_sha256']=sha(B/'CORE_PLAN.json');o['semantic_role']=r['semantic'];o['new_floor_owner']=False;o['connected_finish_revision']='002'
  if 'cast_shadow'in r:o['cast_shadow']=r['cast_shadow'];o.visible_shadow=r['cast_shadow']
 for f in plan['fixture_reservations']:
  o=bpy.data.objects[f['name']];o.location=core.B(f['position_xyz']);o['marker_json']=json.dumps(f);o['connected_finish_revision']='002';o['native_accepted']=False
 contents=bpy.data.collections.new('FIN_RETAINED_RECEIVING_CONTENTS');scene.collection.children.link(contents);contents['export_excluded']=True;receipts=[]
 for r in stock['placements']:receipts.append(m.append_source(Path(r['source']),r['name'],r['asset'],r['position_xyz'],r['yaw_radians'],contents))
 bpy.context.view_layer.update();after={o.name:m.retained.fingerprint(o)for o in scene.objects};assert set(before)<=set(after)
 for n,h in before.items():
  if n not in changed|marker_names:assert after[n]==h,('Unrelated source changed',n)
 actual=dict(plan,parts=core.snapshot(scene,plan));m.newjson(OUT/'qa/BUILD_EVALUATED_CORE.json',actual);ss=stock_snapshot(contents)
 with gzip.open(OUT/'qa/BUILD_EVALUATED_STOCK.json.gz','xt')as f:json.dump(ss,f,separators=(',',':'),allow_nan=False)
 m.newjson(OUT/'qa/OBJECT_PRESERVATION.json',{'status':'PASS_FINISH_ONLY_SOURCE_REVISION','before':before,'after':after,'allowed_modified':sorted(changed|marker_names),'old_objects_unchanged':len(before)-len(changed|marker_names),'new_objects':len(after)-len(before),'all_old_names_retained':True,'old_family_source_files_unchanged':True})
 scene['status']='Connected gallery material/physical optic/receiving finish successor; native selection and visual finish not accepted';scene['connected_finish_plan_sha256']=sha(B/'CORE_PLAN.json');scene['connected_finish_stock_json']=json.dumps(receipts);scene['six_local_sources_eight_active_unchanged']=True
 source=OUT/'source/AST-AQU-016_connected_gallery_finish_r04.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);m.newjson(OUT/'qa/BUILD_RECEIPT.json',{'status':'SOURCE_SAVED_PENDING_REOPEN','source':str(source),'sha256':sha(source),'objects':len(after),'core_parts':len(actual['parts']),'retained_stock_instances':len(receipts),'source_plan_sha256':sha(B/'CORE_PLAN.json'),'Game_or_Catalogue_writes':False,'exports':[],'native_acceptance':False})
 for p,h in pins.items():assert sha(p)==h,p
 print('CONNECTED_GALLERY_FINISH_SOURCE_SAVED',sha(source),flush=True)
if __name__=='__main__':main()
