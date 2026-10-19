extends "res://tests/group6_completion/validate_water_care.gd"
var exercise_circuit:=true
var output_name:="LOCAL"
var rides:Array=[]
func run()->void:
 var host:=LocalHost.new();root.add_child(host)
 var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host)
 load("res://scripts/group6_completion/completion.gd").build(annex,host)
 var floats:Node3D=load("res://scripts/group6_float_20261019/package.gd").build(annex)
 var actor:CharacterBody3D=load("res://scripts/group6_float_20261019/player.gd").new();host.add_child(actor)
 actor.position=Vector3(64,45.48,229)
 await exercise(host,floats,actor)
func exercise(host:Node3D,floats:Node3D,actor:CharacterBody3D)->void:
 for i in range(300):await physics_frame
 for body:RigidBody3D in floats.get_children():
  var id:String=str(body.name);var empty_y:float=body.global_position.y
  print("DOCK ",id," ",body.global_position," ",body.linear_velocity," tilt ",body.global_basis.y.dot(Vector3.UP))
  record(id+"_empty_settled",body.settled_at_dock())
  actor.global_position=body.seat.exit_world_position();actor.velocity=Vector3.ZERO
  for i in range(20):await physics_frame
  var approach:Dictionary=await walk_to(actor,body.seat.exit_world_position()+Vector3.LEFT*.3)
  record(id+"_ordinary_approach",approach.reached)
  await aim(actor,body.seat.global_position+Vector3.UP*.25)
  record(id+"_focused_source_float",actor.interaction_target==body or actor.interaction_target==body.seat)
  await key_e()
  record(id+"_mount",actor.seated and body.seat.occupant==actor)
  if not actor.seated:
   print("MOUNT HOLD ",body.seat.reason," distance ",actor.global_position.distance_to(body.seat.global_position)," target ",actor.body_space_clear(body.seat.global_position,1.2)," path ",body.seat.transfer_clear(actor,actor.global_position));continue
  for i in range(300):await physics_frame
  print("LOADED ",id," ",body.global_position," ",body.linear_velocity," tilt ",body.global_basis.y.dot(Vector3.UP))
  record(id+"_loaded_settled",body.settled_at_dock())
  record(id+"_actual_load_and_draft",absf(body.mass-87)<.01 and empty_y-body.global_position.y>.1 and empty_y-body.global_position.y<.25)
  var blocker:=StaticBody3D.new();var contact:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(.7,1.8,.7);contact.shape=box;blocker.add_child(contact);host.add_child(blocker);blocker.global_position=body.seat.exit_world_position()+Vector3.UP*.9
  for i in range(3):await physics_frame
  body.seat.request_leave(actor);record(id+"_blocked_exit_retains_occupant",actor.seated and body.seat.occupant==actor and is_equal_approx(body.mass,87))
  blocker.queue_free()
  for i in range(3):await physics_frame
  if exercise_circuit:
   await key_e();record(id+"_launch_with_E",body.mode=="riding")
   var previous:Vector3=body.global_position;var max_step:=0.0;var min_y:=previous.y;var max_tilt:=0.0;var travelled:=0.0;var last_arc:float=body.field.project(previous).arc_m
   await key_e();record(id+"_return_requested_with_E",body.return_requested and actor.seated)
   for i in range(24000):
    await physics_frame
    if not body.global_position.is_finite() or not body.angular_velocity.is_finite() or body.angular_velocity.length()>20:
     print("UNSTABLE ",i," pos ",body.global_position," angular ",body.angular_velocity," inertia ",PhysicsServer3D.body_get_direct_state(body.get_rid()).inverse_inertia);quit(1);return
    var now:Vector3=body.global_position;max_step=maxf(max_step,now.distance_to(previous));min_y=minf(min_y,now.y);max_tilt=maxf(max_tilt,acos(clampf(body.global_basis.y.dot(Vector3.UP),-1,1)))
    var arc:float=body.field.project(now).arc_m;var change:float=arc-last_arc
    if change< -body.field.length_m/2:change+=body.field.length_m
    elif change>body.field.length_m/2:change-=body.field.length_m
    travelled+=change;last_arc=arc;previous=now
    if body.return_requested and body.departed and body.settled_at_dock():break
   print("RIDE ",id," arc=",travelled," maxstep=",max_step," miny=",min_y," tilt=",max_tilt," end=",body.global_position," mode=",body.mode)
   rides.append({"dock":id,"arc_m":travelled,"max_step_m":max_step,"minimum_y":min_y,"maximum_tilt_radians":max_tilt})
   record(id+"_occupied_circuit_returns",body.return_requested and body.departed and body.settled_at_dock() and travelled>body.field.length_m-6)
   record(id+"_bounded_loaded_motion",max_step<.09 and min_y>44.75 and max_tilt<.35)
   record(id+"_rider_retained",actor.seated and actor.parked_seat==body.seat and actor.global_position.distance_to(body.seat.global_position)<.08)
   await key_e()
  else:
   if host.has_method("arrive_at") and id=="north_recovery":
    record("verified_travel_from_occupied_float",host.arrive_at(actor.spawn_position,0.0))
    record("travel_releases_load_and_exception",not actor.seated and body.seat.occupant==null and is_equal_approx(body.mass,12) and not actor.get_collision_exceptions().has(body))
    actor.global_position=body.seat.exit_world_position();actor.velocity=Vector3.ZERO
   else:body.seat.request_leave(actor)
  record(id+"_safe_unload",not actor.seated and body.seat.occupant==null and is_equal_approx(body.mass,12))
  for i in range(20):await physics_frame
  record(id+"_supported_exit",actor.is_on_floor())
  if actor.seated:break
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"rides":rides}
 FileAccess.open("res://docs/validation/group6_float_20261019/"+output_name+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("OCCUPIED FLOAT ",result.status," ",errors);quit(0 if errors.is_empty() else 1)
