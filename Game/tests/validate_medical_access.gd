extends "res://tests/medical_test_scene.gd"
var walked_frames: int=0
var travelled_m: float=0

func _initialize() -> void:
	test_name="medical_access";call_deferred("run")

func walk(point: Vector2) -> bool:
	release_inputs()
	var start: Vector2=Vector2(actor.global_position.x,actor.global_position.z)
	var allowance: int=ceili(start.distance_to(point)/3.1*60.0)+240
	for frame in range(allowance):
		var delta: Vector2=point-Vector2(actor.global_position.x,actor.global_position.z)
		var speed: float=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.16 and speed<.08:
			key(KEY_W,false);return support_at(Vector3(point.x,21,point.y))
		if delta.length()>.025: actor.rotation.y=atan2(-delta.x,-delta.y)
		actor.set("pitch",0.0);actor.camera.rotation.x=0.0
		key(KEY_W,delta.length()>maxf(.11,speed*speed/32.0+.035))
		var previous: Vector3=actor.global_position
		if not await advance(1,true): return false
		travelled_m+=Vector2(actor.global_position.x-previous.x,actor.global_position.z-previous.z).length();walked_frames+=1
	return require(false,"Ordinary W-input route blocked at "+str(actor.global_position)+" toward "+str(point))

func route(points: Array) -> bool:
	for point in points:
		if not await walk(Vector2(float(point[0]),float(point[2]))): return false
	return true

func exercise() -> bool:
	if not require(ship.arrive_at(Vector3(-5.4,21.1,-432),0.0),"Existing supported D05 arrival refused"): return false
	# Initial supported arrival starts100mm above the floor; settle before measured travel.
	if not await advance(45): return false
	if not require(absf(actor.global_position.y-21.0)<.08,"Initial D05 arrival did not settle on its real floor"): return false
	if not support_at(Vector3(actor.global_position.x,21,actor.global_position.z)): return false
	if not await route(data.physical_test_routes.core_waiting_round_trip_xyz): return false
	if not await route([[-11,21,-432],[-11,21,-446],[-25,21,-446]]): return false
	var branch: Array=data.physical_test_routes.support_capsule_branch_xyz
	if not await route(branch): return false
	var reverse: Array=branch.duplicate();reverse.reverse()
	if not await route(reverse): return false
	if not await route([[-18,21,-446],[-11,21,-446],[-11,21,-432],[-5.4,21,-432]]): return false
	if not await walk_connected_triage(): return false
	metrics["ordinary_walking_frames"]=walked_frames;metrics["walked_metres"]=travelled_m
	metrics["initial_supported_arrivals"]=1;metrics["later_player_teleports"]=0
	metrics["scope"]="Ordinary player-input waiting/support round trip. Diagnostic cart turn and species/robot fit are separate."
	metrics["triage_scope"]="Same supported player walks all eight real source-open rooms and returns to the core; no later arrival or teleport."
	return true


func walk_connected_triage() -> bool:
	# Continue from the original completed core/waiting/support round trip.
	# Every room visit uses the same production capsule and ordinary W input.
	if not await route([[-11,21,-432],[-11,21,-446],[-11,21,-458]]): return false
	var seen: Array[String]=[]
	for index in [0,4,1,5,2,6,3,7]:
		var room: Dictionary=triage_evidence.rooms[index]
		if not await route([room.corridor_xyz,room.portal_xyz]): return false
		if not await route(room.walk_points_xyz): return false
		if not support_at(xyz(room.walk_points_xyz[-1]),str(data.new_floor_owner)): return false
		seen.append(str(room.programme_child))
		if not await route([room.portal_xyz,room.corridor_xyz]): return false
	if not await route([[-11,21,-458],[-11,21,-446],[-11,21,-432],[-5.4,21,-432]]): return false
	if not require(seen.size()==8,"Walk every exact triage child before returning to the original core"): return false
	metrics["triage_walked_room_ids"]=seen
	return true
