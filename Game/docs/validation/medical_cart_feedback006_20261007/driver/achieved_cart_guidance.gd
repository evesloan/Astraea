extends RefCounted
# Scratch-only input guidance. It receives observed states and returns bounded
# actor commands; it owns no scene nodes and cannot touch cart forces/transforms.
const POSITION_GATE: float=.04
const YAW_GATE: float=.10
const LINEAR_QUIET: float=.03
const ANGULAR_QUIET: float=.04
const SETTLE_FRAMES: int=90
const STALL_FRAMES: int=120
const PROGRESS_EPSILON: float=.002
const REFERENCE_SPEED: float=.65
const REFERENCE_YAW_RATE: float=.45
const OPERATOR_SPEED: float=1.0
const OPERATOR_YAW_RATE: float=1.0
const POSITION_FEEDBACK: float=6.0
const YAW_FEEDBACK: float=2.0
const MAX_HAND_LEAD: float=.22
const MAX_HEADING_LEAD: float=.35
const GRIP_BACKSET: float=.67
const GRIP_HEIGHT: float=1.08
const HAND_HOLD_HEIGHT: float=1.06
const HAND_HOLD_DISTANCE: float=.95
const CAPSULE_RADIUS_AND_COMMAND_MARGIN: float=.305
var goal_position: Vector2
var goal_yaw: float
var reference_position: Vector2
var reference_yaw: float
var maximum_frames: int=900
var frames: int=0
var hold_frames: int=0
var best_error: float=INF
var last_progress_frame: int=0
var mode: String="idle"
var terminal_reason: String=""
var held_actor_yaw: float=0.0
var clipped_command_frames: int=0

func begin(target_position: Vector2,target_yaw: float,actual_position: Vector2,actual_yaw: float,frame_limit: int=900) -> void:
	goal_position=target_position;goal_yaw=target_yaw
	reference_position=actual_position;reference_yaw=actual_yaw
	maximum_frames=frame_limit;frames=0;hold_frames=0;best_error=INF;last_progress_frame=0
	mode="running";terminal_reason="";clipped_command_frames=0

func actual_pose_passes(position: Vector2,yaw: float) -> bool:
	return position.distance_to(goal_position)<=POSITION_GATE and absf(wrapf(yaw-goal_yaw,-PI,PI))<YAW_GATE

func fail(reason: String,actor_yaw: float) -> Dictionary:
	mode="failed";terminal_reason=reason
	return {"status":mode,"reason":reason,"actor_velocity":Vector2.ZERO,"actor_yaw":actor_yaw,"frames":frames,"hold_frames":hold_frames}

