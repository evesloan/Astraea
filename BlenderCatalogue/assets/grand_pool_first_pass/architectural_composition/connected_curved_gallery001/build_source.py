"""Build one new editable connected gallery. No exports/render/shared writes."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,importlib.util,gzip
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
B=Path(__file__).parent;S=B.parent;OUT=B/'source_build001'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
retained=module('retained_correction_methods',S/'pool-east-gallery-canopy-correction001/revision001/build_correction.py');core=retained.core
common=module('programme_source_methods',S/'pool-opposite-gallery-proposal001/reference_programme001/programme_common.py')
def newjson(p,d):
 with p.open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
def append_source(source,name,family,position,yaw,collection,botanical=False):
 with bpy.data.libraries.load(str(source),link=False)as(src,dst):original=tuple(src.objects);dst.objects=list(original)
 objects=dict(zip(original,dst.objects));assert all(objects.values())
 for ob in objects.values():assert ob.type in {'MESH','EMPTY'},(ob.name,ob.type);collection.objects.link(ob)
 bpy.context.view_layer.update();world={n:o.matrix_world.copy()for n,o in objects.items()};states={n:retained.fingerprint(o)for n,o in objects.items()};target=Matrix.Translation(core.B(position))@Matrix.Rotation(yaw,4,'Z')
 if botanical:
  roots=[o for o in objects.values()if o.parent is None];assert len(roots)==1
  root=roots[0];inv=root.matrix_world.inverted();expected={n:target@inv@m for n,m in world.items()};root.matrix_world=target
 else:
  root=bpy.data.objects.new(name+'_Placement',None);collection.objects.link(root);root.matrix_world=target;expected={n:target@m for n,m in world.items()}
  for n,o in objects.items():
   if o.parent is None:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=world[n]
 root.name=name
 for n,o in objects.items():
  if o is not root:o.name=name+'__'+n
  o['retained_source_file']=str(source);o['retained_source_sha256']=sha(source);o['retained_source_object']=n;o['parent_design_id']=family;o['programme_instance']=name;o['source_reference_only']=True;o['architecture_export_excluded']=True;o['export_excluded']=True;o['scale_preserved']=True
 bpy.context.view_layer.update()
 for n,o in objects.items():assert max(abs(o.matrix_world[i][j]-expected[n][i][j])for i in range(4)for j in range(4))<5e-5,(n,'frame')
 return {'instance':name,'family':family,'source':str(source),'sha256':sha(source),'position_xyz':position,'yaw_radians':yaw,'unscaled':True,'objects':list(objects),'source_fingerprints_before_placement':states,'meshes':sum(o.type=='MESH'for o in objects.values())}
def programme_snapshot():
 out=[];dg=bpy.context.evaluated_depsgraph_get()
 col=bpy.data.collections['CG_RETAINED_PROGRAMME']
 for o in sorted(col.all_objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[core.G(ev.matrix_world@p.co)for p in me.vertices];out.append({'name':o.name,'instance':o.get('programme_instance'),'source':o.get('retained_source_file'),'source_name':o.get('retained_source_object'),'vertices_xyz':v,'evaluated_triangles':[list(t.vertices)for t in me.loop_triangles],'fingerprint':retained.fingerprint(o)});ev.to_mesh_clear()
 return out

def main():
 pins=json.loads((B/'SOURCE_JOB_PINS.json').read_text())
 for p,h in pins['inputs'].items():assert sha(p)==h,p
 assert not OUT.exists();OUT.mkdir();(OUT/'source').mkdir();(OUT/'qa').mkdir()
 plan=json.loads((B/'CORE_PLAN.json').read_text());triangles=json.loads((B/'SOURCE_TRIANGLES.json').read_text());assert triangles['plan_sha256']==sha(B/'CORE_PLAN.json');review=json.loads((B/'PURE_GEOMETRY_REVIEW.json').read_text());assert review['status']=='PASS_PURE_CONNECTED_GALLERY_GEOMETRY'and review['plan_sha256']==sha(B/'CORE_PLAN.json')
 bpy.ops.wm.open_mainfile(filepath=plan['source_base']);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
 before={o.name:retained.fingerprint(o)for o in scene.objects};changed=set(plan['modified_existing_parts']);oldmarkers={r['name']for r in plan['fixture_reservations']if r['name'].startswith('EAST_')};new=set(plan['new_parts']);mats={}
 for o in scene.objects:
  if o.type=='MESH':
   for m in o.data.materials:
    role=m.get('astraea_material_role')
    if role and role not in mats:mats[role]=m
 mats['lens']=bpy.data.objects['EAST_Bay_OpalLens_0'].data.materials[0]
 image=bpy.data.images.load(str(B/'artwork/ORIGINAL_GALLERY_DIRECTORY.png'));image.pack();mat=mats['ivory_enamel'].copy();mat.name='CG_original_pool_gallery_directory';mat['astraea_material_role']='pool_gallery_directory';mat['meters_per_tile_uv']=[1.1,1.4];mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest';tex.extension='CLIP';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.75;mats['pool_gallery_directory']=mat
 collection=bpy.data.collections.new('CG_CONNECTED_CURVED_GALLERY');scene.collection.children.link(collection)
 for r in plan['parts']:
  if r['name']not in changed|new:continue
  me=bpy.data.meshes.new(r['name']+'_connected003');me.from_pydata([core.B(v)for v in r['vertices_xyz']],[],triangles['parts'][r['name']]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  if r['name']in changed:o=bpy.data.objects[r['name']];o.data=me
  else:o=bpy.data.objects.new(r['name'],me);collection.objects.link(o)
  assert o.matrix_world==Matrix.Identity(4)
  mat=mats[r['material_role']];me.materials.append(mat);o['parent_design_id']=r.get('parent_family','AST-AQU-016');o['source_group']=r['group'];o['material_role']=r['material_role'];o['support_json']=json.dumps(r['support']);o['collision_contract']=r['collision'];o['source_plan_sha256']=sha(B/'CORE_PLAN.json');o['semantic_role']=r.get('semantic','Connected gallery');o['new_floor_owner']=False
  if 'cast_shadow'in r:o.visible_shadow=r['cast_shadow'];o['cast_shadow']=r['cast_shadow']
  uv=me.uv_layers.new(name='MetreScaled_SourceRole');scale=mat.get('meters_per_tile_uv',[1,1]);axis=core.B(r.get('grain_axis_xyz',[1,0,0]))
  for f in me.polygons:
   normal=f.normal.normalized();u=axis-normal*axis.dot(normal)
   if u.length<.01:
    a=Vector((0,0,1))if abs(normal.z)<.9 else Vector((0,1,0));u=a-normal*a.dot(normal)
   u.normalize();v=normal.cross(u).normalized()
   for li in f.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co
    if r['material_role']=='pool_gallery_directory'and abs(normal.x)>.9:uv.data[li].uv=((-p.y+458.55)/1.1,(p.z-53.95)/1.4)
    else:uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
 for r in plan['fixture_reservations']:
  if r['name']in oldmarkers:o=bpy.data.objects[r['name']]
  else:o=bpy.data.objects.new(r['name'],None);collection.objects.link(o)
  o.location=core.B(r['position_xyz']);o['marker_json']=json.dumps(r);o['export_excluded']=True;o['no_native_light_created']=True
 programme=bpy.data.collections.new('CG_RETAINED_PROGRAMME');scene.collection.children.link(programme);programme['export_excluded']=True;receipts=[]
 for r in plan['retained_furniture']:receipts.append(append_source(Path(r['source']),r['name'],r['catalogue_id'],r['position_xyz'],r['yaw_radians'],programme))
 for r in common.source_inventory(dict(plan,plant_reservations=plan['additional_plants'])):
  a=r['reservation'];receipts.append(append_source(Path(r['source']),'CG_'+r['instance_name'],r['parent_design_id'],a['position_xyz'],a['yaw_radians'],programme,True))
 bpy.context.view_layer.update();after={o.name:retained.fingerprint(o)for o in scene.objects}
 for n,h in before.items():
  if n not in changed|oldmarkers:assert after[n]==h,('Unrelated source changed',n)
 assert set(before)<=set(after)
 actual=dict(plan,parts=core.snapshot(scene,plan));program=programme_snapshot()
 newjson(OUT/'qa/BUILD_EVALUATED_CORE.json',actual)
 with gzip.open(OUT/'qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz','xt')as f:json.dump(program,f,separators=(',',':'),allow_nan=False)
 newjson(OUT/'qa/OBJECT_PRESERVATION.json',{'status':'PASS_OLD_SOURCE_OBJECT_PRESERVATION','before':before,'after':after,'allowed_modified':sorted(changed|oldmarkers),'old_objects_exact':len(before)-len(changed|oldmarkers),'new_objects':len(after)-len(before)})
 scene['status']='Complete connected curved gallery source candidate; independent reopen and visual review pending';scene['source_plan_sha256']=sha(B/'CORE_PLAN.json');scene['user_design_clarification']='Sentinel_512e57bb743881918717a87eb828ab21';scene['connected_gallery_programme_json']=json.dumps(receipts)
 path=OUT/'source/AST-AQU-016_connected_curved_gallery.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 newjson(OUT/'qa/BUILD_RECEIPT.json',{'status':'COMPOSED_SOURCE_SAVED_PENDING_REOPEN','source':str(path),'sha256':sha(path),'plan_sha256':sha(B/'CORE_PLAN.json'),'objects':len(after),'retained_programme':receipts,'Game_or_Catalogue_writes':False,'exports':[],'renders':[]})
 for p,h in pins['inputs'].items():assert sha(p)==h,p
 print('CONNECTED_GALLERY_SOURCE_SAVED',sha(path),flush=True)
if __name__=='__main__':main()
