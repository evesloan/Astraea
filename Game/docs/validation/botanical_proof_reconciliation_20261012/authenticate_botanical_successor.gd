extends SceneTree

func _initialize() -> void:
    load("res://tests/botanical_pair_successor_guard.gd").ensure()
    print("PASS: unchanged Botanical successor authentication and compiler predicates; no runtime acceptance")
    quit(0)
