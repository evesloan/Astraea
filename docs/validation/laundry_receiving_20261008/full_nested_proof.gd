extends SceneTree
func _initialize()->void:
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 guard._ensure()
 assert(guard.checked)
 print("LAUNDRY_FULL_NESTED_SOURCE_PASS")
 quit()
