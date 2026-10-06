import bpy,sys,hashlib,json
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from source_common import *
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from precise_normal_export import precise_normals
receipt=read(R/'REOPEN_QA.json');assert receipt['status']=='PASS_EDITABLE_OPTIC_SUBASSEMBLY_REOPEN'and sha(OUT)==receipt['source_sha256'];E=R/'export001';E.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(OUT));bpy.context.view_layer.update();assert digest(inspect(bpy))==receipt['canonical_snapshot_sha256']
proposal=read(R/'SOURCE_INSERT_GEOMETRY.json');scene=bpy.data.scenes.new('CourtA_aimed_optic_export');bpy.context.window.scene=scene;arrays={};parts=[];material_expectations={};origin=Vector(bvec(proposal['source_light_position_unchanged']))
for index,row in enumerate(proposal['new_parts']):
 ob=bpy.data.objects[row['name']];copy=ob.copy();copy.name='OPT8_%02d'%index;copy.data=ob.data.copy();copy.parent=None;copy.location=Vector((0,0,0));scene.collection.objects.link(copy);me=copy.data;me.calc_loop_triangles();coords=[];uvs=[];normals=[]
 for tri in me.loop_triangles:
  for li,vi in zip(tri.loops,tri.vertices):
   coords.append(wvec(me.vertices[vi].co));uv=me.uv_layers.active.data[li].uv;uvs.append((uv.x,1-uv.y));normals.append(wvec(me.corner_normals[li].vector))
 name=copy.name;arrays[name+'_xyz']=np.array(coords).reshape(-1,3,3);arrays[name+'_uv']=np.array(uvs).reshape(-1,3,2);arrays[name+'_normal']=np.array(normals).reshape(-1,3,3);copy['source_semantic_id']=row['name'];copy['source_sha256']=receipt['source_sha256'];copy['replacement_only']=True;parts.append({'node':name,'semantic':row['name'],'triangles':len(coords)//3,'material':me.materials[0].name})
 mat=me.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=image_nodes(mat.node_tree);assert len(tex)<=1
 material_expectations[mat.name]={'graph_sha256':digest(material_record(mat)),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'base_color':[1.,1.,1.,1.]if tex else list(bs.inputs['Base Color'].default_value),'emission_color':list(bs.inputs['Emission Color'].default_value)[:3],'emission_strength':float(bs.inputs['Emission Strength'].default_value),'image_sha256':hashlib.sha256(tex[0].image.packed_file.data).hexdigest()if tex else None}
marker=bpy.data.objects.new('CA8_BANK0_source_attachment_export',None);scene.collection.objects.link(marker);marker['source_id']='FP2_D11_BANK_0';marker['optical_axis_native']=proposal['aim_world'];marker['native_root_translation']=proposal['source_light_position_unchanged'];marker['full_cone_degrees']=75.;marker['range_m']=7.9;marker['native_energy']=.8
bpy.context.view_layer.update();path=E/'AST-CUL-005_CourtA_aimed_optic_008.glb'
with precise_normals()as precision:bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False)
np.savez_compressed(E/'source_triangle_attributes.npz',**arrays);assert sha(OUT)==receipt['source_sha256']and sha(SOURCE)==SOURCE_SHA
write_new(E/'EXPORT_RECEIPT.json',{'status':'EXPORTED_INDEPENDENT_CHECK_PENDING','path':str(path),'glb_sha256':sha(path),'source_sha256':sha(OUT),'source_unchanged':True,'parts':parts,'triangles':sum(x['triangles']for x in parts),'root_native_translation':proposal['source_light_position_unchanged'],'material_expectations':material_expectations,'normal_precision':precision,'witness_sha256':sha(E/'source_triangle_attributes.npz'),'reference_meshes_exported':False,'actual_lights_exported':False,'old_part_to_replace':proposal['replace_exact_one_in_new_derivative'],'old_batch':'C005_S_0326','old_triangles_to_replace':28,'runtime_installed':False})
print('PASS_OPTIC_EXPORT',sha(path))
