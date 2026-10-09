extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	OS.set_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION", "0")
	OS.set_environment("ASTRAEA_FORCE_ALL_RECEIVED_ROOMS", "1")
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for frame in range(12): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var house: Node3D = ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var homes: Node3D = ship.get_node("ShipSpace/Districts/TidalRoomCandidates")
	var core: Node3D = house.get_node("ListeningSalonCompositeCapReceivingCore")
	assert(homes.get_child_count()==85)
	assert(homes.get_meta("default_scene_enabled"))
	assert(core.get_child_count()==13)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==81)
	var lift: Node3D = house.get_node("TidalGardenPassengerLiftCandidate")
	assert(lift.floor_heights.size()==5)
	assert(ship.find_child("D13_13017_TwinSuite_WIP",true,false)!=null)
	assert(ship.find_child("D13_13041_TwinSuite_WIP",true,false)!=null)
	var ids: Dictionary = {}
	var anchors := 0
	var floor_checks := 0
	var errors: Array = []
	var world := ship.get_world_3d().direct_space_state
	for room: Node3D in homes.get_children():
		assert(not ids.has(room.name))
		ids[room.name]=true
		anchors += room.get_meta("source_rest_slots").size()
		assert(room.get_node("EntryDoor")!=null and room.get_node("BathroomDoor")!=null)
		var p:=room.to_global(Vector3(0,0,1.0))
		var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4)
		var hit:=world.intersect_ray(q)
		if hit.is_empty() or absf(hit.position.y-p.y)>.04: errors.append({"home":str(room.name),"kind":"entry_floor"})
		floor_checks+=1
	assert(anchors==221)
	var result: Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","default_scene_enabled":true,"installed_source_units":85,"rest_anchors":anchors,"landscape_instances":81,"lift_stops":5,"named_cap_members":13,"entry_floor_checks":floor_checks,"errors":errors,"scope":"Actual default-scene registration and bounded floor checks. No full traversal, visual, occupancy, performance, privacy or cart acceptance."}
	FileAccess.open("res://artifacts/tidal_default_adoption.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TIDAL_DEFAULT_ADOPTION ",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
