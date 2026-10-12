extends SceneTree
var checks:=0
var errors:Array[String]=[]
var rail_samples:=0
var body_samples:=0
var frames_moving:=0
var milestones:Array=[]
var longest_step:=0.0
func _initialize()->void:call_deferred("run")
func check(value:bool,why:String)->void:
 checks+=1
 if not value:errors.append(why);push_error(why)
func frames(n:int)->void:
 for i in range(n):await physics_frame
func contact_sample(actuator:Node3D,world:Node3D)->void:
 for wheel:Node3D in actuator.wheel_pivots:
  var foot:=wheel.global_position-Vector3.UP*.16;var q:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.01,foot-Vector3.UP*.05)
  var hit:Dictionary=world.get_world_3d().direct_space_state.intersect_ray(q)
  check(not hit.is_empty() and abs(hit.position.y-55.74)<.002,"Actual guideway rail supports nominal original wheel reference at "+str(foot));rail_samples+=1
 for col:CollisionShape3D in actuator.vehicle.find_children("*","CollisionShape3D",false,false):
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=col.shape;q.transform=col.global_transform;q.exclude=[actuator.vehicle.get_rid()]
  var hits:Array=world.get_world_3d().direct_space_state.intersect_shape(q,16);var unexpected:Array=[]
  for h in hits:
   if h.collider is StaticBody3D and not actuator.vehicle.is_ancestor_of(h.collider):unexpected.append(str(h.collider.get_path()))
  check(unexpected.is_empty(),"Actual moving car shape clear at cursor "+str(actuator.cursor)+" "+str(unexpected));body_samples+=1
func travel_to(actuator:Node3D,world:Node3D,distance:float,label:String)->void:
 check(actuator.request_distance(distance),label+" root source request allowed only secured")
 var count:=0;var previous:Vector3=actuator.vehicle.global_position
 while actuator.moving and count<100000:
  await physics_frame;count+=1;frames_moving+=1
  var step:float=previous.distance_to(actuator.vehicle.global_position);longest_step=maxf(longest_step,step);previous=actuator.vehicle.global_position
  check(step<.105,label+" physics pose advances continuously below straight6m/s step")
  check(not actuator.motion_fault,label+" one motor owns actual vehicle pose")
  check(abs(actuator.bogies[0].position.x)<.20 and abs(actuator.bogies[1].position.x)<.20,label+" physical trucks remain inside exact slide fitting")
  if count%180==0:contact_sample(actuator,world)
  if not errors.is_empty():break
 check(count<100000 and not actuator.moving and abs(actuator.cursor-distance)<.0001,label+" exact arrival without fixture relocation")
 milestones.append({"label":label,"cursor":actuator.cursor,"world":str(actuator.vehicle.global_position),"continuous_physics_frames":count,"fixture_relocations":0})
