extends "res://scripts/group4_loaded_tram_actuator.gd"
# Only plan binding changes. Original restraint/departure/fault/motion guards run.
static func attach_section(parent:Node3D,body:AnimatableBody3D,boarding:Node3D,cart_restraint:Node3D)->Node3D:
	assert(not body.has_meta("group4_source_actuator"),"Exactly one motor owns this source vehicle")
	var section:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r007/PLAN.json"))
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"))
	plan.source_route_points_xz=section.route_points_xz
	plan.source_route_total_m=section.safe_body_cursor_range_m[1]+4.
	plan.safe_body_cursor_range_m=section.safe_body_cursor_range_m
	plan.stops=section.stops
	plan.central_exact_pose=section.central.new_pose
	plan.pose_file="res://aquatic_tram_interior_20261026/r007/POSE_KNOTS.json"
	plan.pose_sha256=FileAccess.get_sha256(plan.pose_file)
	var contracts:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/integration/CONTRACTS.json"))
	assert(plan.pose_sha256==contracts.owned[plan.pose_file],"Exact authored pose table required")
	var motor:Node3D=load("res://aquatic_tram_interior_20261026/integration/motor.gd").new()
	motor.name="Group4LoadedSourceTravelActuator"
	motor.plan=plan;motor.vehicle=body;motor.safety=boarding;motor.restraint=cart_restraint
	motor.set_meta("integration_motion_admitted",false)
	cart_restraint.motor=motor
	parent.add_child(motor)
	body.set_meta("group4_source_actuator",motor.get_instance_id())
	return motor
