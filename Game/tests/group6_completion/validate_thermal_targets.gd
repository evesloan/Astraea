extends "res://tests/group6_completion/validate_water_care.gd"
var thermal_motion:Array=[]
func thermal_checks(room:Node3D,actor:CharacterBody3D,spec:Dictionary)->void:
	for name in spec.water_visual_contact_exclusions:
		var mesh:MeshInstance3D=room.find_child(str(name),true,false)
		record("water_visual_not_walkable_"+str(name),mesh.visible and mesh.get_node_or_null("StaticContact")==null)
	for entry in spec.entries:
		var dry:=vec(entry.dry_xyz);var bed:=vec(entry.bed_xyz)
		actor.global_position=dry+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
		for i in range(20):await physics_frame
		record(str(entry.id)+"_supported_dry_fixture",actor.is_on_floor() and absf(actor.global_position.y-dry.y)<.01)
		var witness:=MotionWitness.new();witness.process_physics_priority=1000;root.add_child(witness);witness.reset(actor)
		for goal in [bed,dry]:
			var w:Dictionary=await walk_to(actor,goal);legs.append(w);record(str(entry.id)+"_original_leg_"+str(legs.size()),w.reached and w.floor_contact)
		witness.active=false;record(str(entry.id)+"_continuous_motion",witness.maximum_step<.12 and witness.minimum_y>44.25 and witness.samples>100)
		thermal_motion.append({"id":entry.id,"physics_samples":witness.samples,"max_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y});witness.queue_free()
		if not errors.is_empty():break
	physical_key(false)
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var floor_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for r in floor_data.regions:
		if str(r.id).begins_with("D08_directory_02_") or str(r.id).begins_with("D08_directory_03_"):regions.append(r)
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"ExactRetainedThermalCompilerFloors")
	record("four_exact_original_floor_owners",floors.get_child_count()==4)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"))
	for spec in plan.rooms:
		var room:Node3D=load("res://"+str(spec.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(spec.programme_key);room.set_meta("programme_key",str(spec.programme_key));host.add_child(room)
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
		var addition:Node3D=load("res://scripts/group6_completion/thermal_entries.gd").build(room);record(str(spec.programme_key)+"_build_succeeded",addition!=null)
		if addition!=null:await thermal_checks(room,actor,spec)
		if not errors.is_empty():break
	record("all_four_thermal_entries_exercised",legs.size()==8)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":thermal_motion,"supported_independent_fixtures":4,"traversal_position_or_velocity_writes":0,"scope":"Exact current received thermal room exports/retained compiler floors, four scoped entry successors and unchanged original player. Water meshes have truthful visual-only contact policy. No swimming, temperature, gravity, operational hoist/chair/species or final-art acceptance."}
	FileAccess.open("res://docs/group6_completion/THERMAL_TARGET002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 THERMAL TARGET ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