func run()->void:
 var world:=Node3D.new();world.name="ActualGroup4GuidewayTravelFixture";root.add_child(world)
 var base:Node3D=load("res://scripts/group4_completion.gd").build(world,true,true)
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"))
 var vehicle:AnimatableBody3D=load("res://scripts/group4_tram_source_actuator.gd").fixture_vehicle(world,Vector3(-5.6,56.1,-462))
 var safety:Node3D=load("res://scripts/group4_boarding_safety.gd").build(world,base,vehicle,true)
 var actuator:Node3D=load("res://scripts/group4_tram_source_actuator.gd").build(world,vehicle,safety,true);await frames(60)
 check(not source.active and not source.north_stop_adopted and not source.shared_pits_adopted,"Production flags and north/pit holds preserved")
 check(actuator.wheel_pivots.size()==4 and actuator.bogies.size()==2,"Original four wheels reused with two new source steering trucks")
 check(vehicle.get_meta("exact_original_portal_contact_components")==18,"Exact source solids preserve both hollow portal frames without unsupported concave pair queries")
 for bridge:Node3D in safety.bridges.values():
  var physical:Transform3D=PhysicsServer3D.body_get_state(bridge.moving.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)
  check(bridge.get_meta("initial_stow_physics_corrected",false) and absf(bridge.moving.rotation.z-PI/2)<.0001 and physical.is_equal_approx(bridge.moving.global_transform),"Actual startup stow matches both node and physics authority "+str(bridge.name))
 check(world.find_children("*cart*","RigidBody3D",true,false).is_empty(),"No cart or stock created in unloaded source fixture")
 check(not actuator.request_distance(source.safe_body_cursor_range_m[0]-1),"Protected low end limit refuses root request")
 check(not actuator.request_distance(source.safe_body_cursor_range_m[1]+1),"Protected high end limit refuses root request")
 var ordered:Array=source.stops.duplicate();ordered.sort_custom(func(a,b):return a.distance_m<b.distance_m)
 for stop in ordered:
  await travel_to(actuator,world,stop.distance_m,stop.station)
  if not errors.is_empty():break
  await frames(20);check(vehicle.global_position.distance_to(Vector3(stop.world_xyz[0],56.1,stop.world_xyz[2]))<.005,stop.station+" unchanged source station/dock alignment")
  check(safety._physical_dock_matches(stop.station),stop.station+" existing source boarding adapter recognizes stationary travelled car")
  if stop.station=="CENTRAL":
   check(safety.request_boarding("CENTRAL"),"Travelled central car allows original source door/bridge sequence");await frames(270)
   check(not actuator.request_stop("AFT"),"Motor refuses departure with deployed bridge/open portals")
   check(safety.request_secure(),"Root source secure request after travelled dock");await frames(270)
   check(safety.unloaded_clear_to_depart(),"Travel resumes only after original portals closed and bridge stowed")
  if stop.station=="FORWARD":
   check(actuator.request_stop("FORE_MIDSHIP"),"Pause source trip starts through same actuator");await frames(60)
   var at:float=actuator.cursor;var pose:Transform3D=vehicle.global_transform;paused=true;await create_timer(.05,true,false,true).timeout
   check(actuator.cursor==at and vehicle.global_transform.is_equal_approx(pose),"Pause freezes car and source steering");paused=false
   # Continue the existing request; no position/cursor reset.
   while actuator.moving:await physics_frame
   check(abs(actuator.cursor-ordered[1].distance_m)<.001,"Paused source journey completes without reset")
 if errors.is_empty():
  await travel_to(actuator,world,source.safe_body_cursor_range_m[1],"AFT_SAFE_END")
  await travel_to(actuator,world,source.safe_body_cursor_range_m[0],"FORWARD_SAFE_END_RETURN")
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"milestones":milestones,"source_route_total_m":source.source_route_total_m,"actual_body_distance_m":actuator.distance_travelled,"source_rail_reference_ray_samples":rail_samples,"actual_body_contact_samples":body_samples,"checked_motion_frames":frames_moving,"maximum_physics_step_m":longest_step,"initial_fixture_placements":1,"teleports_during_trip":0,"original_wheels_reused":4,"north_stop_adopted":false,"shared_pits_adopted":false,"wheel_rail_traction_or_dynamic_forces_tested":false,"loaded_cart_or_original_player_carry_tested":false,"main_integrated":false,"whole_group_accepted":false,"scope":"One unloaded source24 body with original powered portals, source28 steering/slide hardware and source29 buffers on exact continuous016 guideway. Root-callable kinematic source actuator; nominal wheel rail ray references and actual car-contact checks, not wheel-force/passenger/cart/engineering/production transport acceptance."}
 var f:=FileAccess.open("res://artifacts/group4_source_travel.json",FileAccess.WRITE);f.store_string(JSON.stringify(result," "));f.close();print("GROUP4 SOURCE TRAVEL ",result.status,": ",checks," checks; distance",actuator.distance_travelled,"m; wheel refs",rail_samples,"; contacts",body_samples)
 world.queue_free();await process_frame;quit(0 if errors.is_empty() else 1)
