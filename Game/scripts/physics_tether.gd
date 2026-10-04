extends RigidBody3D
# Bounded physical grab shared by carts and loose products; no transform snapping.
var driver:CharacterBody3D
var interaction_owner:Node
var grip_local:=Vector3.ZERO
var follow_camera:=false
var hold_distance:=.95
var hold_height:=1.06
var stiffness:=120.0
var damping:=35.0
var maximum_force:=200.0
var previous_target:=Vector3.ZERO
var target_initialized:=false
func toggle_grab(actor:CharacterBody3D) -> void:
	if is_instance_valid(driver):
		release_grab()
		return
	if actor.get("held_interaction")!=null:return
	driver=actor
	target_initialized=false
	driver.set("held_interaction",interaction_owner)
	sleeping=false
func release_grab() -> void:
	if is_instance_valid(driver) and driver.get("held_interaction")==interaction_owner:driver.set("held_interaction",null)
	driver=null
func _physics_process(delta:float) -> void:
	if not is_instance_valid(driver):return
	if not driver.get("gameplay_input_enabled"):
		release_grab()
		return
	var target:Vector3=driver.global_position+Vector3.UP*hold_height-driver.global_basis.z*hold_distance
	if follow_camera:
		var camera:=driver.get("camera") as Camera3D
		target=camera.global_position-camera.global_basis.z*hold_distance
	var point:Vector3=global_transform*grip_local
	if point.distance_to(target)>2.8:
		release_grab()
		return
	var offset:Vector3=point-global_position
	var velocity_at_grip:Vector3=linear_velocity+angular_velocity.cross(offset-global_basis*center_of_mass)
	# Damping is relative to moving hands, not a brake against world space.
	var target_velocity:Vector3=(target-previous_target)/maxf(delta,.001) if target_initialized else driver.velocity
	target_velocity=target_velocity.limit_length(8.0)
	previous_target=target
	target_initialized=true
	var force:Vector3=((target-point)*stiffness+(target_velocity-velocity_at_grip)*damping).limit_length(maximum_force)
	apply_force(force,offset)
func _exit_tree() -> void:release_grab()
