extends Node3D
# One physical constraint on the root-supplied original cart. No input, clones, snapping or actor reparenting.
const DATA:="res://data/architecture/GROUP4_LOADED_CART_SOURCE_CANDIDATE.json"
var vehicle:AnimatableBody3D
var safety:Node3D
var cart:RigidBody3D
var motor:Node3D
var joint:Generic6DOFJoint3D
var phase:="unlocked"
var motion_fault:=false
var maximum_cart_frame_error_m:=0.0
var locked_cart_frame:Transform3D
static func build(parent:Node3D,body:AnimatableBody3D,boarding:Node3D,original_cart:RigidBody3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
 if not p.active and not candidate_only:return null
 assert(original_cart.persistent_id==&"custodian_cart_001" and original_cart.mass==18 and original_cart.products.size()==4)
 assert(not original_cart.has_meta("group4_restraint_owner"),"Never constrain the same cart through competing owners")
 for path:String in p.original_runtime_pins:assert(FileAccess.get_sha256(path)==p.original_runtime_pins[path])
 var n:Node3D=load("res://scripts/group4_cart_restraint.gd").new();n.name="Group4OriginalCartRestraint";n.vehicle=body;n.safety=boarding;n.cart=original_cart;parent.add_child(n);original_cart.set_meta("group4_restraint_owner",n.get_instance_id());return n
func _ready()->void:process_physics_priority=-24
func stopped()->bool:return is_instance_valid(motor) and not motor.moving and absf(motor.speed)<.001
func cart_in_vehicle()->bool:
 var at:=vehicle.to_local(cart.global_position)
 return absf(at.x)<1.10 and absf(at.z)<2.25 and at.y>-.10 and at.y<.25
func aligned()->bool:
 var pose:Transform3D=vehicle.global_transform.affine_inverse()*cart.global_transform
 return pose.origin.distance_to(Vector3(0,0,.14))<.025 and pose.basis.get_rotation_quaternion().angle_to(Quaternion.IDENTITY)<.03
func request_lock()->bool:
 if not bool(get_meta("integration_joint_admitted",true)):return false
 if phase!="unlocked" or motion_fault or not stopped() or not safety.unloaded_clear_to_depart() or not aligned() or is_instance_valid(cart.driver):return false
 for stock:RigidBody3D in cart.products:
  if is_instance_valid(stock.driver):return false
 phase="closing_clamps";safety.source_clamp_target=true;return true
func attach_physical_joint()->void:
 assert(stopped() and aligned() and safety.clamp_fraction>.999 and not is_instance_valid(joint))
 joint=Generic6DOFJoint3D.new();joint.name="OriginalCartChassisRestraintJoint";add_child(joint);joint.global_position=cart.to_global(Vector3(0,.24,0));joint.global_basis=cart.global_basis
 joint.node_a=joint.get_path_to(vehicle);joint.node_b=joint.get_path_to(cart);joint.exclude_nodes_from_collision=false;joint.solver_priority=2
 for axis:String in ["x","y","z"]:
  joint.call("set_flag_"+axis,Generic6DOFJoint3D.FLAG_ENABLE_LINEAR_LIMIT,true);joint.call("set_flag_"+axis,Generic6DOFJoint3D.FLAG_ENABLE_ANGULAR_LIMIT,true)
  for parameter:int in [Generic6DOFJoint3D.PARAM_LINEAR_LOWER_LIMIT,Generic6DOFJoint3D.PARAM_LINEAR_UPPER_LIMIT,Generic6DOFJoint3D.PARAM_ANGULAR_LOWER_LIMIT,Generic6DOFJoint3D.PARAM_ANGULAR_UPPER_LIMIT]:joint.call("set_param_"+axis,parameter,0.0)
 locked_cart_frame=vehicle.global_transform.affine_inverse()*cart.global_transform;phase="locked"
func request_unlock()->bool:
 if phase!="locked" or not stopped() or not safety.unloaded_clear_to_depart():return false
 var at_station:=false
 for station:String in safety.station_gates:
  if safety._physical_dock_matches(station):at_station=true
 if not at_station:return false
 joint.queue_free();joint=null;phase="opening_clamps";safety.source_clamp_target=false;return true
func loaded_clear_to_depart()->bool:
 if motion_fault or not safety.unloaded_clear_to_depart():return false
 if not cart_in_vehicle():return phase=="unlocked" and not is_instance_valid(joint)
 return phase=="locked" and is_instance_valid(joint) and safety.clamp_fraction>.999 and not is_instance_valid(cart.driver)
func _physics_process(_delta:float)->void:
 if phase=="closing_clamps" and safety.clamp_fraction>.999:
  if not aligned() or is_instance_valid(cart.driver):motion_fault=true;return
  attach_physical_joint()
 elif phase=="opening_clamps" and safety.clamp_fraction<.001:phase="unlocked"
 if phase=="locked":
  if not is_instance_valid(joint):motion_fault=true;return
  var frame:Transform3D=vehicle.global_transform.affine_inverse()*cart.global_transform
  maximum_cart_frame_error_m=maxf(maximum_cart_frame_error_m,frame.origin.distance_to(locked_cart_frame.origin))
func _exit_tree()->void:
 if is_instance_valid(cart) and cart.get_meta("group4_restraint_owner",0)==get_instance_id():cart.remove_meta("group4_restraint_owner")
