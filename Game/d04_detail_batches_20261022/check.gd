extends "res://d04_detail_batches_20261022/bake_r004.gd"
func _initialize()->void:call_deferred("validate_all")
func validate_all()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells_d04.json"))
 var current:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(RES+"INDEX.json"))
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(RES+"BAKE.json"))
 assert(old.rooms.keys()==current.rooms.keys() and report.rooms.size()==120)
 for path:String in report.shared_resource_files:assert(FileAccess.get_sha256(path)==report.shared_resource_files[path])
 var held:Array[Node]=[];var old_meshes:Dictionary={};var new_meshes:Dictionary={};var old_shadows:Dictionary={};var new_shadows:Dictionary={};var refs:Array[WeakRef]=[]
 var before_nodes:=0;var after_nodes:=0;var before_render:=0;var after_render:=0;var triangles:=0;var batches:=0;var instances:=0;var original_lod_surfaces:=0;var retained_lod_surfaces:=0
 for row:Dictionary in report.rooms:
  var prior:Dictionary=old.rooms[row.model].duplicate(true);prior.detail_path=current.rooms[row.model].detail_path;prior.detail_sha256=current.rooms[row.model].detail_sha256;assert(prior==current.rooms[row.model])
  var original_scene:PackedScene=load(row.input_path);var original:Node3D=original_scene.instantiate()
  var scene:PackedScene=load(current.rooms[row.model].detail_path);var candidate:Node3D=scene.instantiate();held.append(candidate)
  assert(FileAccess.get_sha256(current.rooms[row.model].detail_path)==current.rooms[row.model].detail_sha256)
  fingerprints.clear()
  for n:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
   if n.mesh==null:continue
   assert(not n.mesh.resource_path.is_empty());old_meshes[n.mesh.resource_path]=true
   if n.mesh.shadow_mesh!=null:assert(not n.mesh.shadow_mesh.resource_path.is_empty());old_shadows[n.mesh.shadow_mesh.resource_path]=true
   for surface:Dictionary in n.mesh.get("_surfaces"):
    if not surface.get("lods",[]).is_empty():original_lod_surfaces+=1
  for n:MeshInstance3D in candidate.find_children("*","MeshInstance3D",true,false):
   if n.mesh==null:continue
   var source:MeshInstance3D=original.get_node(candidate.get_path_to(n));assert(source!=null)
   assert(identity(n.mesh)==identity(source.mesh) and pose(n,candidate)==pose(source,original))
   assert(identity(n.material_override)==identity(source.material_override))
   for p:String in DRAW_PROPERTIES:assert(identity(n.get(p))==identity(source.get(p)))
   for surface in n.mesh.get_surface_count():assert(identity(n.get_surface_override_material(surface))==identity(source.get_surface_override_material(surface)))
   new_meshes[n.mesh.get_instance_id()]=true
   if n.mesh.shadow_mesh!=null:new_shadows[n.mesh.shadow_mesh.get_instance_id()]=true
   for surface:Dictionary in n.mesh.get("_surfaces"):
    if not surface.get("lods",[]).is_empty():retained_lod_surfaces+=1
   if refs.size()<12:refs.append(weakref(n.mesh))
  for group:Dictionary in row.source_to_batch:
   var n:MultiMeshInstance3D=candidate.get_node(group.batch);assert(n.multimesh.instance_count==group.members.size());batches+=1;instances+=group.members.size()
   var bounds:=AABB();var first:=true
   for i in group.members.size():
    var source:MeshInstance3D=original.get_node(group.members[i].path)
    assert(source!=null and identity(n.multimesh.mesh)==identity(source.mesh))
    assert(n.multimesh.get_instance_transform(i)==pose(source,original),"Instance transform changed")
    assert(source.custom_aabb==AABB() and source.visibility_parent==NodePath(""),"Unsupported culling override")
    assert(identity(n.material_override)==identity(source.material_override))
    for p:String in DRAW_PROPERTIES:assert(identity(n.get(p))==identity(source.get(p)))
    var box:AABB=pose(source,original)*source.get_aabb();bounds=box if first else bounds.merge(box);first=false
   assert(bounds.size[bounds.size.max_axis_index()]<=GRID_M)
   new_meshes[n.multimesh.mesh.get_instance_id()]=true
   if n.multimesh.mesh.shadow_mesh!=null:new_shadows[n.multimesh.mesh.shadow_mesh.get_instance_id()]=true
  var before:=stats(original);var after:=stats(candidate);assert(before.triangles==after.triangles)
  before_nodes+=before.nodes;after_nodes+=after.nodes;before_render+=before.render_nodes;after_render+=after.render_nodes;triangles+=before.triangles
  original.free();original_scene=null;scene=null
  if held.size()%20==0:print("D04_VERIFY ",held.size(),"/120")
  await process_frame
 assert(original_lod_surfaces==retained_lod_surfaces)
 assert(new_meshes.size()<old_meshes.size() and new_shadows.size()<old_shadows.size() and after_nodes<before_nodes and after_render<before_render)
 var result:={"rooms":120,"source_unique_mesh_paths":old_meshes.size(),"source_unique_shadow_paths":old_shadows.size(),"simultaneously_loaded_candidate_meshes":new_meshes.size(),"simultaneously_loaded_candidate_shadows":new_shadows.size(),"before_nodes":before_nodes,"after_nodes":after_nodes,"before_render_nodes":before_render,"after_render_nodes":after_render,"triangles_unchanged":triangles,"lod_surfaces_preserved":original_lod_surfaces,"multimesh_batches":batches,"batched_instances":instances,"maximum_batch_extent_m":GRID_M,"packed_buffers_and_materials_exact":true,"instance_transforms_exact":true,"room_fields_and_contacts_unchanged":true,"full_ship_launched":false,"fps_claim":false,"rid_cause_proven":false}
 for node:Node in held:node.free()
 held.clear();fingerprints.clear()
 for i in 3:await process_frame
 var still_live:=0
 for reference:WeakRef in refs:
  if reference.get_ref()!=null:still_live+=1
 assert(still_live==0,"Shared resources held after all resident scenes released")
 result.unload_samples=refs.size();result.unload_samples_remaining=still_live
 var f:=FileAccess.open(OUTPUT_RESULT(),FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();print(JSON.stringify(result));quit()
func OUTPUT_RESULT()->String:return "/workspace/Astraea-recovered-e6274e77-20261021/Game/d04_detail_batches_20261022/evidence/CHECK.json"
