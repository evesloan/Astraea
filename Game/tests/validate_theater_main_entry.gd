extends SceneTree
# Actual main-scene door, ordinary focused inputs and loaded-cart crossing.
# One initial cart/player fixture only; no controller, leaf, cart or product pose writes afterward.
const ENTRY=preload("res://tests/theater_d11_entry_probe.gd")
const FLOOR: float=69.5
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var camera: Camera3D
var cart: RigidBody3D
var door: Node3D
var stage=preload("res://tests/theater_stage_probe.gd").new()
var data: Dictionary
var frames: int=0
var supports: int=0
var walking_frames: int=0
var loaded_frames: int=0
var peak_leaf_speed: float=0.0
var elapsed_start: int=0
var cart_distance: float=0.0
var last_cart: Vector3
var last_actor: Vector3
var last_leaves: Array[Vector3]=[]
var keys: Dictionary={}
var fixture_ready: bool=false
var failed: bool=false
var geometry: Dictionary
func _initialize() -> void:
	elapsed_start=Time.get_ticks_msec();call_deferred("run")
func _process(_delta: float) -> bool:
	if not failed and Time.get_ticks_msec()-elapsed_start>230000:require(false,"230-second bounded entry test watchdog")
	return false
func require(ok: bool,message: String) -> bool:
	if ok:return true
	failed=true;paused=false;release_inputs();push_error("THEATER MAIN ENTRY: "+message);quit(1);return false
func key(code: Key,pressed: bool) -> void:
	if keys.get(code,false)==pressed:return
	keys[code]=pressed
	var event: InputEventKey=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()
func focus(pressed: bool) -> void:
	var event: InputEventMouseButton=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()
func release_inputs() -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_E]:key(code,false)
	focus(false)
func aim(target: Vector3) -> void:
	var delta: Vector3=target-camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());camera.rotation.x=actor.pitch
func support() -> bool:
	var hit: Dictionary=stage.ray(actor.global_position+Vector3.UP*.14,actor.global_position-Vector3.UP*.18,[actor.get_rid()])
	if not require(not hit.is_empty() and stage.floors.is_ancestor_of(hit.collider),"Player lost existing compiled floor support"):return false
	if not require(absf(actor.global_position.y-FLOOR)<.065 and absf(float(hit.position.y)-FLOOR)<.015 and hit.normal.y>.9,"Player support datum/normal changed"):return false
	supports+=1;return true
func physical_frame() -> bool:
	if not fixture_ready:return true
	if not support():return false
	if not require(actor.global_position.distance_to(last_actor)<.15,"Unchecked player discontinuity"):return false
	last_actor=actor.global_position
	var displacement: float=cart.global_position.distance_to(last_cart)
	if not require(displacement<.15 and cart.linear_velocity.length()<8.0 and cart.global_basis.y.dot(Vector3.UP)>.9,"Loaded cart discontinuity, speed or tip"):return false
	cart_distance+=displacement;last_cart=cart.global_position
	if not require(cart.products.size()==4 and cart.get_parent().name=="PersistentActors","Cart identity/parent changed"):return false
	for product in cart.products:
		var p: Vector3=cart.to_local(product.global_position)
		if not require(product.get_parent()==cart.get_parent() and p.is_finite() and p.y>.8 and p.y<1.3 and absf(p.x)<.4 and absf(p.z)<.6,"One of four real loose products escaped its tray"):return false
	for i in range(2):
		var leaf: AnimatableBody3D=door.leaves[i]
		var speed: float=leaf.global_position.distance_to(last_leaves[i])*60.0
		peak_leaf_speed=maxf(peak_leaf_speed,speed)
		if not require(speed<=1.001,"Source leaf exceeded fitted1m/s maximum"):return false
		last_leaves[i]=leaf.global_position
	return true
func advance(count: int) -> bool:
	for frame in range(count):
		await physics_frame;frames+=1
		if not require(frames<12000,"Entry frame allowance exceeded"):return false
		if failed or not physical_frame():return false
	return true
func walk(target: Vector2) -> bool:
	release_inputs()
	var initial: float=Vector2(actor.global_position.x,actor.global_position.z).distance_to(target)
	var allowance: int=ceili(initial/3.1*60.0)+240
	for frame in range(allowance):
		var delta: Vector2=target-Vector2(actor.global_position.x,actor.global_position.z)
		var speed: float=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.16 and speed<.08:key(KEY_W,false);return support()
		if delta.length()>.025:actor.rotation.y=atan2(-delta.x,-delta.y)
		actor.pitch=0.0;camera.rotation.x=0.0
		key(KEY_W,delta.length()>maxf(.11,speed*speed/32.0+.035))
		if not await advance(1):return false
		walking_frames+=1
	return require(false,"Ordinary walking stalled toward "+str(target)+" at "+str(actor.global_position))
