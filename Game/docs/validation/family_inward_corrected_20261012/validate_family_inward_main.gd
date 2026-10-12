extends SceneTree
func _initialize()->void:call_deferred("run")
func vec(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(35):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var receiver:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate");var assets:Node3D=receiver.get_node("RetainedLandscapeAndSeating")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FAMILY_TERRACE_RECEIVING.json"));var correction:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_meal_arrangement/CHAIR_POSE_SUCCESSOR.json"));var by_name:Dictionary={};var checks:=0;var exclude:Array[RID]=[]
	for row in correction.rows:by_name[str(row.name)]=row
	assert(assets.get_child_count()==157 and int(receiver.get_meta("group2_meal_facing_changes"))==12);checks+=2
	var unchanged:=0
	for item in plan.retained_asset_instances:
		var node:Node3D=assets.get_node(str(item.name));assert(node.position.is_equal_approx(vec(item.world_xyz)));assert(node.scale.is_equal_approx(Vector3.ONE*float(item.scale)));assert(str(node.get_meta("catalogue_id"))==str(item.catalogue_id));checks+=3
		var yaw:float=float(by_name[str(item.name)].corrected_yaw_degrees)if by_name.has(str(item.name))else float(item.yaw)
		assert((node.transform.basis*Vector3(0,0,1)).normalized().is_equal_approx(Vector3(sin(deg_to_rad(yaw)),0,cos(deg_to_rad(yaw)))));checks+=1
		if not by_name.has(str(item.name)):unchanged+=1
		else:
			for body in node.find_children("*","CollisionObject3D",true,false):exclude.append(body.get_rid())
	assert(unchanged==145);checks+=1
	for row in correction.rows:
		var chair:Node3D=assets.get_node(str(row.name));var toward:Vector3=vec(row.meal_setting_world_xyz)-chair.position;toward.y=0;assert((chair.transform.basis*Vector3(0,0,1)).normalized().dot(toward.normalized())>.90);checks+=1
		var query:=PhysicsRayQueryParameters3D.create(chair.global_position+Vector3.UP*.12,chair.global_position-Vector3.UP*.15);query.exclude=exclude;var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query);assert(not hit.is_empty()and absf(hit.position.y-chair.position.y)<.002);checks+=1
		var back:Vector3=chair.global_position+chair.global_transform.basis*Vector3(0,0,-.36);hit=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(back+Vector3.UP*1.1,back+Vector3.UP*.78));assert(not hit.is_empty()and chair.is_ancestor_of(hit.collider));checks+=1
	assert(load("res://scripts/group2_meal_arrangement/pose_successor.gd").apply(receiver)==0);checks+=1
	assert(receiver.get_meta("persistent_id")=="family_terrace_house_001"and not receiver.get_meta("receiving_structure_accepted"));checks+=2
	var result:Dictionary={"status":"PASS","checks":checks,"corrected_existing_chairs":12,"unchanged_other_registered_instances":unchanged,"retained_instances":157,"new_seats_or_capacity":0,"inward_facing_and_actual_floor_back_contacts":true,"idempotent":true,"meal_props_or_programme_remap_adopted":false,"programme_location_hold":"Table Z348 north of historic D16_directory_06 allocation Z356..384;household use proposed;no separate restaurant","scope":"Current combined main existing Family receiver,pose-only correction;all original positions/scales/assets and145 other instance orientations preserved;receiving/meal/staff/admission/seated-body/engineering/final-art remain held"}
	FileAccess.open("res://artifacts/family_inward_main001.json",FileAccess.WRITE).store_string(JSON.stringify(result," ")+"\n");print("FAMILY INWARD MAIN PASS ",checks," checks");quit(0)
