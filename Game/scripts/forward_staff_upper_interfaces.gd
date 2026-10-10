extends RefCounted
# Physical upper envelope and held-closed landing interfaces; original lift remains five-stop.
const DATA := "res://data/architecture/FORWARD_STAFF_UPPER_INTERFACES.json"
static func build(root: Node3D,ship: Node3D) -> Node3D:
	var existing := root.get_node_or_null("ForwardStaffUpperInterfaces") as Node3D
	if existing != null: return existing
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	assert(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb") == d.original_lower_sha256)
	for item in d.model_bindings: assert(FileAccess.get_sha256("res://assets/models/"+str(item.file)) == item.sha256)
	var group := Node3D.new()
	group.name = "ForwardStaffUpperInterfaces"
	group.set_meta("persistent_id","forward_staff_upper_interfaces_001")
	group.set_meta("upper_operation_enabled",false)
	group.set_meta("temporary_receiving_closures_retained",true)
	group.set_meta("structural_load_capacity_accepted",false)
	root.add_child(group)
	var visual: Node3D = load("res://assets/models/"+str(d.envelope_file)).instantiate()
	visual.name = "RetainedUpperEnvelopeAndSills"
	group.add_child(visual)
	var meshes := visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size() == 43)
	for mesh: MeshInstance3D in meshes: load("res://scripts/static_contact_cache.gd").attach(mesh)
	var patch: Node3D = load("res://assets/models/"+str(d.cap_patch_file)).instantiate()
	group.add_child(patch)
	var lower: Node3D = root.get_node("LowerStaffEnclosure")
	for spec in d.cap_replacements:
		var target := lower.find_child(str(spec.mesh),true,false) as MeshInstance3D
		var replacement := patch.find_child(str(spec.mesh),true,false) as MeshInstance3D
		assert(target != null and replacement != null)
		var old := target.get_node("StaticContact")
		target.remove_child(old)
		old.free()
		target.mesh = replacement.mesh
		target.global_transform = replacement.global_transform
		target.set_meta("exact_cap_only_successor",true)
		load("res://scripts/static_contact_cache.gd").attach(target)
	patch.free()
	for spec in d.interfaces:
		var gate: Node3D = load("res://scripts/lift_gate.gd").new()
		gate.name = "HeldLandingGate_D"+str(int(spec.deck))
		gate.persistent_id = StringName(str(spec.gate_id))
		gate.position = Vector3(spec.gate_center[0],spec.gate_center[1],spec.gate_center[2])
		gate.rotation.y = float(spec.gate_yaw)
		gate.set_meta("activation","held_closed_until_existing_lift_binding_and_sweep_verified")
		group.add_child(gate)
		assert(not gate.cabin_present_and_stopped and not gate.requested_open)
	group.set_meta("upper_gate_count",5)
	group.set_meta("envelope_mesh_count",43)
	group.set_meta("old_cap_triangle_count_removed",12)
	var lift := root.get_node_or_null("ForwardStaffLift")
	if lift != null: assert(lift.floor_heights.slice(0,5) == [0.0,6.0,12.0,46.2,52.5])
	return group
