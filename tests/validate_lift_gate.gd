extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var gate:Node3D=load("res://scripts/lift_gate.gd").new()
	gate.name="CommonsGateComponentUnderTest"
	gate.position=Vector3(92.10,84,0)
	gate.rotation.y=PI/2
	ship.get_node("ShipSpace").add_child(gate)
	for frame in range(5):await physics_frame
	assert(gate.leaves.size()==4)
	assert(not gate.has_method("interact"),"Landing gate must not bypass the cabin controller")
	assert(not gate.request_open(),"Absent cabin cannot open a landing gate")
	assert(gate.is_closed_and_clear())
	gate.cabin_present_and_stopped=true
	assert(gate.request_open())
	await sweep(gate,ship)
	assert(gate.open_fraction>.999)
	var obstacle:=RigidBody3D.new()
	obstacle.gravity_scale=0
	obstacle.position=Vector3(92.10,85,0)
	var contact:=CollisionShape3D.new()
	var shape:=SphereShape3D.new()
	shape.radius=.2
	contact.shape=shape
	obstacle.add_child(contact)
	ship.get_node("ShipSpace/PersistentActors").add_child(obstacle)
	for frame in range(5):await physics_frame
	gate.request_close()
	for frame in range(10):await physics_frame
	assert(gate.obstructed and gate.open_fraction>.999,"A loose object inhibits closing")
	assert(not gate.is_closed_and_clear())
	obstacle.queue_free()
	for frame in range(5):await physics_frame
	await sweep(gate,ship)
	assert(gate.is_closed_and_clear())
	gate.cabin_present_and_stopped=false
	assert(not gate.request_open())
	print("LIFT GATE PASS: four leaves,360 fixed-geometry sweep samples, absent-cabin interlock, no direct interaction bypass, rigid-prop obstruction. Landing/cabin integration and loaded transport still pending.")
	main.queue_free()
	await process_frame
	quit()
func sweep(gate:Node3D,ship:Node3D) -> void:
	for frame in range(180):
		await physics_frame
		for leaf in gate.leaves:
			for contact in leaf.get_children():
				if not contact is CollisionShape3D:continue
				var query:=PhysicsShapeQueryParameters3D.new()
				query.shape=contact.shape
				query.transform=contact.global_transform
				query.exclude=[leaf.get_rid()]
				query.margin=.001
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(query,64):
					assert(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Gate leaf clips fixed pocket geometry")
