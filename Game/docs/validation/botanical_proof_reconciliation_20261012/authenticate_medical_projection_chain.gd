extends SceneTree

func _initialize() -> void:
    load("res://tests/medical_triage_successor_guard.gd")._ensure()
    print("PASS: unchanged nested medical/source projection authentication; no live floor or route acceptance")
    quit(0)
