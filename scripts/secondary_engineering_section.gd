extends RefCounted
# Draft only. Parent installs/invokes after adoption gates; no operating plant controls.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.catalogue_id == "AST-ENG-008")
	for filename in data.model_pins:
		assert(FileAccess.get_sha256("res://assets/models/" + str(filename)) == str(data.model_pins[filename]), "Verified retained model required: " + str(filename))
	assert(data.get("runtime_geometry_gate_accepted", false), "Retained core derivative, receiving shoulders, floor/cap and safety closures must be accepted")
	var root := Node3D.new()
	root.name = "SecondaryEngineeringSection_WIP"
	root.set_meta("persistent_id", "secondary_engineering_section_001")
	root.set_meta("programme_key", "D02_directory_02")
	root.set_meta("scope", "Unfinished construction candidate; essential materials/lighting/furnishings/details and visitor view not accepted; no operating reactor")
	root.set_meta("guest_observation_connected", true)
	root.set_meta("external_staff_connection", "unbuilt; visible east safety closures retained")
	root.set_meta("first_pass_quality_accepted", false)
	parent.add_child(root)
	var shell: Node3D = ship.model(root, "AST-ENG-008_receiving_shoulders.glb", "SecondaryEngineeringArchitecture", Vector3.ZERO)
	# Preserve frozen pressure-glass materials and pane collisions. No shader override.
	assert(data.fixtures.size() == 9)
	for item in data.fixtures:
		var marker := shell.find_child(str(item.name), true, false) as Node3D
		if marker == null:
			marker = shell.find_child(str(item.name).validate_node_name(), true, false) as Node3D
		assert(marker != null, "Real source fixture/lens marker required")
		var light := SpotLight3D.new()
		root.add_child(light)
		light.name = ("SecondaryEngineeringSource_" + str(item.name)).validate_node_name()
		light.global_position = marker.global_position - Vector3.UP * .08
		light.rotation.x = -PI / 2
		ship.apply_light_profile(light, "guest_lounge" if item.purpose == "entry" else "staff_work")
		light.spot_angle = 76.0
		light.shadow_enabled = true
		light.set_meta("source_marker", str(item.name))
	# Ship's existing LocalShadowSourceBudget discovers these nine real sources.
	# No added budget, neutral fill or unshadowed fallback.
	assert(data.get("door_fittings", []).is_empty(), "Open-aperture platform installs no dynamic doors")
	# Visible retained staff wall panels close both east boundaries until the
	# external service floor exists. These are safety barriers, not pressure seals.
	assert(data.temporary_service_closures.size() == 2)
	for closure in data.temporary_service_closures:
		var barrier := Node3D.new()
		barrier.name = ("UnbuiltServiceSafetyClosure_" + str(closure.id)).validate_node_name()
		barrier.set_meta("scope", "Visible temporary safety closure; external service route unbuilt and nonoperational")
		root.add_child(barrier)
		for z in [float(closure.center_z) + 1.2, float(closure.center_z)]:
			ship.model(barrier, "AST-STF-001.glb", "RetainedStaffSafetyPanel", Vector3(53.76, 6.0, z), PI / 2)
		var sign := Label3D.new()
		sign.name = "UnbuiltRouteNotice"
		sign.text = "SERVICE LINK UNBUILT\nTEMPORARY SAFETY CLOSURE"
		sign.font_size = 48
		sign.pixel_size = .004
		sign.position = Vector3(53.70, 7.65, float(closure.center_z))
		sign.rotation.y = -PI / 2
		barrier.add_child(sign)
	# All internal apertures remain visibly unfinished/open. Existing legacy
	# door/controller bytes are untouched; tall profile remains a separate gate.
