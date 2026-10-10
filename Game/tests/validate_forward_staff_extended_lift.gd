extends "res://tests/validate_commons_lift.gd"
# New extension coverage is separate from the retained lower-only [1,2,0] test.
# Visit every fixed stop upward and downward without resetting any carried body.
func _initialize() -> void:
	target_lift_name = "ForwardStaffLift"
	test_stop_sequence.assign([1,2,3,4,3,2,1,0])
	super._initialize()

func select_floor_by_focus(lift: Node3D, actor: CharacterBody3D, goal: int) -> void:
	assert(lift.get_script().resource_path == "res://scripts/commons_lift.gd")
	assert(lift.persistent_id == &"forward_staff_lift_001" and lift.identity_prefix == "forward_staff")
	assert(lift.floor_heights.slice(0,5) == [0.0,6.0,12.0,46.2,52.5] and lift.deck_numbers.slice(0,5) == [1,2,3,8,9])
	assert(lift.stop_ids.slice(0,5) == ["D01","D02","D03","D08_WET","D09"])
	assert(lift.stop_codes.slice(0,5) == ["01","02","03","08W","09"])
	assert(lift.stop_names.slice(0,5) == ["Synthesis service","Fusion maintenance","Crew and depot thresholds","D08 wet service","D09 market service"])
	assert(lift.cabin_file == "AST-CIR-003_ten_stop.glb" and lift.landing_gates.size() == 10)
	assert(lift.global_position.distance_to(Vector3(-25,0,-490)) < .001)
	assert(absf(absf(lift.rotation.y)-PI) < .001)
	var button: Node3D = lift.find_child(lift.identity_prefix+"_cabin_"+lift._stop_id(goal),true,false)
	assert(button != null and button.controller == lift and button.floor_index == goal)
	assert(button.persistent_id == StringName(lift.identity_prefix+"_cabin_"+lift._stop_id(goal)))
	assert(button.destination_name == lift.stop_names[goal] and button.face_code == lift.stop_codes[goal])
	await super.select_floor_by_focus(lift,actor,goal)

func wait_trip(lift: Node3D, cart: RigidBody3D, actor: CharacterBody3D, goal: int) -> void:
	# This includes both passes through the blank D04-D07 shaft, with every
	# inherited live static-collision/interlock and carried-load check intact.
	await super.wait_trip(lift,cart,actor,goal)
	assert(lift.current_floor == goal and lift.cabin_gate.cabin_present_and_stopped)
	for index in range(5):
		var gate: Node3D = lift.landing_gates[index]
		assert(gate.persistent_id == StringName(lift._stop_id(index)+"_forward_staff_lift_gate"))
		assert(gate.cabin_present_and_stopped == (index == goal))
		assert(gate.open_fraction > .999 if index == goal else gate.open_fraction < .001)
