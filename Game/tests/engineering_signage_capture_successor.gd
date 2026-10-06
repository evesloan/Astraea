extends RefCounted
# Signage capture only; no audio listener or blocked controls adoption.
const PROOF := "res://docs/ENGINEERING_SIGNAGE_CAPTURE_ADOPTION.json"
const PROOF_SHA := "1ecbca67f63b0c03322a9a003d68ebb550a0e5cec4a16c88c1e7d33bf18afb3a"
static func validate_successor(path: String, historical: String, actual: String, section: Dictionary) -> bool:
	if path!="scripts/presentation.gd": return false
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA)
	var proof: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.adoption_approved and proof.target==path)
	assert(historical==str(section.historical_sha256) and historical==str(proof.historical_caller_sha256))
	assert(str(section.section_sha256)==str(proof.section_predecessor_sha256))
	assert(str(section.capture_audit_file)==str(proof.previous_capture_audit_file) and str(section.capture_audit_sha256)==str(proof.previous_capture_audit_sha256))
	assert(FileAccess.get_sha256("res://"+str(proof.previous_capture_audit_file))==str(proof.previous_capture_audit_sha256))
	assert(actual==str(proof.candidate_sha256) and FileAccess.get_sha256("res://"+path)==actual)
	var source := FileAccess.get_file_as_string("res://"+path)
	var entry := str(proof.exact_added_entry)
	var state := str(proof.exact_added_state_block)
	assert(source.count(entry)==1 and source.count(state)==1)
	assert(source.count(entry+str(proof.entry_anchor))==1 and source.count(state+str(proof.state_block_anchor))==1)
	assert(source.replace(entry, "").replace(state, "").sha256_text()==str(proof.section_predecessor_sha256))
	return true
