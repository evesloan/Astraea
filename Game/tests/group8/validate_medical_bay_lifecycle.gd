extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	actor.position=Vector3(28,21.06,-430);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");var room:Node3D=stream.rooms["D05_directory_02"];var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_bay.json"))
	assert(room.get_meta("stream_loaded",false)and room.has_node(str(p.root_name)),"Scoped Medical Bay hook did not install")
	var n:Node3D=room.get_node(str(p.root_name));var weak:Array=[]
	for light in n.find_children("*","SpotLight3D",true,false):weak.append(weakref(light))
	assert(weak.size()==39)
	var pose:=actor.global_transform;var saved:Node3D=stream.actor
	var fixture:=Node3D.new();root.add_child(fixture);fixture.position=Vector3(0,21,-600);stream.set_physics_process(false);stream.actor=fixture;stream.refresh()
	assert(not room.get_meta("stream_loaded",true)and not room.has_node(str(p.root_name)))
	for ref:WeakRef in weak:assert(ref.get_ref()==null,"New source leaked after actual source-room unload")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for light in budget.sources:assert(is_instance_valid(light),"Dead source leaked into existing budget")
	stream.actor=saved;stream.refresh();stream.set_physics_process(true);fixture.free()
	assert(actor.global_transform.is_equal_approx(pose)and room.get_meta("stream_loaded",false)and room.has_node(str(p.root_name)))
	n=room.get_node(str(p.root_name));assert(n.find_children("*","SpotLight3D",true,false).size()==39 and room.get_child(0).find_children("*","MeshInstance3D",true,false).size()==2225)
	for row in p.doors:assert(n.has_node(str(row.name))and n.get_node(str(row.name)).bound_meshes.size()==10)
	var r:={"status":"PASS","scoped_existing_source_streamer_range_fixture":true,"source_unload_restore_and_dead_light_cleanup":true,"original_actor_pose_and_identity_unchanged":true,"restored_original_meshes":2225,"restored_directional_sources":39,"restored_privacy_pairs":4,"external_catchment_walk_or_clinical_acceptance":false}
	FileAccess.open("res://data/architecture/group8/MEDICAL_BAY_LIFECYCLE_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  ")+"\n");print("GROUP8 MEDICAL BAY PASS: ",JSON.stringify(r))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
