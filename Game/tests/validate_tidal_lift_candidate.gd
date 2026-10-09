extends "res://tests/validate_commons_lift.gd"
# Reuses original physical cart, gate and ordinary-input assertions.
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(120):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var lift:Node3D=load("res://scripts/tidal_lift_candidate.gd").build(ship)
	for frame in range(120):await physics_frame
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	assert(lift.phase=="idle" and lift.current_floor==0)
	# Load the fixture on a stationary cabin, then test entirely physical carry.
	var base:=lift.to_global(Vector3(lift.gate_origin_xz.x,lift.floor_heights[0],lift.gate_origin_xz.y))
	var offset:Vector3=base+lift.global_basis*Vector3(1.85,.04,0)-cart.global_position
	cart.global_position+=offset
	cart.linear_velocity=Vector3.ZERO
	cart.angular_velocity=Vector3.ZERO
	cart.sleeping=false
	for product in cart.products:
		product.global_position+=offset
		product.linear_velocity=Vector3.ZERO
		product.angular_velocity=Vector3.ZERO
		product.sleeping=false
	actor.spawn_position=base+lift.global_basis*Vector3(2.15,.1,1.25)
	actor.global_position=actor.spawn_position
	actor.velocity=Vector3.ZERO
	for frame in range(60):await physics_frame
	assert(not lift.request_floor(-1) and not lift.request_floor(lift.floor_heights.size()))
	await check_boarding(lift,ship)
	for destination in [1,2,3,4,0]:
		await select_floor_by_focus(lift,actor,destination)
		await wait_trip(lift,cart,actor,destination)
		await check_boarding(lift,ship)
		assert(abs(cart.global_position.y-lift.to_global(Vector3(lift.gate_origin_xz.x,lift.floor_heights[destination],lift.gate_origin_xz.y)).y)<.12)
	# Obstruction of the actual threshold must hold departure.
	var blocker:=RigidBody3D.new()
	blocker.gravity_scale=0
	blocker.position=base+lift.global_basis*Vector3(-.1,1,0)
	var contact:=CollisionShape3D.new()
	var shape:=SphereShape3D.new()
	shape.radius=.18
	contact.shape=shape
	blocker.add_child(contact)
	ship.get_node("ShipSpace/PersistentActors").add_child(blocker)
	for frame in range(5):await physics_frame
	lift.request_floor(1)
	for frame in range(100):await physics_frame
	assert(lift.phase=="closing" and abs(lift.cabin.position.y-lift.floor_heights[0])<.001)
	blocker.queue_free()
	lift.request_floor(0)
	for frame in range(100):await physics_frame
	assert(lift.phase=="idle")
	print("TIDAL_CANDIDATE"+" LIFT PASS: physical capsule/cart/four loose bottles carried both directions, bounded acceleration, closed travel gates, obstruction holds departure and same-floor cancellation reopens. Precise RMB/E for every trip destination and unfocused rejection pass. Boarding turns, save and visual acceptance pending.")
	main.queue_free()
	await process_frame
	quit()

func check_boarding(lift: Node3D, ship: Node3D) -> void:
	var excluded: Array[RID] = []
	for actor in ship.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var physics := ship.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	var y: float = lift.floor_heights[lift.current_floor]
	for lane in [-.65,0.0,.65]:
		for step in range(21):
			var p := lift.to_global(Vector3(-2.4+step*.2,y,lane))
			var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.30)
			ray.exclude = excluded
			var support := physics.intersect_ray(ray)
			assert(not support.is_empty(),"Tidal boarding support missing: "+str(p))
			assert(absf(support.position.y-p.y)<.035,"Tidal boarding support step: "+str(p))
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape=capsule
			query.exclude=excluded
			query.transform.origin=p+Vector3.UP*.925
			var hits := physics.intersect_shape(query,32)
			assert(hits.is_empty(),"Tidal boarding blocked: "+str(p)+" "+str(hits))
	print("TIDAL_BOARDING_PASS deck=",lift.deck_numbers[lift.current_floor]," samples=63")
