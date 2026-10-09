extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	OS.set_environment("ASTRAEA_FORCE_ALL_RECEIVED_ROOMS","1")
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var house:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
	var homes:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveRoomCandidates")
	assert(homes.get_child_count()==83 and homes.get_meta("default_scene_enabled"))
	assert(house.get_node("LongLibraryCompositeReceivingCore").get_child_count()==143)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==250)
	assert(FileAccess.get_sha256("res://assets/models/WP06_long_library.glb")=="432baa23a4aa7b9dc422f6d6ec5485cf9826bd252d749ec63039785c252e6c5a")
	var identities:Dictionary={}
	for room in ship.get_node("ShipSpace/Districts/TidalRoomCandidates").get_children():identities[str(room.name)]=true
	var anchors:=0
	var checks:=0
	var errors:Array=[]
	var world:=ship.get_world_3d().direct_space_state
	for room:Node3D in homes.get_children():
		assert(not identities.has(str(room.name)))
		identities[str(room.name)]=true
		anchors+=room.get_meta("source_rest_slots").size()
		assert(room.get_node("EntryDoor")!=null and room.get_node("BathroomDoor")!=null)
		for local_z in [-1.0,1.0]:
			var p:=room.to_global(Vector3(0,0,local_z))
			var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4)
			var hit:=world.intersect_ray(query)
			if hit.is_empty() or absf(hit.position.y-p.y)>.04:errors.append({"room":str(room.name),"kind":"interior_floor" if local_z<0 else "street_floor","expected":str(p),"hit":str(hit.get("position","none"))})
			checks+=1
	assert(anchors==215)
	assert(ship.get_node("ShipSystems/ReceivedRoomResidency").entries.size()==231)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","installed_source_units":83,"rest_anchors":anchors,"landscape_instances":250,"composite_receiving_parts":143,"library_source_unchanged":true,"entrance_pair_checks":checks,"interior_floor_checks":83,"street_floor_checks":83,"unique_with_tidal":true,"errors":errors,"scope":"Actual main registration, source identities and bounded entrance-floor checks. Retained stairs present; new passenger lift, full service/hull/support, privacy, occupancy, visual and full traversal acceptance remain unfinished."}
	FileAccess.open("res://artifacts/quiet_default_adoption.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("QUIET_DEFAULT_ADOPTION ",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
