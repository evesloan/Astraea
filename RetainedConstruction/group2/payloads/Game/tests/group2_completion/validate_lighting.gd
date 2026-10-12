extends SceneTree
# Four representative actual-source visibility samples, using the shared manager.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var actor := CharacterBody3D.new()
	world.add_child(actor)
	var rows: Array = []
	for key in ["780", "781", "787", "port_aft_upper_house"]:
		var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(world, key)
		var contract: Dictionary = section.get_meta("source_contract")
		var eye: Array = contract.source_views[0].camera_world_xyz
		actor.global_position = Vector3(eye[0], eye[1]-1.65, eye[2])
		for frame in range(3):
			await physics_frame
		var manager: Node = load("res://scripts/lighting_budget.gd").new()
		section.add_child(manager)
		manager.configure(section, actor)
		var visible: Array = []
		for light in manager.sources:
			if light.visible:
				assert(light.shadow_enabled and light.omni_range == 10.0)
				assert(manager._has_visible_sample(light), "Actual source visibility ray must clear")
				visible.append(str(light.name))
		assert(visible.size() > 0 and visible.size() <= 8, "Visible source fixture admitted within original budget")
		rows.append({"key": key, "normal_source_eye": eye, "source_count": manager.sources.size(),
			"admitted_count": visible.size(), "admitted_sources": visible, "real_receiver_visibility_rays": true})
		section.free()
		await physics_frame
	var file := FileAccess.open("res://artifacts/group2_completion_lighting.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass": true, "samples": rows,
		"global_budget_unchanged": 8, "ranges_m": 10, "pixel_photometry_accepted": false,
		"scope": "Source visibility/budget fixture only; shared ship and final normal-game appearance unaccepted"}, "\t") + "\n")
	print("GROUP2 LIGHTING PASS: four actual-source eye/visibility samples; original eight-source budget and shadows")
	quit()
