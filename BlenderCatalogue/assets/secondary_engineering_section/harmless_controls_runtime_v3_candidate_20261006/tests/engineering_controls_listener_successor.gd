extends RefCounted
# DRAFT ONLY. Parent must approve/rebase the proof after the theater successor.
# This helper never edits the presentation or discards existing pin history.
const PROOF := "res://docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION.json"
const PROOF_SHA := "d2814ea9abc4ed7b2f62ad2ee2dc6ffeba2801bac34a022ded69485575bb3592"

static func validate_exact_listener_successor(path: String, historical_sha: String,
		actual_sha: String, section_successor: Dictionary) -> bool:
	if path != "scripts/presentation.gd": return false
	assert(FileAccess.get_sha256(PROOF) == PROOF_SHA, "Listener proof bytes differ")
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(bool(proof.adoption_approved), "Listener proof remains a draft")
	assert(str(proof.target) == path)
	assert(historical_sha == str(proof.historical_caller_sha256))
	assert(historical_sha == str(section_successor.historical_sha256))
	assert(str(section_successor.section_sha256) == str(proof.predecessor_sha256))
	assert(actual_sha == str(proof.candidate_sha256))
	assert(FileAccess.get_sha256("res://" + path) == actual_sha)
	var source := FileAccess.get_file_as_string("res://" + path)
	var addition := str(proof.exact_added_line)
	assert(addition == "\tworld_view.audio_listener_enable_3d = true\n")
	assert(source.count(addition) == 1 and source.count(str(proof.anchor_line) + addition) == 1)
	var restored := source.replace(addition, "")
	assert(restored.sha256_text() == str(proof.predecessor_sha256), "Unrelated presentation changes rejected")
	# Caller retains the existing capture-audit and historical-section checks.
	return true
