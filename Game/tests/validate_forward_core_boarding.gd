extends SceneTree
var target_lift_name := "ForwardPublicLift"
var gate_z := -438.0
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
	var lift:Node3D=ship.find_child(target_lift_name,true,false)
	var local_products:Array[Vector3]=[]
	for product in cart.products:local_products.append(cart.to_local(product.global_position))
	cart.position=Vector3(-3.8,.04,gate_z)
	cart.rotation=Vector3(0,-PI/2,0)
	cart.linear_velocity=Vector3.ZERO
	cart.angular_velocity=Vector3.ZERO
	cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*local_products[i]
		cart.products[i].linear_velocity=Vector3.ZERO
		cart.products[i].angular_velocity=Vector3.ZERO
		cart.products[i].sleeping=false
	actor.position=Vector3(-5.42,.1,gate_z)
	actor.rotation.y=-PI/2
	actor.pitch=0
	actor.camera.rotation.x=0
	actor.velocity=Vector3.ZERO
	for frame in range(60):await physics_frame
	assert(actor.position.distance_to(Vector3(-5.42,0,gate_z))<.12,"Lower deck must remain playable with the default upper-deck respawn")
	cart.toggle_grab(actor)
	key(KEY_W,true)
	var boarded:=false
	for frame in range(450):
		await physics_frame
		if actor.position.x>=-1.58:
			boarded=true
			break
	key(KEY_W,false)
	assert(boarded,"Player pushing loaded cart stalled at actual lift threshold")
	for frame in range(90):await physics_frame
	assert(cart.global_position.x>-.4 and cart.global_position.x<.5,"Cart is physically inside cabin")
	cart.release_grab()
	key(KEY_W,true)
	for frame in range(90):
		await physics_frame
		if actor.position.x>=-1.05:break
	key(KEY_W,false)
	for frame in range(30):await physics_frame
	assert(not lift.cabin_gate.threshold_occupied(),"Player and cart clear the gate before travel")
	lift.request_floor(16)
	var arrived:=false
	for frame in range(5000):
		await physics_frame
		if lift.phase=="idle" and lift.current_floor==16:
			arrived=true
			break
	assert(arrived)
	assert(abs(cart.global_position.y-102.0)<.12)
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.8 and abs(p.x)<.4 and abs(p.z)<.6,"Four products retained after boarding and travel")
	# Pull the same loaded cart back over the upper threshold without teleporting.
	key(KEY_S,true)
	for frame in range(120):
		await physics_frame
		if actor.position.x<=cart.position.x-1.58:break
	key(KEY_S,false)
	cart.toggle_grab(actor)
	key(KEY_S,true)
	var exited:=false
	for frame in range(500):
		await physics_frame
		if actor.position.x<=-5.42:exited=true;break
	key(KEY_S,false)
	assert(exited,"Loaded cart could not leave the upper cabin")
	cart.release_grab()
	for frame in range(60):await physics_frame
	assert(cart.position.x<-2.9 and absf(cart.position.y-102.0)<.12)
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.8 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6)
	# Independent recovery fixture only after completing the physical boarding/travel/exit circuit.
	actor.position=Vector3(0,-8,-100);actor.velocity=Vector3.ZERO
	for frame in range(3):await physics_frame
	assert(actor.position.distance_to(actor.spawn_position)<.12,"Below-ship recovery must still return to the configured spawn")
	print(target_lift_name," BOARDING PASS: real player pushes four-product loaded cart intoD01 cabin, travels physically toD17, and pulls it out across the upper threshold. No transforms set during travel/exit; full-network freehand acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
