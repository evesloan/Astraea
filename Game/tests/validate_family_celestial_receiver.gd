extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")
	var receiver:Node3D=house.get_node("FamilyCelestialRoofReceiver")
	assert(receiver.get_meta("source_part_count")==43 and receiver.get_meta("plane_matched_roof_contacts")==25)
	assert(house.get_meta("open_construction_hold")=="FT_RECEIVING_REVIEW_HOLD" and not house.get_meta("receiving_structure_accepted"))
	assert(house.get_meta("installed_guest_units")==82 and house.get_node("RetainedLandscapeAndSeating").get_child_count()==157)
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FAMILY_CELESTIAL_RECEIVER.json"))
	for path in d.source_pins:
		if str(path).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==d.source_pins[path])
	for mesh:MeshInstance3D in receiver.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=mesh.global_transform*mesh.get_aabb()
		assert(bounds.end.y<=83.761,"Receiver projects through residential floor")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.global_position=Vector3(30,78.1,432);actor.velocity=Vector3.ZERO
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
	for i in range(3):await physics_frame
	paused=true
	var physics:=ship.get_world_3d().direct_space_state
	var ceiling_points:Array[Vector3]=[Vector3(15,82.8,416),Vector3(28,82.8,432),Vector3(44,82.8,456)]
	for p in ceiling_points:
		var ray:=PhysicsRayQueryParameters3D.create(p,p+Vector3.UP*1.0);ray.exclude=[actor.get_rid()]
		var hit:=physics.intersect_ray(ray)
		assert(not hit.is_empty(),"Missing retained Celestial ceiling "+str(p))
		assert(hit.position.y<83.44 and not receiver.is_ancestor_of(hit.collider),"New receiving work intrudes below retained roof")
	# Retained inner garden ends at z=482.2; aft witness remains on its actual floor.
	for p in [Vector3(9.2,84,465),Vector3(20,84,432),Vector3(44,84,432),Vector3(28,84,480)]:
		var hit:=physics.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.12,p-Vector3.UP*.30))
		assert(not hit.is_empty() and absf(hit.position.y-84)<.025,"Receiving work changed existing residential floor "+str(p))
	var report={"status":"PASS","receiver_parts":43,"roof_contact_pads":25,"roof_wedges":8,"edge_connected_receivers":1,"original_ceiling_probes":3,"residential_floor_probes":4,"source_game_pins":3,"retained_homes":82,"retained_landscape":157,"open_review":"FT_RECEIVING_REVIEW_HOLD","scope":"Actual main source preservation, below-floor receiver bounds and retained ceiling/floor probes. Plane-matched roof/source contact proof is separate. Full traversal, in-engine visual review and full-ship structural acceptance remain unfinished."}
	FileAccess.open("res://artifacts/family_celestial_receiver.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("FAMILY_CELESTIAL_RECEIVER ",JSON.stringify(report));quit()
