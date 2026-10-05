extends "res://tests/validate_commons_lift.gd"
func _initialize()->void:
	target_lift_name="ForwardStaffLift"
	test_stop_sequence.assign([1,2,0])
	super._initialize()
