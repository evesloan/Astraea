extends "res://scripts/physics_tether.gd"
@export var persistent_id:StringName=&"custodian_cart_001"
var visual_wheels:Array[Node3D]=[]
var products:Array[RigidBody3D]=[]
# Approximate a two-handed handle grip as a spring/damper yaw couple in Nm.
var handle_yaw_stiffness:=60.0
var handle_yaw_damping:=14.0
var maximum_handle_torque:=55.0
func _ready() -> void:
	set_meta("catalogue_file","AST-HSK-005.glb")
	var visual:Node3D=(load("res://assets/models/AST-HSK-005.glb")as PackedScene).instantiate()
	add_child(visual)
	mass=18
	continuous_cd=true
	center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
	center_of_mass=Vector3(0,.36,0)
	linear_damp=.12
	angular_damp=.9
	physics_material_override=PhysicsMaterial.new()
	physics_material_override.friction=.12
	physics_material_override.bounce=.02
	var contacts:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	for item in contacts.boxes:
		var collider:=CollisionShape3D.new()
		collider.name=item.name
		var shape:=BoxShape3D.new()
		shape.size=Vector3(item.size[0],item.size[1],item.size[2])
		shape.margin=.001
		collider.shape=shape
		collider.position=Vector3(item.center[0],item.center[1],item.center[2])
		add_child(collider)
	for item in contacts.wheel_contacts:
		var collider:=CollisionShape3D.new()
		var shape:=SphereShape3D.new()
		shape.radius=item.radius
		collider.shape=shape
		collider.position=Vector3(item.center[0],item.center[1],item.center[2])
		add_child(collider)
	for i in range(4):visual_wheels.append(visual.find_child("WHEEL_ROLL_"+str(i),true,false)as Node3D)
	grip_local=Vector3(0,1.08,.67)
	var handle:Node3D=(load("res://scripts/cart_handle.gd")as GDScript).new()
	handle.name="PhysicalCartHandle"
	handle.cart=self
	handle.position=grip_local
	add_child(handle)
	interaction_owner=handle
	var target:=Area3D.new()
	target.collision_layer=2
	target.collision_mask=0
	target.monitoring=false
	handle.add_child(target)
	var target_shape:=CollisionShape3D.new()
	var target_box:=BoxShape3D.new()
	target_box.size=Vector3(.76,.16,.16)
	target_shape.shape=target_box
	target.add_child(target_shape)
	for i in range(4):
		var product:RigidBody3D=(load("res://scripts/cleaning_bottle.gd")as GDScript).new()
		product.name="CartCleanerBottle_"+str(i)
		product.persistent_id=StringName("cart_001_product_%02d"%i)
		product.position=global_transform*Vector3(-.16+.32*(i%2),.96,-.20+.4*(i/2))
		get_parent().call_deferred("add_child",product)
		products.append(product)
func _physics_process(delta:float) -> void:
	if sleeping and not is_instance_valid(driver):return
	super._physics_process(delta)
	var query:=PhysicsRayQueryParameters3D.create(global_position+Vector3.UP*.2,global_position-Vector3.UP*.12)
	query.exclude=[get_rid()]
	if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():
		# Two hands on the wide handle can apply a bounded yaw couple.
		# A single rear-point force otherwise pivots the nose away from a turn.
		# This remains physical torque: no orientation snapping or pitch/roll lock.
		if is_instance_valid(driver):
			var forward:Vector3=-global_basis.z
			var desired:Vector3=-driver.global_basis.z
			forward.y=0
			desired.y=0
			var error:float=forward.normalized().signed_angle_to(desired.normalized(),Vector3.UP)
			apply_torque(Vector3.UP*clampf(error*handle_yaw_stiffness-angular_velocity.y*handle_yaw_damping,-maximum_handle_torque,maximum_handle_torque))
		# Simplified caster resistance. Full body rotation and loose contents stay physical.
		var lateral:Vector3=global_basis.x*linear_velocity.dot(global_basis.x)
		if lateral.length_squared()>.0001:apply_central_force(-lateral*mass*2.0)
	var speed:float=linear_velocity.dot(-global_basis.z)
	for wheel in visual_wheels:
		if is_instance_valid(wheel):wheel.rotate_x(speed*delta/.09)
