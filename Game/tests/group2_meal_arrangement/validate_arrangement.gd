extends SceneTree
func _initialize()->void:call_deferred("run")
func v(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func run()->void:
	var world:=Node3D.new();world.set_meta("group2_isolated_source_fixture",true);root.add_child(world)
	var space:=Node3D.new();space.name="ShipSpace";world.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var receiver:Node3D=load("res://scripts/family_terrace_receiving.gd").build(world)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_meal_arrangement/CHAIR_POSE_SUCCESSOR.json"))
	var targets:Array[Node3D]=[];var excluded:Array[RID]=[];var checks:=0
	for row in data.rows:
		var chair:Node3D=receiver.get_node("RetainedLandscapeAndSeating/"+str(row.name));targets.append(chair)
		var to:Vector3=(v(row.meal_setting_world_xyz)-chair.position);to.y=0
		assert((chair.transform.basis*Vector3(0,0,1)).normalized().dot(to.normalized())<-.90);checks+=1
		for body in chair.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
	var before:Dictionary={};var untouched:=0
	for mesh in receiver.find_children("*","MeshInstance3D",true,false):
		var changed:=false
		for chair in targets:
			if chair.is_ancestor_of(mesh):changed=true
		if not changed:before[mesh]=mesh.global_transform
	var original_nodes:=receiver.find_children("*","",true,false).size()
	var patch=load("res://scripts/group2_meal_arrangement/pose_successor.gd")
	assert(patch.apply(receiver)==12);assert(patch.apply(receiver)==0);checks+=2
	assert(receiver.find_children("*","",true,false).size()==original_nodes);checks+=1
	for mesh in before:assert(mesh.global_transform.is_equal_approx(before[mesh]));untouched+=1;checks+=1
	load("res://scripts/group2_family_meal/package.gd").build_source_fixture(world)
	for frame in range(20):await physics_frame
	for i in range(targets.size()):
		var chair:=targets[i];var row:Dictionary=data.rows[i];var to:Vector3=v(row.meal_setting_world_xyz)-chair.position;to.y=0
		var forward:Vector3=chair.transform.basis*Vector3(0,0,1)
		assert(forward.normalized().dot(to.normalized())>.90);assert(chair.position.is_equal_approx(v(row.world_xyz)));checks+=2
		var query:=PhysicsRayQueryParameters3D.create(chair.position+Vector3.UP*.12,chair.position-Vector3.UP*.15);query.exclude=excluded
		var floor_hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not floor_hit.is_empty()and abs(floor_hit.position.y-chair.position.y)<.002,"Actual retained floor supports corrected chair");checks+=1
		# A vertical ray at the actual back shell checks its transformed collision.
		var back:Vector3=chair.position+chair.transform.basis*Vector3(0,0,-.36)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(back+Vector3.UP*1.1,back+Vector3.UP*.78))
		assert(not hit.is_empty()and chair.is_ancestor_of(hit.collider),"Back collision follows corrected facing");checks+=1
	var camera_floor:=Vector3(75.7,97.5,353.1)
	var camera_hit:=world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(camera_floor+Vector3.UP*.15,camera_floor-Vector3.UP*.15))
	assert(not camera_hit.is_empty()and abs(camera_hit.position.y-camera_floor.y)<.002,"Review camera stands over the actual retained floor");checks+=1
	FileAccess.open("res://artifacts/group2_meal_arrangement.json",FileAccess.WRITE).store_string(JSON.stringify({"pass":true,"checks":checks,"corrected_existing_chairs":12,"unaffected_retained_mesh_poses":untouched,"facing_meal_settings":true,"actual_floor_and_transformed_back_contacts":true,"idempotent_patch":true,"new_seats_or_capacity":0,"whole_Group2_or_production_adoption_accepted":false},"\t")+"\n")
	print("GROUP2 MEAL ARRANGEMENT PASS12 inward chairs on actual retained receiver");quit()
