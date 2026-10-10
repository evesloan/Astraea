extends "res://tests/validate_tidal_d14_service_receiving.gd"
# Reuse established ordinary capsule/external door shape checks, with one main load.
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var house: Node3D = ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var group: Node3D = house.get_node("TidalD17ServiceReceiving")
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_D17_SERVICE_RECEIVING.json"))
	assert(group.get_meta("persistent_id") == "tidal_d17_service_receiving_001")
	assert(group.get_meta("corridor_mesh_count") == 91 and group.get_meta("named_replacement_count") == 4)
	assert(not group.get_meta("upper_staff_lift_enabled") and not group.get_meta("simultaneous_segregation_accepted"))
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var count_before: int = budget.sources.size()
	assert(load("res://scripts/tidal_d17_service_receiving.gd").build(ship,house) == group)
	assert(budget.sources.size() == count_before)
	for spec in [["TidalD13ServiceReceiving",7],["TidalD14ServiceReceiving",8],["TidalD15ServiceReceiving",9],["TidalD16ServiceReceiving",9],["TidalD17ServiceReceiving",9]]:
		var module: Node3D = house.get_node(str(spec[0]))
		assert(not module.get_meta("upper_staff_lift_enabled"))
		var lights: Array = module.find_children("*","Light3D",true,false)
		assert(lights.size() == spec[1])
		for light: Light3D in lights: assert(budget.sources.count(light) == 1)
	for item in d.named_replacements:
		var owner: Node3D = group.get_node("RetainedD17CorridorClosedShaft") if item.source == "group3" else house
		var target: MeshInstance3D = owner.find_child(str(item.mesh),true,false)
		assert(target.get_meta("tidal_d17_shared_service_opening") and target.get_node_or_null("StaticContact") != null)
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
	for y in [85.2,89.7,94.2,98.7,103.2]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-22,y,-490),Vector3(-24.5,y,-490)))
		assert(not hit.is_empty() and "UnfinishedShaftPhysicalClosure" in str(hit.collider.get_path()))
	for z in [-493.0,-487.0]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-61,103.2,z),Vector3(-64,103.2,z)))
		assert(not hit.is_empty() and "WestMouthPhysicalClosure" in str(hit.collider.get_path()))
	var cap := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,56.2,-490),Vector3(-25,55.4,-490)))
	assert(not cap.is_empty() and absf(cap.position.y-55.74) < .002)
	var excluded: Array[RID] = []
	for actor in ship.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var points: Array[Vector3] = []
	for p in [[-21,-490],[-21,-500],[-33,-500],[-44,-500],[-58,-500],[-61,-493],[-61,-487]]: points.append(Vector3(p[0],102,p[1]))
	for x in [-19,-18.66,-18.3,-17,-15,-13,-11,-10.5]:
		for z in [-486.35,-485.6,-484.85]: points.append(Vector3(x,102,z))
	for z in [-485.6,-484.5,-483.5,-482.25,-482.2,-481.8,-480]:
		for x in [-11.25,-10.5,-9.75]: points.append(Vector3(x,102,z))
	for p in points: check_floor_capsule(world,p,excluded)
	# Nearby retained D13/D14 receivers remain supported and clear.
	for p in [[-44,97.5,-497],[-44,97.5,-490],[-44,93,-497],[-44,93,-490],[-44,88.5,-497],[-44,88.5,-490],[-61,84,-493],[-63.16,84,-487]]: check_floor_capsule(world,Vector3(p[0],p[1],p[2]),excluded)
	var post_checks := 0
	var post_external_shape_queries := 0
	var receiving_exclusions: Array[RID] = excluded.duplicate()
	for body in group.find_children("*","CollisionObject3D",true,false): receiving_exclusions.append(body.get_rid())
	for spec in d.post_checks:
		var x: float = spec.position_xz[0]
		var z: float = spec.position_xz[1]
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x+.3,101.1,z),Vector3(x-.3,101.1,z)))
		assert(not hit.is_empty() and "D17_LinkPost" in str(hit.collider.get_path()))
		post_checks += 1
		var shape := BoxShape3D.new()
		shape.size = Vector3(.198,spec.top_y-spec.bottom_y-.002,.198)
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.transform.origin = Vector3(x,(spec.top_y+spec.bottom_y)/2,z)
		query.margin = 0.0
		query.exclude = receiving_exclusions
		for item in world.intersect_shape(query,16): errors.append({"kind":"receiving_post_external_intersection","x":x,"z":z,"collider":str(item.collider.get_path())})
		post_external_shape_queries += 1
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var door: Node3D = group.get_node("D17_SharedServiceDoor")
	assert(str(door.persistent_id) == "tidal_d17_shared_service_door_001" and door.scale == Vector3.ONE)
	for repeat in range(2):
		door.interact(player)
		for frame in range(100):
			await physics_frame
			check_external_sweep(world,door)
		assert(door.open_fraction < .001)
		for x in [-11.75,-11.3,-10.5,-9.7,-9.25]:
			var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,102.75,-481.3),Vector3(x,102.75,-483.2)))
			if hit.is_empty() or not group.is_ancestor_of(hit.collider): errors.append({"kind":"closed_guard","x":x,"hit":str(hit.get("collider","none")),"position":str(hit.get("position","none"))})
			guard_checks += 1
		door.interact(player)
		for frame in range(100):
			await physics_frame
			check_external_sweep(world,door)
		assert(door.open_fraction > .999)
		door_cycles += 1
	for p in points.slice(28): check_floor_capsule(world,p,excluded)
	# Temporary controller/panel fixture outside ship geometry; upper production lift unchanged.
	var candidate: Node3D = load("res://scripts/commons_lift.gd").new()
	candidate.name = "IsolatedTenStopPanelFixture"
	candidate.position = Vector3(1000,0,0)
	candidate.floor_heights.assign([0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0])
	var lower: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json")).staff
	candidate.deck_numbers.assign(lower.proposed_deck_numbers+[13,14,15,16,17])
	candidate.stop_ids.assign(lower.proposed_stop_ids+["D13","D14","D15","D16","D17"])
	candidate.stop_names.assign(staff.stop_names+["D13 service","D14 service","D15 service","D16 service","D17 service"])
	candidate.stop_codes.assign(staff.stop_codes+["13","14","15","16","17"])
	candidate.cabin_file = "AST-CIR-003_ten_stop.glb"
	candidate.identity_prefix = "forward_staff"
	candidate.persistent_id = &"forward_staff_lift_001"
	ship.add_child(candidate)
	candidate.set_physics_process(false)
	var panel_buttons: Array = []
	for node in candidate.cabin.get_children():
		if node.get_script() == load("res://scripts/lift_button.gd"): panel_buttons.append(node)
	assert(panel_buttons.size() == 10 and candidate.landing_gates.size() == 10)
	var original_buttons: Array = []
	for node in staff.cabin.get_children():
		if node.get_script() == load("res://scripts/lift_button.gd"): original_buttons.append(node)
	for i in range(5):
		assert(panel_buttons[i].persistent_id == original_buttons[i].persistent_id)
		assert(panel_buttons[i].position.is_equal_approx(original_buttons[i].position))
		assert(candidate.landing_gates[i].persistent_id == staff.landing_gates[i].persistent_id)
	for i in range(5,10):
		assert(not candidate.landing_gates[i].cabin_present_and_stopped)
		assert(not candidate.landing_gates[i].request_open())
		assert(panel_buttons[i].position.is_equal_approx(Vector3(1.73,1.73,-(.46+.28*(i-5)))))
	var backing: CollisionShape3D = candidate.cabin.get_node("CabinControlBacking")
	assert(backing.position.is_equal_approx(Vector3(1.815,1.50,-1.02)))
	assert(backing.shape.size.is_equal_approx(Vector3(.13,.80,1.40)))
	assert(staff.floor_heights.size() == 5 and staff.cabin_file == "AST-CIR-003_five_stop.glb")
	candidate.free()
	var result := {"ten_stop_fixture_buttons":10,"ten_stop_native_backing_matched":true,"original_five_button_and_gate_ids_preserved":true,"upper_production_travel_enabled":false,"temporary_fixture_travel_tested":false,"status":"PASS" if errors.is_empty() else "FAIL","actual_main_loaded":true,"source_meshes":91,"named_derivatives":4,"registered_d17_lights":9,"floor_checks":floor_checks,"capsule_checks":capsule_checks,"bearing_rays":post_checks,"post_external_shape_queries":post_external_shape_queries,"door_cycles":door_cycles,"external_door_sweep_queries":sweep_queries,"closed_guard_rays":guard_checks,"retained_d13_d14_d15_d16":true,"shaft_closed":true,"retained_staff_stops_buttons":5,"ordinary_homes":85,"specialty_homes":46,"errors":errors,"limits":"Bounded stationary ordinary capsules, physical receiving contacts and retained door sweeps. Not full movement/cart/species/hygiene, load capacity, final visuals or whole Group1 acceptance."}
	FileAccess.open("res://artifacts/forward_staff_ten_stop_panel.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("FORWARD_STAFF_TEN_STOP_PANEL ",JSON.stringify(result))
	print("PASS: ten-stop panel fixture and retained five-stop D13-D17 interfaces" if errors.is_empty() else "FAIL: bounded D17 receiving")
	quit(0 if errors.is_empty() else 1)
