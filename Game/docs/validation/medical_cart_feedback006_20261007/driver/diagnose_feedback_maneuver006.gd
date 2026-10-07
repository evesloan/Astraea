extends "res://tests/validate_medical_cart.gd"
# Scratch only: one bounded actual-cart-state input guidance rule for all rooms.
# Runtime cart/tether, fixtures, products, physics and original gates are unchanged.
const GUIDE=preload("/workspace/scratch/375c2e438292/medical_receiver_validation_20261007_1232/cart_feedback006/achieved_cart_guidance.gd")
var diagnostic_turns: int=0
var diagnostic_room: String="before connected room guidance"
var diagnostic_requested_yaw: float=0.0
var diagnostic_phase: String="outside room maneuver"
var diagnostic_manoeuvre_active: bool=false
var diagnostic_admission_active: bool=false
var diagnostic_square: Rect2
var diagnostic_trace: Array=[]
var diagnostic_guidance_trace: Array=[]
var diagnostic_waypoints: Array=[]
var diagnostic_total_frames: int=0
var diagnostic_cart_metres: float=0.0
var diagnostic_guidance_frames: int=0
var diagnostic_completed_rooms: Array[String]=[]
var diagnostic_trace_path: String=""

func _initialize() -> void:
	test_name="medical_cart_feedback006"
	call_deferred("run")

func observed_pose(label: String) -> Dictionary:
	if not is_instance_valid(cart) or not is_instance_valid(actor): return {"label":label}
	var desired: Vector3=-actor.global_basis.z
	var actual: Vector3=-cart.global_basis.z
	desired.y=0;actual.y=0
	return {"label":label,"room_id":diagnostic_room,"frames":frames,"turn_call":diagnostic_turns,"cart_position":str(cart.global_position),"cart_rotation":str(cart.global_rotation),"cart_linear_velocity":str(cart.linear_velocity),"cart_angular_velocity":str(cart.angular_velocity),"cart_up_dot":cart.global_basis.y.dot(Vector3.UP),"actor_position":str(actor.global_position),"actor_yaw":actor.global_rotation.y,"requested_yaw":diagnostic_requested_yaw,"requested_yaw_error":wrapf(cart.global_rotation.y-diagnostic_requested_yaw,-PI,PI),"physical_forward_error":actual.normalized().signed_angle_to(desired.normalized(),Vector3.UP),"operator_to_cart_m":actor.global_position.distance_to(cart.global_position),"driver_retained":cart.get("driver")==actor,"driven_frames":driven_frames,"driven_metres":driven_metres,"turn_poses":turn_poses}

func observed_contacts() -> Array:
	var result: Array=[]
	if not is_instance_valid(cart) or space==null: return result
	for child in cart.get_children():
		if not child is CollisionShape3D: continue
		var query: PhysicsShapeQueryParameters3D=PhysicsShapeQueryParameters3D.new()
		query.shape=child.shape
		query.transform=child.global_transform
		query.margin=0.0
		query.exclude=exclusions()
		query.collision_mask=1
		for hit in space.intersect_shape(query,128):
			result.append({"cart_part":str(child.name),"collider":str(hit.collider.get_path()),"shape":hit.shape})
	return result

func authored_square(room: Dictionary) -> Rect2:
	var source: Dictionary=room.source_room
	var corners: Array=source.clear_interior_manoeuvre_local_uv
	var angle: float=float(source.orientation_z)
	var low: Vector2=Vector2(INF,INF)
	var high: Vector2=Vector2(-INF,-INF)
	for u in [float(corners[0][0]),float(corners[1][0])]:
		for v in [float(corners[0][1]),float(corners[1][1])]:
			var source_x: float=float(source.module_center_source_x)+cos(angle)*u-sin(angle)*v
			var source_y: float=float(source.front_source_y)+sin(angle)*u+cos(angle)*v
			var point: Vector2=Vector2(float(data.origin_xyz[0])+source_x,float(data.origin_xyz[2])-source_y)
			low=low.min(point);high=high.max(point)
	return Rect2(low,high-low)

