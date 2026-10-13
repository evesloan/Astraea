extends RefCounted
const CONFIGS={"completion":"GROUP4_COMPLETION_CANDIDATE.json","upper":"GROUP4_AFTMID_UPPER_SOURCE_CANDIDATE.json","boarding":"GROUP4_BOARDING_SAFETY_CANDIDATE.json","travel":"GROUP4_TRAVEL_SOURCE_CANDIDATE.json","loaded":"GROUP4_LOADED_CART_SOURCE_CANDIDATE.json","operating":"GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE.json","information":"GROUP4_STATION_INFORMATION_SOURCE_CANDIDATE.json"}
static func before_budget(ship:Node3D)->Node3D:
	load("res://tests/group4_exact_pit_successor_guard.gd").ensure()
	var plans:Dictionary={}
	for key in CONFIGS:
		plans[key]=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/"+str(CONFIGS[key])))
		assert(plans[key].active,"All supplied source components must be admitted together")
	for key in ["travel","loaded"]:assert(plans[key].north_stop_adopted and plans[key].shared_pits_adopted)
	assert(plans.boarding.terminal_active,"Preserve the two already installed terminals")
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node("Group4Completion"))
	var assembly:Node3D=load("res://scripts/group4_completion.gd").build(districts,false,true)
	load("res://scripts/group4_aftmid_upper_successor.gd").build(assembly)
	var body:AnimatableBody3D=load("res://scripts/group4_boarding_safety.gd").create_candidate_vehicle(assembly,Vector3(0,56.1,-72))
	body.name="Group4OwnedTram_Source024"
	var safety:Node3D=load("res://scripts/group4_boarding_safety.gd").build(assembly,assembly,body)
	safety.set_meta("integration_boarding_admitted",false)
	var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	var restraint:Node3D=load("res://scripts/group4_cart_restraint.gd").build(assembly,body,safety,cart)
	restraint.set_meta("integration_joint_admitted",false)
	body.set_meta("group4_initial_source_cursor",395.3525674298981)
	var motor:Node3D=load("res://scripts/group4_loaded_tram_actuator.gd").attach_loaded(assembly,body,safety,restraint)
	motor.set_meta("integration_motion_admitted",false)
	assembly.set_meta("tram_operations_admitted",false)
	assembly.set_meta("tram_operation_hold","Original cart caster impulse and protected four-metre D09 transit receiving remain unresolved")
	assert(safety.phase=="secured" and restraint.phase=="unlocked" and not motor.moving)
	# Empty newly assembled source vehicle only; original actor/cart/products are never moved.
	motor.cursor=395.3525674298981;motor.target=motor.cursor;motor.speed=0;motor.moving=false;motor.apply_pose(motor.cursor);motor.last_vehicle_pose=body.global_transform
	assert(body.global_position.distance_to(Vector3(0,56.1,-72))<.001)
	safety.previous_vehicle_pose=body.global_transform
	assembly.set_meta("receiving_north_physical_dock",Vector3(-5.6,56.1,-241))
	assembly.set_meta("directory_fore_midship_catchment_z",-216)
	assembly.set_meta("integrated_empty_startup_station","CENTRAL")
	assembly.set_meta("source_scope","Five supplied stations,exact named pits,one source024 body,one loaded successor motor;current-main affected checks pending")
	return assembly
static func after_budget(ship:Node3D)->void:
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var restraint:Node3D=assembly.get_node("Group4OriginalCartRestraint")
	var motor:Node3D=assembly.get_node("Group4LoadedSourceTravelActuator")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	load("res://scripts/group4_tram_operating_controls.gd").build(assembly,body,safety,restraint,motor,actor,budget)
	load("res://scripts/group4_station_information.gd").build(assembly,safety)
