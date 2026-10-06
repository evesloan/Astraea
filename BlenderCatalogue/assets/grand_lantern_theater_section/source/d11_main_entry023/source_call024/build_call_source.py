import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from common import *
pins();assert OUT.is_dir()and not BLEND.exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):
 assert all(n in src.objects for n in ORIGINAL_NAMES);dst.objects=list(ORIGINAL_NAMES)
originals=tuple(dst.objects);assert len(originals)==2
for ob in originals:bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.update();original_snapshot=snapshot(bpy);reference=[]
def world_matrix(ob):
 chain=[]
 while ob is not None:chain.append(ob);ob=ob.parent
 result=Matrix.Identity(4)
 for node in reversed(chain):result=result@node.matrix_basis
 return result
rotation=np.diag([-1.,1.,-1.]);root=bpy.data.objects.new('D11_MAIN_EXTERIOR_CALL_ROOT',None);bpy.context.scene.collection.objects.link(root);root.location=b(ANCHOR);root['catalogue_family']='AST-CUL-005';root['derived_hardware_family']='AST-DOR-002';root['retained_source_sha256']=SOURCE_SHA
for old,name in zip(originals,NAMES):
 matrix=world_matrix(old);world=np.array([w(matrix@v.co)for v in old.data.vertices]);local=(world-np.array(OLD_ANCHOR))@rotation.T
 assert len(old.data.vertices)==8 and len(old.data.polygons)==6 and len(old.data.materials)==1 and not old.modifiers
 me=old.data.copy();me.name=name
 for v,point in zip(me.vertices,local):v.co=b(point)
 me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
 ob['source_part']=old.name;ob['retained_source_sha256']=SOURCE_SHA;ob['source_family']='AST-DOR-002';ob['source_topology_uv_material_retained']=True
 assert [list(f.vertices)for f in me.polygons]==[list(f.vertices)for f in old.data.polygons]
 assert [list(v.uv)for v in me.uv_layers.active.data]==[list(v.uv)for v in old.data.uv_layers.active.data]
 reference.append({'source_part':old.name,'source_world_vertices':world.tolist(),'new_node':name,'expected_local_native':local.tolist(),'source_material':old.data.materials[0].name})
for ob in originals:bpy.data.objects.remove(ob,do_unlink=True)
# Remove dependencies that are not part of this additive subassembly.
for ob in list(bpy.data.objects):
 if ob.name not in {*NAMES,root.name}:bpy.data.objects.remove(ob,do_unlink=True)
marker=bpy.data.objects.new('D11_MAIN_EXTERIOR_CALL_TARGET',None);bpy.context.scene.collection.objects.link(marker);marker.parent=root;marker.location=b((.047,0,0));marker['source_id']='THEATER_D11_MAIN_EXTERIOR_CALL';marker['face_normal_native']=[1.,0.,0.];marker['lens_node']=NAMES[1]
for me in list(bpy.data.meshes):
 if not me.users:bpy.data.meshes.remove(me)
for mat in list(bpy.data.materials):
 if not mat.users:bpy.data.materials.remove(mat)
for im in list(bpy.data.images):
 if not im.users:bpy.data.images.remove(im)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2;scene['source_only_additive']=True;scene['scope']='Two retained-family control meshes for the supported D11 bridge-side door call. Original theater source and all existing geometry unchanged.'
bpy.context.view_layer.update();assert len(scene.objects)==4 and len(bpy.data.meshes)==2 and len(bpy.data.lights)==0
snap=snapshot(bpy);assert len(snap['materials'])==2
for mat in snap['materials']:assert snap['materials'][mat]==original_snapshot['materials'][mat]
write_new(OUT/'SOURCE_EXPECTED.json',{'source_sha256':SOURCE_SHA,'source_parts':reference,'snapshot':snap,'snapshot_sha256':digest(snap),'world_anchor_native':list(ANCHOR),'master_reference_use_sha256':sha(R.parent/'MASTER_REFERENCE_USE.json')})
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND));pins();write_new(OUT/'BUILD_RECEIPT.json',{'status':'SOURCE_BUILT_REOPEN_EXPORT_PENDING','source_path':str(BLEND),'source_sha256':sha(BLEND),'retained_source_sha256':SOURCE_SHA,'meshes':2,'triangles':24,'markers':2,'lights':0,'retained_inputs_unchanged':True});print('PASS_CONTROL_SOURCE_BUILT',sha(BLEND))
