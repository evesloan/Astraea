import bpy,sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from common import *
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from precise_normal_export import precise_normals
pins();receipt=read(OUT/'BUILD_RECEIPT.json');assert sha(BLEND)==receipt['source_sha256']and not GLB.exists();bpy.ops.wm.open_mainfile(filepath=str(BLEND),load_ui=False);bpy.context.view_layer.update();expected=read(OUT/'SOURCE_EXPECTED.json');snap=snapshot(bpy);assert digest(snap)==expected['snapshot_sha256']
arrays={};parts=[];material_expectations={}
sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import image_nodes
for name in NAMES:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();v=[];uv=[];normal=[]
 for tri in me.loop_triangles:
  for vi,li in zip(tri.vertices,tri.loops):v.append(w(me.vertices[vi].co));uv.append((me.uv_layers.active.data[li].uv.x,1-me.uv_layers.active.data[li].uv.y));normal.append(w(me.corner_normals[li].vector))
 arrays[name+'_xyz']=np.array(v).reshape(-1,3,3);arrays[name+'_uv']=np.array(uv).reshape(-1,3,2);arrays[name+'_normal']=np.array(normal).reshape(-1,3,3);parts.append({'node':name,'triangles':len(v)//3,'material':me.materials[0].name})
 mat=me.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');images=image_nodes(mat.node_tree);assert len(images)<=1
 material_expectations[mat.name]={'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'base_color':[1.,1.,1.,1.]if images else list(bs.inputs['Base Color'].default_value),'emission_color':list(bs.inputs['Emission Color'].default_value)[:3],'emission_strength':float(bs.inputs['Emission Strength'].default_value),'image_sha256':hashlib.sha256(images[0].image.packed_file.data).hexdigest()if images else None}
with precise_normals()as precision:bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_active_scene=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False)
np.savez_compressed(OUT/'source_arrays.npz',**arrays);pins();assert sha(BLEND)==receipt['source_sha256'];write_new(OUT/'REOPEN_EXPORT_RECEIPT.json',{'status':'PASS_EDITABLE_REOPEN_EXPORT_BINARY_QA_PENDING','source_sha256':sha(BLEND),'glb_sha256':sha(GLB),'snapshot_sha256':digest(snap),'source_saved_during_reopen':False,'parts':parts,'material_expectations':material_expectations,'normal_precision':precision,'arrays_sha256':sha(OUT/'source_arrays.npz'),'root_native':list(ANCHOR),'originals_unchanged':True});print('PASS_REOPEN_EXPORT',sha(GLB))
