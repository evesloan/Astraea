extends RefCounted
# Bounded small-surface consolidation; retain high-triangle objects rather than duplicate their buffers.
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
const CELL:=8.0
const DRAW=RULES.DRAW
static func build(root:Node3D,lights:Array)->Dictionary:
 assert(not root.has_meta("surface_cells"))
 var bins:Dictionary={};var source_count:=0;var eligible_count:=0;var light_rejections:=0
 for n:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  source_count+=1
  if not RULES.eligible(n,root):continue
  var raw:Dictionary=n.mesh.get("_surfaces")[0]
  if int(raw.get("index_count",raw.vertex_count))>384:continue # At most128 original triangles; no geometry decimation.
  var t:=RULES.pose(n,root);var box:AABB=t*n.get_aabb()
  if box.size[box.size.max_axis_index()]>CELL:continue
  var signature:=RULES.light_signature(root.global_transform*box,n.layers,lights)
  if signature=="OVER_LIMIT":light_rejections+=1;continue
  var center:=box.get_center();var cell:=Vector3i(floori(center.x/CELL),floori(center.y/CELL),floori(center.z/CELL))
  var state:Array=[]
  for prop:String in DRAW:state.append(n.get(prop))
  var key:=str(cell)+":"+str(n.mesh.surface_get_format(0))+":"+str(n.get_active_material(0).get_instance_id())+":"+str(state)
  if not bins.has(key):bins[key]={"members":[],"bounds":box,"state":state,"signature":signature}
  var combined:AABB=bins[key].bounds.merge(box)
  if combined.size[combined.size.max_axis_index()]>CELL:continue
  # Every potentially contributing light remains represented; verified budget caps active sources.
  # Lights outside an original bound attenuate to zero there; reject union capacity overflow.
  if RULES.light_signature(root.global_transform*combined,n.layers,lights)=="OVER_LIMIT":light_rejections+=1;continue
  bins[key].members.append({"node":n,"transform":t,"path":str(root.get_path_to(n))});bins[key].bounds=combined;eligible_count+=1
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
  var batch:=MeshInstance3D.new();batch.name="OpaqueSurfaceCell_%04d"%groups.size();batch.mesh=mesh
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
  batch.visible=false;root.add_child(batch)
  groups.append({"batch":batch,"members":bin.members,"bounds":bin.bounds,"light_signature":bin.signature,"original_shadow_mode":first.cast_shadow})
  saved+=bin.members.size()-1;triangles+=expected.size()/3
 var result:={"groups":groups,"source_meshes":source_count,"eligible_meshes":eligible_count,"saved_submissions":saved,"batch_count":groups.size(),"triangles_reencoded":triangles,"light_rejections":light_rejections,"enabled":false}
 root.set_meta("surface_cells",result);return result
static func raw_faces(mesh:Mesh)->PackedVector3Array:
 var a:Array=mesh.surface_get_arrays(0);var v:PackedVector3Array=a[Mesh.ARRAY_VERTEX];var idx:PackedInt32Array=a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
 if idx.is_empty():return v
 var result:=PackedVector3Array();result.resize(idx.size())
 for i in idx.size():result[i]=v[idx[i]]
 return result

