import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from source_common import *
proposal=read(R/'SOURCE_INSERT_GEOMETRY.json');extract_path=R/'references/FIXTURE_GEOMETRY_EXTRACT.json';extract=read(extract_path);assert sha(SOURCE)==SOURCE_SHA and sha(R/'SOURCE_INSERT_GEOMETRY.json')=='d4927d56bfc0e2e42960eb9505305b2b0c1458f67c3c71fde965f80fef4b343e'
assert sha(extract_path)==proposal['retained_geometry_sha256'];assert not OUT.exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
requested=tuple(x['name']for x in extract['objects'])
with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):
 assert all(n in src.objects for n in requested)
 dst.objects=list(requested) # Loader mutates its request list; immutable tuple stays authoritative.
loaded={n:bpy.data.objects.get(n)for n in requested};assert all(x is not None for x in loaded.values())
def worldmatrix(ob):
 chain=[]
 while ob:chain.append(ob);ob=ob.parent
 matrix=Matrix.Identity(4)
 for x in reversed(chain):matrix=matrix@x.matrix_basis
 return matrix
proof={}
for spec in extract['objects']:
 ob=loaded[spec['name']];matrix=worldmatrix(ob);world=[list(wvec(matrix@v.co))for v in ob.data.vertices];assert len(world)==len(spec['vertices_world']);error=max(abs(a-b)for v,e in zip(world,spec['vertices_world'])for a,b in zip(v,e));assert error<.00003,(ob.name,error)
 proof[ob.name]={'mesh_sha256':digest(mesh_record(ob.data)),'matrix_world':[list(r)for r in matrix],'maximum_world_vertex_difference_m':error}
 ob.parent=None;ob.matrix_world=matrix
 if ob.name not in bpy.context.scene.objects:bpy.context.collection.objects.link(ob)
old=loaded[proposal['replace_exact_one_in_new_derivative']];opal=old.data.materials[0];frame=loaded['FP2_D11_COURT_A_LIGHT_1_hollow_frame'];metal=frame.data.materials[0]
mats={'retained_opal':opal,'retained_frame_metal':metal};mat_before={k:material_record(v)for k,v in mats.items()};image_before={}
for mat in mats.values():
 for n in image_nodes(mat.node_tree):assert n.image.packed_file;image_before[n.image.name]=hashlib.sha256(n.image.packed_file.data).hexdigest()
assert not image_nodes(opal.node_tree),'Original opal is explicitly untextured; do not invent a retained texture'
assert image_nodes(metal.node_tree),'Retained metal texture must survive'
# Only the local derivative loses this one flat lens. The source library is never saved.
bpy.data.objects.remove(old,do_unlink=True)
keep=set(proposal['source_fixture_objects_preserved'])
for ob in list(bpy.data.objects):
 if ob.name not in keep:bpy.data.objects.remove(ob,do_unlink=True)
origin=Vector(bvec(proposal['source_light_position_unchanged']))
for row in proposal['new_parts']:
 me=bpy.data.meshes.new(row['name']);me.from_pydata([Vector(bvec(v))-origin for v in row['vertices_world']],[],row['faces']);me.materials.append(mats[row['material_source']]);me.update()
 ob=bpy.data.objects.new(row['name'],me);bpy.context.collection.objects.link(ob);ob.location=origin;ob['semantic_id']=row['name'];ob['source_only']=True;ob['replaces_subassembly_part']=proposal['replace_exact_one_in_new_derivative'];ob['material_source']=row['material_source']
 scale=.6 if row['material_source']=='retained_frame_metal' else 1.0
 ob['meters_per_tile_uv']=[scale,scale];ob['uv_scale_basis']='Retained champagne metal .6m; untextured original opal uses explicit1m metric UV without invented texture'
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 for face in me.polygons:
  a=me.vertices[face.vertices[0]].co;u=(me.vertices[face.vertices[1]].co-a).normalized();v=face.normal.cross(u).normalized()
  for li in face.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co-a;uv.data[li].uv=(q.dot(u)/scale,q.dot(v)/scale)
marker=bpy.data.objects.new('CA8_BANK0_source_attachment',None);bpy.context.collection.objects.link(marker);marker.location=origin;marker.rotation_euler=Vector(bvec(proposal['aim_world'])).to_track_quat('-Z','Y').to_euler();marker.empty_display_type='ARROWS';marker.empty_display_size=.15
marker['source_id']='FP2_D11_BANK_0';marker['physical_fixture']='CA8_aimed_opal_lens';marker['full_cone_degrees']=75.;marker['range_m']=7.9;marker['native_energy']=.8;marker['source_position_unchanged']=True;marker['runtime_installed']=False
bpy.context.view_layer.update()
for name in keep:assert digest(mesh_record(bpy.data.objects[name].data))==proof[name]['mesh_sha256']
for k,m in mats.items():assert material_record(m)==mat_before[k]
for me in list(bpy.data.meshes):
 if me.users==0:bpy.data.meshes.remove(me)
for mat in list(bpy.data.materials):
 if mat.users==0:bpy.data.materials.remove(mat)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2
scene['scope']='Source-only bounded Court A optical subassembly derivative. Three exact retained references plus seven simple replacement parts; original library preserved; no runtime installation.'
scene['original_source_sha256']=SOURCE_SHA;scene['source_insert_geometry_sha256']=sha(R/'SOURCE_INSERT_GEOMETRY.json');scene['native_visual_acceptance']=False
assert len([o for o in scene.objects if o.type=='MESH'])==10 and len(bpy.data.lights)==0
snapshot=inspect(bpy);assert sha(SOURCE)==SOURCE_SHA
write_new(R/'BUILD_SNAPSHOT.json',snapshot)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
write_new(R/'BUILD_RECEIPT.json',{'status':'SOURCE_BUILT_REOPEN_PENDING','source_sha256':sha(OUT),'original_source_sha256':SOURCE_SHA,'original_unchanged':True,'retained_reference_proofs':proof,'materials':mat_before,'packed_images':image_before,'snapshot_sha256':sha(R/'BUILD_SNAPSHOT.json'),'new_parts':7,'new_triangles':116,'reference_meshes':3,'light_datablocks':0,'native_acceptance':False})
print('BUILT_OPTIC_SOURCE',sha(OUT))
