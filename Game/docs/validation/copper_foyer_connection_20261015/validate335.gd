extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
const D="/workspace/astraea-integration-cutoff-20261013/copper_foyer_connection_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/VESPER_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/STARBOARD_FORE404_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
var legs:Array=[]
var operations:Array=[]
func leg(actor:CharacterBody3D,at:Vector3)->bool:
 var r:Dictionary=await walk_to(actor,at);legs.append(r);return r.reached and r.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,pod:String,want:bool)->bool:
 var at:Vector3=door.get_node(pod).global_position;var delta:Vector3=at-actor.camera.global_position;actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());await aim(actor,at);var focused:bool=actor.interaction_target==door
 if focused:await key_e()
 await frames(100);var ok:bool=focused and door.desired_open==want and is_equal_approx(door.fraction,1. if want else 0.);operations.append({"id":str(door.persistent_id),"original_pod":pod,"at":str(actor.global_position),"control_at":str(at),"normal_RMB_target":focused,"normal_E":focused,"wanted_open":want,"fraction":door.fraction,"obstructed":door.obstructed,"passed":ok});return ok
func cafe_floor(space:PhysicsDirectSpaceState3D,at:Vector3,actor:CharacterBody3D)->bool:
 var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=[actor.get_rid()];var h:=space.intersect_ray(q);return not h.is_empty()and str(h.collider.get_path()).contains("/D09_copper_kettle_source_floor/")and absf(h.position.y-52.5)<.0002
func clear_at(space:PhysicsDirectSpaceState3D,at:Vector3,actor:CharacterBody3D)->bool:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.margin=.001;q.transform.origin=at+Vector3.UP*.925;q.exclude=[actor.get_rid()];return space.intersect_shape(q,64).is_empty()and cafe_floor(space,at,actor)
func clear_segment(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,actor:CharacterBody3D)->bool:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.margin=.001;q.transform.origin=a+Vector3.UP*.925;q.motion=b-a;q.exclude=[actor.get_rid()];var cast:=space.cast_motion(q);return cast[0]>.99999 and cafe_floor(space,(a+b)/2,actor)
func measured_route(space:PhysicsDirectSpaceState3D,actor:CharacterBody3D,start:Vector3,goal:Vector3)->Dictionary:
 var graph:=AStar3D.new();var ids:Dictionary={};var at_by_id:Dictionary={};var n:=0
 for x in range(14,52):
  for z in range(-459,-404):
   var at:=Vector3(x,52.5,z)
   if clear_at(space,at,actor):ids[Vector2i(x,z)]=n;at_by_id[n]=at;graph.add_point(n,at);n+=1
 for xy in ids:
  for step:Vector2i in[Vector2i(1,0),Vector2i(0,1)]:
   var next:Vector2i=xy+step
   if ids.has(next)and clear_segment(space,at_by_id[ids[xy]],at_by_id[ids[next]],actor):graph.connect_points(ids[xy],ids[next],true)
 if graph.get_point_count()==0:return {"passed":false,"reason":"No supported clear Cafe grid points"}
 var a:int=graph.get_closest_point(start);var b:int=graph.get_closest_point(goal);var path:PackedVector3Array=graph.get_point_path(a,b);var raw:Array=[]
 for p in path:raw.append([p.x,p.y,p.z])
 var compact:Array[Vector3]=[]
 for i in range(1,path.size()):
  if i==path.size()-1 or (path[i]-path[i-1]).normalized().dot((path[i+1]-path[i]).normalized())<.999:compact.append(path[i])
 var passed:bool=path.size()>1 and clear_segment(space,start,path[0],actor)and clear_segment(space,path[-1],goal,actor)
 return {"passed":passed,"supported_clear_grid_points":n,"raw_physics_verified_path":raw,"waypoints":compact,"capsule_radius":.3,"capsule_height":1.8,"original_contacts_enabled":true}
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(62,52.53,-404);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(4);var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D09_directory_02");var door:Node3D=cafe.get_node("Group5FoyerDoors");assert(str(door.persistent_id)=="group5:D09_directory_02:original_foyer_threshold"and door.global_position.distance_to(Vector3(14.3,52.5,-432))<.0001);var original_open:bool=door.desired_open;var source_meshes:Dictionary={}
 for mesh:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):source_meshes[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 var space:=ship.get_world_3d().direct_space_state;var plan:Dictionary=measured_route(space,actor,Vector3(48,52.5,-414),Vector3(15.2,52.5,-425.65));var route:Array=plan.get("waypoints",[]);var ok:bool=plan.passed and not original_open and is_zero_approx(door.fraction);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for at:Vector3 in[Vector3(60.1,52.5,-404),Vector3(58.8,52.5,-404),Vector3(55.7,52.5,-404),Vector3(55.7,52.5,-409),Vector3(55.7,52.5,-414),Vector3(53,52.5,-414),Vector3(51,52.5,-414),Vector3(48,52.5,-414)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 for at:Vector3 in route:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await leg(actor,Vector3(15.2,52.5,-425.65))
 if ok:ok=await operate(actor,door,"InteriorControl",true)
 for at:Vector3 in[Vector3(15.6,52.5,-432),Vector3(11.8,52.5,-432),Vector3(6,52.5,-432),Vector3(11.8,52.5,-432),Vector3(12.75,52.5,-435.24)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await operate(actor,door,"PublicControl",false)
 if ok:ok=await operate(actor,door,"PublicControl",true)
 for at:Vector3 in[Vector3(11.8,52.5,-432),Vector3(15.6,52.5,-432),Vector3(15.2,52.5,-425.65)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await operate(actor,door,"InteriorControl",false)
 route.reverse()
 for at:Vector3 in route:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await leg(actor,Vector3(48,52.5,-414))
 for at:Vector3 in[Vector3(51,52.5,-414),Vector3(53,52.5,-414),Vector3(55.7,52.5,-414),Vector3(55.7,52.5,-409),Vector3(55.7,52.5,-404),Vector3(58.8,52.5,-404),Vector3(60.1,52.5,-404),Vector3(62,52.5,-404)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 var preserved:=true
 for mesh in source_meshes:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(source_meshes[mesh].pose)or mesh.mesh!=source_meshes[mesh].mesh:preserved=false
 var restored:bool=door.desired_open==original_open and is_zero_approx(door.fraction)and str(door.persistent_id)=="group5:D09_directory_02:original_foyer_threshold";ok=ok and operations.size()==4 and operations.all(func(r):return r.passed)and preserved and restored
 FileAccess.open(D+"COPPER_FOYER_ROUTE335.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","physics_measured_cafe_path":plan,"original_controller_legs":legs,"ordinary_original_foyer_operations":operations,"all_original_cafe_meshes_and_poses_preserved":preserved,"original_mesh_count":source_meshes.size(),"original_foyer_id_and_closed_state_restored":restored,"route_teleports":0,"all84addressjoins_unresolved":84,"service_or_final_art_admission":false},"  "));print("PASS_COPPER_FOYER_PUBLIC_CORE_CONNECTION"if ok else"FAIL_COPPER_FOYER_PUBLIC_CORE_CONNECTION");quit(0 if ok else 1)
