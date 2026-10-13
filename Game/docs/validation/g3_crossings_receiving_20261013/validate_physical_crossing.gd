extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
var retained_meshes:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/crossing_threshold_successor/RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/crossing_threshold_successor/CROSSING_PHYSICAL_RECEIVING_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_PHYSICAL_CROSSING_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"original_controller_legs":legs,"unrelated_meshes_preserved":retained_meshes,"exact_wall_preimages_replaced":6,"threshold_floor_m2":.9935658322647214,"gates_static_closed":true,"working_gate_backends":0,"original_criteria_preserved":13,"whole_network_accepted":false,"full_build_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_commons_crossings_20261012/CROSSINGS.json"));var w:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/crossing_threshold_successor/RUNTIME_FLOOR_WITNESSES.json"));var historical_path:="/workspace/astraea-integration-cutoff-20261013/G3_STREET_IMMUTABLE_CLASSIFIED_READINESS.json";var historical_sha:String=FileAccess.get_sha256(historical_path)
 if not require(ship.get_node_or_null("ShipSpace/Group3D03RemainingStreets")!=null,"Corrected streets installed prerequisite"):return
 var removed:Dictionary={};var unchanged:Array=[]
 for row in p.exact_runtime_preimages:
  var mesh:MeshInstance3D=ship.get_node_or_null(str(row.path))
  if not require(mesh!=null,"Exact wall predecessor exists "+str(row.path)):return
  var b:AABB=mesh.global_transform*mesh.get_aabb()
  if not require(b.position.distance_to(Vector3(row.min[0],row.min[1],row.min[2]))<.0001 and b.end.distance_to(Vector3(row.max[0],row.max[1],row.max[2]))<.0001,"Exact current wall bounds "+str(row.path)):return
  removed[mesh.get_instance_id()]=true
 for district in ["D04StarboardFullCommons","D04StarboardAftHabitatNeighborhood","D04PortAftHabitatNeighborhood"]:
  for mesh:MeshInstance3D in ship.get_node("ShipSpace/Districts/"+district).find_children("*","MeshInstance3D",true,false):
   if removed.has(mesh.get_instance_id()):continue
   var contact:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
   unchanged.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb(),"contact":contact,"shape":contact.shape if contact!=null else null,"disabled":contact.disabled if contact!=null else false})
 retained_meshes=unchanged.size()
 actor.set_controls_enabled(false);var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 for xyz in w.new:
  var at:=Vector3(xyz[0],xyz[1],xyz[2]);var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not hit.is_empty():
   if not require(removed.has(hit.collider.get_parent().get_instance_id()),"New threshold preimage has no persistent floor owner "+str(at)):return
 var addition:Node3D=load("res://scripts/group3_commons_crossings_20261012/physical_package.gd").build(ship);await frames(4)
 for row in p.exact_runtime_preimages:
  if not require(ship.get_node_or_null(str(row.path))==null,"Only declared wall predecessor removed "+str(row.path)):return
 for row in unchanged:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds,"Unrelated original mesh exact "+str(mesh.name)):return
  if row.contact!=null:
   if not require(is_instance_valid(row.contact)and row.contact.shape==row.shape and row.contact.disabled==row.disabled,"Original contact exact "+str(mesh.name)):return
 for xyz in w.new:
  var at:=Vector3(xyz[0],xyz[1],xyz[2]);var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and addition.get_node("AST-STF-G3-063_current_receiving_successor001").is_ancestor_of(hit.collider)and absf(hit.position.y-12)<.002,"Exact new threshold floor owner "+str(at)):return
 for xyz in w.original:
  var at:=Vector3(xyz[0],xyz[1],xyz[2]);var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and absf(hit.position.y-12)<.002,"Original threshold footprint remains supported "+str(at)):return
 for mesh:MeshInstance3D in addition.find_children("*","MeshInstance3D",true,false):
  var shape:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
  if not require(shape!=null and not shape.disabled and shape.shape is ConcavePolygonShape3D and shape.shape.get_faces()==mesh.mesh.get_faces(),"Exact new physical contact "+str(mesh.name)):return
 for door in p.door_bindings:
  if not require(addition.get_node_or_null(str(door.name))==null,"Unsupported operating gate remains absent "+str(door.name)):return
  var at:=Vector3(door.position[0],13.3,door.position[2]);var hit:Dictionary=ray(space,at+Vector3(0,0,.15),at-Vector3(0,0,.15))
  if not require(not hit.is_empty()and addition.get_node("AST-STF-G3-062").is_ancestor_of(hit.collider),"Original closed source gate physically blocks "+str(door.name)):return
 for xyz in [[57,12,-381.14],[57,12,381.2],[-57,12,381.14]]:
  var center:=Vector3(xyz[0],xyz[1],xyz[2]);actor.global_position=center+Vector3(0,.03,0);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Original native crosslink buffer supported "+str(center)):return
  for goal in [center+Vector3(0,0,.8),center]:
   var leg:Dictionary=await walk_to(actor,goal);legs.append(leg)
   if not require(leg.reached and leg.floor_contact,"Original controller within closed crosslink buffer "+str(center)):return
 if not require(FileAccess.get_sha256(historical_path)==historical_sha,"Historical13 criteria exact bytes preserved"):return
 var h:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(historical_path))
 if not require(h.failed_worker_criteria_preserved.size()+h.failed_floor_criteria_at_closed_source_wall_positions_preserved.size()==13,"No historical failure reclassified as acceptance"):return
 if not require(not addition.get_meta("operating_gates_admitted")and not addition.get_meta("authoritative_identity_mapping")and not addition.get_meta("whole_network_accepted"),"Physical successors retain operational holds"):return
 receipt();print("G3_CROSSING_PHYSICAL_RECEIVING_PASS nchecks=",nchecks," unrelated=",retained_meshes);quit(0)
