extends SceneTree
const MEDICAL_RETAINED = preload("res://tests/medical_successor_guard.gd")
# New district gate. Uses the original player and actual visible door contacts.
# A single existing arrival starts at the D03 staff-lift landing; all approach,
# doorway and return movement afterward is ordinary WASD input.
const CONTRACT: String="res://data/architecture/CREW_HOME_APPROACH_RUNTIME.json"
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var camera: Camera3D
var home: Node3D
var door: Node3D
var floors: Node3D
var budget: Node
var data: Dictionary
var frames: int=0
var support_samples: int=0
var motion_samples: int=0
var last_checked_fraction: float=INF
var walked_frames: int=0
var failed: bool=false
var key_states: Dictionary={}
var selected_markers: Array[String]=[]

func _initialize() -> void: call_deferred("run")

func require(ok: bool,message: String) -> bool:
	if ok: return true
	failed=true
	paused=false
	release_inputs()
	push_error("CREW HOME APPROACH: "+message)
	quit(1)
	return false

func xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

func key(code: Key,pressed: bool) -> void:
	if key_states.get(code,false)==pressed: return
	key_states[code]=pressed
	var event: InputEventKey=InputEventKey.new()
	event.keycode=code
	event.physical_keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func focus(pressed: bool) -> void:
	var event: InputEventMouseButton=InputEventMouseButton.new()
	event.button_index=MOUSE_BUTTON_RIGHT
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func release_inputs() -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_E]: key(code,false)
	focus(false)

func ray(a: Vector3,b: Vector3) -> Dictionary:
	var query: PhysicsRayQueryParameters3D=PhysicsRayQueryParameters3D.create(a,b,1)
	query.exclude=[actor.get_rid()]
	return actor.get_world_3d().direct_space_state.intersect_ray(query)

func support() -> bool:
	var hit: Dictionary=ray(actor.global_position+Vector3.UP*.15,actor.global_position-Vector3.UP*.20)
	if not require(not hit.is_empty() and floors.is_ancestor_of(hit.collider),"Original capsule lost existing compiler support"): return false
	if not require(absf(float(hit.position.y)-12.0)<.015 and absf(actor.global_position.y-12.0)<.06 and float(hit.normal.y)>.9,"D03 support datum/normal changed"): return false
	support_samples+=1
	return true

