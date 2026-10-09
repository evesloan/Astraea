extends RefCounted
# Five-stop Sunset Conservatory passenger connection, using retained common controls.
static func build(house:Node3D)->Node3D:
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="SunsetPassengerLift"
	lift.position=Vector3(-69.5,0,377.2)
	lift.rotation.y=-PI/2
	lift.gate_origin_xz=Vector2.ZERO
	lift.floor_heights.assign([84.0,88.5,93.0,97.5,102.0])
	lift.deck_numbers.assign([13,14,15,16,17])
	lift.identity_prefix="sunset"
	lift.persistent_id=&"sunset_lift_001"
	lift.district_label="Sunset Conservatory"
	lift.cabin_file="AST-CIR-003_five_stop.glb"
	house.add_child(lift)
	return lift
