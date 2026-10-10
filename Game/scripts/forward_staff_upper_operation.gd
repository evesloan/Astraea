extends RefCounted
const DATA := "res://data/architecture/FORWARD_STAFF_UPPER_OPERATION.json"
static func build(ship: Node3D,house: Node3D) -> bool:
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var staff: Node3D = ship.find_child("ForwardStaffLift",true,false)
	var interfaces: Node3D = ship.find_child("ForwardStaffUpperInterfaces",true,false)
	if interfaces.get_meta("upper_operation_enabled",false): return true
	if not d.enabled: return false
	assert(not staff.operation_ready and staff.floor_heights == [0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0])
	assert(staff.stop_ids == ["D01","D02","D03","D08_WET","D09","D13","D14","D15","D16","D17"])
	assert(str(staff.persistent_id) == "forward_staff_lift_001" and staff.cabin_file == "AST-CIR-003_ten_stop.glb")
	assert(staff.landing_gates.size() == 10 and staff.retained_upper_gates.size() == 5)
	assert(FileAccess.get_sha256("res://scripts/commons_lift.gd") == str(d.controller_sha256))
	for path in d.runtime_preimages: assert(FileAccess.get_sha256("res://"+path) == str(d.runtime_preimages[path]))
	var closures: Array[MeshInstance3D] = []
	for spec in d.receiving_reconciliations:
		var deck: int = int(spec.deck)
		var module: Node3D = house.get_node("TidalD"+str(deck)+"ServiceReceiving")
		var closure := module.find_child(str(spec.closure_mesh),true,false) as MeshInstance3D
		assert(closure != null and closure.get_node_or_null("StaticContact") != null)
		var gate: Node3D = staff.landing_gates[deck-8]
		assert(gate == staff.retained_upper_gates["D"+str(deck)] and str(gate.persistent_id) == "D"+str(deck)+"_forward_staff_lift_gate")
		assert(not gate.cabin_present_and_stopped and not gate.requested_open and gate.open_fraction == 0.0)
		assert(gate.global_position.is_equal_approx(Vector3(-23.08,84+4.5*(deck-13),-490)))
		var box: AABB = closure.global_transform*closure.get_aabb()
		assert(box.position.is_equal_approx(Vector3(spec.bounds_min[0],spec.bounds_min[1],spec.bounds_min[2])))
		assert(box.end.is_equal_approx(Vector3(spec.bounds_max[0],spec.bounds_max[1],spec.bounds_max[2])))
		closures.append(closure)
	# Each whole temporary barrier is removed only after its existing closed gate
	# is bound. The exact native successors retain every other source mesh.
	for index in range(closures.size()):
		var closure: MeshInstance3D = closures[index]
		closure.get_parent().remove_child(closure)
		closure.free()
		var module: Node3D = house.get_node("TidalD"+str(int(d.receiving_reconciliations[index].deck))+"ServiceReceiving")
		module.set_meta("upper_staff_lift_enabled",true)
		module.set_meta("upper_d14_d17_held",false)
		module.set_meta("shaft_guard_owner","forward_staff_lift_001 interlocked landing gate")
		module.set_meta("temporary_shaft_closure_reconciled",true)
	interfaces.set_meta("upper_operation_enabled",true)
	interfaces.set_meta("temporary_receiving_closures_retained",false)
	interfaces.set_meta("upper_gates_bound_to_existing_lift",true)
	staff.operation_ready = true
	staff.set_meta("upper_extension_acceptance","bounded_operational_wip_pending_actual_main_check")
	return true
