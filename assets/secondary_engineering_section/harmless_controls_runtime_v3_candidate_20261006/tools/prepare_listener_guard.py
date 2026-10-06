#!/usr/bin/env python3
"""Generate a separate draft listener proof validator, not the shared guard."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];p=R/'docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json';digest=hashlib.sha256(p.read_bytes()).hexdigest()
s='''extends RefCounted
# DRAFT ONLY. Parent must approve/rebase the proof after the theater successor.
# This helper never edits the presentation or discards existing pin history.
const PROOF := "res://docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION.json"
const PROOF_SHA := "%s"

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
	assert(addition == "\\tworld_view.audio_listener_enable_3d = true\\n")
	assert(source.count(addition) == 1 and source.count(str(proof.anchor_line) + addition) == 1)
	var restored := source.replace(addition, "")
	assert(restored.sha256_text() == str(proof.predecessor_sha256), "Unrelated presentation changes rejected")
	# Caller retains the existing capture-audit and historical-section checks.
	return true
''' % digest
(R/'tests/engineering_controls_listener_successor.gd').write_text(s)
(R/'integration/SHARED_GUARD_HOOK.txt').write_text('''FUTURE PARENT-REVIEWED HOOK SPECIFICATION, not a patch to the active theater guard.

The theater worker preserves the existing presentation successor and adds theater_successor() for layout, compiled geometry and ship.gd only.

After the shared guard accepts the existing section-byte case, and before its theater-only path allowlist, add a presentation-only branch that calls:

load("res://tests/engineering_controls_listener_successor.gd").validate_exact_listener_successor(path, historical_sha, actual, section_proof().explicit_runtime_pin_successors[path])

Return only when that helper returns true. Preserve the existing presentation capture audit hash check as well. Do not replace the historical caller SHA, section proof, its constants, or the theater proof. The helper verifies an exact single listener-line addition and reverses it to the exact approved presentation predecessor; unknown presentation changes fail.

This candidate proof is based on the currently observed 94ad78... Game. After theater lands, re-read its shared guard, presentation and validation wrapper. If presentation changed, obtain an explicit successor design before updating this proof; never treat an arbitrary current presentation as the historical section predecessor. Update proof/adoption approval and pinned helper SHA together only in the accepting integration lane. This file does not authorize live edits.
''')
print('Standalone draft listener guard generated; shared guard untouched.')
