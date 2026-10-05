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
	var contacts:Array=rows_for_box(ship,Vector3(104,101.16,46.0),Vector3(8.8,1.2,1.2))
	var report:Dictionary={"scope":"Candidate Royalty transverse transfer census only; no geometry adopted", "bounds":{"x":[99.6,108.4],"y":[100.56,101.76],"z":[45.4,46.6]},"contacts":contacts,"clear":contacts.is_empty()}
	report["full_height_strip_slices"] = []
	for i in range(16):
		var low:float=-0.45+float(i)*102.21/16.0
		var high:float=-0.45+float(i+1)*102.21/16.0
		report.full_height_strip_slices.append({"y":[low,high],"contacts":rows_for_box(ship,Vector3(104,(low+high)*.5,46.0),Vector3(8.8,high-low,1.2))})
	var file:=FileAccess.open("/workspace/scratch/375c2e438292/d17_royalty_aft_cross_census.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print(JSON.stringify(report))
	main.queue_free();await process_frame;quit()
