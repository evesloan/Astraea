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
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/D17_STARBOARD_HOUSE_SECTION_PLAN.json"))
	var report:Dictionary={"scope":"Read-only actual collision census; candidate portals remain closed, no fit/route acceptance","portals":[],"candidate_floor_bands":[]}
	for sign_value in [-1.0,1.0]:
		var side:float=float(sign_value)
		report.portals.append({"centre":[80.0,103.41,side*13.2],"size":[3.0,2.82,.30],"contacts":rows_for_box(ship,Vector3(80.0,103.41,side*13.2),Vector3(3,2.82,.30)),"inner_approach_contacts":rows_for_box(ship,Vector3(80.0,103.1,side*11.0),Vector3(2.8,2.0,1.6))})
	for row in plan.rows:
		var xs:Array=row.candidate_x;var zs:Array=row.candidate_z
		var centre:=Vector3((float(xs[0])+float(xs[1]))*.5,101.88,(float(zs[0])+float(zs[1]))*.5)
		var size:=Vector3(float(xs[1])-float(xs[0]),.24,float(zs[1])-float(zs[0]))
		report.candidate_floor_bands.append({"source_index":row.source_envelope_index,"contacts":rows_for_box(ship,centre,size)})

	report["candidate_support_columns"] = []
	for point in [Vector2(108,-71.4),Vector2(108,-48.6),Vector2(108,-24),Vector2(108,24),Vector2(108,29.6),Vector2(108,50.4),Vector2(108,71.6)]:
		var census:Dictionary={"xz":[point.x,point.y],"size_xz":[.8,1.2],"slices":[],"base_rays":[]}
		for index in range(16):
			var low:float=-3.2+float(index)*(115.2/16.0)
			var high:float=-3.2+float(index+1)*(115.2/16.0)
			census.slices.append({"y":[low,high],"contacts":rows_for_box(ship,Vector3(point.x,(low+high)*.5,point.y),Vector3(.8,high-low,1.2))})
		for delta in [Vector2.ZERO,Vector2(-.4,-.6),Vector2(.4,-.6),Vector2(-.4,.6),Vector2(.4,.6)]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(point.x+delta.x,-.30,point.y+delta.y),Vector3(point.x+delta.x,-10,point.y+delta.y),1)
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
			if hit.is_empty():census.base_rays.append({"delta":[delta.x,delta.y],"hit":false})
			else:census.base_rays.append({"delta":[delta.x,delta.y],"hit":true,"path":str(hit.collider.get_path()),"position":[hit.position.x,hit.position.y,hit.position.z],"normal":[hit.normal.x,hit.normal.y,hit.normal.z]})
		report.candidate_support_columns.append(census)
	var file:=FileAccess.open("res://artifacts/d17_outer_support_census.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print("D17 INTERFACE CENSUS: two proposed portal boxes and sixteen floor bands inspected; no geometry changed")
	main.queue_free();await process_frame;quit()