func physical_contact_box(contact: CollisionShape3D) -> AABB:
	var shape: Shape3D=contact.shape
	var transform: Transform3D=contact.global_transform
	var extents: Vector3=Vector3.ZERO
	for axis in range(3):
		var row: Vector3=Vector3(transform.basis.x[axis],transform.basis.y[axis],transform.basis.z[axis])
		if shape is BoxShape3D:
			extents[axis]=row.abs().dot((shape as BoxShape3D).size*.5)
		elif shape is SphereShape3D:
			extents[axis]=(shape as SphereShape3D).radius*row.length()
		elif shape is CylinderShape3D:
			var cylinder: CylinderShape3D=shape as CylinderShape3D
			extents[axis]=cylinder.height*.5*absf(row.y)+cylinder.radius*sqrt(row.x*row.x+row.z*row.z)
		elif shape is CapsuleShape3D:
			var capsule: CapsuleShape3D=shape as CapsuleShape3D
			extents[axis]=capsule.radius*row.length()+maxf(0.0,capsule.height*.5-capsule.radius)*absf(row.y)
		else:
			require(false,"Unsupported body shape in full-compound containment: "+str(contact.get_path()))
			return AABB()
	return AABB(transform.origin-extents,extents*2.0)

func actual_body_bounds(body: Node3D) -> Dictionary:
	var low: Vector3=Vector3(INF,INF,INF)
	var high: Vector3=Vector3(-INF,-INF,-INF)
	var contacts: int=0
	var visuals: int=0
	for child in body.get_children():
		if child is CollisionShape3D and not child.disabled:
			var box: AABB=physical_contact_box(child as CollisionShape3D)
			low=low.min(box.position);high=high.max(box.end);contacts+=1
	for value in body.find_children("*","MeshInstance3D",true,false):
		var visual: MeshInstance3D=value as MeshInstance3D
		if visual.mesh==null: continue
		var box: AABB=visual.global_transform*visual.get_aabb()
		low=low.min(box.position);high=high.max(box.end);visuals+=1
	if not require(contacts>0,"Actual body requires physical extents: "+str(body.name)): return {}
	var clearance: float=minf(minf(low.x-diagnostic_square.position.x,diagnostic_square.end.x-high.x),minf(low.z-diagnostic_square.position.y,diagnostic_square.end.y-high.z))
	return {"body":str(body.name),"min_xyz":[low.x,low.y,low.z],"max_xyz":[high.x,high.y,high.z],"collision_shapes":contacts,"visible_geometry_parts":visuals,"square_clearance_m":clearance}

func observe_compound_containment() -> bool:
	var bodies: Array[Node3D]=[cart,actor]
	for product in cart.products: bodies.append(product as Node3D)
	var actual_bounds: Array=[]
	var clear: bool=true
	for body in bodies:
		var bounds: Dictionary=actual_body_bounds(body)
		if failed: return false
		actual_bounds.append(bounds)
		if float(bounds.square_clearance_m)<0.0: clear=false
	var entry: Dictionary={"room_id":diagnostic_room,"phase":diagnostic_phase,"frame":frames,"cart_xyz":[cart.global_position.x,cart.global_position.y,cart.global_position.z],"cart_yaw":cart.global_rotation.y,"actor_xyz":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"source_square_min_xz":[diagnostic_square.position.x,diagnostic_square.position.y],"source_square_max_xz":[diagnostic_square.end.x,diagnostic_square.end.y],"bodies":actual_bounds,"all_bodies_contained":clear,"support_samples":support_samples,"probe_floor_rays":probe.floor_rays}
	if not clear or diagnostic_total_frames%10==0: entry["actual_shape_overlaps"]=observed_contacts()
	diagnostic_trace.append(entry)
	metrics["scratch_full_compound_trace"]=diagnostic_trace
	if not clear: print("CART_COMPOUND_EXCURSION ",JSON.stringify(entry))
	return require(clear,"Full cart/operator/products exceeded the authored 3.6m maneuver square during "+diagnostic_phase+" in "+diagnostic_room)

