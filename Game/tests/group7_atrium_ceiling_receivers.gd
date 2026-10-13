extends "res://tests/validate_d04_port_forward_commons_service.gd"

func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	var rows: Array = []
	for x: float in [-40, -28, -16, 0, 16, 28, 40]:
		for z: float in [-58, -46, -24, 0, 24, 46, 58]:
			var emitter := Vector3(x, 106.1, z)
			var cap: Dictionary = ray(space, Vector3(x, 106.20, z), Vector3(x, 106.31, z))
			var down: Dictionary = ray(space, emitter, Vector3(x, 74, z))
			var path: String = str(down.collider.get_path()) if not down.is_empty() else "NONE"
			var compiled: bool = path.contains("/CompiledStructuralFloors_NotFinishedRooms/") or path.contains("/ReceivingSourceStructuralFloors/")
			var standing: bool = false
			if compiled: standing = capsule_clear(space, Vector3(x, down.position.y, z))
			rows.append({"emitter": [x, 106.1, z], "cap_receiver": str(cap.collider.get_path()) if not cap.is_empty() else "NONE",
				"cap_y": cap.position.y if not cap.is_empty() else 0, "first_down_receiver": path,
				"first_down_y": down.position.y if not down.is_empty() else 0,
				"first_receiver_original_compiled_floor": compiled, "ordinary_worker_stance_clear": standing})
	var originals: Array = []
	for name: String in ["ArtificialDaylightCoffer_Fore", "ArtificialDaylightCoffer_Aft"]:
		var node: Node3D = ship.find_child(name, true, false)
		originals.append({"name": name, "found": node != null, "path": str(node.get_path()) if node != null else "NONE", "position": [node.global_position.x, node.global_position.y, node.global_position.z] if node != null else []})
	var out: Dictionary = {"status": "READ_ONLY_ACTUAL_BASELINE_RECEIVER_SURVEY", "probe_count": rows.size(), "rows": rows,
		"original_coffers": originals, "player_position_writes": 0, "source_or_floor_changes": 0,
		"new_ceiling_or_light_accepted": false}
	FileAccess.open("res://../external_packages/group7_completion_20261011/continuation_r011/qa/ACTUAL_CEILING_RECEIVERS.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ")+"\n")
	print(JSON.stringify({"status": out.status, "probes": rows.size(), "original_coffers": originals.size()}))
	quit(0)
