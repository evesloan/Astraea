extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var space:=ship.get_world_3d().direct_space_state
	var records:Array=[]
	for x in [-51.5,51.5]:
		for z in [-71.0,71.0]:
			var static_hits:Array=[]
			var dynamic_hits:Array=[]
			for segment in range(16):
				var low:float=lerpf(-3.19,114.0,segment/16.0)
				var high:float=lerpf(-3.19,114.0,(segment+1)/16.0)
				var shape:=BoxShape3D.new();shape.size=Vector3(.8,high-low,1.2)
				var q:=PhysicsShapeQueryParameters3D.new()
				q.shape=shape;q.margin=.001;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,(low+high)/2,z))
				var hits:=space.intersect_shape(q,256)
				assert(hits.size()<256,"Candidate result set saturated")
				for hit in hits:
					var path:=str(hit.collider.get_path())
					if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:
						if path not in static_hits:static_hits.append(path)
					elif path not in dynamic_hits:dynamic_hits.append(path)
			var supports:Array=[]
			for offset in [Vector2.ZERO,Vector2(-.4,-.6),Vector2(-.4,.6),Vector2(.4,-.6),Vector2(.4,.6)]:
				var ray:=PhysicsRayQueryParameters3D.create(Vector3(x+offset.x,-3.0,z+offset.y),Vector3(x+offset.x,-3.4,z+offset.y))
				var hit:=space.intersect_ray(ray)
				assert(not hit.is_empty(),"Candidate bearing lacks foundation support")
				var path:=str(hit.collider.get_path())
				assert("HUL_KeelPan" in path and absf(hit.position.y+3.2)<.002,"Support must be actual keel-pan top")
				supports.append({"x":x+offset.x,"z":z+offset.y,"y":hit.position.y,"owner":path})
			records.append({"x":x,"z":z,"static_contacts":static_hits,"dynamic_contacts":dynamic_hits,"supports":supports})
	var report={"scope":"Hypothetical four-pier collision and keel contact audit in actual current scene. No geometry constructed and no structural load certification.","body_x_width":.8,"body_z_depth":1.2,"body_y":[-3.19,114.0],"query_margin":.001,"vertical_query_segments":16,"records":records}
	var file:=FileAccess.open("res://artifacts/crown_pier_runtime_audit.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n");file.close()
	for r in records:print("PIER CANDIDATE:",r.x,",",r.z," static:",r.static_contacts," dynamic:",r.dynamic_contacts)
	print("CROWN PIER AUDIT COMPLETE; inspect contact lists before adoption")
	main.queue_free();await process_frame;quit()
