extends SceneTree
func _initialize() -> void:call_deferred("run")
func send_key(code:Key,pressed:bool) -> void:
	var event:=InputEventKey.new()
	event.keycode=code
	event.physical_keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)
func focus(pressed:bool) -> void:
	var event:=InputEventMouseButton.new()
	event.button_index=MOUSE_BUTTON_RIGHT
	event.pressed=pressed
	Input.parse_input_event(event)
func aim(actor:CharacterBody3D,point:Vector3) -> void:
	var delta:Vector3=point-actor.camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.camera.rotation.x=actor.pitch
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(180):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:=ship.find_child("CustodialCart",true,false)as RigidBody3D
	assert(cart!=null and cart.products.size()==4)
	assert(absf(cart.global_position.y-84)<.08 and cart.global_basis.y.dot(Vector3.UP)>.97,"Cart settles upright on actual floor")
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.89 and p.y<1.1 and absf(p.x)<.33 and absf(p.z)<.50,"Four loose products settle inside the upper tray: %s"%str(p))
	assert(ship.arrive_at(Vector3(85.2,84.1,-34.9),0))
	for frame in range(15):await physics_frame
	aim(actor,cart.global_transform*cart.grip_local)
	assert(actor.target_from_view()==cart.interaction_owner,"The real handle is precisely selectable")
	send_key(KEY_E,true)
	for frame in range(3):await physics_frame
	send_key(KEY_E,false)
	assert(cart.driver==null,"Unfocused E cannot grab")
	focus(true)
	send_key(KEY_E,true)
	for frame in range(120):await physics_frame
	send_key(KEY_E,false)
	assert(cart.driver==actor and actor.held_interaction==cart.interaction_owner,"Shared RMB/E takes the physical handle")
	focus(false)
	var start:Vector3=cart.global_position
	send_key(KEY_W,true)
	for frame in range(180):
		await physics_frame
		assert(cart.global_position.is_finite() and cart.linear_velocity.length()<8,"Bounded tether remains finite")
		assert(cart.global_basis.y.dot(Vector3.UP)>.80,"Normal straight pushing keeps cart upright")
	send_key(KEY_W,false)
	for frame in range(60):await physics_frame
	assert(start.z-cart.global_position.z>3.5,"Actual loaded cart advances under physics while player walks")
	assert(actor.held_interaction==cart.interaction_owner)
	var retained:=0
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		if p.y>.85 and absf(p.x)<.4 and absf(p.z)<.58:retained+=1
	print("CART PRODUCTS RETAINED:",retained," position:",cart.global_position)
	assert(retained==4,"Normal straight travel retains loose load")
	focus(true)
	send_key(KEY_E,true)
	for frame in range(5):await physics_frame
	send_key(KEY_E,false)
	assert(cart.driver==null and actor.held_interaction==null,"Focused E releases the handle")
	var bottle:RigidBody3D
	for candidate in cart.products:
		aim(actor,candidate.global_transform*Vector3(0,.125,0))
		if actor.target_from_view()==candidate:
			bottle=candidate
			break
	assert(bottle!=null,"An exposed loose product is individually selectable; occluded bottles remain blocked")
	send_key(KEY_E,true)
	for frame in range(2):await physics_frame
	actor.pitch=0
	actor.camera.rotation.x=0
	for frame in range(90):await physics_frame
	send_key(KEY_E,false)
	assert(bottle.driver==actor and actor.held_interaction==bottle,"Same focus/E convention picks up the loose product")
	assert(bottle.global_position.distance_to(actor.camera.global_position)<1.8)
	assert(bottle.global_position.y>cart.global_position.y+1.2,"Raising the view lifts the loose bottle clear of the tray")
	send_key(KEY_E,true)
	for frame in range(5):await physics_frame
	send_key(KEY_E,false)
	assert(bottle.driver==null and actor.held_interaction==null)
	bottle.interact(actor)
	assert(actor.held_interaction==bottle)
	main._toggle_directory()
	assert(main.directory_open and paused and not actor.gameplay_input_enabled)
	assert(actor.held_interaction==null and bottle.driver==null,"Opening the directory releases the held physical object")
	main._toggle_directory()
	assert(not paused and actor.gameplay_input_enabled)
	cart.toggle_grab(actor)
	send_key(KEY_ESCAPE,true)
	for frame in range(3):await physics_frame
	send_key(KEY_ESCAPE,false)
	assert(cart.driver==null and actor.held_interaction==null and not actor.gameplay_input_enabled,"Escape releases the cart and disables movement input")
	focus(false)
	print("CLEANING CART PASS:settling, four loose products, precise RMB/E handle, physical straight travel, release, individual product pickup/drop, directory pause and Escape release. Turning feel, loaded inter-deck travel, saving and final art remain unverified.")
	main.queue_free()
	await process_frame
	quit()
