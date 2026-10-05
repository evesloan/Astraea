extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	var heights:Array[float]=[]
	var decks:Array[int]=[]
	var ids:Array[String]=[]
	var names:Array[String]=[]
	var codes:Array[String]=[]
	for i in range(18):
		heights.append(float(contract.deck_datums[i].floor_elevation_m))
		decks.append(i+1);ids.append("D%02d"%(i+1));names.append("Deck %02d"%(i+1));codes.append("%02d"%(i+1))
	lift.floor_heights.assign(heights);lift.deck_numbers.assign(decks)
	lift.stop_ids.assign(ids);lift.stop_names.assign(names);lift.stop_codes.assign(codes)
	lift.cabin_file="AST-CIR-003_eighteen_stop.glb"
	lift.gate_origin_xz=Vector2.ZERO
	lift.identity_prefix="primary_panel_test"
	root.add_child(lift)
	for frame in range(12):await physics_frame
	assert(lift.landing_gates.size()==18)
	var seen:Dictionary={}
	var centers:Array[Vector3]=[]
	for i in range(18):
		var button:Node3D=lift.cabin.get_node("primary_panel_test_cabin_D%02d"%(i+1))
		assert(button.floor_index==i and button.display_deck==i+1 and button.face_code=="%02d"%(i+1))
		assert(not seen.has(button.persistent_id));seen[button.persistent_id]=true
		for center in centers:assert(center.distance_to(button.position)>.13,"Precise button targets must not overlap")
		centers.append(button.position)
		var start:Vector3=lift.cabin.global_transform*Vector3(.6,button.position.y,button.position.z)
		var end:Vector3=lift.cabin.global_transform*Vector3(1.86,button.position.y,button.position.z)
		var ray:=PhysicsRayQueryParameters3D.create(start,end)
		ray.collision_mask=3;ray.collide_with_areas=true
		var hit:=lift.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and hit.collider.get_parent()==button,"Every floor button must be independently selectable ahead of backing")
	print("PRIMARY PANEL PASS:18 unique floor destinations and nonoverlapping physical ray targets; authored backing and18 landing identities. No whole-ship shaft, staff access or loaded18-deck travel acceptance implied.")
	lift.queue_free();await process_frame;quit(0)
