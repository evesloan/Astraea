extends RigidBody3D
# Four immersed force samples and velocity drag. No player movement or pose writes.
var field:RefCounted
var draft_m:=.20
var probes:PackedVector3Array=PackedVector3Array([Vector3(.50,.03,0),Vector3(-.50,.03,0),Vector3(0,.03,.50),Vector3(0,.03,-.50)])
var physics_samples:=0
var immersed_samples:=0
var last_submergence:=0.0
func _ready()->void:
	assert(field!=null);mass=12.0;can_sleep=false;linear_damp=0.0;angular_damp=.05
	set_meta("buoyancy_scope","Unoccupied source float, four immersion forces and prescribed current; no avatar/AFK/hoist/save acceptance")
func _integrate_forces(state:PhysicsDirectBodyState3D)->void:
	physics_samples+=1;last_submergence=0.0
	var centre:Dictionary=field.sample(state.transform.origin)
	if not centre.get("wet",false):return
	immersed_samples+=1
	for local in probes:
		var offset:Vector3=state.transform.basis*local;var p:Vector3=state.transform.origin+offset
		if not field.contains_xz(p):continue
		var depth:=maxf(0.0,field.water_y-p.y);var displacement:=clampf(depth/draft_m,0.0,2.0)
		last_submergence+=displacement/4.0
		state.apply_force(Vector3.UP*mass*9.8*displacement/4.0,offset)
	var relative:Vector3=centre.water_velocity-state.linear_velocity
	# Resistance applies only while in water; engine gravity/collision remain active.
	state.apply_central_force(Vector3(relative.x*mass*3.0,-state.linear_velocity.y*mass*4.0,relative.z*mass*3.0))
	state.apply_torque(-state.angular_velocity*mass*.55)
