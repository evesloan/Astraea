extends SceneTree
# Additive physical diagnostic only. No production entry, controller or admission is edited.
var host:Node3D
var player:CharacterBody3D
var car:AnimatableBody3D
var motor:Node3D
var safety:Node3D
var restraint:Node3D
var controls:Node3D
var cart:RigidBody3D
var actor_id:int
var camera_id:int
var cart_id:int
var product_ids:Array=[]
var ring:Array=[]
var maximum_drift:=0.0
var spawn_local:=Vector3(0,.10,1.40)
var settled_local:=Vector3.ZERO
var spawned:=false
var elapsed_frames:=0
var result:Dictionary={"scope":"Bounded real-tram/current-player physics. No full-ship clearance, streaming, GPU or frame-rate acceptance.","commit":"448eab129169f3c205e7db0662fcf774b869a346","failures":[],"completed_stops":[],"spawn_writes":0,"post_spawn_actor_writes":0}
func _initialize()->void:call_deferred("run")
func emit(event:String,data:Dictionary={})->void:
 data["event"]=event;data["physics_frame"]=Engine.get_physics_frames();print("TRAM_CARRY ",JSON.stringify(data))
func finish(reason:String="")->void:
 if not reason.is_empty():result.failures.append(reason)
 result["maximum_horizontal_drift_m"]=maximum_drift;result["recent_frames"]=ring
 if is_instance_valid(motor):result["final"]=sample()
 result["engine"]=Engine.get_version_info();result["physics_hz"]=Engine.physics_ticks_per_second;result["renderer"]=RenderingServer.get_current_rendering_method();result["static_peak_bytes"]=OS.get_static_memory_peak_usage()
 var f:=FileAccess.open(OS.get_environment("ASTRAEA_CARRY_RESULT"),FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 emit("RESULT",result);quit(0 if reason.is_empty() else 1)
func require(ok:bool,reason:String)->bool:
 if not ok:finish(reason)
 return ok
func sample()->Dictionary:
 var at:=car.to_local(player.global_position)
 var collisions:Array=[]
 for i in range(player.get_slide_collision_count()):
  var c:=player.get_slide_collision(i);var n=c.get_collider() as Node
  collisions.append({"owner":str(n.get_path()) if n!=null else "null","normal":c.get_normal(),"collider_velocity":c.get_collider_velocity()})
 return {"cursor":motor.cursor,"speed":motor.speed,"moving":motor.moving,"motion_fault":motor.motion_fault,"car_position":car.global_position,"car_yaw":car.global_rotation.y,"actor_world":player.global_position,"actor_local":at,"actor_velocity":player.velocity,"on_floor":player.is_on_floor(),"platform_velocity":player.get_platform_velocity(),"platform_angular_velocity":player.get_platform_angular_velocity(),"slides":collisions,"safety_phase":safety.phase,"restraint_phase":restraint.phase,"cart_position":cart.global_position,"cart_sleeping":cart.sleeping,"nodes":get_node_count()}
func observe(strict:bool)->String:
 elapsed_frames+=1
 var s:=sample();ring.append(s)
 if ring.size()>120:ring.pop_front()
 if elapsed_frames%60==0:emit("sample",s)
 if motor.motion_fault:return "original_motor_motion_fault"
 if restraint.motion_fault:return "original_restraint_motion_fault"
 if player.get_instance_id()!=actor_id or player.camera.get_instance_id()!=camera_id:return "player_or_camera_identity_changed"
 if player.get_parent()!=host.get_node("PersistentActors") or player.seated:return "unexpected_player_parent_or_seat"
 if cart.get_instance_id()!=cart_id or cart.freeze or cart.products.size()!=4:return "original_cart_identity_or_physics_changed"
 for i in range(4):
  if cart.products[i].get_instance_id()!=product_ids[i] or cart.products[i].freeze:return "original_stock_identity_or_physics_changed"
 if restraint.cart_in_vehicle() or restraint.phase!="unlocked" or is_instance_valid(restraint.joint):return "unladen_guard_changed"
 if is_instance_valid(player.held_interaction) or is_instance_valid(cart.driver):return "unexpected_held_interaction"
 var local:=car.to_local(player.global_position)
 if spawned and (local.y<-.02 or absf(local.x)>=1.0 or absf(local.z)>=2.22):return "player_left_original_actor_aboard_envelope"
 if strict:
  if not player.is_on_floor():return "player_lost_floor_after_settling"
  if not controls.actor_aboard(player):return "original_actor_aboard_rejected"
  var drift:=Vector2(local.x-settled_local.x,local.z-settled_local.z).length();maximum_drift=maxf(maximum_drift,drift)
  # .10m is one-third the standing capsule radius, not an expanded cabin envelope.
  if drift>.10:return "no_input_cabin_local_drift_exceeded_0_10m"
  var q:=PhysicsRayQueryParameters3D.create(player.global_position+Vector3.UP*.15,player.global_position-Vector3.UP*.12,player.collision_mask,[player.get_rid()])
  var hit:=player.get_world_3d().direct_space_state.intersect_ray(q)
  if hit.is_empty() or hit.collider!=car or hit.normal.y<.7:return "floor_support_not_original_car"
 return ""
func run()->void:
 var mapping:Array=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("ASTRAEA_CARRY_MAP")))
 var pack:=PCKPacker.new()
 if not require(pack.pck_start(OS.get_environment("ASTRAEA_CARRY_OVERLAY"))==OK,"overlay_start"):return
 for row in mapping:
  if not require(FileAccess.get_sha256(row.source)==row.sha256,"source_hash "+str(row.path)):return
  if not require(pack.add_file(row.path,row.source)==OK,"overlay_add"):return
 if not require(pack.flush()==OK,"overlay_flush"):return
 if not require(ProjectSettings.load_resource_pack(OS.get_environment("ASTRAEA_CARRY_BASE")),"retained_import_cache_mount"):return
 if not require(ProjectSettings.load_resource_pack(OS.get_environment("ASTRAEA_CARRY_OVERLAY")),"current_dependency_overlay_mount"):return
 emit("sources_mounted",{"count":mapping.size(),"renderer":RenderingServer.get_current_rendering_method()})
 host=Node3D.new();host.name="BoundedActualTram";root.add_child(host)
 load("res://tests/group4_exact_pit_successor_guard.gd").ensure()
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var selected:Array=[];var ids:=["D09_fore_route","D09_aft_route","D09_atrium_circulation","D09_salon5_initial_terrace","D13_residential_street_pilot"]
 for r in definition.regions:
  if r.id in ids:selected.append(r)
 if not require(selected.size()==5,"exact_support_region_set"):return
 var mat:=StandardMaterial3D.new()
 load("res://scripts/structural_floor_builder.gd").build_regions(host,mat,mat,selected)
 var actors:=Node3D.new();actors.name="PersistentActors";host.add_child(actors)
 player=load("res://scripts/group6_swimming_20261019/player.gd").new();player.position=player.spawn_position;actors.add_child(player);player.set_controls_enabled(false);player.set_process_unhandled_input(false)
 cart=load("res://scripts/cleaning_cart.gd").new();cart.name="CustodialCart";cart.position=Vector3(85.2,84.04,-37.3);actors.add_child(cart)
 var assembly:Node3D=load("res://scripts/group4_completion.gd").build(host,true,true)
 car=load("res://scripts/group4_boarding_safety.gd").create_candidate_vehicle(assembly,Vector3(0,56.1,-72));car.name="Group4OwnedTram_Source024"
 safety=load("res://scripts/group4_boarding_safety.gd").build(assembly,assembly,car,true)
 restraint=load("res://scripts/group4_cart_restraint.gd").build(assembly,car,safety,cart,true)
 car.set_meta("group4_initial_source_cursor",395.3525674298981)
 motor=load("res://scripts/group4_loaded_tram_actuator.gd").attach_loaded(assembly,car,safety,restraint,true)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";host.add_child(budget);budget.configure(host,player)
 controls=load("res://scripts/group4_tram_operating_controls.gd").build(assembly,car,safety,restraint,motor,player,budget,true)
 actor_id=player.get_instance_id();camera_id=player.camera.get_instance_id();cart_id=cart.get_instance_id()
 for product in cart.products:product_ids.append(product.get_instance_id())
 result["identities"]={"player":actor_id,"camera":camera_id,"car":car.get_instance_id(),"cart":cart_id,"stock":product_ids,"player_script":player.get_script().resource_path,"motor_script":motor.get_script().resource_path,"car_sync_to_physics":car.sync_to_physics,"floor_regions":ids}
 for i in range(120):await physics_frame
 if not require(player.is_on_floor() and cart.global_position.y>83.9 and not restraint.cart_in_vehicle() and restraint.loaded_clear_to_depart(),"predeparture_support_or_safety"):return
 emit("predeparture",sample())
 if not require(motor.request_stop("FORE_MIDSHIP"),"original_departure_request_rejected"):return
 var initial_cursor:float=motor.cursor
 for i in range(600):
  await physics_frame
  if motor.motion_fault:finish("motion_fault_before_spawn");return
  if absf(motor.cursor-initial_cursor)>.10 and motor.speed>.05:break
 if not require(motor.moving and motor.speed>.05 and absf(motor.cursor-initial_cursor)>.10,"actual_motion_not_established"):return
 var arrival:Vector3=car.to_global(spawn_local)
 var state:=host.get_world_3d().direct_space_state
 var ray:=PhysicsRayQueryParameters3D.create(arrival+Vector3.UP,arrival-Vector3.UP*2);ray.exclude=[player.get_rid()]
 var hit:=state.intersect_ray(ray)
 if not require(not hit.is_empty() and hit.collider==car and hit.normal.y>=.7 and absf(hit.position.y-(arrival.y-.1))<=.15,"checked_spawn_floor_failed"):return
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 var clearance:=PhysicsShapeQueryParameters3D.new();clearance.shape=capsule;clearance.transform.origin=arrival+Vector3.UP*.9;clearance.exclude=[player.get_rid()]
 var blockers:=state.intersect_shape(clearance)
 if not blockers.is_empty():
  var paths:Array=[]
  for b in blockers:paths.append(str(b.collider.get_path()))
  result["spawn_blockers"]=paths;finish("checked_spawn_capsule_blocked");return
 # The only checked in-car arrival. Same original standing floor/capsule criteria.
 # After this block no fixture code writes player position, velocity, parent or camera.
 player.release_parked_seat_for_verified_arrival();player.position=arrival;player.spawn_position=arrival;player.velocity=Vector3.ZERO;player.rotation.y=car.rotation.y
 spawned=true;result.spawn_writes=1;result["spawn"]=sample();emit("checked_moving_spawn",result.spawn)
 for i in range(12):
  await physics_frame
  var failure:=observe(false)
  if not failure.is_empty():finish(failure);return
 if not require(player.is_on_floor(),"player_did_not_settle_on_car_in_12_ticks"):return
 settled_local=car.to_local(player.global_position);result["settled_local"]=settled_local
 var ticks:=0
 while motor.moving and ticks<72000:
  await physics_frame;ticks+=1
  var failure:=observe(true)
  if not failure.is_empty():finish(failure);return
 if not require(not motor.moving and absf(motor.cursor-225.0)<.00001,"first_leg_timeout_or_station_error"):return
 for i in range(30):
  await physics_frame
  var failure:=observe(true)
  if not failure.is_empty():finish(failure);return
 result.completed_stops.append("FORE_MIDSHIP");emit("first_leg_passed",sample())
 # Extended continuity is separately opt-in after the first discriminating leg passes.
 if OS.get_environment("ASTRAEA_CARRY_EXTEND")!="1":finish();return
 for destination in ["FORWARD","FORE_MIDSHIP","CENTRAL","AFT_MIDSHIP","AFT","AFT_MIDSHIP","CENTRAL"]:
  if not require(motor.request_stop(destination),"continuity_request_rejected "+destination):return
  ticks=0
  while motor.moving and ticks<180000:
   await physics_frame;ticks+=1
   var failure:=observe(true)
   if not failure.is_empty():finish(failure);return
  if not require(not motor.moving,"continuity_leg_timeout "+destination):return
  for i in range(30):
   await physics_frame
   var failure:=observe(true)
   if not failure.is_empty():finish(failure);return
  result.completed_stops.append(destination);emit("stop_passed",sample())
 finish()
