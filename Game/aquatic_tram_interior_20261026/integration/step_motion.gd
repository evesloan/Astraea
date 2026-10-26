extends RefCounted
# Standing-body motion only: every leg uses the original collider and mask.
# No ramp, collision exclusion, input injection or change to retained geometry.
const MAX_RISE := 0.22
static var rejections:Dictionary={}
static func reject(reason:String)->bool:
	rejections[reason]=int(rejections.get(reason,0))+1
	return false
static func apply(actor:CharacterBody3D, remaining:Vector3)->bool:
	remaining.y=0
	if remaining.length()<0.002 or remaining.length()>0.12:return reject("motion")
	var start:=actor.global_transform
	if not actor.test_move(start,remaining):return reject("no_obstacle")
	var raised:=start
	if actor.test_move(start,Vector3.UP*MAX_RISE):return reject("up_blocked")
	raised.origin.y+=MAX_RISE
	if actor.test_move(raised,remaining):return reject("forward_blocked")
	raised.origin+=remaining
	var landing:=KinematicCollision3D.new()
	if not actor.test_move(raised,Vector3.DOWN*(MAX_RISE+0.02),landing):return reject("no_support")
	# A capsule landing on a tread edge reports the rounded capsule normal.
	# Verify the actual supporting tread face independently, keeping slope limits.
	var contact:=landing.get_position()+remaining.normalized()*0.015
	var ray:=PhysicsRayQueryParameters3D.create(contact+Vector3.UP*0.05,contact-Vector3.UP*0.05,actor.collision_mask,[actor.get_rid()])
	var tread:=actor.get_world_3d().direct_space_state.intersect_ray(ray)
	if tread.is_empty() or tread.normal.dot(Vector3.UP)<cos(actor.floor_max_angle):return reject("steep_support")
	var destination:=raised.origin+landing.get_travel()
	destination.y=float(tread.position.y)+0.001
	var final_pose:=start;final_pose.origin=destination
	if actor.test_move(final_pose,Vector3.ZERO,null,0.0005,true):return reject("occupied_destination")
	var rise:=destination.y-start.origin.y
	if rise<0.0001 or rise>MAX_RISE:return reject("rise")
	actor.global_position=destination
	actor.velocity.y=0
	return true
