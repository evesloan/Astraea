extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g3_starboard3_private_receiving/CANDIDATE_OVERLAY.zip",true))
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_starboard3_private_20261011/PRIVATE.json"))
 for file in p.model_pins:
  var path:String="res://assets/models/group3_starboard3_private_20261011/"+str(file)
  assert(FileAccess.get_sha256(path)==str(p.model_pins[file]));var packed:PackedScene=load(path);assert(packed!=null);var n:Node3D=packed.instantiate();root.add_child(n);assert(not n.find_children("*","MeshInstance3D",true,false).is_empty());n.free()
 print("PASS_STARBOARD3_FOUR_RESOURCES");quit(0)
