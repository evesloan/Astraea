extends "res://tests/validate_living_gifts.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.position=Vector3(1.75,102.1,120.6);actor.velocity=Vector3.ZERO
	for point in [Vector2(1.75,122.5),Vector2(1.75,132),Vector2(-1.75,132),Vector2(-1.75,120.6)]:await walk(actor,point)
	assert(absf(actor.position.y-106.5)<.12,"Crown stair reaches D18")
	for point in [Vector2(-1.75,132),Vector2(1.75,132),Vector2(1.75,120.6)]:await walk(actor,point)
	assert(absf(actor.position.y-102)<.12,"Crown stair returns to D17")
	for y in [102.0,106.5]:
		actor.position=Vector3(0,y+.1,104);actor.velocity=Vector3.ZERO
		for point in [Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137),Vector2(0,142)]:await walk(actor,point)
		assert(absf(actor.position.y-y)<.12,"Both crown bypasses retain support")
	print("AFT CROWN STAIRS PASS: physical capsule ascends/descends D17-D18 switchback and traverses both bypasses. Broader crown, species fit and final art remain unfinished.")
	quit(0)
