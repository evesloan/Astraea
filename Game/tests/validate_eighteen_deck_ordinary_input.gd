extends SceneTree
# Additive acceptance candidate. UNRUN until root schedules the actual engine.
# No fixture relocation, controller calls, velocity writes, or disabled physics.
const RESULT := "res://artifacts/eighteen_deck_ordinary_input.json"
const INPUT_PATHS := ["scripts/ship.gd", "scripts/player.gd", "scripts/commons_lift.gd", "scripts/lift_button.gd", "scripts/lift_gate.gd", "scripts/primary_atrium_core.gd", "data/design_contract.json", "data/architecture/PRIMARY_ATRIUM_CORE.json", "data/generated/structural_meshes.json", "tests/validate_eighteen_deck_ordinary_input.gd"]
var actor: CharacterBody3D
var ship: Node3D
var lift: Node3D
var heights: Array = []
var initial_hashes: Dictionary = {}
var last := Vector3.ZERO
var frames := 0
var distance_m := 0.0
var phase := "startup"
var failure := ""
var started := Time.get_ticks_msec()
var exits: Dictionary = {}
var stairs_up: Array = []
var stairs_down: Array = []
var milestones: Array = []
var trace: Array = []
var finished := false
func _initialize() -> void: call_deferred("run")
func v(a: Vector3) -> Array: return [a.x,a.y,a.z]
func key(code: Key, down: bool) -> void:
	var event := InputEventKey.new(); event.keycode=code; event.physical_keycode=code; event.pressed=down
	Input.parse_input_event(event); Input.flush_buffered_events()
func focus(down: bool) -> void:
	var event := InputEventMouseButton.new(); event.button_index=MOUSE_BUTTON_RIGHT; event.pressed=down
	Input.parse_input_event(event); Input.flush_buffered_events()
func hashes() -> Dictionary:
	var out: Dictionary={}
	for path in INPUT_PATHS: out[path]=FileAccess.get_sha256("res://"+path)
	return out
func receipt(passed: bool) -> void:
	if finished: return
	finished=true; key(KEY_W,false); key(KEY_E,false); focus(false)
	var end_hashes:=hashes()
	var stable:=end_hashes==initial_hashes
	var result: Dictionary={"status":"PASS" if passed and stable else "FAILED", "failure":failure if stable else "Source changed during run", "phase":phase, "frames":frames, "travelled_m":distance_m, "initial_fixture_relocations":0, "ordinary_player_physics":true, "deck_exits_and_reboarding":exits, "stairs_up":stairs_up, "stairs_down":stairs_down, "milestones":milestones, "input_hashes":initial_hashes, "end_hashes":end_hashes, "trace":trace, "scope":"One actual default-spawn/central-core/18-deck landing-and-bypass/stair/return circuit. Not every destination, cart, other cores, tram, visual quality, freehand comfort or performance acceptance."}
	var file:=FileAccess.open(RESULT,FileAccess.WRITE)
	if file!=null: file.store_string(JSON.stringify(result,"  ")); file.close()
	if passed and stable: print("EIGHTEEN DECK ORDINARY INPUT PASS: default spawn, all18 exits/reboards,17 stairs both ways, physical lift and return; bounded central spine only")
	else: push_error("EIGHTEEN DECK ORDINARY INPUT FAILED: "+str(result.failure)+" during "+phase)
	quit(0 if passed and stable else 1)
func bad(message: String) -> bool:
	failure=message; receipt(false); return false
func _process(_delta: float) -> bool:
	if not finished and Time.get_ticks_msec()-started>1800000: bad("30-minute wall watchdog")
	return false
