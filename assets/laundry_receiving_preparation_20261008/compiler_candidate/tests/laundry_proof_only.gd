extends SceneTree
func _initialize()->void:
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 guard._laundry_ensure()
 assert(guard.laundry_checked and guard.laundry_current_compiled.regions.size()==286)
 print("LAUNDRY_WHOLE_SOURCE_PROOF_PASS")
 quit()
