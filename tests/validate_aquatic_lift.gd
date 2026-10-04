extends "res://tests/validate_commons_lift.gd"
func _initialize() -> void:
	target_lift_name="AquaticPassengerLift"
	test_stop_sequence.assign([2,1,0])
	super._initialize()
