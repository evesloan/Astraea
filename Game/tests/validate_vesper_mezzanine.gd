extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var architecture:Node3D=ship.find_child("VesperMezzanineArchitecture",true,false)
	assert(architecture!=null)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.position=Vector3(9.8,61.1,204.9)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(17.6,204.9),Vector2(17.6,196),Vector2(18.25,192)]:await walk(actor,target)
	assert(absf(actor.position.y-64.5)<.12,"Upper stair must reach the authored mezzanine")
	for target in [Vector2(17.6,196),Vector2(17.6,204.9),Vector2(9.8,204.9)]:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12,"Return stair must reach original D10")
	actor.position=Vector3(18,61.1,208)
	actor.velocity=Vector3.ZERO
	await walk(actor,Vector2(18,200.8))
	assert(absf(actor.position.y-61)<.12,"Lower passage must remain usable beneath upper corridor")
	for i in range(8):
		var light:Node3D=ship.find_child("VesperMezzanineTaskLight_"+str(i),true,false)
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.05)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"New fixture must emit outside its housing")
	print("VESPER MEZZANINE PASS: actual stair up/return, lower passage walking and eight fixture exits. Cart boarding, upper seat approaches, guards and visual acceptance remain pending.")
	main.queue_free()
	await process_frame
	quit()
