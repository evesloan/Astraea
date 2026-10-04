extends SceneTree
func _initialize() -> void:call_deferred("run")
func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(700):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var movement:=delta.normalized()*3.1
		actor.velocity.x=movement.x
		actor.velocity.z=movement.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):
			var c:=actor.get_slide_collision(i)
			print("BLOCKER ",c.get_collider().get_path()," normal ",c.get_normal())
	assert(reached,"Commons route stalled at %s toward %s"%[actor.position,destination])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:=ship.find_child("D09_R070_KindCurios_WIP",true,false)
	assert(district.get_meta("historical_room_id")=="R070")
	var room:=district.get_node("KindCuriosAuthoredRoom")
	for key in ["column_light_-1","column_light_1","ceiling_light_0","ceiling_light_1","ceiling_light_2"]:
		var marker:=room.find_child("DATUM_"+key,true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"R070 real source must exit its fixture")
	for part in room.find_children("CUR_VisualFloorBorder*","MeshInstance3D",true,false):assert(part.get_node_or_null("StaticContact")==null)
	actor.set_physics_process(false)
	actor.position=Vector3(52,52.6,216)
	actor.velocity=Vector3.ZERO
	for destination in [Vector2(60,222.5),Vector2(84,223),Vector2(84,236),Vector2(77,236),Vector2(72,236),Vector2(70,236)]:await walk(actor,destination)
	assert(abs(actor.position.y-52.5)<.12)
	for destination in [Vector2(72,236),Vector2(77,236),Vector2(84,236),Vector2(84,223),Vector2(60,222.5),Vector2(52,216)]:await walk(actor,destination)
	assert(abs(actor.position.y-52.5)<.12)
	print("RETAIL CURIOS PASS: actual R070 stable identity, connected capsule entry/return, five source exits and single floor ownership. Merchandise, loaded-cart turning, guests and final visual acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
