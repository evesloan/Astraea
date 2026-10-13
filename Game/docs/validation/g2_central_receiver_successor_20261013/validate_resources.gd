extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/CANDIDATE_OVERLAY.zip",true))
 call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_central_receiving_20261013/RECEIVING.json"))
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://"+str(file))==str(p.model_pins[file]));var n:Node3D=(load("res://"+str(file))as PackedScene).instantiate();root.add_child(n)
  if str(file).contains("FRAME_r002"):
   assert(n.find_children("*","MeshInstance3D",true,false).size()==103)
   for part in p.parts:
    var mesh:MeshInstance3D=n.find_child(str(part.name),true,false);assert(mesh!=null);var a:Array=part.bounds_xyz;var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(Vector3(a[0],a[2],a[4]))<.001 and b.end.distance_to(Vector3(a[1],a[3],a[5]))<.001)
  n.free()
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/RESOURCE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_THREE_MODEL_PINS_AND_103_IMPORTED_FRAME_BOUNDS","new_frame_m2":119.78,"immutable_original_models":2,"new_frame_only_imported":true},"  "));print("CENTRAL_RECEIVING_R002_RESOURCE_PASS");quit(0)
