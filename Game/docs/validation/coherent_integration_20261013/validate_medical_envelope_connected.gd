extends "/workspace/astraea-integration-cutoff-20261013/g8_privacy_runtime_staging/Game/tests/group8/validate_medical_privacy_successor.gd"
func _initialize()->void:
	OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip",true))
	call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var arch:Node3D=ship.get_node("ShipSpace/Districts/D05MedicalWelcome_WIP/AuthoredMedicalWelcome")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"))
	var guard=load("res://tests/group8/medical_privacy_successor_guard.gd")
	var checks:=0
	for row in p.doors:
		var d:Node3D=arch.get_node(str(row.name))
		assert(d.hinge_nodes.size()==2 and d.bound_meshes.size()==10 and d.open_fraction==1 and d.desired_open)
		for mesh:MeshInstance3D in d.bound_meshes:
			var contact:CollisionShape3D=mesh.get_node("StaticContact").get_child(0)
			var expected:ConcavePolygonShape3D=mesh.mesh.create_trimesh_shape()
			assert(triangles(contact.shape.get_faces(),contact.global_transform)==triangles(expected.get_faces(),mesh.global_transform),"Exact original leaf contact triangles must survive shared binding");checks+=1
		for side in ["left","right"]:
			var node:MeshInstance3D=d.hinge_nodes[0 if side=="left"else 1].get_node("TRIAGE_%02d_privacy_leaf_%s"%[int(row.source_pod_number),side])
			assert(guard.validate_fitted_leaf(node),"Strict pinned fitted source predicate required");checks+=1
	var additions:Node3D=ship.get_node("ShipSpace/Districts/"+str(p.root_name))
	for row in p.runtime_batches:
		var mesh:MeshInstance3D=additions.find_child(str(row.name),true,false);assert(mesh!=null and mesh.has_node("StaticContact")==bool(row.collide))
		var faces:=mesh.mesh.get_faces();var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb
		assert(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002 and faces.size()==int(row.triangles)*3);checks+=1
	var group7:Node3D=ship.get_node("ShipSpace/Districts/Group7CompletionCandidate")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	assert(plan.integration_boundary.name=="envelope" and plan.models.size()==69 and plan.lights.size()==8 and plan.doors.size()==4)
	for row in plan.models:
		var cell:Node3D=group7.get_node(str(row.cell));assert(cell.transform.is_equal_approx(Transform3D.IDENTITY));assert(FileAccess.get_sha256("res://assets/models/"+str(row.file))==str(row.sha256));checks+=1
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for row in plan.lights:
		var light:SpotLight3D=group7.get_node(str(row.id));assert(budget.sources.count(light)==1 and budget.requested_shadow[light.get_instance_id()]);checks+=1
	for row in plan.doors:
		var d:Node3D=group7.get_node(str(row.id));assert(str(d.persistent_id)==str(row.id) and not d.desired_open and d.open_fraction==0);checks+=1
	assert(not ship.get_meta("group5_living_service_candidate_installed",true))
	var result:Dictionary={"status":"PASS_BOUNDARY_BINDING_AND_SOURCE_GEOMETRY","checks":checks,"medical_original_leaf_contacts":80,"medical_fitted_predicates":16,"medical_new_batches":64,"group7_models":69,"group7_sources":8,"group7_doors":4,"group7_boundary":"envelope","all_built_remaining_models":19,"all_built_accepted":false,"medical_motion_and_affected_routes_pending":true,"group7_affected_routes_pending":true,"full_build_or_visual_acceptance":false}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/MEDICAL_ENVELOPE_BINDING_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("MEDICAL_ENVELOPE_BOUNDARY_PASS ",JSON.stringify(result));quit(0)
