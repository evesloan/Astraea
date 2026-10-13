extends "res://tests/validate_d04_port_forward_commons_service.gd"
var mechanical_checks:=0
var samples:=0
var max_frame_error:=0.0
var max_step:=0.0
var steps:Array=[]
var actor:CharacterBody3D
var cart:RigidBody3D
var vehicle:AnimatableBody3D
var motor:Node3D
var safety:Node3D
var restraint:Node3D
var operating:Node3D
var last_cart:=Vector3.ZERO
var products:Array=[]
var cart_initial_stances:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/TRAM_BOARDING_JOINT_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func save_result(status:String)->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":status,"checks":mechanical_checks,"steps":steps,"joint_physics_samples":samples,"maximum_cart_frame_error_m":max_frame_error,"maximum_cart_step_m":max_step,"cart_product_initial_test_stances":cart_initial_stances,"post_initial_cart_product_transform_velocity_writes":0,"stock_ids_and_original_nodes_preserved":products.size()==4,"existing_actor_movement_source_unchanged":true,"whole_loaded_journey_or_save_acceptance":false},"  "))
func require(ok:bool,label:String)->bool:
 mechanical_checks+=1
 if not ok:
  steps.append({"failed":label,"actor":str(actor.global_position)if actor!=null else "none","cart":str(cart.global_position)if cart!=null else "none"});save_result("HOLD");push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func event_key(code:int,on:bool)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=on;Input.parse_input_event(e)
