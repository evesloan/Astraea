extends RefCounted
# Isolated candidate only. No shared bootstrap calls this. Original AST-RES-006
# must be replaced exactly once when explicitly adopted, never double-instanced.
const RECEIPT := "res://royalty_790_completion_20261020/evidence/BUILD_RECEIPT.json"
const MODEL := "res://royalty_790_completion_20261020/exports/ROYALTY790_upper_candidate_r002.glb"
static func build_candidate(parent: Node3D, private_access_and_receivers_accepted: bool = false) -> Node3D:
	assert(parent.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var result := Node3D.new()
	result.name = "Royalty790UpperCandidate"
	result.set_meta("source_index", 790)
	result.set_meta("adopted", false)
	parent.add_child(result)
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(MODEL, state) == OK)
	var source := document.generate_scene(state) as Node3D
	result.add_child(source)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RECEIPT))
	var meshes: Array[Node] = []
	for child in source.find_children("*", "MeshInstance3D", true, false):
		# Visual stair treads use the faithful continuous ramp contacts below.
		if child.name.begins_with("RG_StairFlight_") or child.name.begins_with("RG_StairNosing_"):
			continue
		meshes.append(child as MeshInstance3D)
	load("res://scripts/static_contact_cache.gd").attach_group(source, meshes)
	for row in data.collision_ramps:
		var body := StaticBody3D.new()
		body.name = row.name
		var shape := ConvexPolygonShape3D.new()
		var points := PackedVector3Array()
		for p in row.vertices:
			points.append(Vector3(p[0], p[1], p[2]))
		shape.points = points
		shape.margin = 0.001
		var contact := CollisionShape3D.new()
		contact.shape = shape
		body.add_child(contact)
		result.add_child(body)
	# Reuse unchanged retained cabin, gates and controls. Raised lower receiver
	# preserves continuous lower floor and protected homes: no pit is excavated.
	var lift: Node3D = load("res://scripts/group2_private_vertical/moving_lift.gd").new()
	lift.name = "Royalty790PrivateLift"
	lift.position = Vector3(101.75, 0, 45.65)
	lift.rotation.y = -PI / 2
	lift.gate_origin_xz = Vector2.ZERO
	lift.floor_heights.assign([102.2, 106.5])
	lift.deck_numbers.assign([17, 17])
	lift.stop_ids.assign(["private_lower", "private_upper"])
	lift.stop_names.assign(["Lower living", "Upper gallery"])
	lift.stop_codes.assign(["L", "U"])
	lift.identity_prefix = "royalty790_candidate"
	lift.persistent_id = &"royalty790_candidate_private_lift"
	lift.district_label = "Private suite"
	lift.operation_ready = private_access_and_receivers_accepted
	result.add_child(lift)
	if not private_access_and_receivers_accepted:
		lift.phase = "held_receivers_and_private_access"
		lift.cabin_gate.cabin_present_and_stopped = false
		lift.cabin_gate.request_close()
		for gate in lift.landing_gates:
			gate.cabin_present_and_stopped = false
			gate.request_close()
	# All light bindings are local to physical source fixtures.
	for marker in source.find_children("DATUM_*light*", "Node3D", true, false):
		var light := OmniLight3D.new()
		light.name = "SourceFixtureLight"
		light.position = marker.position
		light.omni_range = 5.0
		light.light_energy = 0.65
		light.light_color = Color(1.0, 0.91, 0.78)
		light.shadow_enabled = false
		source.add_child(light)
	return result
