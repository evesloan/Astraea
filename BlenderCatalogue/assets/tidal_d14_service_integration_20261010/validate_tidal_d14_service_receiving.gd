extends SceneTree
var errors: Array = []
var floor_checks := 0
var capsule_checks := 0
var sweep_queries := 0
var guard_checks := 0
var door_cycles := 0
var obstruction_checks := 0
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var house: Node3D = ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var group: Node3D = house.get_node("TidalD14ServiceReceiving")
	var d13: Node3D = house.get_node("TidalD13ServiceReceiving")
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_D14_SERVICE_RECEIVING.json"))
	assert(group.get_meta("persistent_id") == "tidal_d14_service_receiving_001")
	assert(not group.get_meta("upper_staff_lift_enabled") and group.get_meta("abandoned_west_mouths_physically_closed"))
	assert(group.get_meta("corridor_mesh_count") == 65 and group.get_meta("receiver_mesh_count") == 22 and group.get_meta("named_replacement_count") == 3)
	assert(d13.get_meta("source_mesh_count") == 73 and not d13.get_meta("upper_staff_lift_enabled"))
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var old_count: int = budget.sources.size()
	assert(load("res://scripts/tidal_d14_service_receiving.gd").build(ship,house) == group)
	assert(load("res://scripts/tidal_d13_service_receiving.gd").build(ship,house) == d13)
	assert(budget.sources.size() == old_count)
	for module in [group,d13]:
		var lights: Array = module.find_children("*","Light3D",true,false)
		assert(lights.size() == (8 if module == group else 7))
		for light: Light3D in lights:
			assert(budget.sources.count(light) == 1 and budget.requested_shadow[light.get_instance_id()])
			var source: Node3D = module.get_node("RetainedD13CorridorAndReceiving") if module == d13 else module.get_node("RetainedD14CorridorClosedShaft" if light.get_meta("source_visual_owner") == "corridor" else "D14SharedHouseReceiver")
			var marker: Node3D = source.find_child(str(light.get_meta("source_marker")),true,false)
			assert(marker != null and marker.global_position.distance_to(light.global_position) < .0001)
	var street: Node3D = ship.get_node("ShipSpace/Districts/TidalD14SouthStreetExtension")
	var patched_guard: MeshInstance3D = street.find_child("D14_SouthStreetEndGuard",true,false)
	assert(patched_guard.get_meta("tidal_d14_shared_service_opening"))
	var actual_bounds: AABB = patched_guard.global_transform*patched_guard.get_aabb()
	assert(actual_bounds.position.distance_to(Vector3(-46.05,88.5,-493.6)) < .002)
	assert(actual_bounds.end.distance_to(Vector3(-41.95,89.6,-493.5)) < .002)
	for item in d.named_replacements:
		var owner: Node3D = group.get_node("RetainedD14CorridorClosedShaft") if item.owner == "new_d14_corridor" else street
		var mesh: MeshInstance3D = owner.find_child(str(item.mesh),true,false)
		assert(mesh.get_meta("tidal_d14_shared_service_opening") and mesh.get_node_or_null("StaticContact") != null)
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
	assert(specialty.has("AST-UNIT-D14-28fc6d4a422367c8") and specialty.has("AST-UNIT-D14-438591f109a0905c"))
	assert(house.get_node("ListeningSalonCompositeCapReceivingCore").get_child_count() == 13)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count() == 81)
	var staff: Node3D = ship.find_child("ForwardStaffLift",true,false)
	assert(staff.floor_heights == [0.0,6.0,12.0,46.2,52.5])
	assert(staff.landing_gates.size() == 5 and staff.cabin_file == "AST-CIR-003_five_stop.glb")
	var cabin_buttons := 0
	var button_script: GDScript = load("res://scripts/lift_button.gd")
	for node in staff.cabin.get_children():
		if node.get_script() == button_script: cabin_buttons += 1
	assert(cabin_buttons == 5)
	assert(house.get_node("TidalGardenPassengerLiftCandidate").floor_heights == [84.0,88.5,93.0,97.5,102.0])
	var world := ship.get_world_3d().direct_space_state
	for y in [85.2,89.7]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-22,y,-490),Vector3(-24.5,y,-490)))
		assert(not hit.is_empty() and ("D13_UnfinishedShaftPhysicalClosure" if y < 88 else "D14_UnfinishedShaftPhysicalClosure") in str(hit.collider.get_path()))
	for z in [-493.0,-487.0]:
		var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-61,89.7,z),Vector3(-64,89.7,z)))
		assert(not hit.is_empty() and "WestMouthPhysicalClosure" in str(hit.collider.get_path()))
	var cap := world.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-25,56.2,-490),Vector3(-25,55.4,-490)))
	assert(not cap.is_empty() and absf(cap.position.y-55.74) < .002)
	var excluded: Array[RID] = []
	for actor in ship.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var points14: Array[Vector3] = []
	for p in [[-21,-490],[-21,-498],[-21,-500],[-25,-500],[-33,-500],[-45,-500],[-58,-500],[-61,-500],[-61,-493],[-61,-487],[-44,-498.15],[-44,-498],[-44,-497],[-44,-496],[-44,-495],[-44,-494],[-44,-493.65],[-44,-493.4],[-44,-491]]: points14.append(Vector3(p[0],88.5,p[1]))
	for x in [-44.75,-43.25]: points14.append(Vector3(x,88.5,-493.6))
	var points13: Array[Vector3] = []
	for p in [[-21,-490],[-21,-500],[-33,-500],[-45,-500],[-61,-493],[-61,-487],[-63.16,-493],[-63.34,-493],[-64.5,-493],[-63.16,-487],[-63.34,-487],[-64.5,-487]]: points13.append(Vector3(p[0],84,p[1]))
	for p in points14+points13: check_floor_capsule(world,p,excluded)
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var door14: Node3D = group.get_node("D14_SharedServiceDoor")
	assert(str(door14.persistent_id) == "tidal_d14_shared_service_door_001" and door14.scale == Vector3.ONE)
	for repeat in range(2):
		await cycle_doors(world,player,[door14],group)
	for p in points14.slice(10): check_floor_capsule(world,p,excluded)
	var doors13: Array[Node3D] = [d13.get_node("D13_CleanSupplyDoor"),d13.get_node("D13_SealedReturnsDoor")]
	await cycle_doors(world,player,doors13,d13)
	for p in points13.slice(6): check_floor_capsule(world,p,excluded)
	for door in [door14]+doors13:
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
	var result := {"status":"PASS" if errors.is_empty() else "FAIL","actual_main_loaded":true,"unique_d14_and_d13_installation":true,"d14_corridor_meshes":65,"d14_receiver_meshes":22,"exact_named_replacements":3,"d14_registered_fixture_lights":8,"preserved_d13_registered_fixture_lights":7,"lights_registered_exactly_once":true,"new_d14_floor_area_m2":d.total_new_d14_floor_area_m2,"floor_checks":floor_checks,"capsule_checks":capsule_checks,"external_door_sweep_queries":sweep_queries,"door_close_open_cycles":door_cycles,"closed_guard_rays":guard_checks,"obstruction_checks":obstruction_checks,"d13_and_d14_staff_shaft_closed":true,"abandoned_d14_west_mouths_closed":true,"retained_staff_stops":5,"retained_physical_buttons":5,"retained_staff_cap_top_y":cap.position.y,"public_passenger_lift_unchanged":true,"retained_ordinary_homes":ordinary.size(),"retained_specialty_homes":specialty.size(),"aquatic382_394_identities_preserved":true,"retained_salon_members":13,"errors":errors,"limits":"Bounded actual-main receiving floors, stationary ordinary capsules, retained door cycles and external sweeps only. No upper staff-lift operation, simultaneous segregated/hygiene use, detailed cart/species traversal, structural-load certification, ordinary in-engine/CRT or target hardware acceptance."}
	FileAccess.open("res://artifacts/tidal_d14_service_receiving.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TIDAL_D14_SERVICE_RECEIVING ",JSON.stringify(result))
	print("PASS: bounded D14 receiving and D13 preservation" if errors.is_empty() else "FAIL: bounded D14 receiving")
	quit(0 if errors.is_empty() else 1)

