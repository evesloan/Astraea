extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var prefix:="res://d04_detail_batches_20261022/runtime_r004/"
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(prefix+"BAKE.json"));var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(prefix+"INDEX.json"))
 var paths:Array=report.shared_resource_files.keys();var members:=0;var dependency_count:=0
 for row:Dictionary in report.rooms:
  paths.append(index.rooms[row.model].detail_path)
  var scene:PackedScene=load(row.input_path);var state:=scene.get_state();var nodes:Dictionary={}
  for i in state.get_node_count():nodes[str(state.get_node_path(i)).trim_prefix("./")]=i
  for group:Dictionary in row.source_to_batch:
   for member:Dictionary in group.members:
    assert(nodes.has(member.path));var n:int=nodes[member.path]
    for p in state.get_node_property_count(n):
     var key:String=state.get_node_property_name(n,p)
     if key in ["visibility_range_begin","visibility_range_end"]:assert(is_zero_approx(float(state.get_node_property_value(n,p))),"Per-instance distance culling must remain separate")
    members+=1
 for path:String in paths:
  for dependency:String in ResourceLoader.get_dependencies(path):
   assert(not dependency.contains(".glb") and not dependency.contains("private_shells/") and not dependency.contains("runtime_r003") and not dependency.contains("runtime_r002"),"Unwanted retained-scene dependency: "+dependency)
   dependency_count+=1
 var result:={"assets_checked":paths.size(),"dependencies_checked":dependency_count,"batched_members_with_zero_distance_ranges":members,"old_glb_or_detail_scene_dependencies":0,"invalid_derivative_dependencies":0,"full_ship_launched":false}
 var f:=FileAccess.open("/workspace/Astraea-recovered-e6274e77-20261021/Game/d04_detail_batches_20261022/evidence/DEPENDENCIES.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();print(JSON.stringify(result));quit()
