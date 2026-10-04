extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:Node3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	actor.position=Vector3(89,84.1,8)
	budget.refresh()
	var active:=0
	for light in budget.sources:
		if light.shadow_enabled and light.visible:
			active+=1
			assert(not light.name.begins_with("RoofDaylightSource"),"Occluded roof daylight should not displace local room sources")
			assert(not light.name.begins_with("NightGardenLocalSource"),"Fixtures behind occupied floor should not consume commons budget")
	assert(active<=8)
	var gathering:=ship.find_child("CommonsShelteredGathering",true,false)as Node3D
	assert(gathering!=null)
	for group in [["canopy_plant",2],["underplant",12]]:
		for i in range(group[1]):
			var marker:=gathering.find_child("DATUM_%s_%d"%[group[0],i],true,false)as Node3D
			var ray:=PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.04,marker.global_position-Vector3.UP*.08)
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			assert(not hit.is_empty() and abs(hit.position.y-marker.global_position.y)<.015,"Plants meet the authored island soil")
	for i in range(3):
		var marker:=gathering.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Authored light exits remain outside lenses")
	for p in [Vector3(79,84.1,9.2),Vector3(82,88.6,-9.2),Vector3(88,88.6,-6.8),Vector3(86.3,88.6,-9),Vector3(89.7,88.6,-9)]:
		assert(ship.arrive_at(p,0),"Social/shared-table approaches remain usable")
	print("COMMONS LIGHTING PASS: eight-source cap preserved, occupied-floor/roof-hidden sources deprioritized,14 plant contacts,3 actual lens exits and5 gathering approaches. Final art and target-GPU cost remain unverified.")
	main.queue_free()
	await process_frame
	quit()
