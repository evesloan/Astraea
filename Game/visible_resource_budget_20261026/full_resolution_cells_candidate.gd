extends RefCounted
# Candidate full-resolution static cells. Original editable sources are immutable.
# Imported LOD selection is replaced by full source triangles; measure extra distant primitives.
const CELL:=8.0
const DRAW:=["layers","cast_shadow","extra_cull_margin","gi_mode","ignore_occlusion_culling","sorting_offset","sorting_use_aabb_center"]
static func pose(n:Node3D,root:Node3D)->Transform3D:
 var t:=n.transform;var p:=n.get_parent()
 while p!=root:
  assert(p is Node3D);t=p.transform*t;p=p.get_parent()
 return t
static func eligible(n:MeshInstance3D,root:Node3D)->bool:
 if not n.mesh is ArrayMesh or n.mesh.get_surface_count()!=1 or n.mesh.get_blend_shape_count()!=0:return false
 if n.cast_shadow not in [GeometryInstance3D.SHADOW_CASTING_SETTING_OFF,GeometryInstance3D.SHADOW_CASTING_SETTING_ON]:return false
 if n.get_script()!=null or n.skin!=null or n.skeleton!=NodePath("") or n.material_overlay!=null or n.transparency!=0:return false
 if n.custom_aabb!=AABB() or n.visibility_parent!=NodePath("") or n.visibility_range_begin!=0 or n.visibility_range_end!=0:return false
 if n.mesh.surface_get_primitive_type(0)!=Mesh.PRIMITIVE_TRIANGLES:return false
 var arrays:Array=n.mesh.surface_get_arrays(0)
 for channel:int in [Mesh.ARRAY_BONES,Mesh.ARRAY_WEIGHTS,Mesh.ARRAY_CUSTOM0,Mesh.ARRAY_CUSTOM1,Mesh.ARRAY_CUSTOM2,Mesh.ARRAY_CUSTOM3]:
  if arrays[channel]!=null and not arrays[channel].is_empty():return false
 var mat:Material=n.get_active_material(0)
 if not mat is StandardMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999 or mat.next_pass!=null:return false
 if mat.uv1_triplanar or mat.uv2_triplanar or mat.billboard_mode!=BaseMaterial3D.BILLBOARD_DISABLED or mat.grow or mat.use_point_size:return false
 var ancestor:Node=n
 while ancestor!=root:
  if not ancestor is Node3D or not ancestor.visible or ancestor.get_script()!=null:return false
  if ancestor is CollisionObject3D or ancestor is AnimationPlayer:return false
  ancestor=ancestor.get_parent()
 for child in n.get_children():
  if not child is StaticBody3D:return false
 var t:=pose(n,root)
 # SurfaceTool transform semantics are verified only for positive uniform scale.
 var scale:=t.basis.get_scale()
 if t.basis.determinant()<=0 or absf(scale.x-scale.y)>.00001 or absf(scale.x-scale.z)>.00001:return false
 return true
static func light_signature(box:AABB,layers:int,lights:Array)->String:
 var ids:Array[int]=[];var omni:=0;var spot:=0
 for light in lights:
  if not is_instance_valid(light) or light.light_cull_mask&layers==0:continue
  if light is DirectionalLight3D:ids.append(light.get_instance_id());continue
  var reach:float=light.omni_range if light is OmniLight3D else light.spot_range
  var p:Vector3=light.global_position
  if p.distance_squared_to(p.clamp(box.position,box.end))>reach*reach:continue
  # Count every potential light, including currently hidden budget-controlled sources.
  if light is OmniLight3D:omni+=1
  else:spot+=1
  ids.append(light.get_instance_id())
 if omni>8 or spot>8:return "OVER_LIMIT"
 ids.sort();return str(ids)
static func build(root:Node3D,lights:Array)->Dictionary:
 assert(not root.has_meta("surface_cells"))
 var bins:Dictionary={};var source_count:=0;var eligible_count:=0;var light_rejections:=0
 for n:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  source_count+=1
  if not eligible(n,root):continue
  var t:=pose(n,root);var box:AABB=t*n.get_aabb()
  if box.size[box.size.max_axis_index()]>CELL:continue
  var signature:=light_signature(root.global_transform*box,n.layers,lights)
  if signature=="OVER_LIMIT":light_rejections+=1;continue
  var center:=box.get_center();var cell:=Vector3i(floori(center.x/CELL),floori(center.y/CELL),floori(center.z/CELL))
  var state:Array=[]
  for prop:String in DRAW:state.append(n.get(prop))
  var key:=str(cell)+":"+str(n.mesh.surface_get_format(0))+":"+str(n.get_active_material(0).get_instance_id())+":"+str(state)+":"+signature
  if not bins.has(key):bins[key]={"members":[],"bounds":box,"state":state,"signature":signature}
  var combined:AABB=bins[key].bounds.merge(box)
  if combined.size[combined.size.max_axis_index()]>CELL:continue
  # The union must not gain a light absent from any constituent mesh.
  if light_signature(root.global_transform*combined,n.layers,lights)!=signature:light_rejections+=1;continue
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
static func set_enabled(root:Node3D,enabled:bool)->void:
 var record:Dictionary=root.get_meta("surface_cells")
 for group:Dictionary in record.groups:
  for row:Dictionary in group.members:
   var original_mode:int=group.original_shadow_mode
   row.node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY if enabled and original_mode==GeometryInstance3D.SHADOW_CASTING_SETTING_ON else original_mode
   row.node.visible=not enabled or original_mode==GeometryInstance3D.SHADOW_CASTING_SETTING_ON
  group.batch.visible=enabled
 record.enabled=enabled

static func raw_faces(mesh:Mesh)->PackedVector3Array:
 var a:Array=mesh.surface_get_arrays(0);var v:PackedVector3Array=a[Mesh.ARRAY_VERTEX];var idx:PackedInt32Array=a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
 if idx.is_empty():return v
 var result:=PackedVector3Array();result.resize(idx.size())
 for i in idx.size():result[i]=v[idx[i]]
 return result

static func compact(root:Node3D,lights:Array)->Dictionary:
 var result:Dictionary=build(root,lights)
 if not result.has("groups"):return {"failed":"source shadow CPU arrays unavailable"}
 var converted:=0
 for group:Dictionary in result.groups:
  for row:Dictionary in group.members:
   var original:MeshInstance3D=row.node
   var parent:=original.get_parent();var index:=original.get_index();var original_name:=original.name
   var proxy:=Node3D.new();proxy.transform=original.transform;proxy.visible=original.visible
   for key:StringName in original.get_meta_list():proxy.set_meta(key,original.get_meta(key))
   for key:StringName in original.get_groups():proxy.add_to_group(key)
   parent.add_child(proxy)
   for child in original.get_children():child.reparent(proxy,false)
   original.free();proxy.name=original_name;parent.move_child(proxy,index)
   row.erase("node");converted+=1
  group.batch.visible=true
  group.erase("members")
 root.remove_meta("surface_cells")
 return {"converted_mesh_instances":converted,"batch_count":result.batch_count,"source_meshes":result.source_meshes,"eligible_meshes":result.eligible_meshes,"saved_submissions":result.saved_submissions,"light_rejections":result.light_rejections,"triangles_reencoded":result.triangles_reencoded,"policy":"8m maximum opaque cells; exact source materials and full-resolution main/shadow triangles; original physics and path proxies; no lower-detail LOD"}