func sample() -> bool:
	frames+=1
	var now:=actor.global_position
	if not now.is_finite(): return bad("Nonfinite player position")
	var displacement:=now.distance_to(last)
	# 3.1 m/s walking and 2.4 m/s vertical platform cannot legitimately jump 0.15 m in one fixed60 frame.
	if displacement>.15: return bad("Discontinuous player motion / recovery: "+str(displacement))
	distance_m+=displacement; last=now
	if not actor.is_physics_processing() or not actor.gameplay_input_enabled: return bad("Normal player processing/input disabled")
	if now.y<-.15 or now.y>106.7: return bad("Player left canonical supported vertical bounds")
	var ray:=PhysicsRayQueryParameters3D.create(now+Vector3.UP*.18,now-Vector3.UP*.28)
	ray.exclude=[actor.get_rid()]
	var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
	if hit.is_empty() or hit.normal.y<.65: return bad("No supported floor/stair/cabin beneath player")
	if lift.phase=="moving":
		if lift.cabin_gate.open_fraction>.001: return bad("Moving cabin gate is open")
		for gate in lift.landing_gates:
			if gate.open_fraction>.001: return bad("Shaft landing gate open during movement")
	if frames%30==0: trace.append({"frame":frames,"phase":phase,"position":v(now),"support":str(hit.collider.get_path()),"lift_phase":lift.phase})
	if frames>160000: return bad("Bounded circuit exceeded 160000 fixed60 frames")
	return true
func settle(count: int=20) -> bool:
	key(KEY_W,false)
	for i in range(count):
		await physics_frame
		if not sample(): return false
	return true
func walk(x: float,z: float,y: float) -> bool:
	var initial:=Vector2(x-actor.position.x,z-actor.position.z).length()
	for frame in range(ceili(initial/3.1*60)+420):
		var delta:=Vector3(x-actor.position.x,0,z-actor.position.z)
		var speed:=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.075 and speed<.08:
			key(KEY_W,false)
			if absf(actor.position.y-y)>.14: return bad("Waypoint reached on wrong level: "+str(actor.position)+" expected "+str(y))
			return true
		# Only view orientation is set; displacement remains ordinary W-input physics.
		actor.rotation.y=atan2(-delta.x,-delta.z)
		key(KEY_W,delta.length()>.06+speed*speed/32.0)
		await physics_frame
		if not sample(): return false
	return bad("W movement stalled toward "+str(Vector3(x,y,z))+" at "+str(actor.position))
func path(points: Array,y: float) -> bool:
	for point in points:
		if not await walk(float(point[0]),float(point[1]),y): return false
	return true
func press_button(button: Node3D) -> bool:
	if not await settle(): return false
	var aim: Vector3=button.global_position-actor.camera.global_position
	actor.rotation.y=atan2(-aim.x,-aim.z)
	actor.pitch=atan2(aim.y,Vector2(aim.x,aim.z).length()); actor.camera.rotation.x=actor.pitch
	if actor.target_from_view()!=button: return bad("Physical control cannot be targeted: "+str(button.name))
	focus(true)
	if not await settle(2): return false
	key(KEY_E,true)
	if not await settle(3): return false
	key(KEY_E,false); focus(false)
	return true
func wait_lift(goal: int) -> bool:
	var travel:=absf(float(heights[goal])-lift.cabin.position.y)
	var budget:=ceili((travel/lift.maximum_speed+lift.maximum_speed/lift.acceleration+12)*60)
	for frame in range(budget):
		await physics_frame
		if not sample(): return false
		if lift.phase=="idle" and lift.current_floor==goal: return true
	return bad("Lift did not arrive/open at requested deck "+str(goal+1))
func ride(goal: int) -> bool:
	phase="lift to D%02d"%(goal+1)
	var button:=lift.find_child("primary_atrium_cabin_D%02d"%(goal+1),true,false) as Node3D
	if button==null: return bad("Destination button missing")
	if not await press_button(button): return false
	if lift.destination_floor!=goal: return bad("RMB/E did not select intended destination")
	if not await wait_lift(goal): return false
	if absf(actor.position.y-float(heights[goal]))>.14: return bad("Player not carried to destination")
	milestones.append({"phase":phase,"frame":frames,"position":v(actor.position)})
	return true
func board(deck: int) -> bool:
	return await path([[-3.4,-106],[-.8,-106],[.35,-106],[.35,-104.75]],float(heights[deck]))
