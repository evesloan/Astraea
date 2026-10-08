extends SceneTree
func _initialize()->void:
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 guard._night_ensure()
 assert(guard.night_checked)
 assert(guard.night_current_compiled.regions.size()==284)
 print("NIGHT_TABLE_WHOLE_SOURCE_PROOF_PASS")
 quit()
