extends "res://tests/group6_completion/validate_water_care.gd"
var river_motion:Array=[]
func river_checks(host:Node3D,actor:CharacterBody3D,plan:Dictionary,residency:Node=null)->void:
	for spec in plan.river_entry_interfaces:
		var id:String=str(spec.id);var dry:Vector3=vec(spec.dry_approach_xyz);var bed:Vector3=vec(spec.supported_bed_stance_xyz)
		actor.global_position=dry+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
		if residency!=null:residency.prepare_position(actor.global_position)
		for i in range(20):await physics_frame
		record(id+"_supported_dry_start",actor.is_on_floor() and absf(actor.global_position.y-45.45)<.01)
		var witness:=MotionWitness.new();witness.process_physics_priority=1000;root.add_child(witness);witness.reset(actor)
		for goal in [bed,dry]:
			var w:Dictionary=await walk_to(actor,goal);legs.append(w);record(id+"_original_player_leg_"+str(legs.size()),w.reached and w.floor_contact)
		witness.active=false;record(id+"_continuous_motion",witness.maximum_step<.12 and witness.minimum_y>44.25 and witness.samples>100)
		river_motion.append({"id":id,"physics_samples":witness.samples,"maximum_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y});witness.queue_free()
		if not errors.is_empty():break
	physical_key(false)
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host)
	var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,host)
	record("candidate_build_succeeded",addition!=null)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor)
	if addition!=null:await river_checks(host,actor,JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FIT_CONTRACT.json")))
	record("both_river_entries_exercised",legs.size()==4)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":river_motion,"supported_independent_fixture_starts":2,"traversal_position_or_velocity_writes":0,"scope":"Two real source river bank/bed entry-return paths and unchanged player input/controller; separate supported dry fixtures. No swimming, current, buoyancy, AFK mount, operating hoist, chair/species or final-art acceptance."}
	FileAccess.open("res://docs/group6_completion/RIVER_ENTRY002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 RIVER ENTRY ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
