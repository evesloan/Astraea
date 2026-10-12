extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var rows:Array=[];var window:=AABB(Vector3(-100,-.1,-36),Vector3(50,5.95,72))
	for ob:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
		var a:AABB=ob.global_transform*ob.get_aabb()
		if not a.intersects(window):continue
		var fs:PackedVector3Array=ob.mesh.get_faces();var faces:Array=[]
		for i in range(0,fs.size(),3):
			var tri:Array=[];var b:=AABB(ob.to_global(fs[i]),Vector3.ZERO)
			for j in range(3):
				var v:=ob.to_global(fs[i+j]);b=b.expand(v);tri.append([v.x,v.y,v.z])
			if b.grow(.0001).intersects(window):faces.append(tri)
		if not faces.is_empty():rows.append({"path":str(ob.get_path()),"actual_world_aabb":[a.position.x,a.end.x,a.position.y,a.end.y,a.position.z,a.end.z],"triangles":faces})
	var door:Node3D=ship.find_child("SynthesisServiceDoor",true,false);assert(door!=null and str(door.persistent_id)=="D01_food_synthesis_service_door_A")
	var r:={"status":"PASS_READ_ONLY_ACTUAL_CURRENT_MAIN","current_main":"bc731d6d6d54bb2595331ee2f4368558d4d24fda","old_meshes":rows,"original_synthesis_door":{"id":str(door.persistent_id),"path":str(door.get_path()),"position":[door.global_position.x,door.global_position.y,door.global_position.z]},"actor_route_or_proposed_plant_acceptance":false}
	FileAccess.open("res://data/architecture/group8/SYNTHESIS_ACTUAL_CONTEXT.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  ")+"\n");print("GROUP8 SYNTHESIS CONTEXT PASS: ",rows.size()," actual nearby source meshes")
	main.queue_free();for f in range(4):await process_frame
	quit(0)
