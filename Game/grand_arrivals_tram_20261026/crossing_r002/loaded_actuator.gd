extends "res://grand_arrivals_tram_20261026/grade_r007/loaded_actuator.gd"
# Additional local guard. Existing loaded-cart, portal and unexpected-pose checks
# remain in super; no original controller or production binding is replaced.
var crossing:Node3D
var crossing_interval:=Vector2(INF,-INF)
func configure_crossing(node:Node3D)->void:
	assert(is_instance_valid(node) and not moving)
	crossing=node
	for row:Array in poses:
		# Includes the original complete car envelope beyond the 4m public crossing.
		if row[1]>3 and row[11]<2 and row[2]>=-439 and row[2]<=-425:
			crossing_interval.x=minf(crossing_interval.x,row[0]-.5)
			crossing_interval.y=maxf(crossing_interval.y,row[0]+.5)
	assert(is_finite(crossing_interval.x) and crossing_interval.y>crossing_interval.x)
func needs_crossing(a:float,b:float)->bool:
	return maxf(a,b)>=crossing_interval.x and minf(a,b)<=crossing_interval.y
func update_payload_exclusions()->void:
	crossing.payload_exclusions.clear()
	if not is_instance_valid(restraint) or restraint.phase!="locked" or not restraint.loaded_clear_to_depart():return
	assert(restraint.cart.persistent_id==&"custodian_cart_001" and restraint.cart.products.size()==4)
	crossing.payload_exclusions.append(restraint.cart.get_rid())
	for stock:RigidBody3D in restraint.cart.products:crossing.payload_exclusions.append(stock.get_rid())
func request_distance(at:float)->bool:
	if not bool(get_meta("integration_motion_admitted",false)):return false
	if not is_instance_valid(crossing):return false
	if not safety.unloaded_clear_to_depart() or not restraint.loaded_clear_to_depart():return false
	update_payload_exclusions()
	if needs_crossing(cursor,at) and not crossing.request_lock():return false
	return super.request_distance(at)
func _physics_process(delta:float)->void:
	if not is_instance_valid(crossing):
		if moving:motion_fault=true;moving=false;speed=0
		return
	update_payload_exclusions()
	if moving and needs_crossing(cursor,target) and not crossing.closed_and_clear():
		motion_fault=true;moving=false;speed=0;return
	super._physics_process(delta)
	if motion_fault:return
	if not vehicle.global_transform.is_equal_approx(grade_body_pose(pose_at(cursor))):
		motion_fault=true;moving=false;speed=0;return
	if not needs_crossing(cursor,target):crossing.request_release(true)
