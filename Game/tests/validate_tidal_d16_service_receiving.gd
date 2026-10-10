extends "res://tests/validate_tidal_d14_service_receiving.gd"
# Reuse established ordinary capsule/external door shape checks, with one main load.
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var house: Node3D = ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var group: Node3D = house.get_node("TidalD16ServiceReceiving")
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_D16_SERVICE_RECEIVING.json"))
	assert(group.get_meta("persistent_id") == "tidal_d16_service_receiving_001")
	assert(group.get_meta("corridor_mesh_count") == 86 and group.get_meta("named_replacement_count") == 4)
	assert(not group.get_meta("upper_staff_lift_enabled") and not group.get_meta("simultaneous_segregation_accepted"))
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var count_before: int = budget.sources.size()
	assert(load("res://scripts/tidal_d16_service_receiving.gd").build(ship,house) == group)
	assert(budget.sources.size() == count_before)
	for spec in [["TidalD13ServiceReceiving",7],["TidalD14ServiceReceiving",8],["TidalD15ServiceReceiving",9],["TidalD16ServiceReceiving",9]]:
		var module: Node3D = house.get_node(str(spec[0]))
		assert(not module.get_meta("upper_staff_lift_enabled"))
		var lights: Array = module.find_children("*","Light3D",true,false)
		assert(lights.size() == spec[1])
		for light: Light3D in lights: assert(budget.sources.count(light) == 1)
	for item in d.named_replacements:
		var owner: Node3D = group.get_node("RetainedD16CorridorClosedShaft") if item.source == "group3" else house
		var target: MeshInstance3D = owner.find_child(str(item.mesh),true,false)
		assert(target.get_meta("tidal_d16_shared_service_opening") and target.get_node_or_null("StaticContact") != null)
	var registry: Node = ship.get_node("ShipSystems/ReceivedRoomResidency")
	var ordinary: Dictionary = {}
	var specialty: Dictionary = {}
	for entry in registry.entries:
		if str(entry.parent.name) == "TidalRoomCandidates": ordinary[str(entry.room.name)] = true
		if str(entry.parent.name) == "SpecialtyHomeCandidates": specialty[str(entry.room.name)] = true
	assert(ordinary.size() == 85 and specialty.size() == 46)
	assert(house.get_node("ListeningSalonCompositeCapReceivingCore").get_child_count() == 13)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count() == 81)
	var staff: Node3D = ship.find_child("ForwardStaffLift",true,false)
	assert(staff.floor_heights == [0.0,6.0,12.0,46.2,52.5] and staff.landing_gates.size() == 5)
	assert(staff.cabin_file == "AST-CIR-003_five_stop.glb")
	var buttons := 0
	for node in staff.cabin.get_children():
		if node.get_script() == load("res://scripts/lift_button.gd"): buttons += 1
	assert(buttons == 5)
	assert(house.get_node("TidalGardenPassengerLiftCandidate").floor_heights == [84.0,88.5,93.0,97.5,102.0])
	var world := ship.get_world_3d().direct_space_state
	for y in [85.2,89.7,94.2,98.7]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-22,y,-490),Vector3(-24.5,y,-490)))
		assert(not hit.is_empty() and "UnfinishedShaftPhysicalClosure" in str(hit.collider.get_path()))
	for z in [-493.0,-487.0]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-61,98.7,z),Vector3(-64,98.7,z)))
		assert(not hit.is_empty() and "WestMouthPhysicalClosure" in str(hit.collider.get_path()))
	var cap := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,56.2,-490),Vector3(-25,55.4,-490)))
	assert(not cap.is_empty() and absf(cap.position.y-55.74) < .002)
	var excluded: Array[RID] = []
	for actor in ship.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var points: Array[Vector3] = []
	for p in [[-21,-490],[-21,-500],[-33,-500],[-44,-500],[-58,-500],[-61,-493],[-61,-487]]: points.append(Vector3(p[0],97.5,p[1]))
	for z in [-498.2,-498.06,-498,-497,-495,-493,-490,-487,-484,-482.25,-482.2,-481.8,-480]:
		for x in [-44.75,-44.0,-43.25]: points.append(Vector3(x,97.5,z))
	for p in points: check_floor_capsule(world,p,excluded)
	# Nearby retained D13/D14 receivers remain supported and clear.
	for p in [[-44,93,-497],[-44,93,-490],[-44,88.5,-497],[-44,88.5,-490],[-61,84,-493],[-63.16,84,-487]]: check_floor_capsule(world,Vector3(p[0],p[1],p[2]),excluded)
	var post_checks := 0
	var post_external_shape_queries := 0
	var receiving_exclusions: Array[RID] = excluded.duplicate()
	for body in group.find_children("*","CollisionObject3D",true,false): receiving_exclusions.append(body.get_rid())
	for x in [-45.6,-42.4]:
		for z in [-497.85,-491,-487,-483]:
			var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x+.3,96.65,z),Vector3(x-.3,96.65,z)))
			assert(not hit.is_empty() and "D16_LinkPost" in str(hit.collider.get_path()))
			post_checks += 1
			var shape := BoxShape3D.new()
			shape.size = Vector3(.198,.618,.198)
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = shape
			query.transform.origin = Vector3(x,96.65,z)
			query.margin = 0.0
			query.exclude = receiving_exclusions
			for item in world.intersect_shape(query,16): errors.append({"kind":"receiving_post_external_intersection","x":x,"z":z,"collider":str(item.collider.get_path())})
			post_external_shape_queries += 1
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var door: Node3D = group.get_node("D16_SharedServiceDoor")
	assert(str(door.persistent_id) == "tidal_d16_shared_service_door_001" and door.scale == Vector3.ONE)
	for repeat in range(2):
		door.interact(player)
		for frame in range(100):
			await physics_frame
			check_external_sweep(world,door)
		assert(door.open_fraction < .001)
		for x in [-45.2,-44.0,-42.8]:
			var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,98.25,-481.3),Vector3(x,98.25,-483.2)))
			assert(not hit.is_empty() and group.is_ancestor_of(hit.collider))
			guard_checks += 1
		door.interact(player)
		for frame in range(100):
			await physics_frame
			check_external_sweep(world,door)
		assert(door.open_fraction > .999)
		door_cycles += 1
	for p in points.slice(31): check_floor_capsule(world,p,excluded)
	var result := {"status":"PASS" if errors.is_empty() else "FAIL","actual_main_loaded":true,"source_meshes":86,"named_derivatives":4,"registered_d16_lights":9,"floor_checks":floor_checks,"capsule_checks":capsule_checks,"bearing_rays":post_checks,"post_external_shape_queries":post_external_shape_queries,"door_cycles":door_cycles,"external_door_sweep_queries":sweep_queries,"closed_guard_rays":guard_checks,"retained_d13_d14_d15":true,"shaft_closed":true,"retained_staff_stops_buttons":5,"ordinary_homes":85,"specialty_homes":46,"errors":errors,"limits":"Bounded stationary ordinary capsules, physical receiving contacts and retained door sweeps. Not full movement/cart/species/hygiene, load capacity, final visuals or whole Group1 acceptance."}
	FileAccess.open("res://artifacts/tidal_d16_service_receiving.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TIDAL_D16_SERVICE_RECEIVING ",JSON.stringify(result))
	print("PASS: bounded D16 receiving and D13/D14/D15 preservation" if errors.is_empty() else "FAIL: bounded D16 receiving")
	quit(0 if errors.is_empty() else 1)
