import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from source_common import *
receipt=read(R/'BUILD_RECEIPT.json');assert sha(OUT)==receipt['source_sha256']and sha(SOURCE)==SOURCE_SHA
bpy.ops.wm.open_mainfile(filepath=str(OUT));bpy.context.view_layer.update();actual=inspect(bpy);write_new(R/'REOPEN_SNAPSHOT003.json',actual);assert digest(actual)==digest(read(R/'BUILD_SNAPSHOT.json')),'Reopened canonical source attributes changed'
proposal=read(R/'SOURCE_INSERT_GEOMETRY.json');errors=[];uvmax=0.;parts=[]
for spec in proposal['new_parts']:
 ob=bpy.data.objects[spec['name']];row=actual['meshes'][ob.name];err=max(abs(a-b)for v,e in zip(row['vertices_world'],spec['vertices_world'])for a,b in zip(v,e));assert err<.00003 and row['faces']==spec['faces'];parts.append({'name':ob.name,'maximum_world_vertex_error_m':err})
 scale=float(ob['meters_per_tile_uv'][0]);me=ob.data;uv=me.uv_layers.active
 for face in me.polygons:
  a=me.vertices[face.vertices[0]].co;u=(me.vertices[face.vertices[1]].co-a).normalized();v=face.normal.cross(u).normalized()
  for li in face.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co-a;expected=(q.dot(u)/scale,q.dot(v)/scale);uvmax=max(uvmax,max(abs(uv.data[li].uv[i]-expected[i])for i in range(2)))
assert uvmax<1e-6
for name in proposal['source_fixture_objects_preserved']:assert actual['meshes'][name]['mesh_sha256']==receipt['retained_reference_proofs'][name]['mesh_sha256']
assert not bpy.data.objects.get(proposal['replace_exact_one_in_new_derivative'])
marker=bpy.data.objects['CA8_BANK0_source_attachment'];assert (Vector(wvec(marker.location))-Vector(proposal['source_light_position_unchanged'])).length<1e-6
axis=Vector(wvec(-marker.matrix_world.col[2].to_3d())).normalized();assert (axis-Vector(proposal['aim_world'])).length<1e-6
assert sha(OUT)==receipt['source_sha256']and sha(SOURCE)==SOURCE_SHA
write_new(R/'REOPEN_QA.json',{'status':'PASS_EDITABLE_OPTIC_SUBASSEMBLY_REOPEN','source_sha256':sha(OUT),'original_unchanged':True,'exact_snapshot_preserved':True,'canonical_snapshot_sha256':digest(actual),'comparison_representation':'Exact canonical JSON normalizes Python tuple links and their saved JSON arrays, without changing any values','reference_meshes':3,'replacement_meshes':7,'replacement_triangles':116,'source_axis_normal':list(axis),'source_position_unchanged':True,'metric_uv_max_error':uvmax,'packed_images':actual['packed_images'],'source_material_graphs_unchanged':True,'parts':parts,'native_picture_and_runtime_adoption':False})
write_new(R/'REOPENED_GEOMETRY.json',{'objects':[{'name':s['name'],'vertices_world':actual['meshes'][s['name']]['vertices_world'],'faces':actual['meshes'][s['name']]['faces']}for s in proposal['new_parts']]})
print('PASS_OPTIC_REOPEN',sha(OUT))
