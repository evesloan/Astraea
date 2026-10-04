extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var state := ship.get_world_3d().direct_space_state
	var composition := ship.get_node("ShipSpace/Districts/AtriumFixtureAndBearingComposition_WIP")
	var exclusions: Array[RID] = [player.get_rid()]
	for body in composition.find_children("*","StaticBody3D",true,false): exclusions.append(body.get_rid())
	var fans := composition.find_children("D*_GalleryFan_*","Node3D",false,false)
	assert(fans.size()==32,"Eight bearings on each of four principal terraces")
	for fan in fans:
		var lower: float = fan.get_meta("lower_floor_y")
		var upper: float = fan.get_meta("upper_floor_y")
		var q := PhysicsRayQueryParameters3D.create(fan.global_position+Vector3.UP*.5,fan.global_position-Vector3.UP*.1)
		q.exclude = exclusions
		var hit := state.intersect_ray(q)
		assert(not hit.is_empty() and absf(hit.position.y-lower)<.02,"Column must stand on actual terrace support")
		for marker in fan.find_children("DATUM_upper_bearing_*","Node3D",true,false):
			assert(absf(marker.global_position.y-(upper-.24))<.02,"Bearing shoe matches actual upper slab underside")
			var ray := PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.35,marker.global_position-Vector3.UP*.1)
			ray.exclude = exclusions
			var ceiling := state.intersect_ray(ray)
			assert(not ceiling.is_empty() and absf(ceiling.position.y-upper)<.02,"Upper bearing must meet real gallery, not terminate in open air")
	for column in composition.find_children("D*_LanternBearing_*","Node3D",false,false):
		for index in [1,2]:
			var marker: Node3D = column.find_child("DATUM_light_"+str(index),true,false)
			var ray := PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.75)
			ray.exclude = [player.get_rid()]
			assert(state.intersect_ray(ray).is_empty(),"Inboard fixture must clear the outboard structural fan")
	var reservation := CylinderShape3D.new()
	reservation.radius = 2
	reservation.height = 4
	var points := [Vector2(0,-72),Vector2(0,-56),Vector2(40,-52),Vector2(40,52),Vector2(0,56),Vector2(0,72)]
	for deck in [5,8,11,15]:
		for i in range(points.size()-1):
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = reservation
			query.transform.origin = Vector3(points[i].x,ship.deck_y[deck]+2.05,points[i].y)
			query.motion = Vector3(points[i+1].x-points[i].x,0,points[i+1].y-points[i].y)
			query.exclude = [player.get_rid()]
			assert(state.intersect_shape(query).is_empty(),"Transit envelope starts obstructed")
			assert(state.cast_motion(query)[0]>.999,"Preserve four-metre-wide, four-metre-high reserved transit clearance")
	var lower_service := PhysicsShapeQueryParameters3D.new()
	lower_service.shape = reservation
	lower_service.transform.origin = Vector3(0,2.05,-72)
	lower_service.motion = Vector3(0,0,144)
	lower_service.exclude = [player.get_rid()]
	assert(state.intersect_shape(lower_service).is_empty() and state.cast_motion(lower_service)[0]>.999,"Preserve the current D01 central service clearance beneath the garden")
	assert(ship.arrive_at(Vector3(5,52.6,-42.5),PI),"Overlook must be an actual supported standing position")
	for frame in range(15): await physics_frame
	var sightline := PhysicsRayQueryParameters3D.create(player.camera.global_position,Vector3(-5,22,-12))
	var transparent_contacts: Array[RID] = [player.get_rid()]
	for body in ship.find_children("*","StaticBody3D",true,false):
		if str(body.get_parent().name).to_lower().contains("glass"): transparent_contacts.append(body.get_rid())
	sightline.exclude = transparent_contacts
	var obstruction := state.intersect_ray(sightline)
	assert(obstruction.is_empty() or str(obstruction.collider.get_path()).contains("CANOPY_A"),"A real overlook must reveal the lower garden rather than face an intervening slab")
	print("ATRIUM SUPPORT PASS: 32 supported columns,96 upper-gallery contacts,64 clear optical exits and the reserved four-band transit envelope. Not structural engineering, loaded-cart or tram dynamics acceptance.")
	quit()
