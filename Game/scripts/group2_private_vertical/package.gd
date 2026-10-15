extends RefCounted
# Add-on for five retained private suites. Shared roots never call this implicitly.
static func build_for_section(section: Node3D, key: String, receivers_adopted_and_private_access_ready: bool = false) -> Node3D:
	assert(key != "790", "Royalty790 protected shared roof remains held")
	assert(section.global_transform.is_equal_approx(Transform3D.IDENTITY), "Retained world-coordinate source must remain at zero origin")
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_private_vertical/INTERFACES.json"))
	var row: Dictionary = {}
	for candidate in data.suites:
		if str(int(candidate.source_index)) == key:
			row = candidate
	assert(not row.is_empty())
	var lift: Node3D = load("res://scripts/group2_private_vertical/moving_lift.gd").new()
	lift.name = "PrivateVertical_" + key
	lift.position = Vector3(row.origin_world[0], 0, row.origin_world[2])
	lift.rotation.y = float(row.cabin_yaw) + PI/2
	lift.gate_origin_xz = Vector2.ZERO
	lift.floor_heights.assign([102.0, 106.5])
	# Upper gallery is part of the same D17 home; it adds no ship programme/deck.
	lift.deck_numbers.assign([17, 17])
	lift.stop_ids.assign(["private_lower", "private_upper"])
	lift.stop_names.assign(["Lower living", "Upper gallery"])
	lift.stop_codes.assign(["L", "U"])
	lift.identity_prefix = "group2_construction_" + key
	lift.persistent_id = StringName("group2-construction:" + key + ":private_lift")
	lift.district_label = "Private suite"
	lift.operation_ready = receivers_adopted_and_private_access_ready
	lift.set_meta("source_index", row.source_index)
	lift.set_meta("production_identity_adopted", false)
	lift.set_meta("physical_receiver_adopted", receivers_adopted_and_private_access_ready)
	section.add_child(lift)
	for gate in lift.landing_gates:
		gate.position.x = -float(row.landing_gate_outward_mount_m)
	for light in lift.find_children("*", "Light3D", true, false):
		light.visible = false
	# Keep the inherited eight-source manager responsible for all cabin lights.
	if not receivers_adopted_and_private_access_ready:
		lift.phase = "held_receivers_and_private_access"
		lift.cabin_gate.cabin_present_and_stopped = false
		lift.cabin_gate.request_close()
		for gate in lift.landing_gates:
			gate.cabin_present_and_stopped = false
			gate.request_close()
	return lift

static func build_conversation_receiver(section: Node3D, key: String, base_receiver_adopted: bool) -> Node3D:
	assert(base_receiver_adopted and key != "790")
	assert(section.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var receiver: Node3D = (load("res://assets/group2_private_vertical/CONVERSATION_"+key+"_r001.glb") as PackedScene).instantiate()
	receiver.name = "ConversationReceiver_" + key
	receiver.set_meta("same_private_unit",true)
	receiver.set_meta("full_pit_perimeter_accepted",false)
	section.add_child(receiver)
	load("res://scripts/static_contact_cache.gd").attach_group(receiver,receiver.find_children("*","MeshInstance3D",true,false))
	return receiver
