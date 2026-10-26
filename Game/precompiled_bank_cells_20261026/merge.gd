extends RefCounted
# Offline only: full-resolution bounded surfaces; no runtime source hierarchy retained.
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
const CELL:=16.0 # One retained crew-room envelope; never a whole-deck batch.
const DRAW=RULES.DRAW
static func build(root:Node3D,lights:Array)->Dictionary:
 assert(not root.has_meta("surface_cells"))
 var origins:Dictionary={}
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 for row:Dictionary in definition.instances:origins[row.allocation_key]=Vector3(row.position[0],row.position[1],row.position[2])
 var canonical:Dictionary={}
 var bins:Dictionary={};var source_count:=0;var eligible_count:=0;var light_rejections:=0
 for n:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  source_count+=1
  if not RULES.eligible(n,root):continue
  var raw:Dictionary=n.mesh.get("_surfaces")[0]
  # No triangle cap: this is an offline representation, not a second live buffer set.
  var t:=RULES.pose(n,root);var box:AABB=t*n.get_aabb()
  if box.size[box.size.max_axis_index()]>CELL:continue
  var signature:=RULES.light_signature(root.global_transform*box,n.layers,lights)
  if signature=="OVER_LIMIT":light_rejections+=1;continue
  var allocation:String=str(n.name).split("__")[0]
  var origin:Vector3=origins.get(allocation,Vector3.ZERO)
  if not origins.has(allocation):allocation="shared_receivers"
  var center:=box.get_center()-origin;var cell:=Vector3i.ZERO if origins.has(allocation) else Vector3i(floori(center.x/CELL),floori(center.y/CELL),floori(center.z/CELL))
  var state:Array=[]
  for prop:String in DRAW:state.append(n.get(prop))
  var key:=allocation+":"+str(cell)+":"+str(n.mesh.surface_get_format(0))+":"+str(n.get_active_material(0).get_instance_id())+":"+str(state)
  if not bins.has(key):bins[key]={"members":[],"bounds":box,"state":state,"signature":signature,"origin":origin}
  var combined:AABB=bins[key].bounds.merge(box)
  if combined.size[combined.size.max_axis_index()]>CELL:continue
  # Every potentially contributing light remains represented; verified budget caps active sources.
  # Lights outside an original bound attenuate to zero there; reject union capacity overflow.
  if RULES.light_signature(root.global_transform*combined,n.layers,lights)=="OVER_LIMIT":light_rejections+=1;continue
  bins[key].members.append({"node":n,"transform":Transform3D(Basis.IDENTITY,-origin)*t,"original_transform":t,"path":str(root.get_path_to(n))});bins[key].bounds=combined;eligible_count+=1
 var groups:Array=[];var saved:=0;var triangles:=0
 for key:String in bins:
  var bin:Dictionary=bins[key]
  if bin.members.size()<2:continue
  var first:MeshInstance3D=bin.members[0].node;var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
  var expected:=PackedVector3Array()
  for row:Dictionary in bin.members:
   var source_mesh:Mesh=row.node.mesh;st.append_from(source_mesh,0,row.transform)
   # Compare raw render arrays, not Mesh.get_faces() TriangleMesh welded caches.
   for vertex:Vector3 in raw_faces(source_mesh):expected.append(row.transform*vertex)
  st.set_material(first.get_active_material(0));st.index();var mesh:=st.commit();var actual:=raw_faces(mesh)
  assert(actual.size()==expected.size())
  for i in expected.size():assert(actual[i].distance_to(expected[i])<.00001)
  var batch:=MeshInstance3D.new();batch.name="OpaqueSurfaceCell_%04d"%groups.size();batch.mesh=mesh;batch.position=bin.origin
  for i in DRAW.size():batch.set(DRAW[i],bin.state[i])
  var shadow_vertices:=PackedVector3Array()
  for row:Dictionary in bin.members:
   var source:Mesh=row.node.mesh.shadow_mesh if row.node.mesh.shadow_mesh!=null else row.node.mesh
   for surface in source.get_surface_count():
    var a:Array=source.surface_get_arrays(surface)
    if a[Mesh.ARRAY_VERTEX]==null:
     # Godot4.6.3 compressed position-only shadow buffers have no decoded CPU arrays.
     var raw:Dictionary=source.get("_surfaces")[surface]
     var bytes:PackedByteArray=raw.vertex_data;var count:int=raw.vertex_count;var box:AABB=raw.aabb
     assert(bytes.size()==count*8 and (int(raw.format)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)!=0)
     var vertices:=PackedVector3Array();vertices.resize(count)
     for i in count:vertices[i]=box.position+Vector3(bytes.decode_u16(i*8),bytes.decode_u16(i*8+2),bytes.decode_u16(i*8+4))/65535.0*box.size
     a[Mesh.ARRAY_VERTEX]=vertices
     var indices:=PackedInt32Array();var packed:PackedByteArray=raw.get("index_data",PackedByteArray())
     var stride:=2 if count<65536 else 4
     indices.resize(packed.size()/stride)
     for i in indices.size():indices[i]=packed.decode_u16(i*stride) if stride==2 else packed.decode_u32(i*stride)
     a[Mesh.ARRAY_INDEX]=indices
    var v:PackedVector3Array=a[Mesh.ARRAY_VERTEX]
    var ix:PackedInt32Array=a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
    if ix.is_empty():
     for vertex:Vector3 in v:shadow_vertices.append(row.transform*vertex)
    else:
     for id:int in ix:shadow_vertices.append(row.transform*v[id])
  var shadow_tool:=SurfaceTool.new();shadow_tool.begin(Mesh.PRIMITIVE_TRIANGLES)
  for vertex:Vector3 in shadow_vertices:shadow_tool.add_vertex(vertex)
  shadow_tool.index();mesh.shadow_mesh=shadow_tool.commit()
  var geometry:Array=mesh.get("_surfaces").duplicate(true)
  for surface:Dictionary in geometry:surface.erase("material")
  var shadow_data:Array=mesh.shadow_mesh.get("_surfaces").duplicate(true)
  var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(var_to_bytes([geometry,shadow_data,first.get_active_material(0).get_instance_id()]))
  var geometry_key:=hash.finish().hex_encode()
  if canonical.has(geometry_key):batch.mesh=canonical[geometry_key]
  else:canonical[geometry_key]=mesh
  # Verify the final source-space triangle positions after placing the local prototype.
  var final_faces:=raw_faces(batch.mesh)
  for i in expected.size():assert((batch.transform*final_faces[i]).distance_to(bin.origin+expected[i])<.00001)
  var fallback:Array=[]
  for row:Dictionary in bin.members:
   var n:MeshInstance3D=row.node
   fallback.append([row.original_transform,n.mesh,n.get_active_material(0),n.layers,n.cast_shadow,n.extra_cull_margin,n.gi_mode,n.ignore_occlusion_culling,n.sorting_offset,n.sorting_use_aabb_center,n.lod_bias])
  batch.set_meta("precompiled_fallback",fallback)
  batch.visible=false;root.add_child(batch)
  groups.append({"batch":batch,"members":bin.members,"bounds":bin.bounds,"light_signature":bin.signature,"original_shadow_mode":first.cast_shadow})
  saved+=bin.members.size()-1;triangles+=expected.size()/3
 var result:={"groups":groups,"source_meshes":source_count,"eligible_meshes":eligible_count,"saved_submissions":saved,"batch_count":groups.size(),"triangles_reencoded":triangles,"light_rejections":light_rejections,"unique_compiled_meshes":canonical.size(),"enabled":false}
 root.set_meta("surface_cells",result);return result
static func raw_faces(mesh:Mesh)->PackedVector3Array:
 var a:Array=mesh.surface_get_arrays(0);var v:PackedVector3Array=a[Mesh.ARRAY_VERTEX];var idx:PackedInt32Array=a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
 if idx.is_empty():return v
 var result:=PackedVector3Array();result.resize(idx.size())
 for i in idx.size():result[i]=v[idx[i]]
 return result

