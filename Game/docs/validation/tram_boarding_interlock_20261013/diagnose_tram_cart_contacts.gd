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
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(40)
 var ship:Node3D=main.get_node("World360/Astraea");var base:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
 cart=ship.get_node("ShipSpace/PersistentActors/CustodialCart");vehicle=base.get_node("Group4OwnedTram_Source024");actor=ship.get_node("ShipSpace/PersistentActors/Player")
 var old_pose:Transform3D=cart.global_transform;var stock_poses:Array=[]
 for stock:RigidBody3D in cart.products:stock_poses.append(old_pose.affine_inverse()*stock.global_transform)
 cart.contact_monitor=true;cart.max_contacts_reported=32
 cart.global_transform=vehicle.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.025,.14));cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
 for i in range(cart.products.size()):
  var stock:RigidBody3D=cart.products[i];stock.global_transform=cart.global_transform*stock_poses[i];stock.linear_velocity=Vector3.ZERO;stock.angular_velocity=Vector3.ZERO;stock.sleeping=false
 var observations:Array=[];var excluded:Array[RID]=[cart.get_rid()]
 for stock:RigidBody3D in cart.products:excluded.append(stock.get_rid())
 for i in range(91):
  if i<=10 or i in [30,90]:
   var contacts:Array=[]
   for col:CollisionShape3D in cart.find_children("*","CollisionShape3D",false,false):
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=col.shape;q.transform=col.global_transform;q.exclude=excluded
    for hit in cart.get_world_3d().direct_space_state.intersect_shape(q,32):contacts.append({"cart_shape":str(col.name),"other":str(hit.collider.get_path()),"other_shape_index":hit.shape})
   var solver_contacts:Array=[]
   var state:PhysicsDirectBodyState3D=PhysicsServer3D.body_get_direct_state(cart.get_rid())
   if state!=null:
    for j in range(state.get_contact_count()):
     var other:Object=state.get_contact_collider_object(j)
     solver_contacts.append({"other":str(other.get_path())if other is Node else str(other),"cart_shape_index":state.get_contact_local_shape(j),"other_shape_index":state.get_contact_collider_shape(j),"normal":str(state.get_contact_local_normal(j)),"impulse":str(state.get_contact_impulse(j)),"other_velocity":str(state.get_contact_collider_velocity_at_position(j))})
   observations.append({"solver_contacts":solver_contacts,"frame":i,"cart_local":str(vehicle.global_transform.affine_inverse()*cart.global_transform),"velocity":str(cart.linear_velocity),"vehicle_linear_velocity":str(PhysicsServer3D.body_get_state(vehicle.get_rid(),PhysicsServer3D.BODY_STATE_LINEAR_VELOCITY)),"vehicle_angular_velocity":str(PhysicsServer3D.body_get_state(vehicle.get_rid(),PhysicsServer3D.BODY_STATE_ANGULAR_VELOCITY)),"contacts":contacts})
  await physics_frame
 var report:Dictionary={"status":"DIAGNOSTIC_ONLY","source_checkpoint":"925cf773","policy_successor":"84e41e2c47c6455744ddbd6ac137f502cb14a767caf52837d6bfb739864727de","initial_cursor_successor":"91e25665c9863543c0cda253e1a422c0f9fb1df1b251e19a82e9e573ea659d29","actor_relocated":false,"one_original_cart_and_four_products_initial_stance":true,"post_setup_transform_velocity_writes":0,"observations":observations}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/TRAM_CART_CONTACT_DIAGNOSTIC.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("TRAM_CART_CONTACT_DIAGNOSTIC_COMPLETE");quit(0)
