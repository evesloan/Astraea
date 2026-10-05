extends "res://tests/validate_living_gifts.gd"
var selected_decks:Array[int]=[1]
func walk_route(actor:CharacterBody3D,points:Array)->void:
	for target:Vector2 in points:
		var start:=Vector2(actor.position.x,actor.position.z)
		var count:=maxi(1,ceili(start.distance_to(target)/24.0))
		for i in range(1,count+1):await walk(actor,start.lerp(target,float(i)/count))
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	assert(ship.find_child("LowerStaffNetwork_WIP",true,false)!=null)
	actor.set_physics_process(false)
	var synthesis:Node3D=ship.find_child("SynthesisServiceDoor",true,false)
	if 1 in selected_decks and synthesis.desired_open:synthesis.interact(actor)
	for deck in selected_decks:
		var y:float=(deck-1)*6.0
		actor.position=Vector3(-21,y+.1,-490);actor.velocity=Vector3.ZERO
		await walk_route(actor,[Vector2(-21,-500),Vector2(-57,-500)])
		if deck==1:
			await walk_route(actor,[Vector2(-57,-60),Vector2(-46,-60),Vector2(-46,0),Vector2(-58,0)])
			var door:Node3D=ship.find_child("SynthesisServiceDoor",true,false)
			door.interact(actor)
			for frame in range(100):await physics_frame
			assert(door.open_fraction>.999,"Existing synthesis service door must still open")
			await walk_route(actor,[Vector2(-63.2,0)])
		elif deck==2:
			await walk_route(actor,[Vector2(-57,-432),Vector2(-51,-432)])
		else:
			await walk_route(actor,[Vector2(-57,-432),Vector2(-51,-432),Vector2(-57,-432),Vector2(-57,-216),Vector2(-51,-216)])
		assert(absf(actor.position.y-y)<.12,"Staff route stays on the correct supported deck")
		print("STAFF WALK DECK:",deck," endpoint:",actor.position)
	print("LOWER STAFF ROUTES PASS: actual capsule walks complete selected service routes and supported destination interfaces. Home/depot are bounded thresholds only; staff population and final finish remain pending.")
	quit(0)
