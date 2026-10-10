extends SceneTree
var errors: Array = []
var floor_checks := 0
var capsule_checks := 0
var external_door_sweep_queries := 0
var closed_guard_checks := 0
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var house: Node3D = ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var receiving: Node3D = house.get_node("TidalD13ServiceReceiving")
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_D13_SERVICE_RECEIVING.json"))
	assert(receiving.get_meta("persistent_id") == "tidal_d13_service_receiving_001")
	assert(not receiving.get_meta("upper_staff_lift_enabled") and receiving.get_meta("upper_d14_d17_held"))
	assert(receiving.get_meta("source_mesh_count") == 73)
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var source_count: int = budget.sources.size()
	assert(load("res://scripts/tidal_d13_service_receiving.gd").build(ship,house) == receiving)
	assert(budget.sources.size() == source_count)
	var lights := receiving.find_children("*","Light3D",true,false)
	assert(lights.size() == 7)
	for light: Light3D in lights:
		assert(budget.sources.count(light) == 1)
		assert(budget.requested_shadow[light.get_instance_id()])
		var marker: Node3D = receiving.get_node("RetainedD13CorridorAndReceiving").find_child(str(light.get_meta("source_marker")),true,false)
		assert(marker != null and marker.global_position.distance_to(light.global_position) < .0001)
	var registry: Node = ship.get_node("ShipSystems/ReceivedRoomResidency")
	var ordinary: Dictionary = {}
	var specialty: Dictionary = {}
	for entry in registry.entries:
		if str(entry.parent.name) == "TidalRoomCandidates":
			assert(not ordinary.has(str(entry.room.name)))
			ordinary[str(entry.room.name)] = true
		if str(entry.parent.name) == "SpecialtyHomeCandidates":
			assert(not specialty.has(str(entry.room.name)))
			specialty[str(entry.room.name)] = true
	assert(ordinary.size() == 85 and specialty.size() == 46)
	assert(house.get_node("ListeningSalonCompositeCapReceivingCore").get_child_count() == 13)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count() == 81)
	var staff: Node3D = ship.find_child("ForwardStaffLift",true,false)
	assert(staff.floor_heights == [0.0,6.0,12.0,46.2,52.5])
	assert(staff.landing_gates.size() == 5 and staff.cabin_file == "AST-CIR-003_five_stop.glb")
	var button_script: GDScript = load("res://scripts/lift_button.gd")
	var cabin_buttons := 0
	for node in staff.cabin.get_children():
		if node.get_script() == button_script: cabin_buttons += 1
	assert(cabin_buttons == 5)
	var public_lift: Node3D = house.get_node("TidalGardenPassengerLiftCandidate")
	assert(public_lift.floor_heights == [84.0,88.5,93.0,97.5,102.0])
	var world := ship.get_world_3d().direct_space_state
	var closed_ray := PhysicsRayQueryParameters3D.create(Vector3(-22,85.2,-490),Vector3(-24.5,85.2,-490))
	var closure := world.intersect_ray(closed_ray)
	assert(not closure.is_empty() and "D13_UnfinishedShaftPhysicalClosure" in str(closure.collider.get_path()))
	var cap_ray := PhysicsRayQueryParameters3D.create(Vector3(-25,56.2,-490),Vector3(-25,55.4,-490))
	var cap := world.intersect_ray(cap_ray)
	assert(not cap.is_empty() and absf(cap.position.y-55.74) < .002)
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var doors: Array[Node3D] = [receiving.get_node("D13_CleanSupplyDoor"),receiving.get_node("D13_SealedReturnsDoor")]
	var excluded: Array[RID] = []
	for actor in ship.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	# Static local floor/headroom points only, with the existing doors initially open.
	var points: Array[Vector3] = []
	for p in [[-21,-490],[-21,-498],[-21,-500],[-25,-500],[-33,-500],[-45,-500],[-58,-500],[-61,-500],[-61,-497],[-61,-493],[-61,-487],[-61,-484.5]]:
		points.append(Vector3(p[0],84,p[1]))
	for z in [-493.0,-487.0]:
		for x in [-62.4,-62.98,-63.0,-63.16,-63.34,-63.8,-64.5]: points.append(Vector3(x,84,z))
	for z in [-493.0,-487.0]:
		for edge in [-.75,.75]: points.append(Vector3(-63.16,84,z+edge))
	for p in points: check_floor_capsule(world,p,excluded)
	# Two door close/open cycles, one for each existing controller. Screen moving
	# collision shapes against external architecture; factory rebate contacts are
	# retained by the unmodified source/controller and excluded from this test.
	for door in doors:
		assert(door.scale == Vector3.ONE and door.leaves.size() == 2)
		door.interact(player)
	for frame in range(100):
		await physics_frame
		for door in doors: check_external_sweep(world,door)
	for door in doors:
		assert(door.open_fraction < .001)
		var pos: Vector3 = door.global_position
		for offset in [-.8,0.0,.8]:
			var ray := PhysicsRayQueryParameters3D.create(pos+Vector3(.9,.75,offset),pos+Vector3(-1,.75,offset))
			var hit := world.intersect_ray(ray)
			if hit.is_empty() or not door.is_ancestor_of(hit.collider): errors.append({"kind":"closed_guard","door":str(door.name),"offset":offset,"hit":str(hit.get("collider","none"))})
			closed_guard_checks += 1
		door.interact(player)
	for frame in range(100):
		await physics_frame
		for door in doors: check_external_sweep(world,door)
	for door in doors: assert(door.open_fraction > .999)
	for p in points.slice(12): check_floor_capsule(world,p,excluded)
	print("D13_BEFORE_OBSTRUCTION_ERRORS ",JSON.stringify(errors))
	var obstruction_checks := 0
	for door in doors:
		var blocker := CharacterBody3D.new()
		var contact := CollisionShape3D.new()
		var sphere := SphereShape3D.new()
		sphere.radius = .18
		contact.shape = sphere
		blocker.add_child(contact)
		ship.get_node("ShipSpace/PersistentActors").add_child(blocker)
		blocker.global_position = door.to_global(Vector3(0,1.2,-.65))
		for i in range(4): await physics_frame
		var old_desired: bool = door.desired_open
		door.interact(player)
		assert(door.obstructed and door.desired_open == old_desired)
		blocker.free()
		for i in range(4): await physics_frame
		assert(not door.obstructed)
		obstruction_checks += 1
	var result := {"status":"PASS" if errors.is_empty() else "FAIL","actual_main_loaded":true,"unique_installation":true,"receiving_meshes":73,"actual_registered_fixture_lights":7,"lights_registered_exactly_once":true,"new_missing_only_floor_area_m2":d.floor_reconciliation.total_new_floor_area_m2,"floor_checks":floor_checks,"capsule_checks":capsule_checks,"external_door_sweep_shape_queries":external_door_sweep_queries,"door_close_open_cycles":2,"closed_guard_rays":closed_guard_checks,"obstruction_checks":obstruction_checks,"unfinished_shaft_physically_closed":true,"retained_staff_stops":5,"retained_physical_cabin_buttons":5,"retained_staff_cap_top_y":cap.position.y,"public_passenger_lift_unchanged":true,"retained_ordinary_homes":ordinary.size(),"retained_specialty_homes":specialty.size(),"retained_salon_members":13,"errors":errors,"limits":"Bounded actual-main source receiving, stationary ordinary capsules and controller cycles only. Factory rebate contacts excluded from external architecture sweep. No exhaustive traversal, loaded-cart/species/upper lift/stock operation, final visual or target-hardware acceptance."}
	FileAccess.open("res://artifacts/tidal_d13_service_receiving.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TIDAL_D13_SERVICE_RECEIVING ",JSON.stringify(result))
	print("PASS: bounded D13 receiving and doors" if errors.is_empty() else "FAIL: bounded D13 receiving")
	quit(0 if errors.is_empty() else 1)

