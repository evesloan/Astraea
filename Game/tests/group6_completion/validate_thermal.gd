extends "res://tests/group6_completion/validate_local.gd"
func thermal_route(z:float)->Array:
	return [Vector3(75.2,45.45,z-3.6),Vector3(77,45.45,z-3.6),Vector3(77,45.45,z-1.5),Vector3(77.5,45.45,z-.35),Vector3(81.7,44.4,z-.35),Vector3(77.5,45.45,z-.35),Vector3(77,45.45,z-1.5),Vector3(77,45.45,z-3.6),Vector3(75.2,45.45,z-3.6),Vector3(75.2,45.45,z-2.7)]
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host)
	load("res://scripts/group6_completion/completion.gd").build(annex,host)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FIT_CONTRACT.json"))
	for court in plan.thermal_entry_courts:
		var z:float=float(court.center_xz[1]);var id:String=str(court.source_id)
		var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.spawn_position=Vector3(75.2,45.48,z-2.7);host.add_child(actor);actor.global_position=actor.spawn_position;actor.set_controls_enabled(true)
		for i in range(20):await physics_frame
		var query:=PhysicsShapeQueryParameters3D.new();var shape:=CylinderShape3D.new();shape.radius=.75;shape.height=1.8;shape.margin=.001;query.shape=shape
		query.exclude=[actor.get_rid()];query.transform=Transform3D(Basis.IDENTITY,Vector3(77,46.36,z-1.5))
		record(id+"_turn_proposal_clear",host.get_world_3d().direct_space_state.intersect_shape(query,128).is_empty())
		for i in range(16):
			var angle:=float(i)*TAU/16;var at:=Vector3(77+.74*cos(angle),45.45,z-1.5+.74*sin(angle))
			var hit:=ray(host.get_world_3d().direct_space_state,at+Vector3.UP*.05,at-Vector3.UP*.05)
			record(id+"_turn_floor_"+str(i),not hit.is_empty() and absf(hit.position.y-45.45)<.003)
		var route:Array=thermal_route(z)
		for goal in route:
			var w:Dictionary=await walk_to(actor,goal);legs.append(w);record(id+"_original_player_leg_"+str(legs.size()),w.reached and w.floor_contact)
			if not errors.is_empty():break
		actor.queue_free()
		for i in range(3):await physics_frame
		if not errors.is_empty():break
	physical_key(false)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"supported_fixture_seeds":2,"scope":"Two retained thermal basins, actual bank/bed and visible source entry surfaces; original player walks with normal input. 1.5m dry-turn geometry is a proposal clearance, not wheelchair, broad species, gravity, swimming or water-control acceptance."}
	FileAccess.open("res://docs/group6_completion/THERMAL001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 THERMAL ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
