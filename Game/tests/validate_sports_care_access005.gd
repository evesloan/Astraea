extends "res://tests/medical_test_scene.gd"
# One explicit supported arrival, then original player input only. No cart driving.
const FIXTURE := "res://tests/fixtures/sports_care_access005.json"
const FIXTURE_SHA := "802371a25c9a894509019f6a615296a13d3c8dcef8fc07ac8a466b175bef5176"
const RUNTIME := "res://data/architecture/D07_SPORTS_CARE_RECEIVING.json"
const INFORMATION := "res://data/architecture/packages/sports_care/INFORMATION_TARGETS.json"
var room: Node3D
var track_motion := false
var walked_m := 0.0
var walked_frames := 0
var prior_position := Vector3.ZERO
var completed_steps: Array[String] = []
var information_cycles := 0
var privacy_queries := 0
var boundary_crossings: Dictionary = {"spine_seam":0,"source_mouth":0}

func _initialize() -> void:
	test_name = "sports_care_access005"
	call_deferred("run")

func write_receipt(status: String, detail: String = "") -> void:
	if receipt_path.is_empty(): return
	var out := {"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"walked_frames":walked_frames,"walked_m":walked_m,"support_samples":support_samples,"completed_steps":completed_steps,"information_read_close_cycles":information_cycles,"privacy_queries":privacy_queries,"boundary_crossings":boundary_crossings,"initial_arrival_calls":1,"later_teleports":0,"fixture_sha256":FileAccess.get_sha256(FIXTURE),"runtime_sha256":FileAccess.get_sha256(RUNTIME),"scope":"Actual original-player source dry/changing promenade, wash/WC/shared-rinse approaches, critical privacy eye, both RMB/E information targets, care approach and public-spine return. One initial supported arrival. No loaded-cart, species, activity capacity, operational doors/plumbing, visual or performance acceptance."}
	var file := FileAccess.open(receipt_path, FileAccess.WRITE)
	if file != null: file.store_string(JSON.stringify(out, "  ") + "\n")

func advance(count: int, _unused: bool = false) -> bool:
	for frame in range(count):
		if not await super.advance(1, false): return false
		if not track_motion: continue
		var current: Vector3 = actor.global_position
		if not require(current.distance_to(prior_position) < .25, "Unexpected displacement after single initial arrival"): return false
		if not require(absf(current.y - 35.5) < .08, "Original capsule left D07 datum"): return false
		if not support_at(Vector3(current.x, 35.5, current.z)): return false
		walked_m += Vector2(current.x-prior_position.x, current.z-prior_position.z).length()
		for spec in [[4.0,"spine_seam"],[8.0,"source_mouth"]]:
			var edge := float(spec[0])
			if (prior_position.x < edge and current.x >= edge) or (prior_position.x >= edge and current.x < edge):
				if not require(current.z > 458.0 and current.z < 462.0, "Crossed receiving boundary outside real source mouth"): return false
				boundary_crossings[str(spec[1])] = int(boundary_crossings[str(spec[1])]) + 1
		prior_position = current
	return true

func walk(point: Vector2) -> bool:
	release_inputs()
	var start := Vector2(actor.global_position.x, actor.global_position.z)
	var allowance := ceili(start.distance_to(point)/3.1*60.0) + 240
	for frame in range(allowance):
		var delta := point-Vector2(actor.global_position.x,actor.global_position.z)
		var speed := Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length() < .12 and speed < .08:
			key(KEY_W,false)
			return support_at(Vector3(point.x,35.5,point.y))
		if delta.length() > .025: actor.rotation.y = atan2(-delta.x,-delta.y)
		actor.set("pitch",0.0)
		actor.camera.rotation.x = 0.0
		key(KEY_W,delta.length()>maxf(.08,speed*speed/32.0+.025))
		if not await advance(1): return false
		walked_frames += 1
	return require(false,"Original W-input route blocked at "+str(actor.global_position)+" toward "+str(point))

func structural_privacy_ray(a: Vector3, target: Vector3) -> bool:
	var direction := target-a
	var hit := ray(a,target-direction.normalized()*.02,exclusions())
	privacy_queries += 1
	if not require(not hit.is_empty(),"Private use zone exposed from "+str(a)+" toward "+str(target)): return false
	var collider: Node = hit.collider as Node
	if not require(collider != null and room.is_ancestor_of(collider),"Privacy occlusion must come from retained room"): return false
	var mesh := collider.get_parent() as MeshInstance3D
	return require(mesh != null and str(mesh.name) in data.privacy_structural_runtime_names,"Fixture/furniture cannot substitute for structural privacy screening")

func check_privacy() -> bool:
	if not require(Vector2(actor.global_position.x,actor.global_position.z).distance_to(Vector2(31.9,403.8)) < .12,"Walked critical-eye stance required"): return false
	if not require(absf(actor.camera.global_position.y-37.15)<.08,"Ordinary1.65m eye height required"): return false
	# Fixed sampled shared-aisle rays are static geometry checks, not claims that each eye was walked.
	for spec in data.privacy_rays:
		if not structural_privacy_ray(xyz(spec.eye),xyz(spec.target)): return false
	# Also test the actual normally reached camera, rather than relying only on exact fixture points.
	for spec in data.privacy_rays:
		if absf(float(spec.eye[0])-31.9)<.00001 and absf(float(spec.eye[2])-403.8)<.00001:
			if not structural_privacy_ray(actor.camera.global_position,xyz(spec.target)): return false
	return true

func read_information(identity: String) -> bool:
	var target := room.get_node(NodePath(identity)) as Node3D
	if not require(target != null and not target.expanded,"Exact closed information target required"): return false
	var info: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INFORMATION))
	var matched := false
	for spec in info.candidates:
		if str(spec.id) != identity: continue
		matched = true
		if not require(actor.global_position.distance_to(xyz(spec.approach_feet_world_m)) < .15,"Walked authored information stance required"): return false
	if not require(matched,"Authored information identity missing"): return false
	release_inputs()
	var delta: Vector3 = target.global_position-actor.camera.global_position
	actor.rotation.y = atan2(-delta.x,-delta.z)
	var pitch := atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.set("pitch",pitch)
	actor.camera.rotation.x = pitch
	if not await advance(2): return false
	if not require(actor.target_from_view()==target,"Unchanged player ray must select actual plaque"): return false
	key(KEY_E,true)
	if not await advance(2): return false
	key(KEY_E,false)
	if not await advance(2): return false
	if not require(not target.expanded,"E without RMB must remain inactive"): return false
	focus(true)
	if not await advance(18): return false
	if not require(actor.interaction_target==target and actor.camera.fov<65.0,"Original RMB selection/zoom failed"): return false
	var hint := main.get("interaction_hint") as Label
	if not require(hint != null and hint.text==target.get_interaction_label(),"Original crisp HUD must show target prompt"): return false
	for cycle in range(2):
		key(KEY_E,true)
		if not await advance(2): return false
		key(KEY_E,false)
		if not await advance(5): return false
		if not require(target.expanded and "E · Close" in hint.text and hint.text==target.get_interaction_label(),"Original RMB/E information/HUD did not open"): return false
		key(KEY_E,true)
		if not await advance(2): return false
		key(KEY_E,false)
		if not await advance(5): return false
		if not require(not target.expanded and hint.text==target.get_interaction_label(),"Original RMB/E information/HUD did not close"): return false
		information_cycles += 1
	focus(false)
	if not await advance(18): return false
	return require(actor.interaction_target==null and actor.camera.fov>69.0 and hint.text.is_empty(),"RMB release must clear original focus/HUD")

