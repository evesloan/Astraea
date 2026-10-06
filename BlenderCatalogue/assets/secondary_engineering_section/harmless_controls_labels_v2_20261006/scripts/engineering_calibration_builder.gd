extends RefCounted
# SCRATCH DRAFT. Integration is a separate reviewed step after core cell physics.
# Call once with the EXISTING imported visual; never load another room duplicate.
const ControlScript := preload("res://scripts/engineering_calibration_control.gd")
const BankScript := preload("res://scripts/engineering_calibration_bank.gd")
const AudioScript := preload("res://scripts/engineering_calibration_audio.gd")
const CONTRACT := "res://data/architecture/ENGINEERING_CALIBRATION_DRAFT.json"

static func build(parent: Node3D, visual: Node3D) -> Node3D:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	# Must remain false in this delivered draft. The accepting integration lane
	# makes a reviewed contract revision after actual cell geometry/physics gates.
	if not data.get("adoption_gate_accepted", false):
		push_error("Calibration controls are not yet accepted for integration")
		return null
	assert(parent.is_inside_tree() and visual.is_inside_tree())
	assert(parent.get_node_or_null("EngineeringCalibrationBank") == null)
	assert(int(data.control_count) == 120 and data.controls.size() == 120)
	assert(int(data.max_active_controls) == 4)
	assert(not data.cake.enabled and int(data.cake.spawn_budget) == 0)
	assert(FileAccess.get_sha256("res://assets/models/" + str(data.model_file)) == str(data.model_sha256))
	# No player/controller adjustments are an allowed integration shortcut.
	for path in ["scripts/player.gd", "scripts/fixture_switch.gd", "scripts/physics_tether.gd", "scripts/service_door.gd", "scripts/engineering_cell_gate.gd", "scripts/engineering_cell_gate_target.gd", "scripts/lighting_budget.gd"]:
		assert(FileAccess.get_sha256("res://" + path) == str(data.retained_runtime_pins[path]))
	# Single startup pass over this imported subtree. No per-frame room scans.
	var index: Dictionary = {}
	var pending: Array[Node] = [visual]
	while not pending.is_empty():
		var node: Node = pending.pop_back()
		var label := str(node.name)
		if label.begins_with("ACT_ENG2_") or label.begins_with("TARGET_ENG2_"):
			assert(not index.has(label), "Duplicate source control identity: " + label)
			index[label] = node
		for child in node.get_children(): pending.append(child)
	var seen: Dictionary = {}
	for item in data.controls:
		assert(not seen.has(str(item.id)))
		seen[str(item.id)] = true
		assert(index.has(str(item.source_marker)) and index.has(str(item.actuator_mesh_name)))
		var mesh := index[str(item.actuator_mesh_name)] as MeshInstance3D
		var marker := index[str(item.source_marker)] as Node3D
		assert(mesh != null and marker != null and mesh.material_override == null)
		assert(mesh.get_node_or_null("StaticContact") == null)
		assert(mesh.mesh.get_surface_count() == item.runtime_materials.size())
		for surface in range(mesh.mesh.get_surface_count()):
			assert(mesh.get_surface_override_material(surface) == null)
			assert(str(mesh.get_active_material(surface).resource_name) == str(item.runtime_materials[surface]))
	var bank := Node3D.new()
	bank.name = "EngineeringCalibrationBank"
	bank.set_script(BankScript)
	parent.add_child(bank)
	bank.max_active_controls = int(data.max_active_controls)
	var audio := Node3D.new()
	audio.name = "CalibrationAudio"
	audio.set_script(AudioScript)
	bank.add_child(audio)
	audio.configure(data.audio)
	bank.audio_owner = audio
	for item in data.controls:
		var control := Node3D.new()
		control.name = str(item.id)
		control.set_script(ControlScript)
		bank.add_child(control)
		control.configure(bank, visual, index[str(item.actuator_mesh_name)], index[str(item.source_marker)], item)
		bank.controls_by_id[str(item.id)] = control
	assert(bank.controls_by_id.size() == 120)
	bank.set_meta("source_model_sha256", str(data.model_sha256))
	bank.set_meta("only_local_calibration_effects", true)
	return bank
