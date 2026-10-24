extends SceneTree
# One fresh ORIGINAL-SOURCE actor/cart/four-product set per process. This is a
# bounded physical fixture, not the full selected ship or a scenic acceptance.
# All actor AND vehicle starting transforms precede first tree admission.
# No primitive representation change; exact r001 runtime gates are retained.
const P := "res://tram_passenger_successor_20261024/"
var checks := 0
var failures := 0
var mode := ""
var stage := "source"
var host: Node
var ship: Node3D
var assembly: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var body: AnimatableBody3D
var safety: Node3D
var motor: Node3D
var restraint: Node3D
var controls: Node3D
var products: Array[Dictionary] = []
var samples: Array[Dictionary] = []
var max_speed := 0.0
var max_up_speed := 0.0
var max_cart_error := 0.0
var max_passenger_error := 0.0
var max_body_step := 0.0
var previous_body := Vector3.ZERO
var passenger_frame := Vector3.ZERO
var motion_frames := 0
var primitive_result := {}

func _initialize() -> void:
	call_deferred("run")

func arg(key: String) -> String:
	for value: String in OS.get_cmdline_user_args():
		if value.begins_with(key + "="):
			return value.substr(key.length() + 1)
	return ""

func require(value: bool, message: String) -> bool:
	checks += 1
	if not value:
		failures += 1
		push_error("TRAM_ORIGINAL_CARRY_HOLD: " + stage + ": " + message)
	return value

func verify() -> bool:
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P + "CONTRACTS_r002.json"))
	for bucket: Dictionary in [contract.prerequisites, contract.owned]:
		for path: String in bucket:
			if not require(FileAccess.get_sha256(path) == str(bucket[path]), "exact source " + path):
				return false
	return true

func sample(frame: int) -> void:
	max_speed = maxf(max_speed, cart.linear_velocity.length())
	max_up_speed = maxf(max_up_speed, cart.linear_velocity.y)
	if frame > 12 and frame % 30 != 0 and cart.linear_velocity.length() < 6.0:
		return
	var contacts: Array[Dictionary] = []
	var state := PhysicsServer3D.body_get_direct_state(cart.get_rid())
	if state != null:
		for i in range(state.get_contact_count()):
			var other = state.get_contact_collider_object(i)
			contacts.append({"self_shape":state.get_contact_local_shape(i), "other_shape":state.get_contact_collider_shape(i), "owner":str(other.get_path()) if other is Node else str(other), "normal":str(state.get_contact_local_normal(i)), "impulse":str(state.get_contact_impulse(i)), "other_velocity":str(state.get_contact_collider_velocity_at_position(i))})
	samples.append({"stage":stage,"frame":frame,"cart_local":str(body.to_local(cart.global_position)),"cart_velocity":str(cart.linear_velocity),"vehicle_velocity":str(PhysicsServer3D.body_get_state(body.get_rid(), PhysicsServer3D.BODY_STATE_LINEAR_VELOCITY)),"vehicle_angular_velocity":str(PhysicsServer3D.body_get_state(body.get_rid(), PhysicsServer3D.BODY_STATE_ANGULAR_VELOCITY)),"joint_exists":is_instance_valid(restraint.joint),"contacts":contacts})

func stock_preserved() -> bool:
	if products.size() != 4 or cart.products.size() != 4:
		return false
	for i in range(4):
		var original: Dictionary = products[i]
		var stock: RigidBody3D = cart.products[i]
		if not is_instance_valid(stock) or stock != original.node or stock.persistent_id != original.id or stock.get_parent() != original.parent:
			return false
		var local := cart.to_local(stock.global_position)
		# Identical retained loose-stock bounds from the prior loaded-cart gate.
		if local.y <= .78 or local.y >= 1.35 or absf(local.x) >= .43 or absf(local.z) >= .62:
			return false
	return true

func continuous(frame: int, joint_required: bool) -> bool:
	sample(frame)
	if stage=="fresh_gravity_settling":
		var linear:Vector3=PhysicsServer3D.body_get_state(body.get_rid(),PhysicsServer3D.BODY_STATE_LINEAR_VELOCITY)
		var angular:Vector3=PhysicsServer3D.body_get_state(body.get_rid(),PhysicsServer3D.BODY_STATE_ANGULAR_VELOCITY)
		if not require(linear.length()<.001 and angular.length()<.001,"uncommanded fresh vehicle has no initialization linear/angular velocity"):
			return false
	if not require(cart.global_position.is_finite() and cart.linear_velocity.length() < 6.0 and cart.global_basis.y.dot(Vector3.UP) > .97, "original cart remains finite, upright and below retained6 m/s limit"):
		return false
	if not require(stock_preserved(), "same four loose products remain in retained tray bounds"):
		return false
	if not require(not restraint.motion_fault and not motor.motion_fault, "original source controllers report no fault"):
		return false
	if joint_required:
		var error := body.to_local(cart.global_position).distance_to(restraint.locked_cart_frame.origin)
		max_cart_error = maxf(max_cart_error,error)
		if not require(is_instance_valid(restraint.joint) and error < .025, "original physical joint frame stays below unchanged25 mm limit"):
			return false
	return true

