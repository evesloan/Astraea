extends SceneTree
# UNRUN. Engine-side byte tests for the new helper; no main scene or audio starts.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var helper := load("res://tests/engineering_controls_listener_successor.gd")
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION.json"))
	var sign: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://"+str(proof.signage_capture_proof_file)))
	var preservation: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://"+str(proof.section_preservation_file)))
	var section: Dictionary = preservation.explicit_runtime_pin_successors["scripts/presentation.gd"]
	var source := FileAccess.get_file_as_string("res://scripts/presentation.gd")
	var actual := source.sha256_text()
	assert(helper.validate_presentation_bytes(source,proof,sign,section,actual),"Exact two-stage byte reversal must pass")
	var public_result: bool = helper.validate_successor("scripts/presentation.gd",str(proof.historical_caller_sha256),actual,section)
	assert(public_result == bool(proof.adoption_approved),"Public gate must additionally enforce adoption and pinned live files")
	var line := str(proof.exact_added_line)
	var anchor := str(proof.anchor_line)
	var changes := [
		["listener_missing",source.replace(line,"")],
		["listener_duplicate",source.replace(line,line+line)],
		["listener_disabled",source.replace("world_view.audio_listener_enable_3d = true","world_view.audio_listener_enable_3d = false")],
		["listener_wrong_viewport",source.replace("world_view.audio_listener_enable_3d = true","post_view.audio_listener_enable_3d = true")],
		["listener_wrong_anchor",source.replace(anchor+line,line+anchor)],
		["unrelated_hud",source.replace("WASD · Mouse","WASD · New HUD")],
		["unrelated_renderer",source.replace("world_view.size = Vector2i(640, 360)","world_view.size = Vector2i(800, 450)")],
		["unrelated_fov",source.replace("actor.camera.fov-72.0","actor.camera.fov-90.0")],
		["unrelated_comment",source+"\n# Unreviewed unrelated change\n"],
		["sign_entry_removed",source.replace(str(sign.exact_added_entry),"")],
		["sign_entry_duplicated",source.replace(str(sign.exact_added_entry),str(sign.exact_added_entry)+str(sign.exact_added_entry))],
		["sign_pose_changed",source.replace("Vector3(20.77,6.04,-404.5)","Vector3(21.00,6.04,-404.5)")],
		["older_capture_changed",source.replace("Vector3(-9.4,44.1,-432)","Vector3(-9.8,44.1,-432)")],
		["sign_state_removed",source.replace(str(sign.exact_added_state_block),"")],
		["sign_gate_action_changed",source.replace("closing_gate.interact(actor)","closing_gate.desired_open = false")],
		["old_listener_without_sign",source.replace(str(sign.exact_added_entry),"").replace(str(sign.exact_added_state_block),"")]
	]
	var negatives: Array = []
	for row in changes:
		var mutated: String = row[1]
		assert(mutated != source,"Negative fixture must change bytes: "+str(row[0]))
		assert(not helper.validate_presentation_bytes(mutated,proof,sign,section,mutated.sha256_text()),str(row[0]))
		var relabelled: Dictionary = proof.duplicate(true)
		relabelled.candidate_sha256 = mutated.sha256_text()
		assert(not helper.validate_presentation_bytes(mutated,relabelled,sign,section,mutated.sha256_text()),"Reversal must reject even relabelled candidate hash: "+str(row[0]))
		negatives.append(str(row[0]))
	for row in [["proof","historical_caller_sha256"],["proof","signage_predecessor_sha256"],
		["proof","section_predecessor_sha256"],["proof","target"],["sign","candidate_sha256"],
		["sign","previous_capture_audit_sha256"],["section","historical_sha256"],["section","capture_audit_file"]]:
		var p: Dictionary = proof.duplicate(true)
		var s: Dictionary = sign.duplicate(true)
		var c: Dictionary = section.duplicate(true)
		var altered: Dictionary = p if row[0] == "proof" else s if row[0] == "sign" else c
		altered[str(row[1])] = "UNREVIEWED"
		assert(not helper.validate_presentation_bytes(source,p,s,c,actual),"Wrong historical/proof value accepted")
		negatives.append(str(row[0])+"/"+str(row[1]))
	print(JSON.stringify({"status":"ENGINE_BYTE_CHAIN_CHECK_PASS","actual_presentation_sha256":actual,
		"pure_positive":true,"public_approval_gate":public_result,"negative_cases":negatives,
		"main_scene_loaded":false,"audio_output_captured":false,"audibility_accepted":false}))
	quit(0)
