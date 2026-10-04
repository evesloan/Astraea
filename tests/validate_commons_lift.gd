extends SceneTree
var target_lift_name:="CommonsPassengerLift"
func _initialize() -> void:call_deferred("run")
func wait_trip(lift:Node3D,cart:RigidBody3D,actor:CharacterBody3D,goal:int) -> void:
	var reached:=false
	var previous:=0.0
	for frame in range(800):
		await physics_frame
		assert(abs(lift.travel_velocity)<=lift.maximum_speed+.001)
		if lift.phase=="moving":
			assert(lift.cabin_gate.open_fraction<.001,"Cabin gate stays closed during travel")
			for gate in lift.landing_gates:assert(gate.open_fraction<.001,"All shaft gates stay closed during travel")
			assert(abs(lift.travel_velocity-previous)<.025,"Acceleration is bounded")
		# Detect fitted-frame/roof intersections independently of carried-body tests.
		# Kinematic platforms can otherwise move through static geometry unnoticed.
		for contact in lift.cabin.get_children():
			if not contact is CollisionShape3D:continue
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=contact.shape
			query.transform=contact.global_transform
			query.exclude=[lift.cabin.get_rid()]
			query.margin=.0001
			for hit in lift.get_world_3d().direct_space_state.intersect_shape(query,64):
				if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:
					assert(false,"Moving cabin clips static structure at cabin Y%.4f: %s / %s"%[lift.cabin.position.y,contact.name,hit.collider.get_path()])
		previous=lift.travel_velocity
		assert(cart.get_parent().name=="PersistentActors","Cart is not parented to moving lift")
		assert(abs(cart.global_position.y-lift.cabin.global_position.y)<.16,"Loose physical cart stays on moving platform: cart=%s cabin=%s phase=%s velocity=%s"%[cart.global_position,lift.cabin.global_position,lift.phase,lift.travel_velocity])
		assert(abs(actor.global_position.y-lift.cabin.global_position.y)<.18,"Character follows platform")
		for product in cart.products:
			assert(product.get_parent()==cart.get_parent())
			var p:Vector3=cart.to_local(product.global_position)
			assert(p.y>.80 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6,"Loose load retained during trip")
		if lift.current_floor==goal and lift.phase=="idle":
			reached=true
			break
	assert(reached,"Lift failed to reach requested floor")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(120):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var lift:Node3D=ship.find_child(target_lift_name,true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	assert(lift.phase=="idle" and lift.current_floor==0)
	# Load the fixture on a stationary cabin, then test entirely physical carry.
	var base:=Vector3(lift.gate_origin_xz.x,lift.floor_heights[0],lift.gate_origin_xz.y)
	var offset:Vector3=base+Vector3(1.85,.04,0)-cart.global_position
	cart.global_position+=offset
	cart.linear_velocity=Vector3.ZERO
	cart.angular_velocity=Vector3.ZERO
	cart.sleeping=false
	for product in cart.products:
		product.global_position+=offset
		product.linear_velocity=Vector3.ZERO
		product.angular_velocity=Vector3.ZERO
		product.sleeping=false
	actor.spawn_position=base+Vector3(2.15,.1,1.25)
	actor.global_position=actor.spawn_position
	actor.velocity=Vector3.ZERO
	for frame in range(60):await physics_frame
	assert(not lift.request_floor(-1) and not lift.request_floor(2))
	var button:Node3D=lift.find_child(lift.identity_prefix+"_cabin_D"+str(lift.deck_numbers[1]),true,false)
	var aim:Vector3=button.global_position-actor.camera.global_position
	actor.rotation.y=atan2(-aim.x,-aim.z)
	actor.pitch=atan2(aim.y,Vector2(aim.x,aim.z).length())
	actor.camera.rotation.x=actor.pitch
	assert(actor.target_from_view()==button,"Each cabin floor button must be precisely selectable")
	var key:=InputEventKey.new()
	key.keycode=KEY_E
	key.physical_keycode=KEY_E
	key.pressed=true
	Input.parse_input_event(key.duplicate())
	Input.flush_buffered_events()
	for frame in range(3):await physics_frame
	assert(lift.phase=="idle","Unfocused E cannot select a floor")
	key.pressed=false
	Input.parse_input_event(key.duplicate())
	var focus:=InputEventMouseButton.new()
	focus.button_index=MOUSE_BUTTON_RIGHT
	focus.pressed=true
	Input.parse_input_event(focus.duplicate())
	key.pressed=true
	Input.parse_input_event(key.duplicate())
	Input.flush_buffered_events()
	for frame in range(3):await physics_frame
	assert(lift.destination_floor==1 and lift.phase=="closing","Focused E selects the actual upper button")
	key.pressed=false
	Input.parse_input_event(key.duplicate())
	focus.pressed=false
	Input.parse_input_event(focus.duplicate())
	Input.flush_buffered_events()
	await wait_trip(lift,cart,actor,1)
	assert(abs(cart.global_position.y-lift.floor_heights[1])<.12)
	assert(lift.request_floor(0))
	await wait_trip(lift,cart,actor,0)
	# Obstruction of the actual threshold must hold departure.
	var blocker:=RigidBody3D.new()
	blocker.gravity_scale=0
	blocker.position=base+Vector3(-.1,1,0)
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
	print(target_lift_name+" LIFT PASS: physical capsule/cart/four loose bottles carried both directions, bounded acceleration, closed travel gates, obstruction holds departure and same-floor cancellation reopens. Precise RMB/E cabin button and unfocused rejection pass. Boarding turns, save and visual acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