func leaf_clear() -> bool:
	var leaves: Array=door.get("leaves")
	for leaf_value in leaves:
		var leaf: AnimatableBody3D=leaf_value as AnimatableBody3D
		for value in leaf.get_children():
			var contact: CollisionShape3D=value as CollisionShape3D
			if contact==null: continue
			var query: PhysicsShapeQueryParameters3D=PhysicsShapeQueryParameters3D.new()
			query.shape=contact.shape
			query.transform=contact.global_transform
			query.margin=.001
			query.exclude=[leaf.get_rid()]
			var hits: Array[Dictionary]=actor.get_world_3d().direct_space_state.intersect_shape(query,64)
			if not require(hits.size()<64,"Door-contact query overflow"): return false
			for hit in hits:
				if not require(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Source door contacts intersect fixed architecture: "+str(contact.name)): return false
	motion_samples+=1
	return true

func advance(count: int,check_support: bool=true) -> bool:
	for frame in range(count):
		await physics_frame
		frames+=1
		if not require(frames<12000,"Bounded home gate frame allowance exceeded"): return false
		if failed: return false
		if check_support and not support(): return false
		if is_instance_valid(door):
			var fraction: float=float(door.get("open_fraction"))
			if fraction!=last_checked_fraction:
				if not leaf_clear(): return false
				last_checked_fraction=fraction
	return true

func walk(point: Vector2) -> bool:
	release_inputs()
	var initial: Vector2=Vector2(actor.global_position.x,actor.global_position.z)
	var allowance: int=ceili(initial.distance_to(point)/3.1*60.0)+240
	for frame in range(allowance):
		var delta: Vector2=point-Vector2(actor.global_position.x,actor.global_position.z)
		var speed: float=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.16 and speed<.08:
			key(KEY_W,false)
			return support()
		if delta.length()>.025: actor.rotation.y=atan2(-delta.x,-delta.y)
		actor.set("pitch",0.0)
		camera.rotation.x=0.0
		var braking_distance: float=speed*speed/32.0+.035
		key(KEY_W,delta.length()>maxf(.11,braking_distance))
		if not await advance(1): return false
		walked_frames+=1
	return require(false,"Ordinary walking did not reach "+str(point))

func walk_points(points: Array[Vector2]) -> bool:
	for point in points:
		if not await walk(point): return false
	return true

func aim(point: Vector3) -> void:
	var delta: Vector3=point-camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	var pitch: float=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.set("pitch",pitch)
	camera.rotation.x=pitch

func push_point() -> Vector3:
	var contact: CollisionShape3D=door.find_child("HOME_Push_LEFT_SourceContact",true,false) as CollisionShape3D
	if not require(contact!=null,"Real authored push fitting missing"): return Vector3.ZERO
	return contact.global_position

func tap_e() -> bool:
	key(KEY_E,true)
	if not await advance(2): return false
	key(KEY_E,false)
	return await advance(2)

func operate(expected_open: bool,check_pause: bool=false) -> bool:
	release_inputs()
	aim(push_point())
	if not require(actor.call("target_from_view")==door,"Original camera first hit does not resolve the visible home door"): return false
	focus(true)
	if not await advance(2): return false
	if not require(actor.get("interaction_target")==door,"Original RMB target was not refreshed"): return false
	if not await tap_e(): return false
	focus(false)
	if not require(bool(door.get("desired_open"))==expected_open,"Ordinary E did not change inherited desired state"): return false
	if check_pause:
		var fraction_before: float=float(door.get("open_fraction"))
		if not require(fraction_before>0.0 and fraction_before<1.0,"Pause witness must be mid-travel"): return false
		main.call("_toggle_directory")
		if not require(paused and bool(main.get("directory_open")),"Existing directory did not pause the world"): return false
		for frame in range(8): await process_frame
		if not require(float(door.get("open_fraction"))==fraction_before,"Inherited home door moved while paused"): return false
		main.call("_toggle_directory")
		if not require(not paused and bool(actor.get("gameplay_input_enabled")),"Existing directory did not resume original controls"): return false
	for frame in range(100):
		if not await advance(1): return false
		if absf(float(door.get("open_fraction"))-(1.0 if expected_open else 0.0))<.001: return true
	return require(false,"Inherited door travel did not finish")

func source_fixture(marker_name: String) -> bool:
	var light: OmniLight3D=home.find_child("HomeSource_"+marker_name,true,false) as OmniLight3D
	if not require(light!=null and str(light.get_meta("source_marker",""))==marker_name,"Source-bound fixture missing"): return false
	if not require(ray(light.global_position,light.global_position+Vector3.DOWN*.08).is_empty(),"Fixture exit is inside opaque source geometry"): return false
	var receiver: Dictionary=ray(light.global_position,Vector3(light.global_position.x,11.9,light.global_position.z))
	if not require(not receiver.is_empty() and floors.is_ancestor_of(receiver.collider),"Source light lacks an unobstructed real floor receiver"): return false
	budget.call("refresh")
	if not await advance(15): return false
	if not require(light.visible and light.shadow_enabled,"Supported walking pose did not select its real home fixture"): return false
	var active: int=0
	for value in budget.get("sources"):
		var source: Light3D=value as Light3D
		if source.visible and source.shadow_enabled: active+=1
	if not require(active<=8 and int(budget.get("shadow_source_budget"))==8,"Shared source budget changed"): return false
	selected_markers.append(marker_name)
	return true

func run() -> void:
	data=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not require(data.runtime_adoption_approved and not data.first_pass_accepted and int(data.new_floor_owners)==0,"Unreviewed or falsely accepted home contract"): return
	for path in data.retained_runtime_pins:
		if not require(FileAccess.get_sha256("res://"+str(path))==str(data.retained_runtime_pins[path]),"Retained controller changed: "+str(path)): return
	for path in data.preserve_floors:
		if not require(MEDICAL_RETAINED.retained_sha256("res://"+str(path))==str(data.preserve_floors[path]),"Existing floor ownership bytes changed"): return
	main=(load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship=main.get_node("World360/Astraea") as Node3D
	actor=ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	camera=actor.get("camera") as Camera3D
	home=ship.find_child("CrewHomeApproach_WIP",true,false) as Node3D
	floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	if not require(home!=null and floors!=null and actor.is_physics_processing(),"Actual home or original player missing"): return
	var representations: Dictionary={str(data.home_model):0,str(data.wall_model):0,str(data.retained_wall_model):0}
	for value in ship.find_children("*","Node3D",true,false):
		var node: Node3D=value as Node3D
		var file_name: String=str(node.get_meta("catalogue_file",""))
		if representations.has(file_name): representations[file_name]=int(representations[file_name])+1
	if not require(representations[str(data.home_model)]==1 and representations[str(data.wall_model)]==1 and representations[str(data.retained_wall_model)]==0,"Old enclosure must remain preserved on disk, not duplicated in the live opening"): return
	door=home.find_child("HomeServiceDoor",true,false) as Node3D
	if not require(door!=null and str(door.get("persistent_id"))==str(data.door.persistent_id_proposal),"Stable source-fitting door identity missing"): return
	if not require(door.get_script().get_base_script().resource_path=="res://scripts/service_door.gd","Home door must inherit the existing functioning controller"): return
	if not require(not bool(door.get("desired_open")) and is_zero_approx(float(door.get("open_fraction"))),"Home privacy door must begin physically closed"): return
	if not require(bool(ship.call("arrive_at",Vector3(-21,12.1,-490),0.0)),"Existing D03 staff arrival rejected"): return
	if not await advance(30,false): return
	if not await walk_points([Vector2(-21,-500),Vector2(-57,-500),Vector2(-57,-432),Vector2(-50.2,-432)]): return
	aim(push_point())
	focus(false)
	if not await tap_e(): return
	if not require(not bool(door.get("desired_open")),"Unfocused E operated the home door"): return
	if not await operate(true,true): return
	if not await walk(Vector2(-47.05,-432.1)): return
	aim(push_point())
	focus(true)
	if not await advance(2) or not await tap_e(): return
	focus(false)
	if not require(bool(door.get("obstructed")) and bool(door.get("desired_open")) and float(door.get("open_fraction"))>.999,"Actual capsule in the real sweep must prevent closing"): return
	if not await walk(Vector2(-45.2,-432)) or not await advance(8): return
	if not require(not bool(door.get("obstructed")),"Actual clear-space recovery failed"): return
	if not await source_fixture("HOME_TASK_1_EMITTER"): return
	if not await walk_points([Vector2(-45.2,-424.8),Vector2(-41,-424.8)]): return
	if not await source_fixture("HOME_TASK_2_EMITTER"): return
	if not await walk_points([Vector2(-45.2,-424.8),Vector2(-45.8,-432.2)]): return
	if not await operate(false) or not await operate(true): return
	# Close from a supported exterior pose within the unchanged2.5m ray,
	# rather than the farther arrival pose while the leaf is fully open.
	if not await walk_points([Vector2(-45.2,-432),Vector2(-48.8,-433.2)]): return
	if not await operate(false): return
	if not await walk_points([Vector2(-57,-432),Vector2(-57,-500),Vector2(-21,-500),Vector2(-21,-490)]): return
	release_inputs()
	var result: Dictionary={"status":"PASS","scope":"Actual original-player home approach/return, inherited door and source fixtures; no loaded-cart/home occupancy/visual/whole-ship acceptance","frames":frames,"ordinary_walk_frames":walked_frames,"support_samples":support_samples,"door_contact_samples":motion_samples,"selected_home_markers":selected_markers,"new_floor_owners":0,"first_pass_accepted":false}
	var file: FileAccess=FileAccess.open("res://artifacts/crew_home_approach_validation.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"\t"))
	print("CREW HOME APPROACH PASS:",JSON.stringify(result))
	main.queue_free()
	await process_frame
	quit(0)
