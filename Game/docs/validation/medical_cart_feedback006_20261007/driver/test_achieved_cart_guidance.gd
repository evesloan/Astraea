extends SceneTree
const DRIVER=preload("/workspace/scratch/375c2e438292/medical_receiver_validation_20261007_1232/cart_feedback006/achieved_cart_guidance.gd")
var checks: int=0

func check(ok: bool,label: String) -> bool:
	if not ok:
		push_error("GUIDANCE NEGATIVE TEST FAIL: "+label);quit(1);return false
	checks+=1
	return true

func sample(driver: Variant,cart_position: Vector2,yaw: float,velocity: Vector3,angular_velocity: Vector3,actor_position: Vector2,actor_yaw: float,dt: float) -> Dictionary:
	var grip: Vector3=Vector3(cart_position.x+sin(yaw)*.67,22.08,cart_position.y+cos(yaw)*.67)
	return driver.step(cart_position,yaw,grip,velocity,angular_velocity,Vector3(actor_position.x,21,actor_position.y),actor_yaw,dt)

func _initialize() -> void:
	var driver=DRIVER.new()
	driver.begin(Vector2.ZERO,0.0,Vector2(.15,0),0.0)
	if not check(not driver.actual_pose_passes(Vector2(.15,0),0.0),"Operator arrival cannot substitute for actual cart position"): return
	if not check(not driver.actual_pose_passes(Vector2.ZERO,.11),"Correct operator heading cannot substitute for actual cart yaw"): return
	var result: Dictionary={}
	for frame in range(140):
		# The actor is already at the neutral target; the cart remains stuck.
		result=sample(driver,Vector2(.15,0),0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
		if str(result.status)=="failed": break
		if not check(str(result.status)!="done","Frozen wrong cart never completes"): return
	if not check(str(result.status)=="failed" and "actual-cart progress" in str(result.reason),"Stuck real cart hits finite physical-progress limit"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="holding" and driver.hold_frames==0,"Matching state only starts a settle; it does not pass immediately"): return
	for frame in range(89):
		result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
		if not check(str(result.status)!="done","Cannot complete before90observed frozen-input settle frames"): return
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="done" and int(result.hold_frames)==90,"Actual correct quiet cart completes after full settle"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	result=sample(driver,Vector2(.041,0),0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="failed" and "left its achieved pose" in str(result.reason),"Leaving the pose during settle fails rather than retrying"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=sample(driver,Vector2.ZERO,0.0,Vector3(.1,0,0),Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="running","Moving cart cannot start settled completion"): return
	driver.begin(Vector2(1,0),0.0,Vector2.ZERO,0.0,5)
	for frame in range(6): result=sample(driver,Vector2(float(frame)*.01,0),0.0,Vector3(.1,0,0),Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="failed" and "frame limit" in str(result.reason),"Hard budget still applies while actual cart makes progress"): return
	driver.begin(Vector2(10,0),1.5,Vector2.ZERO,0.0)
	driver.reference_position=Vector2(5,0);driver.reference_yaw=1.0
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="running","Large reference lag remains a bounded physical command"): return
	var hand: Vector3=result.desired_hand_target
	var grip: Vector3=result.observed_cart_grip
	if not check(hand.distance_to(grip)<=.220001 and float(result.hand_lead_m)<=.220001,"Total hand lead includes reference lag and stays capped"): return
	if not check(absf(float(result.heading_lead_rad))<=.350001,"Total commanded heading lead includes reference lag and stays capped"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),1.5,1.0/60)
	if not check(str(result.status)=="failed" and "heading" in str(result.reason),"An already excessive heading lead is rejected, not repaired by an instant look snap"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=sample(driver,Vector2.ZERO,0.0,Vector3(0,.1,0),Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="running","Vertical bounce prevents settled completion"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3(.1,0,0),Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="running","Pitch/roll motion prevents settled completion"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3.ZERO,Vector2(0,1.62),0.0,1.0/60)
	result=sample(driver,Vector2.ZERO,0.0,Vector3.ZERO,Vector3(0,0,.1),Vector2(0,1.62),0.0,1.0/60)
	if not check(str(result.status)=="failed" and "quiet" in str(result.reason),"New roll motion during frozen-input settle fails"): return
	driver.begin(Vector2.ZERO,0.0,Vector2(-.04,0),0.0)
	driver.reference_position=Vector2.ZERO
	var planar_cap: float=sqrt(.22*.22-.02*.02)
	result=sample(driver,Vector2(-.04,0),0.0,Vector3.ZERO,Vector3.ZERO,Vector2(-.04+planar_cap+.0002,1.62),0.0,1.0/60)
	if not check(str(result.status)=="running" and result.actor_velocity.x<0,"A needed tiny lead correction is not discarded by entering frozen settle"): return
	driver.begin(Vector2.ZERO,0.0,Vector2.ZERO,0.0)
	result=driver.step(Vector2.ZERO,0.0,Vector3(0,22.4,.67),Vector3.ZERO,Vector3.ZERO,Vector3(0,21,1.62),0.0,1.0/60)
	if not check(str(result.status)=="failed" and "vertical grip" in str(result.reason),"Measured vertical grip displacement cannot evade the full3D lead cap"): return
	print("ACHIEVED_CART_GUIDANCE_NEGATIVE_TESTS PASS: ",checks," assertions; no scene/cart force or transform access")
	quit(0)