func mouse(on:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=on;Input.parse_input_event(e)
func press(button:Node3D,label:String)->bool:
 actor.camera.look_at(button.global_position,Vector3.UP);mouse(true);await frames(3)
 var target:Node=actor.target_from_view()
 if not require(target==button,label+" exact original RMB target; actual="+str(target.get_path()if target!=null else "none")):return false
 event_key(KEY_E,true);await frames(3);event_key(KEY_E,false);mouse(false);steps.append({"ordinary_RMB_E":label});return true
func wait_phase(target:String,budget:int=400)->bool:
 for i in range(budget):
  if safety.phase==target:return true
  await physics_frame
 return require(false,"Mechanical phase timeout "+target+" actual="+safety.phase)
func continuity()->bool:
 samples+=1
 var frame:Transform3D=vehicle.global_transform.affine_inverse()*cart.global_transform
 var error:float=frame.origin.distance_to(restraint.locked_cart_frame.origin)
 max_frame_error=maxf(max_frame_error,error);max_step=maxf(max_step,cart.global_position.distance_to(last_cart));last_cart=cart.global_position
 if not require(error<.025 and not restraint.motion_fault and not motor.motion_fault and is_instance_valid(restraint.joint),"Original joint frame continuity"):return false
 for i in range(products.size()):
  var item:Dictionary=products[i];var stock:RigidBody3D=item.node;var at:Vector3=cart.to_local(stock.global_position)
  if not require(is_instance_valid(stock)and stock.persistent_id==item.id and stock.get_parent()==item.parent and at.y>.78 and at.y<1.35 and absf(at.x)<.43 and absf(at.z)<.62,"Original loose product retained "+str(i)):return false
 return require(cart.global_basis.y.dot(Vector3.UP)>.97 and cart.global_position.is_finite()and cart.linear_velocity.length()<6,"Upright bounded original cart")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var base:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
 actor=ship.get_node("ShipSpace/PersistentActors/Player");cart=ship.get_node("ShipSpace/PersistentActors/CustodialCart");vehicle=base.get_node("Group4OwnedTram_Source024");motor=base.get_node("Group4LoadedSourceTravelActuator");safety=base.get_node("Group4BoardingSafety");restraint=base.get_node("Group4OriginalCartRestraint");operating=base.get_node("Group4SourceOperatingControls")
 var gate:Node3D=safety.station_gates.CENTRAL;var bridge:Node3D=safety.bridges.CENTRAL
 if not require(safety.unloaded_clear_to_depart()and not safety.request_boarding("AFT"),"Exact stationary Central dock only"):return
 # Single supported actor start; all following boarding positions use original walking.
 actor.global_position=gate.to_global(Vector3(-1.55,0,-1.10));actor.global_position.y=56.13;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);await frames(30)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-56.1)<.12,"Supported Central call stance"):return
 if not await press(operating.controls["STATION_CALL:CENTRAL"],"Central station call"):return
 await frames(40)
 if not require(gate.open_fraction<.0001 and bridge.fraction<.999 and not motor.request_distance(motor.cursor+1),"Barrier closed while bridge deploys; departure denied"):return
 if not await wait_phase("boarding"):return
 await frames(140)
 if not require(gate.open_fraction>.999 and bridge.fraction>.999 and safety.car_gates.PORT.open_fraction>.999,"Actual bridge before both Central portals open"):return
 var leg:Dictionary=await walk_to(actor,gate.to_global(Vector3(0,0,0)))
 if not require(leg.reached and leg.floor_contact and gate.threshold_occupied(),"Original actor reaches supported occupied threshold"):return
 if not require(safety.request_secure(),"Secure request with occupied threshold"):return
 await frames(80)
 if not require(gate.open_fraction>.999 and bridge.fraction>.999 and not safety.unloaded_clear_to_depart(),"Occupied original actor prevents close and departure"):return
 steps.append({"occupied_stance":str(actor.global_position),"gate_pose":str(gate.global_position),"bridge_pose":str(bridge.global_position),"vehicle_pose":str(vehicle.global_position)})
 leg=await walk_to(actor,vehicle.to_global(Vector3(-.65,0,0)))
 steps.append({"centre_crossing":leg,"phase":safety.phase,"gate_fraction":gate.open_fraction,"bridge_fraction":bridge.fraction})
 if not require(leg.reached and leg.floor_contact,"Original actor crosses portal centre into car"):return
 # Authored fixed pods occupy X[-.8,-.49] and[.49,.8]; the clear source aisle is centred.
 leg=await walk_to(actor,vehicle.to_global(Vector3(0,0,0)))
 steps.append({"source_centre_aisle_entry":leg})
 if not require(leg.reached and leg.floor_contact,"Source centre aisle entry"):return
 leg=await walk_to(actor,vehicle.to_global(Vector3(0,0,-1.3)))
 steps.append({"console_approach":leg})
 if not require(leg.reached and leg.floor_contact,"Supported longitudinal console approach"):return

 if not await wait_phase("secured"):return
 if not require(gate.open_fraction<.0001 and bridge.fraction<.0001 and safety.unloaded_clear_to_depart(),"Closed portals precede stowed bridge and departure clearance"):return
 # One original cart/load initial test stance. Never write transforms/velocities after this setup.
 var local_load:Array=[]
 for stock:RigidBody3D in cart.products:local_load.append(cart.global_transform.affine_inverse()*stock.global_transform);products.append({"node":stock,"id":stock.persistent_id,"parent":stock.get_parent()})
 cart_initial_stances=1
 cart.global_transform=vehicle.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.04,.14));cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
 for i in range(products.size()):
  var stock:RigidBody3D=products[i].node;stock.global_transform=cart.global_transform*local_load[i];stock.linear_velocity=Vector3.ZERO;stock.angular_velocity=Vector3.ZERO;stock.sleeping=false
 await frames(120)
 if not require(restraint.aligned()and cart.mass==18 and cart.products.size()==4 and cart.persistent_id==&"custodian_cart_001","Original18kg loaded cart settles on source restraint datum"):return
 if not await press(operating.controls["CLAMP:"],"Original cart clamp"):return
 for i in range(140):
  await physics_frame
  if restraint.phase=="locked":break
 if not require(restraint.phase=="locked"and restraint.loaded_clear_to_depart(),"Actual original cart joint installed after four clamp strokes"):return
 last_cart=cart.global_position
 for i in range(60):await physics_frame;if not continuity():return
 var start:float=motor.cursor
 if not require(motor.request_distance(start+1),"Bounded one-metre original loaded successor motion"):return
 for i in range(600):
  await physics_frame
  if not continuity():return
  if not motor.moving:break
 if not require(not motor.moving and absf(motor.cursor-start-1)<.00001 and not restraint.request_unlock(),"Stopped away from dock refuses loaded release"):return
 if not require(motor.request_stop("CENTRAL"),"Original source return to exact Central dock"):return
 for i in range(600):
  await physics_frame
  if not continuity():return
  if not motor.moving:break
 await frames(20)
 if not require(not motor.moving and safety._physical_dock_matches("CENTRAL"),"Physical Central return"):return
 if not await press(operating.controls["CLAMP:"],"Original cart release"):return
 await frames(140)
 if not require(restraint.phase=="unlocked"and not is_instance_valid(restraint.joint)and safety.clamp_fraction<.001,"Original physical joint released and all clamps caster-clear"):return
 if not require(cart.get_meta("group4_restraint_owner")==restraint.get_instance_id()and cart.interaction_owner.get_script()==load("res://scripts/group4_cart_handle_guard.gd"),"Original handle remains sole scoped owner"):return
 save_result("PASS_CENTRAL_BOARDING_AND_BOUNDED_ORIGINAL_CART_JOINT");print("TRAM_BOARDING_JOINT_PASS checks=",mechanical_checks," samples=",samples);quit(0)
