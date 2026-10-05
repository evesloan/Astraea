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
	var mesh:MeshInstance3D=ship.find_child("HUL_LowerBand_03",true,false) as MeshInstance3D
	assert(mesh!=null)
	var faces:PackedVector3Array=mesh.mesh.get_faces();var rows:Array=[]
	for p in [Vector2(115.6,29),Vector2(116,29.6),Vector2(116.4,30.2)]:
		var origin:=Vector3(p.x,20,p.y);var hits:Array=[]
		for i in range(0,faces.size(),3):
			var a:Vector3=mesh.global_transform*faces[i];var b:Vector3=mesh.global_transform*faces[i+1];var c:Vector3=mesh.global_transform*faces[i+2]
			var hit=Geometry3D.ray_intersects_triangle(origin,Vector3.DOWN,a,b,c)
			if hit!=null and hit.y>6 and hit.y<12:hits.append({"y":hit.y,"triangle":[[a.x,a.y,a.z],[b.x,b.y,b.z],[c.x,c.y,c.z]]})
		var physics=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,Vector3(p.x,-10,p.y),1))
		rows.append({"xz":[p.x,p.y],"decoded_render_hits":hits,"physics_y":physics.position.y})
	var file:=FileAccess.open("/workspace/scratch/375c2e438292/hull_band03_import_contact_audit.json",FileAccess.WRITE);file.store_string(JSON.stringify({"mesh_path":str(mesh.get_path()),"rows":rows,"import_compression_disabled":false},"  "));file.close()
	print("Band03 decoded mesh/contact audit written")
	main.queue_free();await process_frame;quit()
