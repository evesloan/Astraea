extends RefCounted
# Connected fore-port shell only. Horizontal slabs stay with the floor compiler.
const CONTRACT := "res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json"
# Exact frozen export batches, not a broad stair/guard name match.
const VISUAL_STAIR_BATCHES := [
	"GPM_CELL_-1_-22_5_ASTRAEA_warm_stone_visual_only_stair_tread",
	"GPM_CELL_-1_-22_5_ASTRAEA_dark_rubber_visual_only_stair_tread",
	"GPM_CELL_-1_-21_5_ASTRAEA_warm_stone_visual_only_stair_tread",
	"GPM_CELL_-1_-21_5_ASTRAEA_dark_rubber_visual_only_stair_tread",
	"GPM_CELL_-1_-22_6_ASTRAEA_dark_rubber_visual_only_stair_tread",
	"GPM_CELL_-1_-22_6_ASTRAEA_warm_stone_visual_only_stair_tread"
]

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.catalogue_id == "AST-AQU-016" and data.floor_regions.size() == 8)
	var root := Node3D.new()
	root.name = "GrandPoolOrchardSection_WIP"
	root.set_meta("persistent_id", "grand_pool_orchard_section_001")
	root.set_meta("programme_keys", data.programme_ids)
	root.set_meta("scope", "Connected Grand Pool / Orchard Market architecture; water physics, stock, occupation and final art unfinished")
	parent.add_child(root)
	for identity in [{"name":"GrandPoolProgramme", "key":"D08_directory_01", "alias":"D08_pool0"}, {"name":"OrchardMarketProgramme", "key":"D09_directory_01", "alias":"D09_market0"}]:
		var programme := Node3D.new()
		programme.name = identity.name
		programme.set_meta("programme_key", identity.key)
		programme.set_meta("historical_room_id", identity.alias)
		programme.set_meta("historical_alias_only", true)
		root.add_child(programme)
	var shell: Node3D = ship.model(root, "AST-AQU-016.glb", "GrandPoolConnectedArchitecture", Vector3.ZERO)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	var removed := 0
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		if "glass" in str(mesh.name).to_lower():
			mesh.material_override = glass
		if str(mesh.name) in VISUAL_STAIR_BATCHES:
			var contact := mesh.get_node_or_null("StaticContact")
			assert(contact != null, "Frozen visual stair batch must have only its automatic static contact removed")
			contact.free()
			mesh.set_meta("runtime_collision_contract", "visual_only_stair_tread")
			removed += 1
		else:
			assert(not "visual_only_stair_tread" in str(mesh.name), "Unrecognized stair batch needs an explicit contract update")
	assert(removed == VISUAL_STAIR_BATCHES.size(), "Frozen export is missing a named stair batch")
	# Three exact flight prisms. The real source return landing remains its own
	# static solid; top and arrival landings remain compiler-owned, never doubled.
	for index in range(data.stair_collision_contacts.quads_xyz.size()):
		var points := PackedVector3Array()
		for xyz in data.stair_collision_contacts.quads_xyz[index]:
			var p := Vector3(xyz[0], xyz[1], xyz[2])
			points.append(p)
			points.append(p - Vector3.UP * float(data.stair_collision_contacts.thickness_m))
		var body := StaticBody3D.new()
		body.name = "GrandPoolStairFlightContact_%02d" % index
		var contact := CollisionShape3D.new()
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		shape.margin = .001
		contact.shape = shape
		body.add_child(contact)
		root.add_child(body)
	for entry in data.door_fittings:
		assert(entry.export == "AST-DOR-002_wide.glb")
		var marker := source_marker(shell, "DATUM_" + str(entry.name))
		assert(marker != null, "Door requires its frozen source fitting marker")
		var door: Node3D = load("res://scripts/guest_entry_door.gd").new()
		door.name = ("GrandPoolDoor_" + str(entry.name)).validate_node_name()
		door.persistent_id = StringName("grand_pool_" + str(entry.name).replace(".", "_") + "_door_001")
		door.visual_file = str(entry.export)
		door.leaf_width = 1.18
		door.leaf_travel = 1.24
		door.enclosure_width = 5.16
		door.door_description = "wet stair door" if entry.name == "wet_market_stair" else "wet lift door" if entry.name == "wet_market_lift" else "wet service door" if entry.name == "service_46.2" else "market service door"
		door.position = root.to_local(marker.global_position)
		door.rotation.y = float(entry.yaw_radians)
		door.open_fraction = 0.0
		door.desired_open = false
		root.add_child(door)
	var lift_data: Dictionary = data.wet_market_link.lift
	var lift: Node3D = load("res://scripts/commons_lift.gd").new()
	lift.name = "GrandPoolLocalLift"
	var lift_marker := source_marker(shell, "DATUM_local_lift_root")
	assert(lift_marker != null)
	lift.position = root.to_local(lift_marker.global_position)
	lift.rotation.y = float(lift_data.yaw_radians)
	lift.floor_heights.assign(lift_data.relative_floor_heights)
	lift.deck_numbers.assign([8, 9])
	lift.stop_ids.assign(["D08_WET", "D09"])
	lift.stop_names.assign(["Grand Pool wet terrace", "Orchard Market wet arrival"])
	lift.stop_codes.assign(["08W", "09"])
	lift.gate_origin_xz = Vector2(-1.8, 0)
	lift.identity_prefix = "grand_pool_local"
	lift.district_label = "Grand Pool"
	lift.cabin_file = str(lift_data.cabin_file)
	lift.persistent_id = &"grand_pool_local_lift_001"
	root.add_child(lift)
	assert(data.fixtures.size() == 25)
	for item in data.fixtures:
		var marker := source_marker(shell, str(item.name))
		assert(marker != null, "Every section source needs its real housing/lens marker")
		var light := SpotLight3D.new()
		root.add_child(light)
		light.name = ("GrandPoolSource_" + str(item.name)).validate_node_name()
		light.global_position = marker.global_position
		light.rotation.x = -PI / 2
		ship.apply_light_profile(light, "staff_work" if item.profile == "staff_work" else "aquatic_edge" if item.profile == "wet_terrace" else "guest_lounge")
		light.light_energy = float(item.suggested_energy)
		light.spot_range = float(item.suggested_range_m)
		light.spot_angle = float(item.suggested_spot_angle_degrees)
		light.shadow_enabled = true
		light.set_meta("source_marker", str(item.name))
		# The existing ship-wide LocalShadowSourceBudget discovers these sources
		# after all builders finish; no extra budget or unshadowed fallback exists.
	_build_visual_water(root, ship, data)

static func source_marker(shell: Node, marker_name: String) -> Node3D:
	var marker := shell.find_child(marker_name, true, false) as Node3D
	if marker == null:
		marker = shell.find_child(marker_name.validate_node_name(), true, false) as Node3D
	return marker

static func _build_visual_water(root: Node3D, ship: Node3D, data: Dictionary) -> void:
	# The shared existing shader expects nine non-degenerate perimeter segments.
	# Collinear subdivisions preserve the clear rectangular lane without an island.
	var outline := PackedVector2Array([Vector2(-40,-457), Vector2(-34,-457), Vector2(-28,-457), Vector2(-22,-457), Vector2(-22,-432), Vector2(-22,-407), Vector2(-31,-407), Vector2(-40,-407), Vector2(-40,-432)])
	var material := ShaderMaterial.new()
	material.shader = load("res://shaders/shallow_water.gdshader")
	material.set_shader_parameter("boundary", outline)
	var water: MeshInstance3D = ship.floor_mesh(root, "GrandPoolTrialWater_VisualOnly_NoSwimming", outline, float(data.section.water_level_trial_y), material, false)
	water.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	water.set_meta("scope", "Simple trial water appearance only; no swimming, buoyancy, water entry or physics acceptance")
