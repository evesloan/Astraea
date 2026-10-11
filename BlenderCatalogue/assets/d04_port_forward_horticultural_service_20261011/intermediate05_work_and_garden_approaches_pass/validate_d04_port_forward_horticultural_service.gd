extends "res://tests/validate_d04_port_forward_commons_service.gd"
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_HORTICULTURAL_SERVICE.json"));var open:bool=p.open_garden_service
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var owned:Node3D=ship.find_child("D04PortForwardHorticulturalService",true,false)
	for path in p.source_pins:record("source_"+str(path),FileAccess.get_sha256("res://../"+str(path))==p.source_pins[path])
	for file in p.model_pins:record("model_"+str(file),FileAccess.get_sha256("res://assets/models/"+str(file))==p.model_pins[file])
	for s in p.parts:
		var mesh:MeshInstance3D=owned.find_child(str(s.name),true,false);record("owned_"+str(s.name),mesh!=null)
		var b:AABB=mesh.global_transform*mesh.get_aabb();var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=b.size-Vector3.ONE*.004;shape.margin=.0001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,b.get_center());var bad:Array=[]
		for h in space.intersect_shape(q,64):
			if not mesh.is_ancestor_of(h.collider):bad.append(str(h.collider.get_path()))
		record("foreign_contact_"+str(s.name),bad.is_empty());if not bad.is_empty():print("FOREIGN ",s.name," ",bad)
	for i in range(p.service_stations.size()):
		var at:=vec(p.service_stations[i]);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("work_floor_"+str(i),not h.is_empty() and str(h.collider.get_parent().name)=="D04CS_Floor" and absf(h.position.y-16.5)<.002);record("work_capsule_"+str(i),capsule_clear(space,at));record("work_cart_"+str(i),cart_clear(space,at,PI))
	for j in range(9):record("workbay_cart_turn_"+str(j),cart_clear(space,vec(p.service_stations[0]),j*PI/4))
	var old:MeshInstance3D=ship.find_child(str(p.preimage.name),true,false);record("exact_garden_preimage_gate",(old==null)==open)
	for s in p.sashes:
		var at:=vec(s.worker_stance);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("garden_worker_floor_"+str(s.name),not h.is_empty() and str(h.collider.get_parent().name)=="D04CS_Floor");record("garden_worker_capsule_"+str(s.name),capsule_clear(space,at))
	var bench:=Vector3(-66.6,16.5,-357.2);var floor_hit:=ray(space,bench+Vector3.UP*.02,bench-Vector3.UP*.02);record("clean_tray_worker_floor",not floor_hit.is_empty() and str(floor_hit.collider.get_parent().name)=="D04CS_Floor");record("clean_tray_worker_capsule",capsule_clear(space,bench))
	var walks:Array=[]
	for goal in [Vector3(-66.3,16.5,-361.8),Vector3(-66.3,16.5,-358.8),Vector3(-65.3,16.5,-358.45),Vector3(-66.6,16.5,-358.45),Vector3(-66.6,16.5,-357.2),Vector3(-66.6,16.5,-358.45),Vector3(-67.8,16.5,-358.6),Vector3(-66.3,16.5,-358.8),Vector3(-66.3,16.5,-361.8)]:
		if walks.is_empty():player.global_position=goal+Vector3.UP*.03;player.velocity=Vector3.ZERO;for i in range(15):await physics_frame
		else:
			var w:Dictionary=await walk_to(player,goal);walks.append(w);record("work_actual_walk_"+str(walks.size()),w.reached and w.floor_contact)
			if goal.distance_to(bench)<.001:
				var h:=ray(space,player.camera.global_position,Vector3(-67.45,17.565,-356.98));record("actual_clean_tray_work_reach",not h.is_empty() and str(h.collider.get_parent().name).begins_with("D04HS_TrayHandle"))
			if goal.distance_to(Vector3(-67.8,16.5,-358.6))<.001:
				var h:=ray(space,player.camera.global_position,Vector3(-68.65,17.435,-359.05));record("actual_closed_cuttings_work_reach",not h.is_empty() and str(h.collider.get_parent().name)in["D04HS_CuttingsHandle","D04HS_CuttingsLid"])
			continue
		walks.append({"initial_fixture":true})
	var operation:Dictionary={}
	var garden_walks:Array=[]
	if open:
		var control:Node3D=owned.get_node("GardenServiceControl");record("three_original_sash_contacts",control.leaves.size()==3)
		# Separate interaction fixture, outside the moving sash volume.
		player.global_position=Vector3(-80.15,16.53,-361.4);player.velocity=Vector3.ZERO;for i in range(15):await physics_frame
		var d:Vector3=vec(p.control_at)-player.camera.global_position;player.rotation.y=atan2(-d.x,-d.z);player.camera.rotation.x=atan2(d.y,Vector2(d.x,d.z).length())
		var right:=InputEventMouseButton.new();right.button_index=MOUSE_BUTTON_RIGHT;right.pressed=true;Input.parse_input_event(right);for i in range(4):await physics_frame
		record("precise_service_control_target",player.interaction_target==control)
		var e:=InputEventKey.new();e.keycode=KEY_E;e.physical_keycode=KEY_E;e.pressed=true;Input.parse_input_event(e);await physics_frame;e.pressed=false;Input.parse_input_event(e);for i in range(100):
			await physics_frame
			if i%10==0:
				for j in range(control.leaves.size()):
					var leaf:AnimatableBody3D=control.leaves[j];record("authored_hinge_origin_"+str(i)+"_"+str(j),leaf.global_position.distance_to(vec(p.sashes[j].pivot))<.00004);var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(1.146,2.446,.176);shape.margin=.0001;q.shape=shape;q.transform=leaf.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,-1.225,.09));q.exclude=[leaf.get_rid()];var hits:=space.intersect_shape(q,64);record("actual_sash_motion_clear_"+str(i)+"_"+str(j),hits.is_empty());if not hits.is_empty():print("MOTION_CONTACT ",i," ",j," ",leaf.global_transform," ",hits)
		record("ordinary_RMB_E_garden_open",control.desired_open and control.open_fraction>.999)
		for s in p.sashes:
			var h:=ray(space,Vector3(s.pivot[0],18,-358),Vector3(s.pivot[0],18,-357));record("actual_open_maintenance_reach_"+str(s.name),h.is_empty())
		for goal in [Vector3(-83.55,16.5,-361.4),Vector3(-83.55,16.5,-359.6),Vector3(-84.42,16.5,-359.6),Vector3(-84.42,16.5,-357.82),Vector3(-84,16.5,-357.82),Vector3(-82.4,16.5,-357.82),Vector3(-80.8,16.5,-357.82),Vector3(-82.4,16.5,-357.82),Vector3(-84.42,16.5,-357.82),Vector3(-84.42,16.5,-359.6),Vector3(-83.55,16.5,-359.6),Vector3(-83.55,16.5,-361.4),Vector3(-80.15,16.5,-361.4)]:
			var w:Dictionary=await walk_to(player,goal);garden_walks.append(w);record("garden_worker_actual_walk_"+str(garden_walks.size()),w.reached and w.floor_contact)
			if garden_walks.size()==6:control.interact(player);record("actual_worker_stance_blocks_close",control.obstructed and control.desired_open)
		d=vec(p.control_at)-player.camera.global_position;player.rotation.y=atan2(-d.x,-d.z);player.camera.rotation.x=atan2(d.y,Vector2(d.x,d.z).length());for i in range(4):await physics_frame
		record("precise_return_service_control_target",player.interaction_target==control)
		var blocker:=RigidBody3D.new();blocker.freeze=true;var col:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.4,.4,.4);col.shape=shape;blocker.add_child(col);owned.add_child(blocker);blocker.global_position=Vector3(-82.4,18,-358);for i in range(3):await physics_frame
		control.interact(player);record("dynamic_worker_or_load_blocks_close",control.obstructed and control.desired_open);blocker.free();for i in range(3):await physics_frame
		e.pressed=true;Input.parse_input_event(e);await physics_frame;e.pressed=false;Input.parse_input_event(e);for i in range(100):await physics_frame
		record("ordinary_RMB_E_garden_close",not control.desired_open and control.open_fraction<.001);
		for j in range(3):
			var item:Dictionary=p.sashes[j];var h:=ray(space,Vector3(item.pivot[0],18,-358),Vector3(item.pivot[0],18,-357));record("closed_again_maintenance_contact_"+str(j),not h.is_empty() and h.collider==control.leaves[j])
		right.pressed=false;Input.parse_input_event(right)
		operation={"precise_RMB_E":true,"all_three_sashes_opened_closed":control.open_fraction<.001,"dynamic_close_guard_tested":true,"plant_or_stock_state_operations":false}
	var result={"status":"PASS"if errors.is_empty()else"FAIL","check_count":checks.size(),"checks":checks,"errors":errors,"model_pins":p.model_pins,"work_player_walks":walks,"garden_worker_walks":garden_walks,"garden_service_operation":operation,"stage":"connected"if open else"sealed","private_court_service_complete":false,"shared_clean_soiled_crossing_operation_accepted":false,"cart_safe_vertical_accepted":false,"whole_neighborhood_complete":false}
	FileAccess.open("res://artifacts/d04_port_forward_horticultural_service_"+result.stage+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
