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
	assert(FileAccess.get_sha256("res://tools/qa_inputs/AST-RES-005.glb")=="8cfa8eb9a7775b6d5ba855f826176b6d34a35760a1c86fe9cc7dd051d2b3cb52")
	var candidate:Node3D=(load("res://tools/qa_inputs/AST-RES-005.glb") as PackedScene).instantiate() as Node3D;ship.add_child(candidate);candidate.global_transform=Transform3D.IDENTITY
	for index in [5,6]:
		var mesh:MeshInstance3D=candidate.find_children("*Footing_"+str(index)+"*","MeshInstance3D",true,false)[0]
		mesh.create_trimesh_collision()
		for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=2;body.collision_mask=0
	for frame in range(4):await physics_frame
	var rows:Array=[]
	for spec in [[5,29.6],[6,46.0]]:
		var meshes:Array=candidate.find_children("*Footing_"+str(spec[0])+"*","MeshInstance3D",true,false);assert(meshes.size()==1)
		var mesh:MeshInstance3D=meshes[0];var faces:PackedVector3Array=mesh.mesh.get_faces();var samples:Array=[]
		for i in range(9):
			for j in range(9):
				var x:float=115.64+float(i)*.72/8.0;var z:float=float(spec[1])-.54+float(j)*1.08/8.0;var origin:=Vector3(x,20,z);var ys:Array=[]
				for k in range(0,faces.size(),3):
					var hit=Geometry3D.ray_intersects_triangle(origin,Vector3.DOWN,mesh.global_transform*faces[k],mesh.global_transform*faces[k+1],mesh.global_transform*faces[k+2])
					if hit!=null:ys.append(hit.y)
				assert(ys.size()>=2);ys.sort()
				var phys=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,Vector3(x,-10,z),1));assert(not phys.is_empty())
				assert("HUL_LowerBand_03" in str(phys.collider.get_path()))
				var bottom=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,-10,z),origin,2))
				var top=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(origin,Vector3(x,-10,z),2))
				assert(not bottom.is_empty() and not top.is_empty())
				assert(abs(bottom.position.y-float(ys.front()))<.00002 and abs(top.position.y-float(ys.back()))<.00002)
				samples.append({"candidate_collision_bottom_y":bottom.position.y,"candidate_collision_top_y":top.position.y,"xz":[x,z],"candidate_bottom_y":ys.front(),"candidate_top_y":ys.back(),"retained_hull_y":phys.position.y,"overlap_m":phys.position.y-float(ys.front()),"inside_wedge":float(ys.front())<=phys.position.y and phys.position.y<=float(ys.back())})
		rows.append({"footing_index":spec[0],"mesh":mesh.name,"surface_format":mesh.mesh.surface_get_format(0),"samples":samples})
	var all_inside:bool=true
	for row in rows:
		for sample in row.samples:all_inside=all_inside and sample.inside_wedge
	var report:Dictionary={"pass":all_inside,"loader":"Godot editor-imported QA fixture; transient instance against unchanged actual main ship, no gameplay adoption", "scope":"162 interior samples: imported candidate render/collision interval contains retained-hull physics; exact raw-source coordinate1mm comparison still differs", "rows":rows}
	var file:=FileAccess.open("res://artifacts/royalty_editor_import_contact_screen.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	assert(all_inside,"New imported wedge must contain retained hull at every sample")
	print("EDITOR-IMPORTED CANDIDATE CONTACT SCREEN: ",all_inside)
	candidate.queue_free();main.queue_free();await process_frame;quit()
