extends "res://tests/validate_commons_lift.gd"
func _initialize()->void:
	target_lift_name="PrimaryAtriumLift"
	test_stop_sequence.assign([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,0])
	super._initialize()
