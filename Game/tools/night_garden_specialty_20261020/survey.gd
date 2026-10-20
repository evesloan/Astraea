extends SceneTree
func _initialize()->void:
	call_deferred("run")
func run()->void:
	var world:=Node3D.new();root.add_child(world)
	var commons:Node3D=load("res://assets/models/AST-COM-003.glb").instantiate();world.add_child(commons);commons.position=Vector3(63,84,0)
	for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh!=null:load("res://scripts/static_contact_cache.gd").attach(mesh)
	for path in ["structural_meshes","received_structural_meshes"]:
		var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/"+path+".json"))
		for region in data.regions:
			if absf(float(region.floor_y)-93.0)>.01:continue
			var faces:=PackedVector3Array()
			for tri in region.triangles:
				var near:=false
				for p in tri:
					if p[0]>60 and p[0]<103 and absf(p[1])<110:near=true
				if near:
					for j in [0,2,1]:faces.append(Vector3(tri[j][0],93,tri[j][1]))
			if faces.is_empty():continue
			var body:=StaticBody3D.new();body.name=str(region.id);world.add_child(body)
			var col:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces);col.shape=shape;body.add_child(col)
	await physics_frame;await physics_frame
	var result:Dictionary={"scope":"Focused current AST-COM-003 plus exact D15 generated baseline floor owners; no full ship startup", "rays":[]}
	for p in [Vector3(84,93,-42),Vector3(96.3,93,-42),Vector3(84,93,42),Vector3(96.3,93,42),Vector3(90.5,93,-13.5),Vector3(90.5,93,13.5)]:
		var hit:Dictionary=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.4,p-Vector3.UP*.4))
		result.rays.append({"point":[p.x,p.y,p.z],"hit":not hit.is_empty(),"owner":str(hit.collider.get_path()) if not hit.is_empty() else ""})
	for sign in [-1,1]:
		var hit:Dictionary=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(90.5,94.5,sign*13),Vector3(90.5,94.5,sign*15)))
		result.rays.append({"portal_sign":sign,"blocked":not hit.is_empty(),"owner":str(hit.collider.get_path()) if not hit.is_empty() else ""})
	var file:=FileAccess.open("res://docs/validation/night_garden_specialty_20261020/BASELINE_FOCUSED_SURVEY.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();print(JSON.stringify(result));quit()