func travel(target: float) -> bool:
	if not require(motor.request_distance(target), "original loaded motor admits bounded request only after real secured/locked gates"):
		return false
	previous_body = body.global_position
	for frame in range(600):
		await physics_frame
		motion_frames += 1
		if not continuous(frame,true):
			return false
		var step := previous_body.distance_to(body.global_position)
		max_body_step = maxf(max_body_step,step)
		previous_body = body.global_position
		if not require(step < .105, "retained continuous motor step below105 mm; no pose jump"):
			return false
		var passenger_error := body.to_local(actor.global_position).distance_to(passenger_frame)
		max_passenger_error = maxf(max_passenger_error,passenger_error)
		if not require(actor.is_on_floor() and passenger_error < .025, "actual original CharacterBody remains supported and within25 mm local stance during carry"):
			return false
		if not motor.moving:
			return require(absf(motor.cursor-target) < .00001, "exact continuous source arrival")
	return require(false,"bounded motor trip did not finish within600 physical frames")

func run() -> void:
	mode = arg("--floor")
	if not require(mode == "baseline", "r002 uses only unchanged original convex contacts; primitive mode is held") or not verify():
		finish()
		return
	host = Node.new()
	host.name = "AstraeaOriginalSourceCarryFixture_UNACCEPTED"
	root.add_child(host)
	var viewport := SubViewport.new()
	viewport.name = "World360"
	viewport.size = Vector2i(640,360)
	viewport.own_world_3d = true
	viewport.audio_listener_enable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	host.add_child(viewport)
	ship = Node3D.new()
	ship.name = "Astraea"
	viewport.add_child(ship)
	var space := Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts := Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors := Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var systems := Node.new();systems.name="ShipSystems";ship.add_child(systems)
	assembly = load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd").create(districts)
	if not require(assembly != null,"retained exact source section/vehicle/stations assembled once"):
		finish();return
	body = assembly.get_node("Group4OwnedTram_Source024")
	safety = assembly.get_node("Group4BoardingSafety")
	if not require(body.has_meta("initial_pose_before_tree") and body.transform.is_equal_approx(body.get_meta("initial_pose_before_tree")),"full source vehicle pose was assigned before initial tree admission"):
		finish();return
	# These are the only actor pose assignments: fresh instances are outside the
	# tree and have never entered physics. No existing actor or stock is moved.
	actor = load("res://scripts/player.gd").new()
	actor.position = body.to_global(Vector3(0,.025,-1.3))
	actor.spawn_position = actor.position
	actor.rotation.y = body.rotation.y
	actors.add_child(actor)
	cart = load("res://scripts/cleaning_cart.gd").new()
	cart.name = "CustodialCart"
	cart.transform = body.global_transform * Transform3D(Basis.IDENTITY,Vector3(0,.025,.14))
	cart.contact_monitor = true
	cart.max_contacts_reported = 32
	actors.add_child(cart)
	motor = load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd").attach_original_cart(assembly,cart)
	restraint = assembly.get_node("Group4OriginalCartRestraint")
	var budget: Node = load("res://scripts/lighting_budget.gd").new()
	budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.configure(ship,actor)
	controls=load("res://scripts/group4_tram_operating_controls.gd").build(assembly,body,safety,restraint,motor,actor,budget)
	load("res://scripts/group4_station_information.gd").build(assembly,safety)
	await process_frame
	for stock: RigidBody3D in cart.products:
		products.append({"node":stock,"id":stock.persistent_id,"parent":stock.get_parent()})
	if not require(viewport.audio_listener_enable_3d and actor.camera.current,"real listener-enabled World360 with original player's current camera"):
		finish();return
	if not require(cart.mass==18 and cart.continuous_cd and cart.persistent_id==&"custodian_cart_001" and cart.products.size()==4,"unchanged original cart mass, CCD, identity and four loose products"):
		finish();return
	stage="fresh_gravity_settling"
	for frame in range(120):
		await physics_frame
		if not continuous(frame,false):
			finish();return
	if not require(restraint.aligned() and actor.is_on_floor(),"fresh original cart settles at exact restraint datum and actual passenger is supported"):
		finish();return
	if not require(safety.stationary_frames>=15 and safety._physical_dock_matches("CENTRAL") and safety.unloaded_clear_to_depart(),"actual exact curved dock, fifteen stationary frames, closed doors and stowed bridges"):
		finish();return
	if not require(not motor.request_stop("AFT") and not restraint.request_lock() and not safety.request_boarding("CENTRAL"),"production admission holds refuse every request before fixture-only permission"):
		finish();return
	# Local test authority follows real source settling/dock/closed-door gates.
	# No production file or assembly-admission flag is enabled by this fixture.
	stage="original_clamp_and_joint"
	restraint.set_meta("integration_joint_admitted",true)
	if not require(restraint.request_lock(),"original clamp request accepted without snapping or forcing alignment"):
		finish();return
	for frame in range(160):
		await physics_frame
		if not continuous(frame,false):
			finish();return
		if restraint.phase=="locked":break
	if not require(restraint.phase=="locked" and is_instance_valid(restraint.joint) and restraint.loaded_clear_to_depart(),"four actual clamp strokes produce the original single physical joint"):
		finish();return
	for frame in range(60):
		await physics_frame
		if not continuous(frame,true):
			finish();return
	passenger_frame=body.to_local(actor.global_position)
	var start:float=motor.cursor
	stage="one_metre_outward_carry"
	motor.set_meta("integration_motion_admitted",true)
	if not await travel(start+1.):
		finish();return
	if not require(not restraint.request_unlock(),"original unlock refused away from exact dock"):
		finish();return
	stage="physical_return_to_central"
	if not await travel(start):
		finish();return
	for i in range(20):await physics_frame
	if not require(safety._physical_dock_matches("CENTRAL"),"physical return meets unchanged15-frame/5 mm/1 mrad dock criteria"):
		finish();return
	stage="original_joint_release"
	if not require(restraint.request_unlock(),"original joint release allowed only after exact stopped dock"):
		finish();return
	for frame in range(160):
		await physics_frame
		if not continuous(frame,false):
			finish();return
		if restraint.phase=="unlocked":break
	require(restraint.phase=="unlocked" and not is_instance_valid(restraint.joint) and safety.clamp_fraction<.001,"original joint released and clamps caster-clear")
	motor.set_meta("integration_motion_admitted",false)
	restraint.set_meta("integration_joint_admitted",false)
	require(not safety.get_meta("integration_boarding_admitted") and not assembly.get_meta("tram_operations_admitted"),"boarding/production assembly never admitted")
	finish()

