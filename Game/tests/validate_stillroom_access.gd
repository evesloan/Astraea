extends "res://tests/medical_test_scene.gd"
var travelled_m := 0.0
var walked_frames := 0
func _initialize() -> void:
	test_name="stillroom_player_access"
	call_deferred("run")
func write_receipt(status: String,detail: String="") -> void:
	if receipt_path.is_empty():return
	FileAccess.open(receipt_path,FileAccess.WRITE).store_string(JSON.stringify({"status":status,"detail":detail,"walked_m":travelled_m,"walked_frames":walked_frames,"support_samples":support_samples,"scope":"Unchanged player W-input dogleg arrival, two source approaches and return to spine. No driven-cart or final-art acceptance."},"  "))
func support_at(point: Vector3,owner: String="") -> bool:
	var hit: Dictionary=ray(point+Vector3.UP*.14,point-Vector3.UP*.16,exclusions())
	if not require(not hit.is_empty(),"Missing support: "+str(point)):return false
	var original:=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	var receiving:=ship.get_node("ShipSpace/StillroomCandidateStructuralFloors")
	if not require(original.is_ancestor_of(hit.collider) or receiving.is_ancestor_of(hit.collider),"Wrong support owner: "+str(point)):return false
	if not require(absf(hit.position.y-point.y)<.015 and hit.normal.y>.95,"Bad support level/normal: "+str(point)):return false
	support_samples+=1
	return true
func walk(point: Vector2) -> bool:
	release_inputs()
	var start := Vector2(actor.global_position.x, actor.global_position.z)
	var allowance := ceili(start.distance_to(point) / 3.1 * 60.0) + 240
	for frame in range(allowance):
		var delta := point - Vector2(actor.global_position.x, actor.global_position.z)
		var speed := Vector2(actor.velocity.x, actor.velocity.z).length()
		if delta.length() < .16 and speed < .08:
			key(KEY_W, false)
			return support_at(Vector3(point.x, 78.0, point.y))
		if delta.length() > .025: actor.rotation.y = atan2(-delta.x, -delta.y)
		actor.set("pitch", 0.0)
		actor.camera.rotation.x = 0.0
		key(KEY_W, delta.length() > maxf(.11, speed * speed / 32.0 + .035))
		var previous: Vector3 = actor.global_position
		if not await advance(1, false): return false
		if not require(actor.global_position.distance_to(previous) < .25, "Unexpected displacement after arrival"): return false
		if not require(absf(actor.global_position.y - 78.0) < .08, "Player left D12 floor datum"): return false
		if not support_at(Vector3(actor.global_position.x, 78.0, actor.global_position.z)): return false
		travelled_m += Vector2(actor.global_position.x - previous.x, actor.global_position.z - previous.z).length()
		walked_frames += 1
	return require(false, "W-input route blocked at " + str(actor.global_position) + " toward " + str(point))

func run() -> void:
	started=Time.get_ticks_msec()
	receipt_path="res://artifacts/stillroom_player_access.json"
	main=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for frame in range(12):await physics_frame
	ship=main.get_node("World360/Astraea")
	built=ship.get_node("ShipSpace/Districts/StillroomReceiving_WIP")
	load("res://scripts/tidal_lift_candidate.gd").build(ship)
	actor=ship.get_node("ShipSpace/PersistentActors/Player")
	cart=ship.find_child("CustodialCart",true,false)
	space=ship.get_world_3d().direct_space_state
	for frame in range(6):await physics_frame
	if not require(ship.arrive_at(Vector3(0,78.1,-216),-PI/2),"Spine arrival refused"):return
	if not await advance(45,false):return
	var points: Array[Vector2]=[Vector2(4,-216),Vector2(8.6,-216),Vector2(11,-216),Vector2(11,-226),Vector2(16,-226),Vector2(16,-241),Vector2(16,-246.7),Vector2(34,-246.7),Vector2(34,-226),Vector2(34,-246.7),Vector2(16,-246.7),Vector2(16,-241),Vector2(16,-226),Vector2(11,-226),Vector2(11,-216),Vector2(11,-206),Vector2(16,-206),Vector2(16,-191),Vector2(14.5,-190.6),Vector2(16,-191),Vector2(16.3,-188.8),Vector2(16.3,-185.1),Vector2(14,-185.1),Vector2(16.3,-185.1),Vector2(16.3,-188.8),Vector2(16,-191),Vector2(16,-206),Vector2(11,-206),Vector2(11,-216),Vector2(8.6,-216),Vector2(4,-216),Vector2(0,-216)]
	for point in points:
		if not await walk(point):return
	release_inputs()
	write_receipt("PASS")
	print("STILLROOM_PLAYER_ACCESS PASS metres=",travelled_m," frames=",walked_frames)
	quit(0)
