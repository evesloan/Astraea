from pathlib import Path
import bpy,bmesh,json,hashlib,sys,importlib.util,gzip
from mathutils import Vector
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;S=B.parents[1];ORIGINAL=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/architectural_composition/east_gallery_arrival001/combined_source002/source/AST-AQU-016_east_gallery_composed.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
core=module('retained_core_methods',S/'pool-opposite-gallery-proposal001/source_blockin001/build_core.py')
def fingerprint(o):
 d={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[[float(v)for v in row]for row in o.matrix_world],'properties':{k:core.canonical(o[k])for k in o.keys()}}
 if o.type=='MESH':
  mesh=o.data;d.update(vertices=[list(v.co)for v in mesh.vertices],faces=[list(f.vertices)for f in mesh.polygons],material_indices=[f.material_index for f in mesh.polygons],uv_layers={u.name:[list(p.uv)for p in u.data]for u in mesh.uv_layers},materials=[core.mat_state(m)for m in mesh.materials],modifiers=[{'name':m.name,'type':m.type,'properties':{p.identifier:core.canonical(getattr(m,p.identifier))for p in m.bl_rna.properties if not p.is_readonly and p.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}}}for m in o.modifiers])
 return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def main():
 assert sha(ORIGINAL)=='9aa232ad30c515eabb128804b6d430ae2cfc3d76f93383a612165281620e6f05'
 plan=json.loads((B/'CORE_PLAN.json').read_text());gate=json.loads((B/'CORE_REVIEW.json').read_text());assert gate['status']=='PASS_CORE_PURE_GEOMETRY' and gate['plan_sha256']==sha(B/'CORE_PLAN.json')
 out=B/'source001';assert not out.exists();out.mkdir();(out/'qa').mkdir();(out/'source').mkdir()
 bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
 before={o.name:fingerprint(o)for o in scene.objects};changed=set(plan['correction']['changed_existing_parts']);new=set(plan['correction']['new_parts']);markers={r['name']for r in plan['fixture_reservations']}
 mats={}
 for o in scene.objects:
  if o.type=='MESH':
   for m in o.data.materials:
    role=m.get('astraea_material_role')
    if role and role not in mats:mats[role]=m
 mats['lens']=bpy.data.objects['EAST_Bay_OpalLens_0'].data.materials[0]
 collection=bpy.data.objects['EAST_Bay_WarmRearCanopy'].users_collection[0]
 for row in plan['parts']:
  if row['name']not in changed|new:continue
  mesh=bpy.data.meshes.new(row['name']+'_canopy_revision002');mesh.from_pydata([core.B(v)for v in row['vertices_xyz']],[],row['faces']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
  if row['name']in changed:o=bpy.data.objects[row['name']];o.data=mesh
  else:o=bpy.data.objects.new(row['name'],mesh);collection.objects.link(o)
  assert o.matrix_world==__import__('mathutils').Matrix.Identity(4)
  mat=mats[row['material_role']];mesh.materials.append(mat)
  o['parent_design_id']='AST-AQU-016';o['source_group']=row['group'];o['material_role']=row['material_role'];o['support_json']=json.dumps(row['support']);o['collision_contract']=row['collision'];o['source_plan_sha256']=sha(B/'CORE_PLAN.json');o['new_floor_owner']=False;o['semantic_role']=row.get('semantic','Fitted canopy revision');o['canopy_composition_revision']='002'
  if 'cast_shadow'in row:o['cast_shadow']=row['cast_shadow'];o.visible_shadow=row['cast_shadow']
  uv=mesh.uv_layers.new(name='MetreScaled_SourceRole');scale=mat.get('meters_per_tile_uv',[1,1]);axis=core.B(row.get('grain_axis_xyz',[1,0,0]))
  for face in mesh.polygons:
   normal=face.normal.normalized();u=axis-normal*axis.dot(normal)
   if u.length<.01:
    alternative=Vector((0,0,1))if abs(normal.z)<.9 else Vector((0,1,0));u=alternative-normal*alternative.dot(normal)
   u.normalize();v=normal.cross(u).normalized()
   for li in face.loop_indices:
    p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
 for r in plan['fixture_reservations']:
  o=bpy.data.objects[r['name']];o.location=core.B(r['position_xyz']);o['marker_json']=json.dumps(r);o['canopy_composition_revision']='002'
 bpy.context.view_layer.update();after={o.name:fingerprint(o)for o in scene.objects}
 assert set(after)-set(before)==new
 assert not set(before)-set(after)
 for name,h in before.items():
  if name not in changed|markers:assert after[name]==h,('Unrelated object changed',name)
 actual=dict(plan,parts=core.snapshot(scene,plan));(out/'qa/BUILD_EVALUATED_CORE.json').write_text(json.dumps(actual,indent=2)+'\n')
 (out/'qa/OBJECT_PRESERVATION.json').write_text(json.dumps({'status':'PASS_EXACT_UNRELATED_OBJECT_PRESERVATION','source_preimage_sha256':sha(ORIGINAL),'before':before,'after':after,'changed_expected':sorted(changed|markers),'new_expected':sorted(new),'unchanged_count':len(before)-len(changed|markers),'all_old_names_retained':True},indent=2)+'\n')
 scene['status']='Canopy composition correction; source reopen and same-angle visual review pending';scene['canopy_revision_plan_sha256']=sha(B/'CORE_PLAN.json')
 source=out/'source/AST-AQU-016_east_gallery_canopy_r02.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 receipt={'status':'SOURCE_SAVED_PENDING_REOPEN','source':str(source),'sha256':sha(source),'plan_sha256':sha(B/'CORE_PLAN.json'),'objects':len(after),'modified_existing_objects':len(changed|markers),'new_objects':len(new),'unrelated_objects_exact':len(before)-len(changed|markers),'Game_or_Catalogue_writes':False,'exports':[],'renders':[]};(out/'qa/BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 assert sha(ORIGINAL)=='9aa232ad30c515eabb128804b6d430ae2cfc3d76f93383a612165281620e6f05'
if __name__=='__main__':main()