func cycle_doors(world: PhysicsDirectSpaceState3D,player: CharacterBody3D,doors: Array,module: Node3D) -> void:
	for door in doors:
		assert(door.scale == Vector3.ONE and door.leaves.size() == 2)
		door.interact(player)
	for frame in range(100):
		await physics_frame
		for door in doors: check_external_sweep(world,door)
	for door in doors:
		assert(door.open_fraction < .001)
		var pos: Vector3 = door.global_position
		var offsets: Array = [-1.95,-1.6,-.8,0.0,.8,1.6,1.95] if module.name == "TidalD14ServiceReceiving" else [-.8,0.0,.8]
		for offset in offsets:
			var a: Vector3 = pos+Vector3(offset,.75,.9) if module.name == "TidalD14ServiceReceiving" else pos+Vector3(.9,.75,offset)
			var b: Vector3 = pos+Vector3(offset,.75,-1) if module.name == "TidalD14ServiceReceiving" else pos+Vector3(-1,.75,offset)
			var hit := world.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
			if hit.is_empty() or not (module.is_ancestor_of(hit.collider) or "D14_SouthStreetEndGuard" in str(hit.collider.get_path())): errors.append({"kind":"closed_guard","door":str(door.name),"offset":offset,"hit":str(hit.get("collider","none"))})
			guard_checks += 1
		door.interact(player)
	for frame in range(100):
		await physics_frame
		for door in doors: check_external_sweep(world,door)
	for door in doors:
		assert(door.open_fraction > .999)
		door_cycles += 1

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
			sweep_queries += 1
			for hit in world.intersect_shape(q,16):
				if hit.collider is StaticBody3D: errors.append({"kind":"external_door_sweep","door":str(door.name),"fraction":door.open_fraction,"collider":str(hit.collider.get_path())})
