"""One new scratch GLB, eight local flight roots. Source never saved; no render/Game write."""
import sys,json
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from job_common import *
import bpy,numpy as np
from mathutils import Matrix
sys.path.insert(0,str(R/'dependencies'));from precise_normal_export import precise_normals
from proven_source_snapshot import props,C
verify_pins();assert OUT.is_dir()and SNAPSHOT.is_file()and not GLB.exists()and not EXPORT_RECEIPT.exists()
snapshot=read(SNAPSHOT);assert snapshot['source_sha256']==SOURCE_SHA and snapshot['mesh_count']==24 and snapshot['triangle_count']==416
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);bpy.context.view_layer.update();old_names=set(bpy.context.scene.objects.keys());expected={o['name']for o in snapshot['objects']};assert old_names==expected and len(bpy.data.lights)==0
source_rows={o['name']:o for o in snapshot['objects']}
# Preserve the exact local mesh coordinates. Each saved flight already has one
# shared source origin, so the new grouping root takes that origin and children
# receive identity local transforms. The lens-parented source empty stays unchanged.
for spec in snapshot['export_roots']:
 assert spec['name']not in bpy.data.objects
 original=bpy.data.objects[spec['mesh_children'][0]];root=bpy.data.objects.new(spec['name'],None);bpy.context.scene.collection.objects.link(root);root.matrix_world=original.matrix_world.copy()
 for k,v in spec['extras'].items():root[k]=v
 for name in spec['mesh_children']:
  ob=bpy.data.objects[name];assert ob.type=='MESH'and not ob.modifiers and ob.parent is None
  assert np.array_equal(np.asarray(ob.matrix_world),np.asarray(root.matrix_world))
  ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
assert len(bpy.context.scene.objects)==40 and sum(o.type=='MESH'for o in bpy.context.scene.objects)==24 and sum(o.type=='EMPTY'for o in bpy.context.scene.objects)==16 and len(bpy.data.lights)==0
for name,source in source_rows.items():
 ob=bpy.data.objects[name];assert props(ob)==source['extras'];actual=C@np.asarray(ob.matrix_world,dtype=np.float64)@C.T;assert np.array_equal(actual,np.asarray(source['world_matrix_godot'])),('Reparenting moved actual source',name)
 if ob.type=='MESH':assert max(abs(float(v))for pt in ob.data.vertices for v in pt.co)<3
 else:assert ob.parent.name==source['parent']and np.array_equal(C@np.asarray(ob.matrix_basis,dtype=np.float64)@C.T,np.asarray(source['local_matrix_godot']))
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2
with precise_normals()as precision:
 bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_active_scene=True,export_yup=True,export_apply=False,export_extras=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_image_format='AUTO',export_cameras=False,export_lights=False,export_animations=False,export_draco_mesh_compression_enable=False,export_gpu_instances=False)
verify_pins();assert GLB.is_file()
write_new(EXPORT_RECEIPT,{'status':'EXPORTED_PENDING_INDEPENDENT_BINARY_QA','source':str(SOURCE),'source_sha256':SOURCE_SHA,'source_unchanged':True,'snapshot_sha256':sha(SNAPSHOT),'glb':str(GLB),'glb_sha256':sha(GLB),'glb_bytes':GLB.stat().st_size,'mesh_count':24,'source_attachment_empties':8,'additional_flight_group_roots':8,'expected_node_count':40,'triangle_count':416,'normal_precision':precision,'source_saved':False,'rendered':False,'new_lights':0,'runtime_written':False,'full_tread_or_native_illumination_proven':False,'corner_limit':snapshot['corner_limit']});print('EXPORTED',sha(GLB))
