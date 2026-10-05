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
	var report:Dictionary={"scope":"Outer Royalty support strips only; no geometry adoption", "strips":[]}
	for spec in [["fore",112.0,29.6,8.8,1.2],["aft",112.0,46.0,8.8,1.2],["outer",116.0,37.8,.8,17.6]]:
		var row:Dictionary={"name":spec[0],"centre_xz":[spec[1],spec[2]],"size_xz":[spec[3],spec[4]],"slices":[]}
		for i in range(16):
			var low:float=11.8+float(i)*89.96/16.0
			var high:float=11.8+float(i+1)*89.96/16.0
			row.slices.append({"y":[low,high],"contacts":rows_for_box(ship,Vector3(float(spec[1]),(low+high)*.5,float(spec[2])),Vector3(float(spec[3]),high-low,float(spec[4])))})
		report.strips.append(row)
	var file:=FileAccess.open("/workspace/scratch/375c2e438292/d17_royalty_outer_frame_census.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print("Outer frame strip census written")
	main.queue_free();await process_frame;quit()
