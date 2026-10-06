extends "res://tests/validate_commons_lift.gd"
# The common fixture resets cart/products only once, before its first trip.
# Every subsequent ascent, descent and gate obstruction is ordinary physics.
func _initialize() -> void:
	target_lift_name = "GrandPoolLocalLift"
	test_stop_sequence.assign([1,0])
	super._initialize()

func select_floor_by_focus(lift: Node3D, actor: CharacterBody3D, goal: int) -> void:
	assert(lift.get_script().resource_path == "res://scripts/commons_lift.gd")
	assert(lift.persistent_id == &"grand_pool_local_lift_001" and lift.identity_prefix == "grand_pool_local")
	assert(lift.floor_heights == [0.0,6.3] and lift.deck_numbers == [8,9])
	assert(lift.stop_ids == ["D08_WET","D09"] and lift.stop_codes == ["08W","09"])
	assert(lift.cabin_file == "AST-CIR-003.glb" and lift.landing_gates.size() == 2)
	assert(lift.global_position.distance_to(Vector3(-15.4,46.2,-412.4)) < .001)
	assert(absf(absf(lift.rotation.y)-PI) < .001)
	var button: Node3D = lift.find_child(lift.identity_prefix+"_cabin_"+lift._stop_id(goal),true,false)
	assert(button != null and button.controller == lift and button.floor_index == goal)
	assert(button.persistent_id == StringName(lift.identity_prefix+"_cabin_"+lift._stop_id(goal)))
	await super.select_floor_by_focus(lift,actor,goal)

func wait_trip(lift: Node3D, cart: RigidBody3D, actor: CharacterBody3D, goal: int) -> void:
	# Preserve all inherited per-frame cabin/static-geometry, cart, capsule,
	# four-loose-product, acceleration and closed-travel-gate assertions.
	await super.wait_trip(lift,cart,actor,goal)
	assert(lift.current_floor == goal and lift.cabin_gate.cabin_present_and_stopped)
	for index in range(2):
		var gate: Node3D = lift.landing_gates[index]
		assert(gate.persistent_id == StringName(lift._stop_id(index)+"_grand_pool_local_lift_gate"))
		assert(gate.cabin_present_and_stopped == (index == goal))
		assert(gate.open_fraction > .999 if index == goal else gate.open_fraction < .001)
