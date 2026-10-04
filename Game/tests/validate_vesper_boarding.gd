extends SceneTree
func _initialize() -> void:call_deferred("run")
func key(code:Key,pressed:bool) -> void:
	var event:=InputEventKey.new()
	event.keycode=code
	event.physical_keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var lift:Node3D=ship.find_child("VesperDiningLift",true,false)
	var local_products:Array[Vector3]=[]
	for product in cart.products:local_products.append(cart.to_local(product.global_position))
	cart.position=Vector3(18.5,61.04,192)
	cart.rotation=Vector3(0,-PI/2,0)
	cart.linear_velocity=Vector3.ZERO
	cart.angular_velocity=Vector3.ZERO
	cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*local_products[i]
		cart.products[i].linear_velocity=Vector3.ZERO
		cart.products[i].angular_velocity=Vector3.ZERO
		cart.products[i].sleeping=false
	actor.position=Vector3(16.88,61.1,192)
	actor.rotation.y=-PI/2
	actor.pitch=0
	actor.camera.rotation.x=0
	actor.velocity=Vector3.ZERO
	for frame in range(60):await physics_frame
	cart.toggle_grab(actor)
	key(KEY_W,true)
	var boarded:=false
	for frame in range(450):
		await physics_frame
		if actor.position.x>=20.72:
			boarded=true
			break
	key(KEY_W,false)
	assert(boarded,"Player pushing loaded cart stalled at actual lift threshold")
	for frame in range(90):await physics_frame
	assert(cart.global_position.x>21.9 and cart.global_position.x<22.8,"Cart is physically inside cabin")
	cart.release_grab()
	key(KEY_W,true)
	for frame in range(90):
		await physics_frame
		if actor.position.x>=21.25:break
	key(KEY_W,false)
	for frame in range(30):await physics_frame
	assert(not lift.cabin_gate.threshold_occupied(),"Player and cart clear the gate before travel")
	lift.request_floor(1)
	var arrived:=false
	for frame in range(800):
		await physics_frame
		if lift.phase=="idle" and lift.current_floor==1:
			arrived=true
			break
	assert(arrived)
	assert(abs(cart.global_position.y-64.5)<.12)
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.8 and abs(p.x)<.4 and abs(p.z)<.6,"Four products retained after boarding and travel")
	print("VESPER LIFT BOARDING PASS: actual player pushes loaded cart across both gate planes andfitted threshold, releases and clears threshold, then reaches the D10 upper dining level with four loose products. Full turning, exit and tram acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
