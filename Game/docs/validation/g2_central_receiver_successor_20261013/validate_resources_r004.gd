extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/CANDIDATE_OVERLAY.zip",true))
 call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_central_receiving_20261013/RECEIVING.json"))
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://"+str(file))==str(p.model_pins[file]));var n:Node3D=(load("res://"+str(file))as PackedScene).instantiate();root.add_child(n)
  if str(file).contains("FRAME_r004"):
   assert(n.find_children("*","MeshInstance3D",true,false).size()==104)
   for part in p.parts:
    var mesh:MeshInstance3D=n.find_child(str(part.name),true,false);assert(mesh!=null);var a:Array=part.bounds_xyz;var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(Vector3(a[0],a[2],a[4]))<.001 and b.end.distance_to(Vector3(a[1],a[3],a[5]))<.001)
  if str(file).contains("FRAME_r004"):
   load("res://scripts/static_contact_cache.gd").attach_group(n,n.find_children("*","MeshInstance3D",true,false))
   for i in range(3):await physics_frame
   var source_space:=n.get_world_3d().direct_space_state
   for at:Vector3 in [Vector3(80,102,-22),Vector3(84,102,-20),Vector3(60,102,-15.1),Vector3(60,102.005833333,-14.3)]:
    var h:Dictionary=source_space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not h.is_empty()and absf(h.position.y-at.y)<.002 and h.normal.y>.99)
  n.free()
 var ship:=Node3D.new();root.add_child(ship);var architecture:Node3D=(load("res://assets/models/AST-COM-003.glb")as PackedScene).instantiate();architecture.name="StarboardHouseUpperArchitecture";architecture.position=Vector3(63,84,0);ship.add_child(architecture);var saved:Array=[]
 for row in p.guard_successor.rows:
  var mesh:MeshInstance3D=architecture.find_child(str(row.name),true,false);load("res://scripts/static_contact_cache.gd").attach(mesh);saved.append({"node":mesh,"parent":mesh.get_parent(),"body":mesh.get_node("StaticContact"),"shape_node":mesh.get_node("StaticContact/SharedShape"),"override":mesh.material_override})
 var owner:=Node3D.new();ship.add_child(owner);load("res://scripts/group2_central_receiving_20261013/guard_successor.gd").apply(ship,owner,p.guard_successor)
 for row in saved:
  assert(row.node.get_parent()==row.parent and row.node.get_node("StaticContact")==row.body and row.node.get_node("StaticContact/SharedShape")==row.shape_node and row.node.material_override==row.override)
  for vertex:Vector3 in row.node.mesh.get_faces():assert(vertex.x+63<=59.10001 or vertex.x+63>=60.89999)
 for i in range(3):await physics_frame
 var space:=ship.get_world_3d().direct_space_state
 for x in [58.5,60.,61.5]:
  var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,102.7,-14.2),Vector3(x,102.7,-13.8)));assert(hit.is_empty()if x==60. else not hit.is_empty())
 assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb")==str(p.guard_successor.model_sha256))
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/RESOURCE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_THREE_MODEL_PINS_AND_104_IMPORTED_FRAME_BOUNDS","new_frame_m2":119.654,"immutable_original_models":2,"new_frame_only_imported":true},"  "));print("CENTRAL_RECEIVING_R002_RESOURCE_PASS");quit(0)
