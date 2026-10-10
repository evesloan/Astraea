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
	var cap := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,105.6,-490),Vector3(-25,105.0,-490)))
	assert(not cap.is_empty() and absf(cap.position.y-105.34) < .002)
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
	var lower_root: Node3D = ship.find_child("LowerStaffNetwork_WIP",true,false)
	var upper: Node3D = lower_root.get_node("ForwardStaffUpperInterfaces")
	assert(not upper.get_meta("upper_operation_enabled") and upper.get_meta("envelope_mesh_count") == 43)
	assert(load("res://scripts/forward_staff_upper_interfaces.gd").build(lower_root,ship) == upper)
	var old_cap := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,55.4,-490),Vector3(-25,55.9,-490)))
	assert(old_cap.is_empty())
	var wall_rays := 0
	for y in [55.8,63.99,64.01,71.99,72.01,79.99,80.01,83.0,84.2,88.2,88.6,92.8,93.2,97.2,97.6,101.8,102.2,104.9]:
		for end in [Vector3(-28,y,-490),Vector3(-25,y,-493),Vector3(-25,y,-487)]:
			var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,y,-490),end))
			if hit.is_empty() or not upper.is_ancestor_of(hit.collider): errors.append({"kind":"upper_shaft_wall_gap","y":y,"end":str(end),"hit":str(hit.get("collider","none"))})
			wall_rays += 1
	for y in [56.0,70.0,82.8]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,y,-490),Vector3(-22.5,y,-490)))
		if hit.is_empty() or not upper.is_ancestor_of(hit.collider): errors.append({"kind":"upper_blank_front_gap","y":y})
	var receiving_rids: Array[RID] = []
	for deck in range(13,18):
		var old_module: Node3D = house.get_node("TidalD"+str(deck)+"ServiceReceiving")
		for body in old_module.find_children("*","CollisionObject3D",true,false): receiving_rids.append(body.get_rid())
	var upper_gate_rays := 0
	var upper_sill_rays := 0
	for deck in range(13,18):
		var y: float = 84+4.5*(deck-13)
		var gate: Node3D = upper.get_node("HeldLandingGate_D"+str(deck))
		assert(str(gate.persistent_id) == "D"+str(deck)+"_forward_staff_lift_gate")
		assert(gate.open_fraction < .001 and not gate.request_open())
		var central := PhysicsShapeQueryParameters3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = .3
		capsule.height = 1.8
		central.shape = capsule
		central.transform.origin = Vector3(-23.08,y+.925,-490)
		central.exclude = receiving_rids
		var gate_blocks_capsule := false
		for contact in world.intersect_shape(central,32):
			if gate.is_ancestor_of(contact.collider): gate_blocks_capsule = true
		if not gate_blocks_capsule: errors.append({"kind":"held_gate_central_capsule_unblocked","deck":deck})
		for z in [-490.8,-490.4,-489.6,-489.2]:
			var query := PhysicsRayQueryParameters3D.create(Vector3(-22.5,y+.75,z),Vector3(-23.7,y+.75,z))
			query.exclude = receiving_rids
			var hit := world.intersect_ray(query)
			if hit.is_empty() or not gate.is_ancestor_of(hit.collider): errors.append({"kind":"held_upper_gate_gap","deck":deck,"z":z,"hit":str(hit.get("collider","none"))})
			upper_gate_rays += 1
			var support := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-23.185,y+.05,z),Vector3(-23.185,y-.20,z)))
			if support.is_empty() or absf(support.position.y-y) > .002: errors.append({"kind":"upper_sill_gap","deck":deck,"z":z})
			upper_sill_rays += 1
	# Conservative full upper primary-cabin AABB, inflated 5mm. Moving gate interfaces held separately.
	var swept := PhysicsShapeQueryParameters3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(3.61,104.945-55.845,4.01)
	swept.shape = box
	swept.transform.origin = Vector3(-25,(104.945+55.845)/2,-490)
	swept.margin = 0.0
	swept.exclude = excluded
	var cabin_intrusions: Array = []
	for hit in world.intersect_shape(swept,128):
		if hit.collider is StaticBody3D: cabin_intrusions.append(str(hit.collider.get_path()))
	# Record physical blockers without claiming travel readiness.
	assert(staff.floor_heights == [0.0,6.0,12.0,46.2,52.5])
	var result := {"upper_envelope_meshes":43,"upper_shaft_wall_rays":wall_rays,"upper_blank_front_rays":3,"upper_gate_closed_rays":upper_gate_rays,"upper_gate_central_capsule_barriers":5,"retained_gate_collision_meeting_seam_m":.005,"upper_sill_floor_rays":upper_sill_rays,"primary_upper_cabin_envelope_intrusions":cabin_intrusions,"primary_upper_cabin_envelope_clear":cabin_intrusions.is_empty(),"upper_operation_enabled":false,"old_cap_exactly_reconciled":true,"temporary_closures_retained":true,"status":"PASS" if errors.is_empty() else "FAIL","actual_main_loaded":true,"source_meshes":91,"named_derivatives":4,"registered_d17_lights":9,"floor_checks":floor_checks,"capsule_checks":capsule_checks,"bearing_rays":post_checks,"post_external_shape_queries":post_external_shape_queries,"door_cycles":door_cycles,"external_door_sweep_queries":sweep_queries,"closed_guard_rays":guard_checks,"retained_d13_d14_d15_d16":true,"shaft_closed":true,"retained_staff_stops_buttons":5,"ordinary_homes":85,"specialty_homes":46,"errors":errors,"limits":"Bounded stationary ordinary capsules, physical receiving contacts and retained door sweeps. Not full movement/cart/species/hygiene, load capacity, final visuals or whole Group1 acceptance."}
	FileAccess.open("res://artifacts/forward_staff_upper_interfaces.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("FORWARD_STAFF_UPPER_INTERFACES ",JSON.stringify(result))
	print("PASS: held forward staff upper interfaces and D13-D17 preservation" if errors.is_empty() else "FAIL: bounded D17 receiving")
	quit(0 if errors.is_empty() else 1)
