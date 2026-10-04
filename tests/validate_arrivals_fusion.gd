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
		var probe:=PhysicsShapeQueryParameters3D.new()
		probe.shape=actor.get_child(0).shape
		probe.transform=actor.get_child(0).global_transform
		probe.transform.origin+=(Vector3(destination.x,actor.position.y,destination.y)-actor.position).normalized()*.08
		probe.exclude=[actor.get_rid()]
		for hit in actor.get_world_3d().direct_space_state.intersect_shape(probe,20):print("PROBE ",hit.collider.get_path())
		for i in range(actor.get_slide_collision_count()):
			var c:=actor.get_slide_collision(i)
			print("BLOCKER ",c.get_collider().get_path()," normal ",c.get_normal())
	assert(reached,"Arrivals route stalled at %s toward %s"%[actor.position,destination])
func opaque_between(ship:Node3D,a:Vector3,b:Vector3) -> bool:
	var excluded:Array[RID]=[]
	for iteration in range(32):
		var ray:=PhysicsRayQueryParameters3D.create(a,b)
		ray.exclude=excluded
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty():return false
		var owner:Node=hit.collider.get_parent()
		if owner is MeshInstance3D and owner.material_override is ShaderMaterial:
			excluded.append(hit.rid)
			continue
		return true
	return false
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:=ship.find_child("D01_D02_ArrivalsFusion_Integrated_WIP",true,false)
	assert(district!=null)
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D01_D02_arrivals_fusion.json"))
	for p in definition.guest_viewpoints.values():
		for q in definition.concealed_service_view_targets:
			assert(opaque_between(ship,Vector3(p[0],p[1],p[2]),Vector3(q[0],q[1],q[2])),"Opaque architecture must screen service circulation, including from upper guest views")
	var ray:=PhysicsRayQueryParameters3D.create(Vector3(-27,10.99,-432),Vector3(-27,12.1,-432))
	var roof:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
	assert(not roof.is_empty() and absf(roof.position.y-11.76)<.015,"D03 crew boundary is opaque and intact")
	var architecture:=district.get_node("ArrivalsAuthoredArchitecture")
	for i in range(11):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var source_ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(source_ray).is_empty(),"Arrival fixture exit must be outside its lens")
	for i in range(2):
		var marker:=architecture.find_child("DATUM_wallwash_"+str(i),true,false)as Node3D
		var direction:Vector3=(Vector3(-47.15,7.5,-432)-marker.global_position).normalized()
		var source_ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+direction*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(source_ray).is_empty(),"Wallwash source is outside its housing")
	actor.set_physics_process(false)
	actor.position=Vector3(-5,.1,-432)
	actor.velocity=Vector3.ZERO
	for p in [Vector2(-18,-432),Vector2(-30,-432),Vector2(-43.5,-432),Vector2(-43.5,-443.8)]:await walk(actor,p)
	assert(absf(actor.position.y-6)<.12,"Ceremonial stair reaches actual D02 visitor floor")
	for p in [Vector2(-34.5,-443.8),Vector2(-30,-443),Vector2(-18,-443),Vector2(-12,-432),Vector2(-18,-422),Vector2(-34.5,-422),Vector2(-34.5,-419.9),Vector2(-43.5,-419.9),Vector2(-43.5,-432),Vector2(-29,-432)]:await walk(actor,p)
	assert(absf(actor.position.y)<.12,"Both upper flights return to supported D01 arrival")
	var lift=district.get_node("ArrivalsVisitorLift")
	assert(lift.floor_heights==[0.0,6.0] and lift.deck_numbers==[1,2])
	assert(lift.find_child("arrivals_cabin_D2",true,false)!=null)
	assert(ship.find_child("commons_cabin_D14",true,false)!=null,"Existing commons floor controls retain their identities")
	print("ARRIVALS SECTION PASS: connected ceremonial stair/upper-gallery circuit,25 screened staff sightlines, intact D03 boundary,13 fixture exits and distinct reused lift configuration. Art, occupancy, engineering loads and arrivals loaded-lift travel still pending.")
	main.queue_free()
	await process_frame
	quit()
