extends RefCounted
# Conditional sign-capture -> listener successor. No historical file is rewritten.
# Pure byte validation is separately exposed for negative tests; only the public
# successor entry point checks approval, all proof pins and the actual live file.
const PROOF := "res://docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION.json"
const PROOF_SHA := "284daccbe85fc2c8e5c98a3808989aa7a6c12365130ead93e8eba69f0bea1b62"
const HISTORICAL := "c225697f5c5d59f0ece4e24eb17a2c46efa752cb17385c8cbcd1d56ce81377b8"
const SECTION := "76f5cef2f50caec7d49facd8ed34579c46fef37605c9f3d63050a986eddc4a80"
const SIGN := "aabcfa21a0dd0ab763ef08bc7a0ba3422bea1df9f9383e5b2999e4dfa1198c51"
const LISTENER := "\tworld_view.audio_listener_enable_3d = true\n"
const ANCHOR := "\tworld_view.own_world_3d = true\n"

static func validate_successor(path: String, historical: String, actual: String, section: Dictionary) -> bool:
	if path != "scripts/presentation.gd" or historical != HISTORICAL: return false
	if FileAccess.get_sha256(PROOF) != PROOF_SHA: return false
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	if not bool(proof.get("adoption_approved", false)): return false
	for pair in [["signage_capture_proof_file","signage_capture_proof_sha256"],
		["signage_capture_helper_file","signage_capture_helper_sha256"],
		["section_capture_audit_file","section_capture_audit_sha256"],
		["section_preservation_file","section_preservation_sha256"]]:
		if FileAccess.get_sha256("res://" + str(proof[pair[0]])) != str(proof[pair[1]]): return false
	var retained: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://" + str(proof.section_preservation_file)))
	if retained.explicit_runtime_pin_successors["scripts/presentation.gd"] != section: return false
	var sign_proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://" + str(proof.signage_capture_proof_file)))
	if not bool(sign_proof.get("adoption_approved", false)): return false
	if FileAccess.get_sha256("res://" + path) != actual: return false
	var source := FileAccess.get_file_as_string("res://" + path)
	return validate_presentation_bytes(source, proof, sign_proof, section, actual)

static func validate_presentation_bytes(source: String, proof: Dictionary, sign_proof: Dictionary,
		section: Dictionary, actual: String) -> bool:
	# This function proves ONLY the two exact byte reversals. It does not grant
	# adoption or read a substitute string as though it were the live file.
	if str(proof.get("target", "")) != "scripts/presentation.gd": return false
	if str(proof.get("historical_caller_sha256", "")) != HISTORICAL: return false
	if str(section.get("historical_sha256", "")) != HISTORICAL: return false
	if str(sign_proof.get("historical_caller_sha256", "")) != HISTORICAL: return false
	if str(section.get("section_sha256", "")) != SECTION: return false
	if str(proof.get("section_predecessor_sha256", "")) != SECTION: return false
	if str(sign_proof.get("section_predecessor_sha256", "")) != SECTION: return false
	if str(proof.get("signage_predecessor_sha256", "")) != SIGN: return false
	if str(sign_proof.get("candidate_sha256", "")) != SIGN: return false
	if str(sign_proof.get("target", "")) != "scripts/presentation.gd": return false
	if str(proof.get("section_capture_audit_file", "")) != str(section.get("capture_audit_file", "")): return false
	if str(proof.get("section_capture_audit_sha256", "")) != str(section.get("capture_audit_sha256", "")): return false
	if str(sign_proof.get("previous_capture_audit_file", "")) != str(section.get("capture_audit_file", "")): return false
	if str(sign_proof.get("previous_capture_audit_sha256", "")) != str(section.get("capture_audit_sha256", "")): return false
	if source.sha256_text() != actual or actual != str(proof.get("candidate_sha256", "")): return false
	if str(proof.get("exact_added_line", "")) != LISTENER or str(proof.get("anchor_line", "")) != ANCHOR: return false
	if source.count(LISTENER) != 1 or source.count(ANCHOR + LISTENER) != 1: return false
	var sign_source := source.replace(LISTENER, "")
	if sign_source.sha256_text() != SIGN: return false
	var entry := str(sign_proof.get("exact_added_entry", ""))
	var state := str(sign_proof.get("exact_added_state_block", ""))
	if entry.is_empty() or state.is_empty(): return false
	if sign_source.count(entry) != 1 or sign_source.count(state) != 1: return false
	if sign_source.count(entry + str(sign_proof.get("entry_anchor", ""))) != 1: return false
	if sign_source.count(state + str(sign_proof.get("state_block_anchor", ""))) != 1: return false
	return sign_source.replace(entry, "").replace(state, "").sha256_text() == SECTION
