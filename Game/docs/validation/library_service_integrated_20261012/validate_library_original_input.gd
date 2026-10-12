extends "res://tests/validate_d04_port_forward_commons_service.gd"
var legs:Array=[]
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for i in range(40):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var id:=actor.get_instance_id()
	actor.global_position=Vector3(2,78.03,-456);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
	for i in range(45):await physics_frame
	var room:Node3D=ship.get_node("ShipSpace/Districts/LongLibraryReceiving_WIP")
	record("Original supported fore-route seed",actor.is_on_floor()and bool(room.get_meta("stream_loaded")))
	record("Installed passive service root",room.has_node("Group8LongLibraryService_WIP"))
	var points:Array[Vector2]=[Vector2(10,-456),Vector2(22,-456),Vector2(22,-451),Vector2(22,-452.2),Vector2(38,-452.2),Vector2(41.8,-451.9),Vector2(41.8,-453.2),Vector2(46.6,-453.2),Vector2(46.6,-459.05),Vector2(48.15,-459.05),Vector2(46.6,-459.05),Vector2(43.3,-458.5),Vector2(43.8,-458.5),Vector2(46.6,-458.5),Vector2(46.6,-462.7),Vector2(41.55,-462.7),Vector2(46.6,-462.7),Vector2(46.6,-458.5),Vector2(43.8,-458.5),Vector2(43.8,-456.6),Vector2(46.6,-456.6),Vector2(46.6,-453.2),Vector2(41.8,-453.2),Vector2(41.8,-451.9),Vector2(41.8,-449.2),Vector2(44,-449.2),Vector2(47.6,-448.75),Vector2(44,-449.2),Vector2(41.8,-451.9),Vector2(38,-452.2),Vector2(22,-452.2),Vector2(22,-451),Vector2(10,-451),Vector2(10,-456),Vector2(2,-456)]
	for point in points:
		var leg:Dictionary=await walk_to(actor,Vector3(point.x,78,point.y));legs.append(leg)
		record("Original W-input library leg "+str(legs.size()),leg.reached and leg.floor_contact)
		if not leg.reached:break
	physical_key(false)
	record("Same original player identity",actor.get_instance_id()==id)
	record("All source walk waypoints exercised",legs.size()==35)
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"legs":legs,"setup_fixtures":1,"within_route_position_or_velocity_writes":0,"physical_W_input":true,"scope":"Current installed library with original player's running controller,35 supported public/care/collection route legs and one supported initial fore-route fixture;no cart/species/stock/save/engineering/final-art acceptance"}
	FileAccess.open("res://artifacts/group8_library_original_input001.json",FileAccess.WRITE).store_string(JSON.stringify(result," ")+"\n")
	print("GROUP8 LIBRARY ORIGINAL INPUT ",result.status," ",legs.size()," legs");quit(0 if errors.is_empty()else 1)
