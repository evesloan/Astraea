extends "res://tests/validate_commons_lift.gd"
func _initialize()->void:
	target_lift_name="PrimaryAtriumLift"
	test_stop_sequence.assign([17,0])
	super._initialize()