func operator_quarter_arc_margin(center: Vector2,from_yaw: float,to_yaw: float) -> float:
	# Exact extrema for the circle's X/Z projection occur at endpoints or
	# cardinal angles inside the directed short arc. Include capsule radius.
	var delta: float=wrapf(to_yaw-from_yaw,-PI,PI)
	var angles: Array[float]=[from_yaw,from_yaw+delta]
	for index in range(-4,5):
		var candidate: float=float(index)*PI/2
		var along: float=wrapf(candidate-from_yaw,-PI,PI)
		if (delta>=0.0 and along>=0.0 and along<=delta) or (delta<0.0 and along<=0.0 and along>=delta): angles.append(candidate)
	var low: Vector2=Vector2(INF,INF)
	var high: Vector2=Vector2(-INF,-INF)
	for angle in angles:
		var point: Vector2=center+Vector2(sin(angle),cos(angle))*1.62
		low=low.min(point-Vector2.ONE*.30);high=high.max(point+Vector2.ONE*.30)
	return minf(minf(low.x-diagnostic_square.position.x,diagnostic_square.end.x-high.x),minf(low.y-diagnostic_square.position.y,diagnostic_square.end.y-high.y))


func write_diagnostic_trace() -> void:
	if started<=0: return
	if diagnostic_trace_path.is_empty(): diagnostic_trace_path="res://artifacts/medical_cart_feedback006_trace_"+str(started)+".json"
	var file: FileAccess=FileAccess.open(diagnostic_trace_path,FileAccess.WRITE)
	if file!=null:
		file.store_string(JSON.stringify({"scope":"Scratch feedback-driver observations; no registered successor or freehand acceptance","full_compound_frames":diagnostic_trace,"guidance_frames":diagnostic_guidance_trace,"waypoints":diagnostic_waypoints,"completed_rooms":diagnostic_completed_rooms},"  ")+"\n")
		metrics["scratch_trace_file"]=diagnostic_trace_path
	metrics.erase("scratch_full_compound_trace")

func require(ok: bool,message: String) -> bool:
	if not ok and not failed:
		var observed: Dictionary=observed_pose("feedback diagnostic failure")
		observed["actual_shape_overlaps"]=observed_contacts()
		metrics["failure_observation"]=observed
		metrics["scratch_completed_rooms"]=diagnostic_completed_rooms
		metrics["scratch_waypoints"]=diagnostic_waypoints
		print("CART_FEEDBACK_FAILURE ",JSON.stringify(observed)," ",message)
		write_diagnostic_trace()
	return super.require(ok,message)

func advance(count: int,check_d05_support: bool=false) -> bool:
	for index in range(count):
		var before: Vector3=cart.global_position if diagnostic_manoeuvre_active or diagnostic_admission_active else Vector3.ZERO
		if not await super.advance(1,check_d05_support): return false
		if diagnostic_manoeuvre_active or diagnostic_admission_active:
			diagnostic_cart_metres+=Vector2(cart.global_position.x-before.x,cart.global_position.z-before.z).length()
		if diagnostic_manoeuvre_active:
			diagnostic_total_frames+=1
			if not observe_compound_containment(): return false
	return true

func preflight_actor_step(velocity: Vector2) -> bool:
	var capsule: CapsuleShape3D=CapsuleShape3D.new()
	capsule.radius=.3;capsule.height=1.8
	var query: PhysicsShapeQueryParameters3D=PhysicsShapeQueryParameters3D.new()
	query.shape=capsule;query.margin=.001;query.collision_mask=1
	query.exclude=[actor.get_rid()]
	# Check next capsule against real cart/products and all world obstacles.
	# The same30mm support clearance as the original geometric cart probe.
	query.transform=Transform3D(Basis.IDENTITY,actor.global_position+Vector3(velocity.x/60.0,.93,velocity.y/60.0))
	var hits: Array=space.intersect_shape(query,128)
	if not hits.is_empty():
		var paths: Array=[]
		for hit in hits: paths.append(str(hit.collider.get_path()))
		metrics["blocked_actor_command_colliders"]=paths
	return require(hits.size()<128 and hits.is_empty(),"Feedback operator command has a real collision; no bypass")

