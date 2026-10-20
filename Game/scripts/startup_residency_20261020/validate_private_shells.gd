extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var index_path := "res://data/architecture/startup_residency_20261020/private_shells.json" if OS.get_cmdline_user_args().is_empty() else OS.get_cmdline_user_args()[0]
 var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(index_path))
 var tested:=0
 var detail_count:=0
 var shell_count:=0
 for file in data.rooms:
  var record:Dictionary=data.rooms[file]
  assert(FileAccess.get_sha256("res://assets/models/"+file)==record.sha256)
  assert(FileAccess.get_sha256(str(record.shell_path))==record.shell_sha256)
  var source:Node3D=load("res://assets/models/"+file).instantiate()
  var shell:Node3D=load(str(record.shell_path)).instantiate()
  root.add_child(source);root.add_child(shell)
  var mesh_count:=source.find_children("*","MeshInstance3D",true,false).size()
  assert(mesh_count==record.shell_mesh_paths.size()+record.detail_mesh_paths.size())
  assert(shell.find_children("*","MeshInstance3D",true,false).size()==record.shell_mesh_paths.size())
  for path in record.shell_mesh_paths:
   var before:MeshInstance3D=source.get_node(path)
   var after:MeshInstance3D=shell.get_node(path)
   assert(before.global_transform.is_equal_approx(after.global_transform))
   assert(before.mesh.get_surface_count()==after.mesh.get_surface_count())
   for surface in range(before.mesh.get_surface_count()):
    assert(var_to_bytes(before.mesh.surface_get_arrays(surface))==var_to_bytes(after.mesh.surface_get_arrays(surface)),"Architectural render data changed")
    var a:Material=before.get_active_material(surface)
    var b:Material=after.get_active_material(surface)
    assert(a.get_class()==b.get_class())
    for property in a.get_property_list():
     if not(int(property.usage)&PROPERTY_USAGE_STORAGE) or str(property.name) in ["resource_path","resource_local_to_scene"]:continue
     var av=a.get(str(property.name));var bv=b.get(str(property.name))
     if av is Resource:
      assert(av==bv or av.resource_path==bv.resource_path)
     else:assert(av==bv,"Architectural material property changed")
  if record.has("detail_path"):
   assert(FileAccess.get_sha256(str(record.detail_path))==record.detail_sha256)
   var details:Node3D=load(str(record.detail_path)).instantiate();root.add_child(details)
   for path in record.detail_mesh_paths:
    var before:MeshInstance3D=source.get_node(path)
    var after:MeshInstance3D=details.get_node(path)
    assert(before.global_transform.is_equal_approx(after.global_transform))
    assert(before.mesh.get_surface_count()==after.mesh.get_surface_count())
    for surface in range(before.mesh.get_surface_count()):
     assert(var_to_bytes(before.mesh.surface_get_arrays(surface))==var_to_bytes(after.mesh.surface_get_arrays(surface)),"Private detail render data changed")
     var a:Material=before.get_active_material(surface)
     var b:Material=after.get_active_material(surface)
     assert(a.get_class()==b.get_class())
     for property in a.get_property_list():
      if not(int(property.usage)&PROPERTY_USAGE_STORAGE) or str(property.name) in ["resource_path","resource_local_to_scene"]:continue
      var av=a.get(str(property.name));var bv=b.get(str(property.name))
      if av is Resource:
       assert(av==bv or av.resource_path==bv.resource_path)
      else:assert(av==bv,"Private detail material property changed")
   for path in record.shell_mesh_paths:assert(details.get_node(path).mesh==null)
   details.free()
  for path in record.detail_mesh_paths:
   assert(source.has_node(path) and not shell.has_node(path))
  detail_count+=record.detail_mesh_paths.size();shell_count+=record.shell_mesh_paths.size();tested+=1
  source.free();shell.free()
 print("PRIVATE_SHELL_PARTITION_PASS ",JSON.stringify({"rooms":tested,"exact_original_shell_meshes":shell_count,"deferred_catalogue_meshes":detail_count,"no_geometry_simplification":true}))
 quit()