func exit_and_reboard(deck: int) -> bool:
	phase="D%02d exit, supported bypass, reboard"%(deck+1)
	var y:=float(heights[deck])
	if not await path([[.35,-106],[-.8,-106],[-3.4,-106],[-5.5,-106],[-5.5,-111],[0,-111],[0,-114],[0,-111],[5.5,-111],[5.5,-80],[5.5,-111],[0,-111],[-5.5,-111],[-5.5,-106]],y): return false
	if not await board(deck): return false
	exits["D%02d"%(deck+1)]={"frame":frames,"floor_y":y,"physical_exit_bypass_reboard":true}
	return true
func run() -> void:
	initial_hashes=hashes()
	for path_name in initial_hashes:
		if str(initial_hashes[path_name]).is_empty(): bad("Missing input: "+str(path_name)); return
	var contract: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for datum in contract.deck_datums: heights.append(float(datum.floor_elevation_m))
	var main: Node=(load("res://scenes/main.tscn") as PackedScene).instantiate(); root.add_child(main)
	for frame in range(120): await physics_frame
	ship=main.get_node("World360/Astraea"); actor=ship.get_node("ShipSpace/PersistentActors/Player"); lift=ship.find_child("PrimaryAtriumLift",true,false)
	if actor.position.distance_to(Vector3(63,52.5,-20.5))>.15: bad("Actual default spawn differs from retained supported salon start"); return
	if heights.size()!=18 or lift.floor_heights!=heights: bad("Canonical and lift datums disagree"); return
	last=actor.global_position
	phase="default salon spawn to D09 central lift"
	# Reverse existing validate_salon route, then nominated east atrium/backbone corridor.
	if not await path([[66,-12],[63,-4],[56,0],[49.5,0],[49.5,-65.5],[45,-65.5],[45,-72],[5.5,-72],[5.5,-111],[0,-111],[-5.5,-111],[-5.5,-104.35],[-3.5,-104.35]],52.5): return
	var call:=lift.find_child("D09_primary_atrium_lift_call",true,false) as Node3D
	if call==null: bad("D09 call button absent"); return
	if not await press_button(call) or not await wait_lift(8): return
	if not await path([[-3.5,-106]],52.5) or not await board(8): return
	if not await exit_and_reboard(8): return
	for deck in range(18):
		if lift.current_floor!=deck:
			if not await ride(deck): return
		if not await exit_and_reboard(deck): return
	# Physical lift exit leads directly to the known upper stair landing.
	phase="D18 cabin to upper stairs"
	if not await path([[.35,-106],[-.8,-106],[-5.5,-106],[-5.5,-100],[-1.75,-100],[-1.75,-98.4]],106.5): return
	for lower in range(16,-1,-1):
		phase="stair descent D%02d to D%02d"%[lower+2,lower+1]
		var half: float=(float(heights[lower])+float(heights[lower+1]))*.5
		if not await walk(-1.75,-87,half): return
		if not await walk(1.75,-87,half): return
		if not await walk(1.75,-98.4,float(heights[lower])): return
		stairs_down.append(lower+1)
		if lower>0 and not await walk(-1.75,-98.4,float(heights[lower])): return
	for lower in range(17):
		phase="stair ascent D%02d to D%02d"%[lower+1,lower+2]
		var half: float=(float(heights[lower])+float(heights[lower+1]))*.5
		if not await walk(1.75,-96.5,float(heights[lower])): return
		if not await walk(1.75,-87,half): return
		if not await walk(-1.75,-87,half): return
		if not await walk(-1.75,-98.4,float(heights[lower+1])): return
		stairs_up.append(lower+2)
		if lower<16 and not await walk(1.75,-98.4,float(heights[lower+1])): return
	phase="D18 stairs to retained waiting cabin"
	if not await path([[-1.75,-100],[-5.5,-100],[-5.5,-106]],106.5) or not await board(17): return
	if not await ride(8): return
	phase="D09 return to actual default salon spawn"
	if not await path([[.35,-106],[-.8,-106],[-5.5,-106],[-5.5,-111],[0,-111],[5.5,-111],[5.5,-72],[45,-72],[45,-65.5],[49.5,-65.5],[49.5,0],[56,0],[63,-4],[66,-12],[63,-20.5]],52.5): return
	if not await settle(30): return
	if exits.size()!=18 or stairs_up.size()!=17 or stairs_down.size()!=17: bad("Incomplete circuit coverage"); return
	receipt(true)