func finish() -> void:
	# Revoke local test permission even on failure; never attempt a corrective
	# pose/velocity reset, contact exclusion or joint removal to salvage a result.
	if is_instance_valid(motor):motor.set_meta("integration_motion_admitted",false)
	if is_instance_valid(restraint):restraint.set_meta("integration_joint_admitted",false)
	var result:Dictionary={"status":"PASS_BOUNDED_ORIGINAL_SOURCE_CARRY" if failures==0 else "HOLD_BOUNDED_ORIGINAL_SOURCE_CARRY","mode":mode,"setup_successor":"initial_pose_r002","stage":stage,"checks":checks,"failures":failures,"maximum_cart_speed_m_s":max_speed,"maximum_upward_speed_m_s":max_up_speed,"maximum_joint_frame_error_m":max_cart_error,"maximum_passenger_local_error_m":max_passenger_error,"maximum_vehicle_step_m":max_body_step,"motion_frames":motion_frames,"actual_vehicle_distance_m":motor.distance_travelled if is_instance_valid(motor) else 0.,"primitive":primitive_result,"samples":samples,"one_fresh_original_player_cart_and_four_products":is_instance_valid(actor) and is_instance_valid(cart) and products.size()==4,"fixture_pose_velocity_writes_after_tree_entry":0,"production_selection":false,"do_not_infer":["whole selected ship or scenic acceptance","baseline-versus-successor causality without matched results","full loaded route","target-platform performance"]}
	print("TRAM_ORIGINAL_CARRY_RESULT "+JSON.stringify(result))
	var output:=arg("--report")
	if not output.is_empty():
		var file:=FileAccess.open(output,FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(result,"  ")+"\n")
	if is_instance_valid(host):host.free()
	quit(0 if failures==0 else 1)
