extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var room:=ship.find_child("D13_13041_TwinSuite_WIP",true,false) as Node3D
	var shell:=room.get_node("AuthoredTwinSuite") as Node3D
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p:Vector3=mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=69.04 and p.x<=81.96 and p.z>=-53.01 and p.z<=-45.79,"Retreat respects historical13041 allocation")
			assert(p.y>=83.77 and p.y<88.26,"Retreat fits below D14")
	var path:=[Vector3(84,84.1,-42),Vector3(84,84.1,-49.4),Vector3(73.8,84.1,-49.4)]
	for i in range(path.size()-1):
		for step in range(31):assert(ship.arrive_at(path[i].lerp(path[i+1],step/30.0),0),"Connected street and shared salon remain usable")
	for z in [-50.05,-48.75]:
		for step in range(21):assert(ship.arrive_at(Vector3(73.8,84.1,-49.4).lerp(Vector3(73.8,84.1,z),step/20.0),0),"Sleeping approaches bifurcate before the screen")
		for step in range(31):assert(ship.arrive_at(Vector3(73.8,84.1,z).lerp(Vector3(69.7,84.1,z),step/30.0),0),"Both private recesses retain reachable window positions")
	var beds:=room.find_children("HistoricalBedAnchor_*","Node3D",true,false)
	assert(beds.size()==2)
	for bed in beds:
		assert(absf(bed.global_position.x-71.7)<.002 and absf(bed.global_position.y-84)<.002)
		assert(minf(absf(bed.global_position.z+51.05),absf(bed.global_position.z+47.75))<.002,"Keep13041 historical bed anchors")
	var entry:=room.get_node("Suite13041EntryDoor")
	var bath:=room.get_node("Suite13041BathDoor")
	assert(entry.persistent_id==&"D13_13041_entry_door_A" and bath.persistent_id==&"D13_13041_bath_door_A")
	assert(entry.global_position.distance_to(Vector3(82,84,-49.4))<.002)
	var state:=ship.get_world_3d().direct_space_state
	for datum_name in ["light_0","light_1","light_2","bath_light"]:
		var marker:=shell.find_child("DATUM_"+datum_name,true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.1)).is_empty(),"Source exit stays clear in new profile")
	print("TWIN RETREAT PASS:166 route/branch probes,2 historical bed anchors,unique door IDs,allocation/D14 fit and4 source exits. Window scenery, carts, NPCs, saving and final art unfinished.")
	main.queue_free()
	await process_frame
	quit()
