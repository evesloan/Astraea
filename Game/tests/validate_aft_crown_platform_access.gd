extends "res://tests/validate_bridge_enclosure_access.gd"
# One initial placement; all subsequent public/staff journeys use physical movement.
# Reuse the shared-door proof: precise RMB/E on both sides, unfocused rejection,
# closed collision, reversal, occupied opening/closing and live pause/resume.
const PLATFORM_PUBLIC_ROUTE := [Vector2(0,95),Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137),Vector2(0,142),Vector2(-5.5,142),Vector2(-5.5,137),Vector2(-5.5,108),Vector2(0,108),Vector2(0,95),Vector2(0,108),Vector2(5.5,108),Vector2(5.5,142),Vector2(16,142),Vector2(16,108),Vector2(16,142),Vector2(-16,142),Vector2(-16,108),Vector2(-16,142),Vector2(-16,188),Vector2(0,188),Vector2(0,198),Vector2(0,188),Vector2(16,188),Vector2(16,142),Vector2(0,142)]
var platform_doors:Dictionary={}

func collect_platform_doors(ship:Node3D) -> void:
	var platform:Node3D=ship.find_child("AftCrownPlatform_WIP",true,false)
	var aft:Node3D=ship.find_child("AftCommandCrown_WIP",true,false)
	var central:Node3D=ship.find_child("CentralCommandCrown_WIP",true,false)
	assert(platform!=null and aft!=null and central!=null)
	assert(platform.find_child("AftCrownPlatformArchitecture",true,false)!=null)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json"))
	var old_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_COMMAND_RUNTIME.json"))
	assert(data.doors.size()==2 and old_data.doors.size()==6)
	bridge_doors.clear();platform_doors.clear()
	bridge_doors.append_array(central.find_children("CrownDoor_*","Node3D",true,false))
	bridge_doors.append_array(aft.find_children("AftCommandDoor_*","Node3D",true,false))
	for entry in data.doors:
		var door:Node3D=platform.get_node("AftPlatformDoor_"+str(entry.name))
		bridge_doors.append(door)
		platform_doors["port_exit" if float(entry.position[0])<0 else "starboard_exit"]=door
	for entry in old_data.doors:
		if float(entry.position[2])<100:continue
		platform_doors["port_return" if float(entry.position[0])<0 else "starboard_return"]=aft.get_node("AftCommandDoor_"+str(entry.name))
	assert(platform_doors.size()==4 and bridge_doors.size()==20)
	var identities:Dictionary={}
	for door in bridge_doors:
		assert(not identities.has(door.persistent_id));identities[door.persistent_id]=true
	for label in platform_doors:
		var door:Node3D=platform_doors[label]
		var side:float=-1.0 if str(label).begins_with("port") else 1.0
		var terminal:bool=str(label).ends_with("exit")
		assert(door.position.distance_to(Vector3(side*(32.0 if terminal else 7.5),FLOOR,141.92 if terminal else 101.92))<.001)
		assert(door.global_basis.z.dot(Vector3.BACK)>.999,"All four inward sweeps point toward -Z")
		assert(door.get_script().resource_path=="res://scripts/service_door.gd" and door.get_meta("catalogue_file")=="AST-STF-008.glb")

func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	collect_platform_doors(ship);assert_closed()
	actor.set_physics_process(false);actor.position=Vector3(0,FLOOR+.1,95);actor.velocity=Vector3.ZERO
	require_closed=true
	await walk_route(actor,PLATFORM_PUBLIC_ROUTE)
	var reverse:Array=PLATFORM_PUBLIC_ROUTE.duplicate();reverse.reverse()
	await walk_route(actor,reverse)
	require_closed=false
	await walk_route(actor,[Vector2(0,108),Vector2(5.5,108),Vector2(5.5,142),Vector2(0,145)])
	for side in [-1.0,1.0]:
		var prefix:String="port" if side<0 else "starboard"
		var terminal:Node3D=platform_doors[prefix+"_exit"]
		var corridor:Node3D=platform_doors[prefix+"_return"]
		await walk_route(actor,[Vector2(side*32,145)])
		await exercise_door(ship,actor,terminal,1.0)
		await walk_route(actor,[Vector2(side*32,104),Vector2(side*7.5,104)])
		await exercise_door(ship,actor,corridor,1.0)
		await walk_route(actor,[Vector2(side*7.5,98),Vector2(side*7.5,104),Vector2(side*32,104),Vector2(side*32,145),Vector2(0,145)])
	print("AFT CROWN PLATFORM ACCESS PASS: physical public approach/return through both retained core bypasses, receiving zone, both foyer wings, fan and onward spine with all20 command/service doors closed; both screened L-routes and four new shared thresholds exercised from both sides, including occupied opening/closing and live interruption. Scripted capsule only; capacity and final art remain pending.")
	main.queue_free();await process_frame;quit()
