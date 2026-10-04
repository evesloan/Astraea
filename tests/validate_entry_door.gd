extends SceneTree
func _initialize() -> void:call_deferred("run")
func animate_clear(ship:Node3D,door:Node3D) -> void:
	for frame in range(100):
		await physics_frame
		for leaf in door.leaves:
			for collider in leaf.get_children():
				if not collider is CollisionShape3D:continue
				var query:=PhysicsShapeQueryParameters3D.new()
				query.shape=collider.shape
				query.transform=collider.global_transform
				query.margin=.001
				query.exclude=[leaf.get_rid()]
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(query,64):
					assert(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Sliding leaf clips fixed pocket or room at %.3f"%door.open_fraction)
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var door:Node3D=ship.find_child("Suite13017EntryDoor",true,false)
	assert(door!=null and door.leaves.size()==2)
	door.interact(actor)
	await animate_clear(ship,door)
	assert(door.open_fraction<.001)
	assert(ship.arrive_at(Vector3(84.1,84.1,-42),PI/2))
	for frame in range(15):await physics_frame
	assert(actor.target_from_view()==door)
	var focus:=InputEventMouseButton.new()
	focus.button_index=MOUSE_BUTTON_RIGHT
	focus.pressed=true
	Input.parse_input_event(focus.duplicate())
	var key:=InputEventKey.new()
	key.keycode=KEY_E
	key.physical_keycode=KEY_E
	key.pressed=true
	Input.parse_input_event(key.duplicate())
	await animate_clear(ship,door)
	assert(door.open_fraction>.999,"Focused E opens the actual entry")
	key.pressed=false
	Input.parse_input_event(key.duplicate())
	assert(ship.arrive_at(Vector3(84,84.1,-40.45),PI/2))
	for frame in range(15):await physics_frame
	var marker:=door.find_child("DATUM_call_button",true,false)as Node3D
	var delta:Vector3=marker.global_position-actor.camera.global_position
	actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.camera.rotation.x=actor.pitch
	assert(actor.target_from_view()==door,"The physical call plate remains selectable with leaves retracted")
	key.pressed=true
	Input.parse_input_event(key.duplicate())
	await animate_clear(ship,door)
	assert(door.open_fraction<.001,"Call plate closes the entry")
	key.pressed=false
	Input.parse_input_event(key.duplicate())
	focus.pressed=false
	Input.parse_input_event(focus.duplicate())
	key.pressed=true
	Input.parse_input_event(key.duplicate())
	for frame in range(10):await physics_frame
	assert(door.open_fraction<.001,"Unfocused E cannot operate entry")
	door.interact(actor)
	await animate_clear(ship,door)
	assert(door.open_fraction>.999,"Entry reopens before occupancy tests")
	assert(ship.arrive_at(Vector3(82,84.1,-42),0))
	for frame in range(10):await physics_frame
	door.interact(actor)
	assert(door.obstructed and door.desired_open,"Person in the opening prevents closing")
	assert(ship.arrive_at(Vector3(84.1,84.1,-42),PI/2))
	# Let the physics server synchronize the teleported actor before spawning a prop.
	for frame in range(10):await physics_frame
	var prop:=RigidBody3D.new()
	prop.gravity_scale=0
	prop.position=Vector3(82,85,-42)
	var contact:=CollisionShape3D.new()
	var sphere:=SphereShape3D.new()
	sphere.radius=.2
	contact.shape=sphere
	prop.add_child(contact)
	ship.get_node("ShipSpace/PersistentActors").add_child(prop)
	for frame in range(10):await physics_frame
	assert(prop.global_position.distance_to(Vector3(82,85,-42))<.01,"Obstruction fixture must remain in the opening")
	door.interact(actor)
	assert(door.obstructed and door.desired_open,"Loose physics prop prevents closing")
	print("ENTRY DOOR PASS:400 motion samples clear of real enclosed pockets/walls, RMB/E and physical call-plate targeting, unfocused rejection, person/rigid-prop obstruction. No locks, save or loaded-cart acceptance.")
	main.queue_free()
	await process_frame
	quit()
