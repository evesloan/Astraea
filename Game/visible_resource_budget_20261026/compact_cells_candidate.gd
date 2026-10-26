extends RefCounted
# Candidate only: exact immutable opaque surface cells with source-path proxies.
const CELLS=preload("res://d04_surface_cells_20261023/batcher.gd")
static func build(root:Node3D,lights:Array)->Dictionary:
 var occlusion:Dictionary=load("res://scripts/static_room_occlusion.gd").install(root)
 var plan:Dictionary=CELLS.build(root,lights)
 var converted:=0;var retained:=0
 for group:Dictionary in plan.groups:
  var safe:=true
  for row:Dictionary in group.members:
   if row.node.top_level:safe=false
   var source:Mesh=row.node.mesh.shadow_mesh if row.node.mesh.shadow_mesh!=null else row.node.mesh
   if not source is ArrayMesh:safe=false;continue
   for surface:Dictionary in source.get("_surfaces"):
    if not surface.get("lods",[]).is_empty():safe=false
  if not safe:retained+=group.members.size();group.batch.free();continue
  var shadow:=SurfaceTool.new();shadow.begin(Mesh.PRIMITIVE_TRIANGLES)
  for row:Dictionary in group.members:
   var source:Mesh=row.node.mesh.shadow_mesh if row.node.mesh.shadow_mesh!=null else row.node.mesh
   for surface in source.get_surface_count():shadow.append_from(source,surface,row.transform)
  group.batch.mesh.shadow_mesh=shadow.commit()
  group.batch.cast_shadow=group.original_shadow_mode
  for row:Dictionary in group.members:
   var original:MeshInstance3D=row.node
   var parent:=original.get_parent();var index:=original.get_index();var original_name:=original.name
   var proxy:=Node3D.new();proxy.transform=original.transform;proxy.visible=original.visible
   for key:StringName in original.get_meta_list():proxy.set_meta(key,original.get_meta(key))
   # Collision/controller nodes preserve object IDs, local pose and parent path.
   parent.add_child(proxy)
   for child in original.get_children():child.reparent(proxy,false)
   original.free();proxy.name=original_name;parent.move_child(proxy,index)
   row.erase("node");converted+=1
  group.batch.visible=true
  group.erase("members")
 root.remove_meta("surface_cells")
 return {"converted_mesh_instances":converted,"rejected_members":retained,"batches":plan.batch_count,"eligible":plan.eligible_meshes,"source_meshes":plan.source_meshes,"light_rejections":plan.light_rejections,"occlusion":occlusion,"scope":"Candidate: original immutable opaque model nodes become same-path metadata/physics proxies; exact cell meshes/materials and shadow geometry retained. No doors or authored assets replaced."}
