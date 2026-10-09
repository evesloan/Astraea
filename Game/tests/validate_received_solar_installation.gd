extends SceneTree

func _initialize() -> void:
	print("SOLAR_PHASE initialize")
	call_deferred("run")

func run() -> void:
	print("SOLAR_PHASE load production scene")
	var main: Node = load("res://scenes/main.tscn").instantiate()
	print("SOLAR_PHASE build production scene")
	root.add_child(main)
	var ship := main.get_node("World360/Astraea") as Node3D
	print("SOLAR_PHASE production scene ready")
	for frame in range(12):
		await physics_frame
	assert(ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false))
	var old_floors := ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	assert(old_floors.get_child_count() == 303)
	var floors := ship.get_node("ShipSpace/ReceivedSectionStructuralFloors")
	assert(floors.get_child_count() == 2)
	var room := ship.get_node("ShipSpace/Districts/ReceivedSections/D02_directory_09") as Node3D
	assert(room.position == Vector3(-8,6,398))
	assert(room.get_meta("programme_key") == "D02_directory_09")
	assert(room.find_children("*","MeshInstance3D",true,false).size() == 206)
	var rows: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"))
	for i in range(2):
		load("res://tests/medical_triage_successor_guard.gd")._botanical_validate_slab(floors.get_child(i),rows.regions[i])
	var physics := ship.get_world_3d().direct_space_state
	var support_count := 0
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	# Source entry centerline spans the actual existing core,0.2m seam and
	# authored archive floor. These are physical queries, not player traversal.
	for step in range(33):
		var p := Vector3(-6.0 - step*0.25,6,432)
		var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*0.15,p-Vector3.UP*0.4)
		var hit := physics.intersect_ray(ray)
		assert(not hit.is_empty(),"Unsupported receiving seam")
		assert(absf(hit.position.y-6.0)<0.025)
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = capsule
		query.transform = Transform3D(Basis.IDENTITY,p+Vector3.UP*0.925)
		var collisions := physics.intersect_shape(query,32)
		if not collisions.is_empty():
			for collision in collisions: print("BLOCKED_ENTRY ",p," ",collision.collider.get_path())
			quit(1)
			return
		support_count += 1
	var actor := ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	actor.position = Vector3(-6,6.1,432)
	actor.velocity = Vector3.ZERO
	for frame in range(20): await physics_frame
	var walking_frames := 0
	for target_x in [-18.0,-6.0]:
		actor.rotation.y = PI/2 if target_x<actor.position.x else -PI/2
		var down := InputEventKey.new()
		down.physical_keycode=KEY_W; down.keycode=KEY_W; down.pressed=true
		Input.parse_input_event(down)
		var reached := false
		for frame in range(320):
			var before := actor.position
			await physics_frame
			walking_frames += 1
			assert(actor.position.distance_to(before)<.15 and absf(actor.position.y-6)<.08)
			var ray := PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.15,actor.position-Vector3.UP*.2)
			ray.exclude=[actor.get_rid()]
			var support := physics.intersect_ray(ray)
			assert(not support.is_empty() and absf(support.position.y-6)<.02)
			if absf(actor.position.x-target_x)<.08: reached=true; break
		var up := InputEventKey.new()
		up.physical_keycode=KEY_W; up.keycode=KEY_W; up.pressed=false
		Input.parse_input_event(up)
		if not reached: print("ENTRY_WALK_FAILED ",actor.position); quit(1); return
		for frame in range(12): await physics_frame
	var receipt := {"section":"D02_directory_09","old_floor_owners":303,"new_floor_owners":2,"source_mesh_nodes":206,"entry_support_and_capsule_samples":support_count,"ordinary_player_traversal":true,"walking_frames":walking_frames,"initial_verified_arrivals":1,"post_start_teleports":0,"visual_review":false,"scope":"Actual production scene installation, exact shared-builder slab geometry/contact and sampled entry support/clearance and unchanged-player entry/return; final art, cart and full-room acceptance remain separate"}
	var file := FileAccess.open("res://artifacts/received_solar_installation.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt,"\t"))
	print("PASS: received Solar archive main-scene installation and entry support",JSON.stringify(receipt))
	quit()
