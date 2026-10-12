extends "res://tests/group8/validate_medical_bay.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	plan=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_bay.json"));actor.position=Vector3(28,21.06,-430);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");var room:Node3D=stream.rooms["D05_directory_02"];addition=load("res://scripts/group8/medical_bay.gd").build(ship,room)
	for f in range(8):await physics_frame
	for row in plan.runtime_batches:
		var mesh:MeshInstance3D=addition.find_child(str(row.runtime_node_name),true,false)
		if str(row.category)=="moving_leaf":
			for d in plan.doors:
				var driver:Node3D=addition.get_node(str(d.name));var found=driver.find_child(str(row.runtime_node_name),true,false)
				if found!=null:mesh=found
		verify(mesh!=null,"Source copy or fitted runtime mesh missing")
		var lo:=Vector3(INF,INF,INF);var hi:=-lo;var faces:=mesh.mesh.get_faces()
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb;verify(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002 and faces.size()==int(row.triangles)*3,"Exact source-import initial bounds or triangles changed")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var admitted:Dictionary={}
	await go(actor,Vector3(28,21,-460));await go(actor,Vector3(23,21,-460));budget.refresh()
	var bed:SpotLight3D=addition.get_node("G8B_Bed1_light_TaskSource");verify(bed.visible and bed.shadow_enabled and budget._has_visible_sample(bed),"Reached bed work stance did not admit its actual housed source");admitted[str(bed.name)]=true
	await go(actor,Vector3(28,21,-460));await go(actor,Vector3(28,21,-418));await go(actor,Vector3(23,21,-418));budget.refresh()
	var surgery:SpotLight3D=addition.get_node("G8B_Surgery1_task_TaskSource");verify(surgery.visible and surgery.shadow_enabled and budget._has_visible_sample(surgery),"Reached surgery work stance did not admit its actual housed source");admitted[str(surgery.name)]=true
	await go(actor,Vector3(28,21,-418));await go(actor,Vector3(28,21,-404));budget.refresh()
	var wash:SpotLight3D=addition.get_node("G8B_Wash_transfer_task_TaskSource");verify(wash.visible and wash.shadow_enabled and budget._has_visible_sample(wash),"Reached transfer/wash stance did not admit its actual housed source");admitted[str(wash.name)]=true
	var report:={"status":"PASS","checks":checks,"exact_new_runtime_meshes":plan.runtime_batches.size(),"new_sources_admitted_at_reached_stances":admitted,"walk_legs":legs,"walk_frames":frames,"walk_distance_m":distance,"setup_placements":1,"subsequent_teleports":0,"actual_shadow_budget_unchanged":true,"clinical_species_cart_engineering_final_art_acceptance":false}
	FileAccess.open("res://data/architecture/group8/MEDICAL_BAY_FIXTURE_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 MEDICAL BAY PASS: ",JSON.stringify(report))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
