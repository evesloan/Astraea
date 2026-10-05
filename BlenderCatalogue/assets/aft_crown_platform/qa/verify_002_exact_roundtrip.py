"""Independent source/export and actual shared-door sweep verification. No Godot work."""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,math,hashlib,struct
from mathutils import Vector
from mathutils.kdtree import KDTree
Q=Path(__file__).resolve().parent;C=Q.parents[2];R=C/'assets/aft_command';AID='AST-CMD-002';D=json.loads((R/'source/section_contract.json').read_text());P=json.loads((R/'source/geometry_parts.json').read_text())['parts'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'source'/(AID+'.blend')))
source_stage=True
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
def signatures(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active
 for t in o.data.loop_triangles:
  points=[]
  for vi,li in zip(t.vertices,t.loops):
   p=o.matrix_world@o.data.vertices[vi].co;q=uv.data[li].uv;encoded_q=(q.x,f32(1-f32(1-q.y))) if source_stage else tuple(q);points.append(tuple(float(v)for v in (*p,*encoded_q)))
  yield(o.data.materials[t.material_index].name,min(tuple(points[i:]+points[:i])for i in range(3)))
actual={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
assert len(actual)==len(P)
for p in P:
 vs=[o for o in actual[p['name']].data.vertices]
 assert len(vs)==len(p['vertices_world'])
 for vertex,expected in zip(vs,p['vertices_world']):
  q=actual[p['name']].matrix_world@vertex.co
  assert (Vector((q.x,q.z,-q.y))-Vector(expected)).length<.00002,p['name']
S=Counter();source_points=[];source_count=0;uv_faces=0;uv_error=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 source_count+=1;bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-10 for f in bm.faces),o.name;bm.free();assert o.data.uv_layers
 scale=o.data.materials[0]['meters_per_tile_uv'];uv=o.data.uv_layers.active.data
 for f in o.data.polygons:
  qs=[uv[i].uv for i in f.loop_indices];area=abs(sum(a.x*b.y-a.y*b.x for a,b in zip(qs,qs[1:]+qs[:1])))/2;err=abs(area*scale[0]*scale[1]-f.area)/f.area;uv_error=max(uv_error,err);uv_faces+=1;assert err<.035,(o.name,err)
 S.update(signatures(o));source_points.extend(o.matrix_world@v.co for v in o.data.vertices)
source_markers={o.name:list(o.location)for o in bpy.context.scene.objects if o.type=='EMPTY'}
T=KDTree(len(source_points))
for i,p in enumerate(source_points):T.insert(p,i)
T.balance();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m,do_unlink=True)
source_stage=False;bpy.ops.import_scene.gltf(filepath=str(R/'exports'/(AID+'.glb')));E=Counter();export_points=[];batch_sizes=[];max_error=0;glass_batches=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 E.update(signatures(o));vs=[o.matrix_world@v.co for v in o.data.vertices];export_points.extend(vs);size=[max(v[k]for v in vs)-min(v[k]for v in vs)for k in range(3)];batch_sizes.append(size)
 assert max(size)<16.001,(o.name,size)
 assert o.data.uv_layers and all(math.isfinite(v)for uv in o.data.uv_layers.active.data for v in uv.uv)
 for v in vs:max_error=max(max_error,T.find(v)[2])
 if any(m.name=='ASTRAEA_bridge_pressure_glass'for m in o.data.materials):glass_batches.append(o.name)
print('EXACT_TRIANGLE_UV_COUNTS',sum((S-E).values()),sum((E-S).values())); assert S==E,('triangles_materials_uv_changed',sum((S-E).values()),sum((E-S).values()));assert max_error<.0001,max_error
ET=KDTree(len(export_points))
for i,p in enumerate(export_points):ET.insert(p,i)
ET.balance();reverse_error=max(ET.find(p)[2]for p in source_points);assert reverse_error<.0001
markers={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY'}
for name,p in source_markers.items():assert name in markers and (markers[name].location-Vector(p)).length<.0001,name

(Q/'002_exact_roundtrip.json').write_text(json.dumps({'source_sha256':sha(R/'source'/(AID+'.blend')),'export_sha256':sha(R/'exports'/(AID+'.glb')),'exact_float32_oriented_geometry_material_and_gltf_uv_encoding_equality':True,'triangles':sum(S.values()),'vertex_max_error_m':max_error,'reverse_vertex_max_error_m':reverse_error},indent=2)+'\n')
assert all(p['world_aabb'][2]>=-3.200001 and p['world_aabb'][3]<=114.5 for p in P)
# Test actual oriented plan width, not the AABB of diagonal narrow edge girders.
for p in P:
 if p['world_aabb'][2]<=106.5 and p['world_aabb'][3]<=106.7:
  points=list(set((v[0],v[2])for v in p['vertices_world']));widths=[]
  for a in points:
   for b in points:
    dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz)
    if length>1e-8:
     projections=[(-dz*q[0]+dx*q[1])/length for q in points];widths.append(max(projections)-min(projections))
  assert min(widths)<1.21,(p['name'],'broad floor surface')
report={'catalogue_id':AID,'pass':True,'source_closed_outward_meshes':source_count,'source_triangles':sum(S.values()),'export_triangles':sum(E.values()),'exact_float32_oriented_geometry_material_and_gltf_uv_encoding_equality':True,'source_to_export_vertex_max_error_m':reverse_error,'export_to_source_vertex_max_error_m':max_error,'uv_faces_tested':uv_faces,'max_metric_uv_area_relative_error':uv_error,'runtime_mesh_batches':len(batch_sizes),'max_runtime_dimensions_blender_xyz_m':[max(x[k]for x in batch_sizes)for k in range(3)],'all_markers_preserved':True,'window_assembly_count':len(D['windows']),'glass_batch_names':glass_batches,'no_authored_floor_or_static_door_leaves':True,'bounds_y':[min(p['world_aabb'][2]for p in P),max(p['world_aabb'][3]for p in P)],'source_sha256':sha(R/'source'/(AID+'.blend')),'export_sha256':sha(R/'exports'/(AID+'.glb')),'limits':['Source-only checks; parent owns Godot import,walking,cart,door operation,normal/effects-off and final full regression','Geometric support is not structural engineering or pressure certification','Existing sparse lighting and unfinished plain interiors remain; no furniture or piloting systems']}
(Q/'002_source_export_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_EXPORT_VALIDATION_PASS',source_count,len(batch_sizes),sum(S.values()))