func achieved_waypoint(center: Vector2,yaw: float,label: String,inside_square: bool) -> bool:
	diagnostic_turns+=1;diagnostic_requested_yaw=yaw;diagnostic_phase=label
	var driver=GUIDE.new()
	driver.begin(center,yaw,Vector2(cart.global_position.x,cart.global_position.z),cart.global_rotation.y,900)
	var began_frames: int=frames
	var began_cart_metres: float=diagnostic_cart_metres
	var began_operator_metres: float=driven_metres
	var zone: Rect2=diagnostic_square if inside_square else Rect2()
	for frame in range(901):
		if not require(cart.get("driver")==actor,"Common guidance lost the original physical tether"): return false
		if not require(absf(cart.global_position.y-21.0)<.12 and cart.global_basis.y.dot(Vector3.UP)>.98,"Guided loaded cart tipped or left D05 support"): return false
		var grip_local: Vector3=cart.get("grip_local")
		var measured_grip: Vector3=cart.global_transform*grip_local
		if not require(grip_local.is_equal_approx(Vector3(0,1.08,.67)) and absf(float(cart.get("hold_distance"))-.95)<.000001 and absf(float(cart.get("hold_height"))-1.06)<.000001,"Guidance must preserve original cart grip/hold geometry"): return false
		var command: Dictionary=driver.step(Vector2(cart.global_position.x,cart.global_position.z),cart.global_rotation.y,measured_grip,cart.linear_velocity,cart.angular_velocity,actor.global_position,actor.global_rotation.y,1.0/60.0,zone)
		diagnostic_guidance_trace.append({"room_id":diagnostic_room,"label":label,"frame":frames,"command":command,"cart_xyz":[cart.global_position.x,cart.global_position.y,cart.global_position.z],"cart_yaw":cart.global_rotation.y,"actor_xyz":[actor.global_position.x,actor.global_position.y,actor.global_position.z]})
		if str(command.status)=="failed":
			metrics["failed_guidance_command"]=command
			return require(false,"Bounded achieved-cart guidance: "+str(command.reason))
		if str(command.status)=="done":
			actor.velocity=Vector3.ZERO
			var record: Dictionary={"room_id":diagnostic_room,"label":label,"goal_center_xz":[center.x,center.y],"goal_yaw":yaw,"actual_pose":observed_pose("actual cart waypoint after90frozen-input settle frames"),"position_error_m":Vector2(cart.global_position.x,cart.global_position.z).distance_to(center),"yaw_error_rad":absf(wrapf(cart.global_rotation.y-yaw,-PI,PI)),"physics_frames":frames-began_frames,"actual_cart_metres":diagnostic_cart_metres-began_cart_metres,"actual_operator_metres":driven_metres-began_operator_metres,"settle_frames":int(command.hold_frames),"clipped_command_frames":driver.clipped_command_frames}
			diagnostic_waypoints.append(record)
			print("CART_ACHIEVED_WAYPOINT ",JSON.stringify(record))
			return require(float(record.position_error_m)<=.04 and float(record.yaw_error_rad)<.10 and int(record.settle_frames)==90,"Actual cart waypoint was not strictly achieved")
		if frame%6==0:
			probe.check_pose(ship,actor,cart,Vector3(driver.reference_position.x,21.03,driver.reference_position.y),driver.reference_yaw,21.0)
			if failed: return false
		var velocity: Vector2=command.actor_velocity
		if not preflight_actor_step(velocity): return false
		var old_actor: Vector3=actor.global_position
		var old_heading: float=actor.rotation.y
		actor.rotation.y=float(command.actor_yaw)
		actor.set("pitch",0.0);actor.camera.rotation.x=0
		actor.velocity=Vector3(velocity.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60.0,velocity.y)
		actor.move_and_slide()
		var moved: float=Vector2(actor.global_position.x-old_actor.x,actor.global_position.z-old_actor.z).length()
		driven_metres+=moved
		if moved>.00001 or absf(wrapf(actor.rotation.y-old_heading,-PI,PI))>.00001: driven_frames+=1
		diagnostic_guidance_frames+=1
		if not await advance(1,true): return false
		if not product_state(): return false
		if diagnostic_guidance_frames%6==0:
			for wheel in probe.wheel_specs:
				var q: Array=wheel.center
				var foot: Vector3=cart.global_transform*Vector3(float(q[0]),0,float(q[2]))
				if not support_at(Vector3(foot.x,21,foot.z),str(data.new_floor_owner)): return false
	return require(false,"Hard guidance frame bound reached without actual completion")

