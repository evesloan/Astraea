extends "res://scripts/player.gd"
# Additive Group6 player specialization; the protected base controller remains exact.
var body_collider:CollisionShape3D
var parked_seat:Area3D
var seated:=false
var seat_exit_position:=Vector3.ZERO
var water_field:RefCounted
var water_state:="dry"
var water_depth_m:=0.0
var head_under_water:=false


func _ready()->void:
	super._ready()
	for child in get_children():
		if child is CollisionShape3D:body_collider=child;break
	assert(body_collider!=null)
	water_field=load("res://scripts/group6_completion/river_water_field.gd").new()

func _physics_process(delta:float)->void:
	if seated:
		velocity=Vector3.ZERO;jump_requested=false
		if not is_instance_valid(parked_seat) or not parked_seat.is_inside_tree():try_leave_parked_seat()
		else:global_position=parked_seat.seat_world_position()
		update_water_state();update_interaction(delta)
		return
	super._physics_process(delta)
	update_water_state()

func update_interaction(delta:float)->void:
	var focus:Node=parked_seat if seated and is_instance_valid(parked_seat) else held_interaction
	interaction_target = (focus if is_instance_valid(focus) else target_from_view()) if gameplay_input_enabled and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else null
	if interaction_requested:
		if gameplay_input_enabled and is_instance_valid(interaction_target):interaction_target.interact(self)
		interaction_requested=false
	camera.fov=lerpf(camera.fov,58.0 if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else 72.0,1.0-exp(-delta*10.0))

func update_water_state()->void:
	# Only the pinned river has a sampled volume. Thermal visual water is not
	# silently promoted to a gameplay volume. This adds state, not swim forces.
	var sample:Dictionary=water_field.sample(global_position)
	water_depth_m=float(sample.get("depth_m",0.0)) if sample.get("wet",false) else 0.0
	head_under_water=water_depth_m>camera.position.y
	water_state="submerged" if head_under_water else ("wading" if water_depth_m>0.0 else "dry")

func body_space_clear(at:Vector3,height:float)->bool:
	var capsule:=CapsuleShape3D.new();capsule.radius=.22 if height<1.8 else .3;capsule.height=height
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule
	query.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*height*.5)
	query.collision_mask=collision_mask;query.exclude=[get_rid()];query.margin=.005
	return get_world_3d().direct_space_state.intersect_shape(query,1).is_empty()

func passage_clear(from:Vector3,to:Vector3)->bool:
	var capsule:=CapsuleShape3D.new();capsule.radius=.22;capsule.height=1.2
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule
	query.transform=Transform3D(Basis.IDENTITY,from+Vector3.UP*.6)
	query.motion=to-from;query.exclude=[get_rid()];query.collision_mask=collision_mask;query.margin=.005
	var fractions:=get_world_3d().direct_space_state.cast_motion(query)
	return fractions[0]>=.9999

func try_mount_parked_seat(seat:Area3D)->bool:
	if not gameplay_input_enabled or seated or is_instance_valid(held_interaction) or not seat.is_inside_tree():return false
	if is_instance_valid(seat.occupant):return false
	var target:Vector3=seat.seat_world_position()
	if global_position.distance_to(target)>2.5 or not body_space_clear(target,1.2):return false
	if not seat.transfer_clear(self,global_position):return false
	seat_exit_position=seat.exit_world_position()
	parked_seat=seat;seat.occupant=self;seated=true
	(body_collider.shape as CapsuleShape3D).radius=.22
	(body_collider.shape as CapsuleShape3D).height=1.2;body_collider.position.y=.6
	camera.position.y=1.05;global_position=target;velocity=Vector3.ZERO
	jump_requested=false
	update_water_state()
	return true

func try_leave_parked_seat()->bool:
	if not seated:return false
	var destination:Vector3=parked_seat.exit_world_position() if is_instance_valid(parked_seat) and parked_seat.is_inside_tree() else seat_exit_position
	if not body_space_clear(destination,1.8):return false
	if is_instance_valid(parked_seat) and parked_seat.is_inside_tree():
		if not parked_seat.transfer_clear(self,destination):return false
	elif not passage_clear(global_position,destination):return false
	var ground:=PhysicsRayQueryParameters3D.create(destination+Vector3.UP*.05,destination-Vector3.UP*.15,collision_mask,[get_rid()])
	if get_world_3d().direct_space_state.intersect_ray(ground).is_empty():return false
	release_parked_seat_for_verified_arrival()
	global_position=destination;velocity=Vector3.ZERO;update_water_state()
	return true

func release_parked_seat_for_verified_arrival()->void:
	# Ship arrive_at has already checked a standing capsule and supporting floor.
	if is_instance_valid(parked_seat):parked_seat.occupant=null
	parked_seat=null;seated=false
	(body_collider.shape as CapsuleShape3D).radius=.3
	(body_collider.shape as CapsuleShape3D).height=1.8;body_collider.position.y=.9
	camera.position.y=1.65
