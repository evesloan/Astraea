extends "res://tests/validate_commons_lift.gd"
func _initialize() -> void:
	test_stop_sequence.assign([1,2,3,4,0])
	call_deferred("run")