func drive_connected_triage() -> bool:
	if not require(cart.get("driver")==actor,"Original tether required at admission junction"): return false
	if not await super.turn_to(0): return false
	if not await super.line_to(Vector2(-11,-458),0): return false
	if not await super.turn_to(PI/2): return false
	var actual_turns: Array=[]
	for index in [0,4,1,5,2,6,3,7]:
		var room: Dictionary=triage_evidence.rooms[index]
		diagnostic_room=str(room.programme_child)
		var corridor: Vector3=xyz(room.corridor_xyz)
		var inside: Vector3=xyz(room.inside_xyz)
		var yaw: float=float(room.inward_yaw)
		var quarter: float=yaw+PI/2
		var direction: Vector3=Basis(Vector3.UP,quarter)*Vector3.FORWARD
		var target: Vector2=Vector2(inside.x,inside.z)+Vector2(direction.x,direction.z)*.20
		if not await super.line_to(Vector2(corridor.x,corridor.z),PI/2): return false
		if not await super.turn_to(yaw): return false
		diagnostic_admission_active=true
		if not await achieved_waypoint(target,yaw,"rolling offset admission",false): return false
		diagnostic_admission_active=false
		diagnostic_square=authored_square(room)
		diagnostic_manoeuvre_active=true
		if not observe_compound_containment(): return false
		if not verify_actual_room_cart_pose(room,yaw): return false
		var actual_center: Vector2=Vector2(cart.global_position.x,cart.global_position.z)
		var arc_margin: float=operator_quarter_arc_margin(actual_center,cart.global_rotation.y,quarter)
		if not require(actual_center.distance_to(target)<=.04 and arc_margin>=.05,"Actual admission lacks the unchanged strict start/arc margin"): return false
		var before_yaw: float=cart.global_rotation.y
		if not await achieved_waypoint(target,quarter,"useful work-facing turn",true): return false
		if not verify_actual_room_cart_pose(room,quarter): return false
		var turned: float=absf(wrapf(cart.global_rotation.y-before_yaw,-PI,PI))
		if not require(turned>deg_to_rad(80.0),"Actual quarter-turn is less than80degrees"): return false
		actual_turns.append({"room_id":diagnostic_room,"actual_turn_radians":turned,"actual_position":str(cart.global_position)})
		if not await achieved_waypoint(target,yaw,"physical inward realignment",true): return false
		if not verify_actual_room_cart_pose(room,yaw): return false
		if not observe_compound_containment(): return false
		diagnostic_manoeuvre_active=false
		diagnostic_admission_active=true
		if not await achieved_waypoint(Vector2(corridor.x,corridor.z),yaw,"same-portal backing exit",false): return false
		diagnostic_admission_active=false
		if not await super.turn_to(PI/2): return false
		diagnostic_completed_rooms.append(diagnostic_room)
	if not require(diagnostic_completed_rooms.size()==8,"Same original loaded cart must complete all eight rooms"): return false
	if not await super.line_to(Vector2(-11,-458),PI/2): return false
	if not await super.turn_to(PI): return false
	if not await super.line_to(Vector2(-11,-446),PI): return false
	if not await super.turn_to(-PI/2): return false
	if not product_state(): return false
	triage_cart_metrics["triage_loaded_cart_room_ids"]=diagnostic_completed_rooms
	triage_cart_metrics["triage_actual_room_turns"]=actual_turns
	triage_cart_metrics["triage_door_operation_accepted"]=false
	triage_cart_metrics["triage_full_in_place_uturn_accepted"]=false
	triage_cart_metrics["triage_scope"]="Scratch bounded achieved-cart-state actor guidance; same four-product cart, unchanged physical tether and source-open rooms. No ordinary-input or registered-test acceptance."
	return true

func exercise() -> bool:
	if not await super.exercise(): return false
	metrics["scratch_completed_rooms"]=diagnostic_completed_rooms
	metrics["scratch_waypoints"]=diagnostic_waypoints
	metrics["scratch_guidance_physics_frames"]=diagnostic_guidance_frames
	metrics["scratch_full_body_frames"]=diagnostic_total_frames
	metrics["scratch_observed_cart_metres"]=diagnostic_cart_metres
	metrics["production_cart_or_tether_changes"]=false
	metrics["direct_cart_force_transform_velocity_writes_by_guidance"]=0
	metrics["ordinary_input_or_freehand_comfort_accepted"]=false
	write_diagnostic_trace()
	return require(diagnostic_completed_rooms.size()==8 and diagnostic_waypoints.size()==32,"Complete8room/32achieved-waypoint common-rule result required")
