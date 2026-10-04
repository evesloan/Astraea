extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(50):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var edge:Node3D=ship.find_child("D16CourtConversationEdge",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	assert(edge!=null)
	for part in edge.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=part.global_transform*part.get_aabb()
		assert(bounds.position.x>=64.09 and bounds.end.x<=67.11 and bounds.end.y<101.76,"Conversation edge must preserve D16 route and D17 underside")
		if str(part.name).begins_with("TALK_VisualFloor"):assert(part.get_node_or_null("StaticContact")==null)
	for i in range(2):
		var chair:Node3D=ship.find_child("D16ConversationChair_"+str(i),true,false)
		var omit:Array[RID]=[]
		for body in chair.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		for x in [-.40,.40]:
			for z in [-.28,.28]:
				var p:Vector3=chair.global_transform*Vector3(x,0,z)
				var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.03,p-Vector3.UP*.03)
				query.exclude=omit
				var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
				assert(not hit.is_empty() and abs(hit.position.y-97.5)<.015,"Conversation chair feet require actual deck support")
		var light:Node3D=edge.find_child("DATUM_light_"+str(i),true,false)
		var query:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.08)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(query).is_empty(),"Conversation fixture exit must be clear")
		var plant:Node3D=ship.find_child("D16ConversationPlant_"+str(i),true,false)
		omit.clear()
		for body in plant.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		query=PhysicsRayQueryParameters3D.create(plant.global_position+Vector3.UP*.03,plant.global_position-Vector3.UP*.03)
		query.exclude=omit
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not hit.is_empty() and "TALK_Soil_" in str(hit.collider.get_path()),"Planted end must have fitted soil")
	actor.set_physics_process(false)
	actor.position=Vector3(68,97.6,1.6)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(64,1.6),Vector2(64,3.8),Vector2(65.3,3.8),Vector2(64,3.8),Vector2(64,8.2),Vector2(65.3,8.2),Vector2(64,8.2),Vector2(64,1.6),Vector2(68,1.6)]:await walk(actor,target)
	assert(abs(actor.position.y-97.5)<.12)
	print("STARBOARD CONVERSATION PASS: real front-lane and two chair-side approaches, eight supported chair feet, two fitted planted ends, clear fixture exits and protected upper slab. Seated use, species ergonomics, plant-wide clipping and final art pending.")
	main.queue_free()
	await process_frame
	quit()
