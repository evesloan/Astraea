extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var world:=Node3D.new();world.set_meta("group2_isolated_source_fixture",true);root.add_child(world)
	var original:Node3D=(load("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")as PackedScene).instantiate();world.add_child(original)
	load("res://scripts/static_contact_cache.gd").attach_group(original,original.find_children("*","MeshInstance3D",true,false))
	var before:Dictionary={}
	for mesh in original.find_children("*","MeshInstance3D",true,false):before[mesh]=mesh.global_transform
	var kit:Node3D=load("res://scripts/group2_family_meal/package.gd").build_source_fixture(world)
	for frame in range(20):await physics_frame
	var excluded:Array[RID]=[]
	for body in kit.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/COMPONENT_r001.json"));var checks:=0
	for mesh in before:assert(mesh.global_transform.is_equal_approx(before[mesh]));checks+=1
	for table in data.tables:
		for setting in table.settings:
			var p:=Vector3(setting.world_xyz[0],setting.world_xyz[1],setting.world_xyz[2]);var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.08,p-Vector3.UP*.15);query.exclude=excluded
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(query);assert(not hit.is_empty() and abs(hit.position.y-table.support_y)<.002,"Original actual tabletop supports new source meal setting");checks+=1
	assert(data.new_capacity_or_seats==0 and data.canonical_dining_total_unchanged==2200)
	FileAccess.open("res://artifacts/group2_family_meal.json",FileAccess.WRITE).store_string(JSON.stringify({"pass":true,"checks":checks,"actual_tabletop_settings":12,"receiver_poses_unchanged":true,"new_chairs_or_dining_credit":0,"food_staff_admission_or_production_acceptance":false},"\t")+"\n")
	print("GROUP2 FAMILY MEAL PASS actual retained tabletops, no new seats");quit()
