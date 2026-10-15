extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
const D="/workspace/astraea-integration-cutoff-20261013/vesper_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
var legs:Array=[]
var operations:Array=[]
func leg(actor:CharacterBody3D,at:Vector3)->bool:
 var r:Dictionary=await walk_to(actor,at);legs.append(r);return r.reached and r.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,want:bool)->bool:
 var at:Vector3=door.leaves[0].global_transform*Vector3(.55,1.26,0);var delta:Vector3=at-actor.camera.global_position;actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());await aim(actor,at);var focused:bool=actor.interaction_target==door
 if focused:await key_e()
 await frames(100);var ok:bool=focused and door.desired_open==want and is_equal_approx(door.open_fraction,1. if want else 0.);operations.append({"at":str(actor.global_position),"leaf_point":str(at),"RMB_target_original_door":focused,"normal_E":focused,"wanted_open":want,"open_fraction":door.open_fraction,"passed":ok});return ok
func volume(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,excluded:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=excluded;var out:Array=[]
 for hit in space.intersect_shape(q,512):out.append(str(hit.collider.get_path()))
 return out
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(-2,61.03,170);var space:=ship.get_world_3d().direct_space_state;var group:Node3D=ship.get_node("ShipSpace/VesperServiceReceiving20261015");var room:Node3D=ship.get_node("ShipSpace/Districts/GentleWaters_LivingGifts_Vesper_Section_WIP");var door:Node3D=room.find_child("VesperServiceDoor",true,false);var initial_open:bool=door.desired_open;var initial_door_pose:Transform3D=door.global_transform;var lift:Node3D=room.get_node("AquaticPassengerLift");var lift_stops:Array=lift.floor_heights.duplicate();var local_lift:Node3D=room.find_child("VesperDiningLift",true,false);var local_stops:Array=local_lift.floor_heights.duplicate();var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"));var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var excluded:Array[RID]=[actor.get_rid()]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var preimages:Array=[];var floors:Array=[];var contacts:Array=[];var unexplained:Array=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.35
  while x<float(rect[1])-.25:
   var z:float=rect[2]+.35
   while z<float(rect[3])-.25:
    var at:=Vector3(x,61,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var old:=space.intersect_ray(q)
    if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
    var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);floors.append({"at":str(at),"supported":not h.is_empty()and absf(h.position.y-61)<.003})
    z+=2.
   x+=2.
 for row in p.bounds:
  if "Lens"in str(row.name):continue
  var lo:=vec(row.min);var hi:=vec(row.max);var paths:Array=[]
  if "MissingOnlyFloor"in str(row.name)or"SourceJoinedRoof"in str(row.name):
   for rect in plan.floor_rectangles:
    for path in volume(space,Vector3(rect[0],lo.y,rect[2]),Vector3(rect[1],hi.y,rect[3]),excluded):
     if not path in paths:paths.append(path)
  else:paths=volume(space,lo,hi,excluded)
  for path in paths:
   var kind:=""
   if "/D10_vesper_floor/"in path and("EmbeddedDiningTie"in str(row.name)or"Edge"in str(row.name)or"GatewayCross"in str(row.name)):kind="positive_joint_at_retained_dining_slab_edge"
   if "/D10_aft_route/"in path and("EmbeddedAxialTie"in str(row.name)or"Axial"in str(row.name)or"Edge"in str(row.name)):kind="positive_joint_at_retained_axial_slab_edge"
   var r:Dictionary={"part":row.name,"owner":path,"classification":kind};contacts.append(r)
   if kind.is_empty():unexplained.append(r)
 var bearings:Array=[]
 for at:Vector3 in[Vector3(53.8,61,229),Vector3(53.8,61,230),Vector3(53.8,61,231),Vector3(3.8,61,168.7),Vector3(3.8,61,170),Vector3(3.8,61,171.3)]:
  var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var h:=space.intersect_ray(q);bearings.append({"at":str(at),"owner":str(h.collider.get_path())if not h.is_empty()else"","passed":not h.is_empty()and absf(h.position.y-61)<.003})
 var preserved:=true;var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"VESPER_SOURCE_RECEIVING_SURVEY320.json"));var mesh_count:int=room.find_children("*","MeshInstance3D",true,false).size()
 for row in source.source_mesh_bounds:
  var node:MeshInstance3D=root.get_node_or_null(str(row.path));
  if node==null:preserved=false;continue
  var b:AABB=node.global_transform*node.get_aabb()
  if b.position.distance_to(vec(row.min))>.0001 or b.end.distance_to(vec(row.max))>.0001 or node.mesh.resource_path!=str(row.mesh):preserved=false
 var original_state:Dictionary={}
 for node:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):original_state[node]={"pose":node.global_transform,"mesh":node.mesh}
 actor.global_position=Vector3(2,61.03,170);actor.velocity=Vector3.ZERO;actor.set_physics_process(true);actor.set_controls_enabled(true);await frames(20);var ok:bool=preimages.is_empty()and unexplained.is_empty()and floors.all(func(a):return a.supported)and bearings.all(func(a):return a.passed)and preserved and mesh_count==source.source_mesh_bounds.size()
 for at:Vector3 in[Vector3(62,61,170),Vector3(62,61,190),Vector3(62,61,210),Vector3(62,61,230),Vector3(55,61,230),Vector3(51,61,230),Vector3(46.2,61,230),Vector3(46.2,61,237)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await operate(actor,door,false)
 var closed_contact:bool=not capsule_clear(space,Vector3(48.6,61,237))
 if ok:ok=closed_contact and await operate(actor,door,true)
 for at:Vector3 in[Vector3(51,61,237),Vector3(51,61,234.8),Vector3(51,61,237),Vector3(51.25,61,239.85),Vector3(51,61,237),Vector3(46.2,61,237)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 if ok:ok=await operate(actor,door,false)
 if ok and initial_open:ok=await operate(actor,door,true)
 for at:Vector3 in[Vector3(46.2,61,230),Vector3(51,61,230),Vector3(55,61,230),Vector3(62,61,230),Vector3(62,61,210),Vector3(62,61,190),Vector3(62,61,170),Vector3(2,61,170)]:
  if not ok:break
  if not await leg(actor,at):ok=false
 for node in original_state:
  if not is_instance_valid(node)or node.mesh!=original_state[node].mesh or not node.global_transform.is_equal_approx(original_state[node].pose):preserved=false
 # Moving door leaves intentionally operate, then return to their original open pose.
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var identities:bool=door.persistent_id==&"D10_banquet7_service_door"and door.global_transform.is_equal_approx(initial_door_pose)and door.desired_open==initial_open and lift.floor_heights==lift_stops and local_lift.floor_heights==local_stops
 ok=ok and identities and preserved and legs.size()==22 and operations.size()==4 and lights.size()==10 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"CANDIDATE_RUNTIME322.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","new_floor_preimages":preimages,"floor_samples":floors,"source_contacts":contacts,"unexplained_contacts":unexplained,"source_bearings":bearings,"original_controller_legs":legs,"normal_door_operations":operations,"closed_door_contact":closed_contact,"original_meshes_bounds_resources_poses_preserved":preserved,"retained_mesh_count":mesh_count,"original_ids_stops_and_door_state_restored":identities,"source_lights":lights,"operational_or_final_acceptance":false},"  "));print("PASS_VESPER_PHYSICAL_RECEIVING"if ok else"FAIL_VESPER_PHYSICAL_RECEIVING");quit(0 if ok else 1)
