extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var hull:Node3D=ship.find_child("LowerHullBody_WIP",true,false)
	assert(hull.get_meta("persistent_id")=="lower_hull_body_001")
	var omit:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not hull.is_ancestor_of(body):omit.append(body.get_rid())
	var space:=ship.get_world_3d().direct_space_state
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_HULL_BODY.json"))
	var triangles:Array=[]
	for mesh_node in hull.find_children("*","MeshInstance3D",true,false):
		var vertices:PackedVector3Array=mesh_node.mesh.get_faces()
		for n in range(0,vertices.size(),3):triangles.append([mesh_node.global_transform*vertices[n],mesh_node.global_transform*vertices[n+1],mesh_node.global_transform*vertices[n+2]])
	var maximum_loft_deviation:=0.0
	var checked:=0
	for y in [1.0,8.0,14.0]:
		var j:=0
		while j+1<data.rings.size() and float(data.rings[j+1].y)<y:j+=1
		var lo:Dictionary=data.rings[j];var hi:Dictionary=data.rings[j+1]
		var t:float=(y-float(lo.y))/(float(hi.y)-float(lo.y))
		for i in range(0,lo.inner.size(),8):
			var k:int=(i+1)%lo.inner.size()
			var a:=Vector2(lo.inner[i][0],lo.inner[i][1]).lerp(Vector2(hi.inner[i][0],hi.inner[i][1]),t)
			var b:=Vector2(lo.inner[k][0],lo.inner[k][1]).lerp(Vector2(hi.inner[k][0],hi.inner[k][1]),t)
			var p:Vector2=(a+b)/2;var direction:Vector2=p.normalized()
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x-direction.x,y,p.y-direction.y),Vector3(p.x+5*direction.x,y,p.y+5*direction.y));ray.exclude=omit
			var hit:=space.intersect_ray(ray)
			assert(not hit.is_empty(),"Actual lower shell contact is missing")
			# Loft quads at changing corners are triangulated; bilinear ring midpoints are not exact surface contacts.
			var closest:Vector3=ray.to
			for triangle in triangles:
				var point=Geometry3D.segment_intersects_triangle(ray.from,ray.to,triangle[0],triangle[1],triangle[2])
				if point!=null and ray.from.distance_to(point)<ray.from.distance_to(closest):closest=point
			assert(hit.position.distance_to(closest)<.005,"Physics contact must match the actual exported triangle surface")
			var deviation:float=hit.position.distance_to(Vector3(p.x,y,p.y))
			maximum_loft_deviation=maxf(maximum_loft_deviation,deviation)
			assert(deviation<.7,"Loft deviation must fit within the unused0.7m frame reservation")
			checked+=1
	print("LOWER HULL MAX LOFT RAY DEVIATION:",maximum_loft_deviation)
	var pan:=PhysicsRayQueryParameters3D.create(Vector3(0,-2,0),Vector3(0,-4,0));pan.exclude=omit
	var support:=space.intersect_ray(pan)
	assert(not support.is_empty()and absf(support.position.y+3.2)<.01 and support.normal.y>.99,"Actual keel pan top")
	var hollow:=PhysicsRayQueryParameters3D.create(Vector3(0,1,-20),Vector3(0,1,20));hollow.exclude=omit
	assert(space.intersect_ray(hollow).is_empty(),"Shell does not convex-fill the interior")
	var open_upper:=PhysicsRayQueryParameters3D.create(Vector3(110,18,0),Vector3(130,18,0));open_upper.exclude=omit
	assert(space.intersect_ray(open_upper).is_empty(),"Upper guest facade remains unbuilt rather than blanked over")
	print("LOWER HULL PASS:",checked," inner shell contact samples, actual keel support and unfilled interior. Upper hull/windows, apertures, structural loads and final exterior art unfinished.")
	quit()
