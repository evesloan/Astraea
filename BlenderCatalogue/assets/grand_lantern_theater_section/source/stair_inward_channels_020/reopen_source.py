"""Read-only independent reopen. Writes only reports and actual mesh read-back."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from fixture_recipe import *
sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import material_record,mesh_record,image_nodes,bvec,wvec
OUT=R/'AST-CUL-005_inward_stair_channels_020.blend';receipt=read(R/'BUILD_RECEIPT.json');assert sha(OUT)==receipt['source_sha256']
recipe=read(R/'ACTUAL_SOURCE_RECIPE.json');assert sha(R/'ACTUAL_SOURCE_RECIPE.json')==receipt['actual_recipe_sha256']
bpy.ops.wm.open_mainfile(filepath=str(OUT));bpy.context.view_layer.update()
assert len(bpy.data.objects)==32 and len(bpy.data.meshes)==24 and len(bpy.data.lights)==0
expected_names={r['name']for r in recipe['objects']}|{r['attachment_empty']for r in recipe['fixtures']};assert set(bpy.data.objects.keys())==expected_names
rows=[];max_vertex_error=0.;max_uv_error=0.;uvrows=[]
for row in recipe['objects']:
 ob=bpy.data.objects[row['name']];me=ob.data;assert ob.type=='MESH' and not ob.modifiers and len(me.materials)==1
 spec=recipe['materials'][row['material_family']];assert me.materials[0].name==spec['datablock'];assert digest(material_record(me.materials[0]))==spec['retained_material_record_sha256']
 vertices=[list(wvec(ob.matrix_world@v.co))for v in me.vertices];faces=[list(p.vertices)for p in me.polygons];assert faces==row['faces']
 error=max(abs(vertices[i][k]-p[k])for i,p in enumerate(row['vertices_world'])for k in range(3));assert error<.00003;max_vertex_error=max(error,max_vertex_error)
 assert len(me.uv_layers)==1 and me.uv_layers[0].name=='metric_material_uv';uv=me.uv_layers[0];scale=spec['meters_per_tile_uv'];err=0.
 for face in me.polygons:
  origin=me.vertices[face.vertices[0]].co;u=(me.vertices[face.vertices[1]].co-origin).normalized();v=face.normal.cross(u).normalized()
  for li in face.loop_indices:
   point=me.vertices[me.loops[li].vertex_index].co-origin;expected=(point.dot(u)/scale[0],point.dot(v)/scale[1]);actual=uv.data[li].uv
   assert all(math.isfinite(float(x))for x in actual);err=max(err,*[abs(actual[k]-expected[k])for k in range(2)])
 assert err<1e-6;max_uv_error=max(max_uv_error,err);uvrows.append({'mesh':ob.name,'tile_scale_m':scale,'maximum_per_face_metric_uv_error':err,'face_count':len(me.polygons)})
 rows.append({**row,'vertices_world':vertices,'faces':faces})
attachments=[]
for f in recipe['fixtures']:
 ob=bpy.data.objects[f['attachment_empty']];assert ob.type=='EMPTY'and ob.parent and ob.parent.name.endswith('_LENS')
 actual=list(wvec(ob.matrix_world.translation));error=max(abs(actual[k]-f['attachment_world'][k])for k in range(3));assert error<.00003
 assert ob['energy_unset_until_native_trial']and not ob['runtime_light_installed'];assert all(k not in ob for k in ['energy','watts','light_energy'])
 f['attachment_world']=actual;attachments.append({'name':ob.name,'parent_lens':ob.parent.name,'world':actual,'maximum_storage_error_m':error})
recipe['objects']=rows;recipe['status']='ACTUAL_REOPENED_ADDITIVE_MESH_READBACK';recipe['saved_source_sha256']=sha(OUT)
for path,expected in recipe['input_pins'].items():assert sha(Path(path))==expected,('Original input changed',path)
write_new(R/'REOPENED_GEOMETRY.json',recipe)
write_new(R/'SOURCE_REOPEN_REPORT.json',{'status':'PASS_ACTUAL_REOPEN_COUNTS_MATERIALS_UV_ATTACHMENTS','source_sha256':sha(OUT),'meshes':24,'closed_mesh_geometry_checks':'Separate pure QA reads REOPENED_GEOMETRY.json','attachment_empties':attachments,'light_datablocks':0,'maximum_vertex_storage_error_m':max_vertex_error,'maximum_metric_uv_error':max_uv_error,'per_face_material_uv_checks':uvrows,'original_inputs_unchanged':True,'source_saved_during_reopen':False,'runtime_illumination_proven':False})
assert sha(OUT)==receipt['source_sha256'];print('REOPEN_PASS',len(rows),'meshes;',len(attachments),'source attachments; max vertex',max_vertex_error,'UV',max_uv_error)
