extends "res://tests/validate_living_gifts.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/PRIMARY_ATRIUM_CORE.json"))
	actor.set_physics_process(false)
	actor.position=Vector3(1.75,.1,-98.4);actor.velocity=Vector3.ZERO
	for i in range(17):
		for point in [Vector2(1.75,-96.5),Vector2(1.75,-87),Vector2(-1.75,-87),Vector2(-1.75,-98.4)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i+1]))<.12,"Public stair must reach the next real deck")
		print("PRIMARY ASCENT:",i+2," ",actor.position)
		await walk(actor,Vector2(1.75,-98.4))
	for i in range(16,-1,-1):
		await walk(actor,Vector2(-1.75,-98.4))
		for point in [Vector2(-1.75,-87),Vector2(1.75,-87),Vector2(1.75,-98.4)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i]))<.12,"Public stair must descend to the correct deck")
	print("PRIMARY DESCENT COMPLETE:",actor.position)
	# Ordinary north-spine/lobby/atrium route on each existing deck.
	for y in data.floor_y:
		actor.position=Vector3(0,float(y)+.1,-114);actor.velocity=Vector3.ZERO
		for point in [Vector2(0,-111),Vector2(5.5,-111),Vector2(5.5,-82),Vector2(5.5,-76)]:await walk(actor,point)
		assert(absf(actor.position.y-float(y))<.12)
	print("PRIMARY CORE STAIRS PASS: real capsule ascends and descends all17 switchbacks across18 canonical decks; each deck has a supported north-spine/lobby/atrium bypass. Final art, all-species fit and full ship destinations remain unfinished.")
	quit(0)
