extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_remaining_five_pairs_20261013/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_forward_receiving_20261013/FORWARD.json"))
 for path in p.model_pins:
  assert(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]));var model:Node3D=(load("res://"+str(path))as PackedScene).instantiate();root.add_child(model)
  if str(path).contains("FRAMES"):
   assert(model.find_children("*","MeshInstance3D",true,false).size()==155)
   for part in p.parts:
    var mesh:MeshInstance3D=model.find_child(str(part.name),true,false);var b:AABB=mesh.global_transform*mesh.get_aabb();var a:Array=part.bounds_xyz;assert(b.position.distance_to(Vector3(a[0],a[2],a[4]))<.001 and b.end.distance_to(Vector3(a[1],a[3],a[5]))<.001)
   load("res://scripts/static_contact_cache.gd").attach_group(model,model.find_children("*","MeshInstance3D",true,false))
   for i in range(3):await physics_frame
   var space:=model.get_world_3d().direct_space_state
   for at:Vector3 in [Vector3(-69.5,102,-395),Vector3(69,102,-395),Vector3(-69.5,102,-385),Vector3(69,102,-385)]:
    var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not hit.is_empty()and absf(hit.position.y-at.y)<.002 and hit.normal.y>.99)
   assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(63.45,102.02,-390),Vector3(63.45,101.98,-390))).is_empty())
  model.free()
 assert(load("res://scripts/group2_forward_receiving_20261013/package.gd")!=null);print("FORWARD_PAIR_FIVE_RESOURCES_155_FRAME_PARTS_PASS");quit(0)
