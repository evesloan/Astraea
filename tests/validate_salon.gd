extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var state := ship.get_world_3d().direct_space_state
	var room := ship.get_node("ShipSpace/Districts/D09_StarboardTerrace_AuthoredFootprint_WIP")
	assert(room.get_meta("allocation_room_id")=="D09_salon5")
	var capsule := CapsuleShape3D.new()
	capsule.height = 1.8
	capsule.radius = 0.3
	var route := [Vector2(48,0),Vector2(56,0),Vector2(63,-4),Vector2(66,-12),Vector2(63,-20.5),Vector2(63,-24)]
	for i in range(route.size()-1):
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = capsule
		query.transform.origin = Vector3(route[i].x,53.43,route[i].y)
		query.motion = Vector3(route[i+1].x-route[i].x,0,route[i+1].y-route[i].y)
		query.exclude = [player.get_rid()]
		assert(state.intersect_shape(query).is_empty(),"Salon's circulation segment must start clear")
		assert(state.cast_motion(query)[0]>.999,"Portal, oblique arrival and quiet approach must remain connected")
	for point in [Vector3(55,52.6,-19),Vector3(62,52.6,-9),Vector3(68,52.6,-12)]:
		assert(ship.arrive_at(point,0),"Gallery and conversation stopping positions need support and clearance")
	for fixture in room.find_children("SalonCeilingSource_*","SpotLight3D",false,false)+room.find_children("ConversationSource_*","SpotLight3D",false,false):
		var optical_ray := PhysicsRayQueryParameters3D.create(fixture.global_position,fixture.global_position+Vector3.DOWN*.8)
		optical_ray.exclude = [player.get_rid()]
		assert(state.intersect_ray(optical_ray).is_empty(),"Fixture exit ray is blocked by its own housing or ceiling")
	var section_samples := [[Vector2(55,-30),4.2],[Vector2(60,-21),4.9],[Vector2(68,-5),5.6],[Vector2(53,-21),4.85],[Vector2(53,-23),4.2+1.4/6],[Vector2(55,-20),4.2+4*1.4/6]]
	for sample in section_samples:
		var xz: Vector2 = sample[0]
		var hit := state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(xz.x,55,xz.y),Vector3(xz.x,60,xz.y)))
		assert(not hit.is_empty() and absf(hit.position.y-(52.5+sample[1]))<.08,"Ceiling must follow the authored rising section")
	print("SALON PASS: preserved D09_salon5 identity; connected doorway and oblique circulation; three stopping positions; nine optical exits; rising ceiling section. No NPC, cart or final visual approval.")
	quit()