func step(cart_position: Vector2,cart_yaw: float,cart_grip: Vector3,cart_velocity: Vector3,cart_angular_velocity: Vector3,actor_world_position: Vector3,actor_yaw: float,dt: float,working_square: Rect2=Rect2()) -> Dictionary:
	if mode=="failed": return fail(terminal_reason,actor_yaw)
	if mode=="done": return {"status":"done","actor_velocity":Vector2.ZERO,"actor_yaw":held_actor_yaw,"frames":frames,"hold_frames":hold_frames}
	if not cart_position.is_finite() or not cart_grip.is_finite() or not cart_velocity.is_finite() or not actor_world_position.is_finite() or not is_finite(cart_yaw) or not cart_angular_velocity.is_finite() or not is_finite(actor_yaw) or dt<=0.0 or dt>.05: return fail("Invalid observed state or fixed-step interval",actor_yaw)
	var actor_position: Vector2=Vector2(actor_world_position.x,actor_world_position.z)
	var hand_height: float=actor_world_position.y+HAND_HOLD_HEIGHT
	var vertical_lead: float=hand_height-cart_grip.y
	if absf(vertical_lead)>MAX_HAND_LEAD: return fail("Actual vertical grip separation exceeds hand-lead cap",actor_yaw)
	var planar_lead_limit: float=sqrt(MAX_HAND_LEAD*MAX_HAND_LEAD-vertical_lead*vertical_lead)
	frames+=1
	if frames>maximum_frames: return fail("Hard waypoint frame limit",actor_yaw)
	var pose_ok: bool=actual_pose_passes(cart_position,cart_yaw)
	var quiet: bool=cart_velocity.length()<=LINEAR_QUIET and cart_angular_velocity.length()<=ANGULAR_QUIET
	if mode=="holding":
		var frozen_hand_xz: Vector2=actor_position-Vector2(sin(held_actor_yaw),cos(held_actor_yaw))*HAND_HOLD_DISTANCE
		var frozen_hand: Vector3=Vector3(frozen_hand_xz.x,hand_height,frozen_hand_xz.y)
		if frozen_hand.distance_to(cart_grip)>MAX_HAND_LEAD+.0001 or absf(wrapf(held_actor_yaw-cart_yaw,-PI,PI))>MAX_HEADING_LEAD+.0001: return fail("Frozen-input settle exceeds total physical lead bounds",actor_yaw)
		if not pose_ok: return fail("Actual cart left its achieved pose during frozen-input settle",actor_yaw)
		if not quiet: return fail("Actual cart did not remain quiet during frozen-input settle",actor_yaw)
		hold_frames+=1
		if hold_frames>=SETTLE_FRAMES: mode="done"
		return {"status":mode,"actor_velocity":Vector2.ZERO,"actor_yaw":held_actor_yaw,"frames":frames,"hold_frames":hold_frames,"position_error_m":cart_position.distance_to(goal_position),"yaw_error_rad":absf(wrapf(cart_yaw-goal_yaw,-PI,PI))}
	var error: float=cart_position.distance_to(goal_position)+.5*absf(wrapf(cart_yaw-goal_yaw,-PI,PI))
	if error<best_error-PROGRESS_EPSILON:
		best_error=error;last_progress_frame=frames
	elif frames-last_progress_frame>=STALL_FRAMES:
		return fail("No sufficient actual-cart progress for120frames",actor_yaw)
	reference_position=reference_position.move_toward(goal_position,REFERENCE_SPEED*dt)
	reference_yaw+=clampf(wrapf(goal_yaw-reference_yaw,-PI,PI),-REFERENCE_YAW_RATE*dt,REFERENCE_YAW_RATE*dt)
	# Cap the TOTAL command relative to the observed cart, including reference
	# lag; limiting only a correction term would not bound the physical lead.
	var yaw_error_to_reference: float=wrapf(reference_yaw-cart_yaw,-PI,PI)
	var requested_heading: float=reference_yaw+YAW_FEEDBACK*yaw_error_to_reference
	var bounded_heading: float=cart_yaw+clampf(wrapf(requested_heading-cart_yaw,-PI,PI),-MAX_HEADING_LEAD,MAX_HEADING_LEAD)
	var commanded_yaw: float=actor_yaw+clampf(wrapf(bounded_heading-actor_yaw,-PI,PI),-OPERATOR_YAW_RATE*dt,OPERATOR_YAW_RATE*dt)
	var heading_lead: float=wrapf(commanded_yaw-cart_yaw,-PI,PI)
	if absf(heading_lead)>MAX_HEADING_LEAD+.0001: return fail("Rate-limited actor heading would exceed total observed-cart lead",actor_yaw)
	var actual_grip: Vector2=Vector2(cart_grip.x,cart_grip.z)
	var reference_grip: Vector2=reference_position+Vector2(sin(reference_yaw),cos(reference_yaw))*GRIP_BACKSET
	var requested_hand: Vector2=reference_grip+(reference_position-cart_position)*POSITION_FEEDBACK
	var bounded_hand: Vector2=actual_grip+(requested_hand-actual_grip).limit_length(planar_lead_limit)
	var heading_offset: Vector2=Vector2(sin(commanded_yaw),cos(commanded_yaw))*HAND_HOLD_DISTANCE
	var operator_target: Vector2=bounded_hand+heading_offset
	var clipped: bool=false
	if working_square.has_area():
		var center_zone: Rect2=working_square.grow(-CAPSULE_RADIUS_AND_COMMAND_MARGIN)
		if not center_zone.has_area(): return fail("No feasible capsule-center zone",actor_yaw)
		var bounded: Vector2=operator_target.clamp(center_zone.position,center_zone.end)
		clipped=bounded.distance_to(operator_target)>.000001
		operator_target=bounded
		var projected_hand_xz: Vector2=operator_target-heading_offset
		var projected_hand: Vector3=Vector3(projected_hand_xz.x,hand_height,projected_hand_xz.y)
		if projected_hand.distance_to(cart_grip)>MAX_HAND_LEAD+.0001: return fail("Working zone requires total hand lead beyond the fixed cap",actor_yaw)
		if clipped: clipped_command_frames+=1
	var velocity: Vector2=(operator_target-actor_position).limit_length(OPERATOR_SPEED*dt)/dt
	var next_hand_xz: Vector2=actor_position+velocity*dt-heading_offset
	var next_hand: Vector3=Vector3(next_hand_xz.x,hand_height,next_hand_xz.y)
	var applied_hand_lead: float=next_hand.distance_to(cart_grip)
	if applied_hand_lead>MAX_HAND_LEAD+.0001: return fail("Rate-limited actor step would exceed total observed-grip lead",actor_yaw)
	var references_complete: bool=reference_position.distance_to(goal_position)<.00001 and absf(wrapf(reference_yaw-goal_yaw,-PI,PI))<.00001
	var operator_quiet: bool=velocity.length()<=LINEAR_QUIET and absf(wrapf(commanded_yaw-actor_yaw,-PI,PI))/dt<=ANGULAR_QUIET
	# Freezing replaces the candidate step; validate that final frozen command
	# too, rather than skipping a tiny correction required by the lead cap.
	var current_hand_xz: Vector2=actor_position-Vector2(sin(actor_yaw),cos(actor_yaw))*HAND_HOLD_DISTANCE
	var current_hand: Vector3=Vector3(current_hand_xz.x,hand_height,current_hand_xz.y)
	var freeze_lead_ok: bool=current_hand.distance_to(cart_grip)<=MAX_HAND_LEAD+.0001 and absf(wrapf(actor_yaw-cart_yaw,-PI,PI))<=MAX_HEADING_LEAD+.0001
	if references_complete and pose_ok and quiet and operator_quiet and freeze_lead_ok:
		mode="holding";hold_frames=0;held_actor_yaw=actor_yaw
		velocity=Vector2.ZERO;commanded_yaw=actor_yaw
		heading_lead=wrapf(actor_yaw-cart_yaw,-PI,PI);applied_hand_lead=current_hand.distance_to(cart_grip)
		heading_offset=Vector2(sin(actor_yaw),cos(actor_yaw))*HAND_HOLD_DISTANCE
		operator_target=actor_position
	return {"status":mode,"actor_velocity":velocity,"actor_yaw":commanded_yaw,"operator_target":operator_target,"reference_position":reference_position,"reference_yaw":reference_yaw,"position_error_m":cart_position.distance_to(goal_position),"yaw_error_rad":absf(wrapf(cart_yaw-goal_yaw,-PI,PI)),"cart_speed_mps":cart_velocity.length(),"cart_angular_speed_rps":cart_angular_velocity.length(),"cart_yaw_speed_rps":cart_angular_velocity.y,"heading_lead_rad":heading_lead,"hand_lead_m":applied_hand_lead,"desired_hand_target":Vector3((operator_target-heading_offset).x,hand_height,(operator_target-heading_offset).y),"observed_cart_grip":cart_grip,"reference_cart_yaw_error_rad":yaw_error_to_reference,"command_clipped_to_square":clipped,"clipped_command_frames":clipped_command_frames,"frames":frames,"hold_frames":hold_frames}