func call_button(index: int,expected: bool,focused: bool=true) -> bool:
	release_inputs();aim(ENTRY.xyz(data.controls[index].target_native))
	if not require(actor.target_from_view()==door,"Actual camera ray misses source-backed control "+str(index)):return false
	focus(focused)
	if not await advance(2):return false
	key(KEY_E,true)
	if not await advance(2):return false
	key(KEY_E,false);focus(false)
	if not await advance(2):return false
	return require(bool(door.desired_open)==expected,"Focused/unfocused input changed the wrong desired state")
func await_pose(open: bool) -> bool:
	for frame in range(240):
		if not await advance(1):return false
		if float(door.open_fraction)==(1.0 if open else 0.0):
			ENTRY.check_installation(ship);return true
	return require(false,"Door failed to reach requested terminal pose")
func closed_barrier() -> bool:
	for z in [-127.4,-124.6]:
		for y in [70.0,71.2,72.35]:
			var hit: Dictionary=stage.ray(Vector3(-33.75,y,z),Vector3(-34.75,y,z),[actor.get_rid(),cart.get_rid()])
			if not require(not hit.is_empty() and hit.collider in door.leaves,"Closed source leaf failed barrier ray"):return false
	return true
func grip_cart(expected: bool) -> bool:
	release_inputs();aim(cart.global_transform*cart.grip_local)
	if not require(actor.target_from_view()==cart.interaction_owner,"Original real cart handle is unreachable"):return false
	focus(true)
	if not await advance(2):return false
	key(KEY_E,true)
	if not await advance(2):return false
	key(KEY_E,false);focus(false)
	if not await advance(2):return false
	return require((cart.driver==actor)==expected and (actor.held_interaction==cart.interaction_owner)==expected,"Original cart grip/release failed")
func drive_until(x: float) -> bool:
	actor.rotation.y=PI/2;actor.pitch=0.0;camera.rotation.x=0.0;key(KEY_W,true)
	for frame in range(900):
		if not await advance(1):return false
		loaded_frames+=1
		if not require(cart.driver==actor and actor.held_interaction==cart.interaction_owner,"Loaded grip changed while crossing"):return false
		for local in [Vector3(-.3,0,-.5),Vector3(.3,0,-.5),Vector3(-.3,0,.5),Vector3(.3,0,.5)]:stage.floor_at(cart.global_transform*local)
		if actor.global_position.x<=x:
			key(KEY_W,false);return await advance(35)
	key(KEY_W,false);return require(false,"Ordinary loaded-cart crossing stalled")
func save_result() -> void:
	var output: String=OS.get_environment("THEATER_ENTRY_QA_OUTPUT")
	if output.is_empty():return
	var result: Dictionary={"status":"PASS_INSTALLED_D11_MAIN_ENTRY","frames":frames,"ordinary_walk_frames":walking_frames,"loaded_cart_frames":loaded_frames,"support_samples":supports,"cart_distance_m":cart_distance,"peak_leaf_speed_m_s":peak_leaf_speed,"two_source_groups":2,"reused_mesh_contact_batches":6,"moving_triangles":724,"new_call_triangles":24,"other_inactive_groups":37,"initial_fixture_only":true,"source_geometry":geometry,"full_venue_or_save_acceptance":false}
	var file: FileAccess=FileAccess.open(output,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(result,"  ",true,true));file.close()