func check_floor_capsule(world: PhysicsDirectSpaceState3D,p: Vector3,excluded: Array[RID]) -> void:
	var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.18,p-Vector3.UP*.4)
	ray.exclude = excluded
	var hit := world.intersect_ray(ray)
	if hit.is_empty() or absf(hit.position.y-p.y) > .035: errors.append({"kind":"floor","point":str(p),"hit":str(hit.get("position","none"))})
	floor_checks += 1
	var q := PhysicsShapeQueryParameters3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	q.shape = capsule
	q.transform.origin = p+Vector3.UP*.925
	q.margin = .001
	q.exclude = excluded
	for item in world.intersect_shape(q,16): errors.append({"kind":"capsule","point":str(p),"collider":str(item.collider.get_path())})
	capsule_checks += 1

func check_external_sweep(world: PhysicsDirectSpaceState3D,door: Node3D) -> void:
	var excluded: Array[RID] = []
	for body in door.find_children("*","CollisionObject3D",true,false): excluded.append(body.get_rid())
	for leaf in door.leaves:
		for contact in leaf.get_children():
			if not contact is CollisionShape3D: continue
			var q := PhysicsShapeQueryParameters3D.new()
			q.shape = contact.shape
			q.transform = contact.global_transform
			q.margin = .001
			q.exclude = excluded
			external_door_sweep_queries += 1
			for hit in world.intersect_shape(q,16):
				if hit.collider is StaticBody3D: errors.append({"kind":"external_door_sweep","door":str(door.name),"fraction":door.open_fraction,"collider":str(hit.collider.get_path())})
