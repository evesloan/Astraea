extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var world:=Node3D.new();root.add_child(world)
	var assembly:Node3D=load("res://aquatic_tram_interior_20261026/integration/assembly.gd").create(world,"AFT_MIDSHIP")
	for i in range(5):await physics_frame
	var bridge:Node3D=assembly.get_node("Group4Bridge_AFT_MIDSHIP")
	var rows:Array=[]
	for col:CollisionShape3D in bridge.find_children("*","CollisionShape3D",true,false):
		var points:PackedVector3Array=col.shape.points if col.shape is ConvexPolygonShape3D else col.shape.get_faces()
		var bounds:=AABB(col.to_global(points[0]),Vector3.ZERO)
		for p in points:bounds=bounds.expand(col.to_global(p))
		rows.append({"owner":str(col.get_parent().name),"min":str(bounds.position),"max":str(bounds.end),"pose":str(col.global_transform)})
	var result:={"bridge_pose":str(bridge.global_transform),"moving_pose":str(bridge.moving.global_transform),"fraction":bridge.fraction,"rows":rows}
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output));var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));quit()