func run() -> void:
	main=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(150):await physics_frame
	ship=main.get_node("World360/Astraea")as Node3D;stage.configure(ship)
	actor=stage.actor;camera=actor.camera;cart=stage.cart;door=ENTRY.get_door(ship);data=ENTRY.contract()
	ENTRY.check_installation(ship);geometry=ENTRY.check_external_geometry(ship)
	stage.check_motion_poses_and_barriers()
	var products: Array[Vector3]=[]
	for product in cart.products:products.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	cart.global_position=Vector3(-29,FLOOR+.04,-126);cart.rotation=Vector3(0,PI/2,0);cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*products[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	assert(ship.arrive_at(ENTRY.xyz(data.controls[1].stance_native)+Vector3.UP*.1,PI/2))
	actor.set_physics_process(true);actor.set_controls_enabled(true)
	for frame in range(90):await physics_frame
	last_actor=actor.global_position;last_cart=cart.global_position
	for leaf in door.leaves:last_leaves.append(leaf.global_position)
	fixture_ready=true
	# Exterior: ordinary unfocused input does nothing; focused E closes the real pair.
	if not await call_button(1,true,false):return
	if not await call_button(1,false):return
	if not await advance(30):return
	var mid: float=float(door.open_fraction)
	if not require(mid>0.0 and mid<1.0,"Pause witness was not mid-motion"):return
	main.call("_toggle_directory")
	if not require(paused,"Existing directory did not pause world"):return
	for frame in range(8):await process_frame
	if not require(float(door.open_fraction)==mid,"Door moved while world paused"):return
	main.call("_toggle_directory")
	if not require(not paused and actor.gameplay_input_enabled,"Existing input did not resume"):return
	if not await await_pose(false)or not closed_barrier():return
	if not await call_button(1,true)or not await await_pose(true):return
	# Walk through the supported existing opening to the interior control.
	for point in [Vector2(-32.8,-126),Vector2(-36,-126),Vector2(-35.9,-130.8)]:
		if not await walk(point):return
	if not await call_button(0,false):return
	if not await advance(45):return
	var reversed_from: float=float(door.open_fraction)
	if not require(reversed_from>0.0 and reversed_from<1.0,"Reversal witness needs moving leaves"):return
	if not await call_button(0,true)or not await await_pose(true):return
	# Reversal and completed closure from the other source-backed control.
	if not await call_button(0,false)or not await await_pose(false)or not closed_barrier():return
	if not await call_button(0,true)or not await await_pose(true):return
	for point in [Vector2(-36,-126),Vector2(-34.25,-126)]:
		if not await walk(point):return
	# Direct inherited interaction is a deliberate occupied-opening test, not a fake input claim.
	door.interact(actor)
	if not require(door.obstructed and door.desired_open and float(door.open_fraction)==1.0,"Player in full travel volume must reject closure"):return
	if not await advance(12):return
	if not await walk(Vector2(-32.8,-126)):return
	if not await walk(Vector2(-32.8,-128.05)):return
	if not await call_button(1,false):return
	if not await walk(Vector2(-33.83,-126)):return
	var stopped: float=float(door.open_fraction)
	if not require(door.obstructed and stopped>0.0 and stopped<1.0,"Approaching original capsule did not stop moving pair"):return
	if not await advance(15):return
	if not require(float(door.open_fraction)==stopped,"Occupied door kept moving"):return
	if not await walk(Vector2(-32.8,-126)):return
	if not await await_pose(false):return
	if not await walk(Vector2(-32.8,-128.05)):return
	if not await call_button(1,true)or not await await_pose(true):return
	# Existing four-product cart reaches the aperture under ordinary held-cart W.
	for point in [Vector2(-31,-128.05),Vector2(-27.38,-128.05),Vector2(-27.38,-126)]:
		if not await walk(point):return
	if not await grip_cart(true)or not await drive_until(-32.58)or not await grip_cart(false):return
	if not await walk(Vector2(-32.8,-128.05)):return
	if not await call_button(1,true):return
	if not require(door.obstructed and float(door.open_fraction)==1.0,"Actual loaded cart across travel must reject closure"):return
	var grip: Vector3=cart.global_transform*Vector3(0,0,1.62)
	if not await walk(Vector2(grip.x,grip.z)):return
	if not await grip_cart(true)or not await drive_until(-36.4)or not await grip_cart(false):return
	for point in [Vector2(-36.4,-128.0),Vector2(-35.9,-130.8)]:
		if not await walk(point):return
	if not await call_button(0,false)or not await await_pose(false)or not closed_barrier():return
	if not await call_button(0,true)or not await await_pose(true):return
	stage.check_motion_poses_and_barriers();ENTRY.check_installation(ship)
	if not require(peak_leaf_speed>.95 and loaded_frames>240 and cart_distance>8.0,"Meaningful motion and loaded crossing witnesses missing"):return
	save_result();release_inputs()
	print("THEATER MAIN ENTRY PASS: both original source leaves,724 unchanged contact triangles, focused controls both sides, close/open/reversal/pause, original player and real loaded-cart obstruction, supported ordinary walking and four loose products. Other37groups remain inactive. No broad-body, lift, save or complete-venue acceptance.")
	main.queue_free();await process_frame;quit(0)
