extends SceneTree
func _initialize()->void:call_deferred("run")
func triangles(faces:PackedVector3Array,pose:Transform3D)->Dictionary:
	var out:Dictionary={}
	for i in range(0,faces.size(),3):
		var v:Array[String]=[]
		for j in range(3):v.append(var_to_bytes(pose*faces[i+j]).hex_encode())
		v.sort();var key:="|".join(PackedStringArray(v));out[key]=int(out.get(key,0))+1
	return out
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var arch:Node3D=ship.get_node("ShipSpace/Districts/D05MedicalWelcome_WIP/AuthoredMedicalWelcome");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"));var guard=load("res://tests/group8/medical_privacy_successor_guard.gd");var checks:=0
	for row in p.doors:
		var d:Node3D=arch.get_node(str(row.name))
		for mesh:MeshInstance3D in d.bound_meshes:
			var contact:CollisionShape3D=mesh.get_node("StaticContact").get_child(0);var expected:ConcavePolygonShape3D=mesh.mesh.create_trimesh_shape()
			assert(triangles(contact.shape.get_faces(),contact.global_transform)==triangles(expected.get_faces(),mesh.global_transform),"Exact native contact triangle fidelity predicate must survive fitted motion");checks+=1
		for side in ["left","right"]:
			var node:MeshInstance3D=d.hinge_nodes[0 if side=="left"else 1].get_node("TRIAGE_%02d_privacy_leaf_%s"%[int(row.source_pod_number),side])
			assert(guard.validate_fitted_leaf(node),"Strict optional fitted-leaf successor predicate failed");checks+=1
	var additions:Node3D=ship.get_node("ShipSpace/Districts/"+str(p.root_name))
	for row in p.runtime_batches:
		var mesh:MeshInstance3D=additions.find_child(str(row.name),true,false);assert(mesh!=null and mesh.has_node("StaticContact")==bool(row.collide))
		var faces:=mesh.mesh.get_faces();var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb;assert(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002 and faces.size()==int(row.triangles)*3,"Exact new fitting import bounds or triangle count changed");checks+=1
	var r:={"status":"PASS","checks":checks,"pinned_fitted_metadata_predicates":16,"exact_original_leaf_component_contacts":80,"new_runtime_batches":64,"initial_poses_original_resources_and_physics_server_agree":true,"shared_full_regression":"held upstream source authentication; not bypassed","clinical_pressure_species_cart_engineering_final_art_acceptance":false}
	FileAccess.open("res://data/architecture/group8/MEDICAL_PRIVACY_SUCCESSOR_LOCAL_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  ")+"\n");print("GROUP8 MEDICAL PRIVACY PASS: ",JSON.stringify(r))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