func run() -> void:
	started = Time.get_ticks_msec()
	receipt_path = "res://artifacts/"+test_name+"_attempt_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json"
	if not require(FileAccess.get_sha256(FIXTURE)==FIXTURE_SHA,"Pinned acceptance fixture required"): return
	data = JSON.parse_string(FileAccess.get_file_as_string(FIXTURE))
	for path in data.unchanged_input_sha256:
		if not require(FileAccess.get_sha256("res://"+str(path))==str(data.unchanged_input_sha256[path]),"Original test/controller/budget changed: "+str(path)): return
	if not require(FileAccess.get_sha256(RUNTIME)==str(data.runtime_sha256) and FileAccess.get_sha256(INFORMATION)==str(data.information_manifest_sha256),"Receiving and information contracts changed"): return
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	actor = ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart = ship.find_child("CustodialCart",true,false) as RigidBody3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	built = ship.find_child("D07_SportsCare_Receiving_WIP",true,false) as Node3D
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual installed main scene and original actors required"): return
	room = built.get_node("WholeRetainedSportsCare") as Node3D
	space = ship.get_world_3d().direct_space_state
	var proof: Dictionary = load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(proof.get("validation_completed",false)),"Full current nested source/import/contact proof required"): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled,"Original active player required"): return
	var shapes := actor.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CapsuleShape3D and absf(shapes[0].shape.radius-.3)<.000001 and absf(shapes[0].shape.height-1.8)<.000001 and absf(actor.camera.position.y-1.65)<.000001,"Original body and eye contract required"): return
	if not require(ship.arrive_at(xyz(data.initial_fixture),-PI/2),"Single initial public-spine arrival refused"): return
	if not await advance(45): return
	if not support_at(Vector3(0,35.5,460),str(data.initial_floor_owner)): return
	if not require(actor.global_position.distance_to(Vector3(0,35.5,460))<.15,"Initial spine arrival failed to settle"): return
	prior_position = actor.global_position
	track_motion = true
	for step in data.steps:
		if step.kind=="walk":
			for point in step.points_xz:
				if not await walk(Vector2(float(point[0]),float(point[1]))): return
		elif step.kind=="privacy":
			if not check_privacy(): return
		elif step.kind=="information":
			if not await read_information(str(step.id)): return
		else:
			require(false,"Unknown acceptance step")
			return
		completed_steps.append(str(step.id))
	if not require(information_cycles==4 and privacy_queries==378 and int(boundary_crossings.spine_seam)>=2 and int(boundary_crossings.source_mouth)>=2,"Complete privacy, information and outward/return crossing coverage required"): return
	if not require(actor.global_position.distance_to(Vector3(0,35.5,460))<.15,"Return to original public-spine fixture required"): return
	release_inputs()
	write_receipt("PASS")
	print("SPORTS CARE ACCESS PASS: ",walked_m," metres, ",walked_frames," original-input frames, ",privacy_queries," structural privacy rays, four read-close cycles; cart acceptance separate")
	main.queue_free()
	await process_frame
	quit(0)
