extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/starboard_fore404_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/VESPER_SERVICE_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(x1-x0,4.06,z1-z0);shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,62.57,(z0+z1)/2);var result:Array=[]
 for hit in space.intersect_shape(q,1024):result.append(str(hit.collider.get_path()))
 return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(62,52.53,-408);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(50,52.5,-414));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(50,52.5,-414));await frames(4);var space:=ship.get_world_3d().direct_space_state;var samples:Array=[]
 for at:Vector3 in[Vector3(7.5,52.5,-414),Vector3(7.8,52.5,-414),Vector3(8.1,52.5,-414),Vector3(12,52.5,-414),Vector3(24,52.5,-414),Vector3(40,52.5,-414),Vector3(54,52.5,-414),Vector3(55.7,52.5,-414),Vector3(55.7,52.5,-408),Vector3(55.7,52.5,-404),Vector3(59,52.5,-404),Vector3(60.35,52.5,-404),Vector3(60.65,52.5,-404),Vector3(61.5,52.5,-404)]:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);samples.append({"at":[at.x,at.y,at.z],"floor":str(h.collider.get_path())if not h.is_empty()else"","floor_y":h.position.y if not h.is_empty()else null,"clear":capsule_clear(space,at)})
 var volumes:Array=[]
 for r in[[52.001,57.4,-415.7,-412.3],[54.,57.4,-412.3,-403.1],[57.4,60.49995,-404.9,-403.1]]:
  var shape:=BoxShape3D.new();shape.size=Vector3(r[1]-r[0],4.19,r[3]-r[2]);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=Vector3((r[0]+r[1])/2,54.135,(r[2]+r[3])/2);var paths:Array=[]
  for hit in space.intersect_shape(q,1024):paths.append(str(hit.collider.get_path()))
  volumes.append({"rect":r,"y":[52.04,56.23],"contacts":paths})
 var source_meshes:Array=[];var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D09_directory_02");var doors:Array=[]
 for node:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):
  var b:AABB=node.global_transform*node.get_aabb();source_meshes.append({"path":str(node.get_path()),"name":str(node.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"origin":str(node.global_position),"mesh":node.mesh.resource_path,"triangles":node.mesh.get_faces().size()/3})
 for n:Node3D in cafe.find_children("*","Node3D",true,false):
  if n.get_script()!=null and "door"in n.get_script().resource_path:doors.append({"name":str(n.name),"script":n.get_script().resource_path,"at":str(n.global_position),"id":str(n.persistent_id)})
 var inside:Array=[]
 for at:Vector3 in[Vector3(51,52.5,-414),Vector3(48,52.5,-414),Vector3(48,52.5,-420),Vector3(48,52.5,-432),Vector3(40,52.5,-432),Vector3(32,52.5,-432),Vector3(24,52.5,-432),Vector3(16,52.5,-432),Vector3(10,52.5,-432),Vector3(6,52.5,-432)]:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);inside.append({"at":[at.x,at.y,at.z],"floor":str(h.collider.get_path())if not h.is_empty()else"","clear":capsule_clear(space,at)})
 FileAccess.open(D+"COPPER_KETTLE_RECEIVING_PREIMAGES328.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"MEASURED_CURRENT_NAMED_CORE_TARGET","samples":samples,"new_route_volumes":volumes,"actual_cafe_meshes":source_meshes,"source_doors":doors,"sampled_inside_route":inside,"cafe_parent_live":cafe.is_inside_tree(),"production_changed":false},"  "));print("PASS_STARBOARD_TARGET_PREIMAGES");quit(0)
