extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
var operations:Array=[]
var fixtures_started:=0
var routes_completed:=0
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
	var result:Dictionary=await walk_to(actor,goal)
	result.scope=label;legs.append(result)
	record("staff_leg_"+str(legs.size()),result.reached and result.floor_contact)
	return result.reached and result.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,side:String,want:bool)->bool:
	var control:Node3D=door.get_node(side)
	await aim(actor,control.to_global(Vector3(0,0,.055)))
	record("normal_RMB_target_"+str(operations.size()),actor.interaction_target==door)
	await key_e()
	for i in range(85):await physics_frame
	var ok:bool=door.fraction==(1.0 if want else 0.0) and door.desired_open==want
	operations.append({"door":String(door.persistent_id),"side":side,"requested_open":want,"actual_desired_open":door.desired_open,"fraction":door.fraction,"normal_original_player_input":true,"passed":ok})
	record("normal_E_endpoint_"+str(operations.size()),ok)
	return ok
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	load("res://scripts/group5_completion.gd").build(ship)
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHOPPING_PROMENADE.json"))
	var keys:Array=["SHOP_D09_P72_F314","SHOP_D09_P100_F184","SHOP_D09_S72_A080","SHOP_D09_S100_A210"]
	var all_shops:bool=OS.get_environment("ASTRAEA_GROUP5_WALK_ALL")=="1"
	if all_shops:
		keys=[]
		for row in records.chunks:
			if row.has("family_index") and not bool(row.get("retained",false)):keys.append(str(row.chunk_id))
		record("all99_retained_footprint_fixtures",keys.size()==99)
	for key in keys:
		var spec:Dictionary={}
		for row in records.chunks:
			if str(row.chunk_id)==key:spec=row;break
		record("existing_family_"+key,not spec.is_empty() and int(spec.family_index)>=0 and int(spec.family_index)<=9)
		if spec.is_empty():break
		var s:float=spec.front_sign_x
		var origin:=Vector3(spec.position[0],52.5,spec.position[2])
		# One original supported fixture per local shop route, never a route teleport.
		actor.global_position=origin+Vector3(-s*7,.03,-3.5);actor.velocity=Vector3.ZERO
		actor.set_controls_enabled(true);manager.prepare_position(actor.global_position)
		for i in range(15):await physics_frame
		fixtures_started+=1
		record("supported_initial_service_fixture_"+key,actor.is_on_floor())
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks"),key)
		var rear:Node3D=chunk.get_node("StockStreetDoors")
		var work:Node3D=chunk.get_node("WorkBayDoors")
		if not await operate(actor,rear,"BackControl",true):break
		if not await leg(actor,origin+Vector3(-s*4.5,0,-3.5),"retained rear circuit through real stock threshold into wrapping/work bay"):break
		if not await operate(actor,rear,"FrontControl",false):break
		if not await operate(actor,work,"BackControl",true):break
		if not await leg(actor,origin+Vector3(-s*2.1,0,-3.5),"stock/work bay through original screened opening to public-side service stance"):break
		if not await leg(actor,origin+Vector3(-s*2.6,0,-3.5),"walk into actual doorway guard before testing occupied close"):break
		# Actual player's capsule holds the door open at this threshold-side stance.
		await aim(actor,work.get_node("FrontControl").to_global(Vector3(0,0,.055)))
		record("guard_normal_target_"+key,actor.interaction_target==work)
		await key_e()
		for i in range(5):await physics_frame
		record("worker_blocks_close_"+key,work.desired_open and work.fraction==1 and work.obstructed)
		if not (work.desired_open and work.fraction==1 and work.obstructed):print("GROUP5_GUARD_STANCE ",actor.global_position," occupied ",work._occupied()," desired ",work.desired_open," fraction ",work.fraction," obstructed ",work.obstructed)
		if not await leg(actor,origin+Vector3(-s*4.5,0,-3.5),"continuous service egress back through work-bay threshold"):break
		if not await operate(actor,work,"BackControl",false):break
		if not await operate(actor,rear,"FrontControl",true):break
		if not await leg(actor,origin+Vector3(-s*7,0,-3.5),"stock threshold return to unchanged district service floor"):break
		if not await operate(actor,rear,"BackControl",false):break
		record("district_doors_end_closed_"+key,rear.fraction==0 and work.fraction==0 and not rear.desired_open and not work.desired_open)
		routes_completed+=1
		print("GROUP5_DISTRICT_WALK ",key," legs ",legs.size()," errors ",errors)
		if not errors.is_empty():break
	physical_key(false)
	if all_shops:record("all99_local_staff_routes_completed",routes_completed==99)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"original_player_legs":legs,"normal_RMB_E_operations":operations,"initial_supported_fixtures":fixtures_started,"local_routes_completed":routes_completed,"requested_all99":all_shops,"teleports_inside_each_route":0,"scope":"Local shop staff entry/workbay/egress routes in actual main, using original player and normal RMB/E; read exact fixtures/completion counts and all99 flag. One supported relocation between fixtures; none within a route. Not connected shipwide/public walking routes, cart/species, pressure/permission, stock operations/save, engineering or final visuals.","whole_group_accepted":false}
	FileAccess.open("res://artifacts/group5_staff_walk.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("PASS: Group5 staff walking" if errors.is_empty() else "HOLD: Group5 staff walking",JSON.stringify({"checks":checks.size(),"legs":legs.size(),"operations":operations.size(),"errors":errors}))
	quit(0 if errors.is_empty() else 1)
