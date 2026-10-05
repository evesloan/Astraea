extends "res://tests/validate_living_gifts.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var court:Node3D=ship.find_child("D09_D10_OrchardExchange_WIP",true,false)
	assert(court!=null and court.get_meta("programme_keys")==["D09_directory_04","D10_directory_04"])
	var architecture:Node3D=court.find_child("OrchardExchangeArchitecture",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.position=Vector3(6,52.6,-232)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(6,-236),Vector2(9.25,-236),Vector2(9.25,-246.5),Vector2(12.75,-246.5),Vector2(12.75,-236.2)]:await walk(actor,target)
	for frame in range(15):
		actor.velocity=Vector3(0,-.1,0)
		actor.move_and_slide()
		await physics_frame
	assert(abs(actor.position.y-61)<.12,"Orchard stair must reach the actual D10 floor")
	for target in [Vector2(15.8,-236.2),Vector2(15.8,-241.5),Vector2(15.8,-235),Vector2(23,-233.6),Vector2(26,-233.6),Vector2(23,-233.6),Vector2(15.8,-236.2),Vector2(12.75,-236.2),Vector2(12.75,-246.5),Vector2(9.25,-246.5),Vector2(9.25,-236),Vector2(6,-236),Vector2(6,-231)]:await walk(actor,target)
	assert(abs(actor.position.y-52.5)<.12,"Orchard stairs must return to retail without teleportation")
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var q:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.07)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"Court fixture exit obstructed")
	print("ORCHARD EXCHANGE PASS: actual retail approach, both stair directions, upper lift stage and food-hall threshold;5 fixture exits. Food hall seating, physical boarding turns, species ergonomics and final art pending.")
	main.queue_free()
	await process_frame
	quit()
