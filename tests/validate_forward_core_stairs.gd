extends "res://tests/validate_living_gifts.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	actor.set_physics_process(false)
	actor.position=Vector3(1.75,.1,-430.4);actor.velocity=Vector3.ZERO
	for i in range(16):
		for point in [Vector2(1.75,-428.5),Vector2(1.75,-419),Vector2(-1.75,-419),Vector2(-1.75,-430.4)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i+1]))<.12,"Public stair must reach the next real deck")
		print("FORWARD ASCENT:",i+2," ",actor.position)
		await walk(actor,Vector2(1.75,-430.4))
	for i in range(15,-1,-1):
		await walk(actor,Vector2(-1.75,-430.4))
		for point in [Vector2(-1.75,-419),Vector2(1.75,-419),Vector2(1.75,-430.4)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i]))<.12,"Public stair must descend to the correct deck")
	print("FORWARD DESCENT COMPLETE:",actor.position)
	# Ordinary north-spine/lobby/atrium route on each existing deck.
	for y in data.floor_y:
		actor.position=Vector3(0,float(y)+.1,-446);actor.velocity=Vector3.ZERO
		for point in [Vector2(0,-443),Vector2(5.5,-443),Vector2(5.5,-414),Vector2(0,-414),Vector2(0,-408)]:await walk(actor,point)
		assert(absf(actor.position.y-float(y))<.12)
	# Preserve the actual port arrivals connections; no unsupported starboard branch.
	for y in [0.0,6.0]:
		actor.position=Vector3(-10,y+.1,-432);actor.velocity=Vector3.ZERO
		for point in [Vector2(0,-432),Vector2(5.5,-432),Vector2(0,-432),Vector2(-10,-432)]:await walk(actor,point)
		assert(absf(actor.position.y-y)<.12,"Existing arrivals crosslink stays supported")
	print("FORWARD CORE STAIRS PASS: real capsule ascends and descends all16 switchbacks across17 canonical decks; each deck has a supported supported longitudinal bypass. Final art, all-species fit and full ship destinations remain unfinished.")
	quit(0)
