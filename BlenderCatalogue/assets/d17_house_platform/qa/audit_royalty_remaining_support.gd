extends SceneTree
func _initialize()->void:call_deferred("run")
func rows_for_box(ship:Node3D,centre:Vector3,size:Vector3)->Array:
	var shape:=BoxShape3D.new();shape.size=size
	var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,centre);q.collision_mask=1
	var hits:=ship.get_world_3d().direct_space_state.intersect_shape(q,1024)
	assert(hits.size()<1024,"Unsaturated geometry census required")
	var paths:Array=[]
	for hit in hits:
		if hit.collider is StaticBody3D:
			var path:=str(hit.collider.get_path())
			if path not in paths:paths.append(path)
	paths.sort();return paths
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var report:Dictionary={"scope":"Additional Royalty support hypotheses only, no geometry adoption"}
	report["candidate_support_columns"] = []
	for point in [Vector2(100,46),Vector2(108,46),Vector2(116,29.6),Vector2(116,46)]:
		var census:Dictionary={"xz":[point.x,point.y],"size_xz":[.8,1.2],"slices":[],"base_rays":[]}
		for index in range(16):
			var low:float=-3.2+float(index)*(115.2/16.0)
			var high:float=-3.2+float(index+1)*(115.2/16.0)
			census.slices.append({"y":[low,high],"contacts":rows_for_box(ship,Vector3(point.x,(low+high)*.5,point.y),Vector3(.8,high-low,1.2))})
		for delta in [Vector2.ZERO,Vector2(-.4,-.6),Vector2(.4,-.6),Vector2(-.4,.6),Vector2(.4,.6)]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(point.x+delta.x,20.0,point.y+delta.y),Vector3(point.x+delta.x,-10,point.y+delta.y),1)
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
			if hit.is_empty():census.base_rays.append({"delta":[delta.x,delta.y],"hit":false})
			else:census.base_rays.append({"delta":[delta.x,delta.y],"hit":true,"path":str(hit.collider.get_path()),"position":[hit.position.x,hit.position.y,hit.position.z],"normal":[hit.normal.x,hit.normal.y,hit.normal.z]})
		report.candidate_support_columns.append(census)
	report["upper_frame_reservation"]={"bounds":{"x":[94,118],"y":[101.76,106.5],"z":[29,51]},"contacts":rows_for_box(ship,Vector3(106,104.13,40),Vector3(24,4.74,22))}
	var file:=FileAccess.open("/workspace/scratch/375c2e438292/d17_royalty_remaining_support_census.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print("Royalty remaining support census written")
	main.queue_free();await process_frame;quit()
