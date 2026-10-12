extends "res://tests/group6_completion/validate_thermal_targets.gd"
var support_motion:Array=[]
var support_evidence:Array=[]
func support_checks(host:Node3D,room:Node3D,actor:CharacterBody3D,spec:Dictionary,budget:Node)->void:
	var addition:Node3D=room.get_node("Group6ThermalSupport");var space:=room.get_world_3d().direct_space_state
	record(str(spec.programme_key)+"_fixed_support_no_occupied_gameplay",not addition.get_meta("occupied_hoist_water_species_accepted") and addition.get_meta("new_room_capacity")==0)
	record(str(spec.programme_key)+"_78_source_meshes",addition.find_children("*","MeshInstance3D",true,false).size()==78)
	for station in spec.stations:
		var id:String=str(station.id);var dry:=vec(station.dry_entry_xyz);var stance:=vec(station.operator_xyz)
		actor.global_position=dry+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
		for j in range(20):await physics_frame
		record(id+"_supported_fixture",actor.is_on_floor() and absf(actor.global_position.y-dry.y)<.01)
		var witness:=MotionWitness.new();witness.process_physics_priority=1000;host.add_child(witness);witness.reset(actor)
		var toward:Dictionary=await walk_to(actor,stance);legs.append(toward);record(id+"_normal_transfer_approach",toward.reached and toward.floor_contact)
		var fitting:Dictionary=station.task_light;var light:SpotLight3D=addition.get_node(str(fitting.id)+"_PhysicalSource");var target:=vec(fitting.target_xyz)
		record(id+"_exact_source",light.global_position.distance_to(vec(fitting.source_xyz))<.00001)
		var query:=PhysicsRayQueryParameters3D.create(light.global_position,target);query.exclude=[actor.get_rid()];var hit:=space.intersect_ray(query)
		record(id+"_real_seat_light_path",hit.is_empty())
		query=PhysicsRayQueryParameters3D.create(target,target+Vector3.DOWN*.12);query.exclude=[actor.get_rid()];hit=space.intersect_ray(query)
		record(id+"_real_seat_receiver",not hit.is_empty() and str(hit.collider.get_parent().name).ends_with("seat_pad"))
		var capsule:=CapsuleShape3D.new();capsule.radius=.75;capsule.height=1.7;var q:=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,vec(station.turn_proposal_xyz)+Vector3.UP*.86);q.exclude=[actor.get_rid()]
		var overlap:=space.intersect_shape(q,64);record(id+"_1_5m_source_turn_proposal_clear",overlap.is_empty())
		budget.refresh();var active:=0
		for source:Light3D in budget.sources:
			if not is_instance_valid(source) or not source.is_inside_tree():continue
			if budget.requested_shadow.get(source.get_instance_id(),false):
				record(id+"_shadow_visibility_"+str(source.name),source.visible==source.shadow_enabled)
				if source.visible:active+=1
		record(id+"_original_eight_shadow_cap",active>0 and active<=8)
		var receiver:=actor.global_position+Vector3.UP*.8;var offset:=receiver-light.global_position
		record(id+"_mounted_task_reaches_actor",light.visible and offset.length()<light.spot_range and offset.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)) and budget._clear_sample(light.global_position,receiver))
		support_evidence.append({"id":id,"turn_proposal_clear":overlap.is_empty(),"seat_receiver":str(hit.collider.get_path()) if not hit.is_empty() else "missing","active_shadow_sources":active,"source":fitting.source_xyz,"supported_operator":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"wheelchair_hoist_species_accepted":false})
		var back:Dictionary=await walk_to(actor,dry);legs.append(back);record(id+"_normal_return",back.reached and back.floor_contact)
		witness.active=false;record(id+"_continuous_motion",witness.maximum_step<.12 and witness.minimum_y>44.85 and witness.samples>30);support_motion.append({"id":id,"samples":witness.samples,"max_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y});witness.queue_free()
		if not errors.is_empty():break
	physical_key(false)
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var floor_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for r in floor_data.regions:
		if str(r.id).begins_with("D08_directory_02_") or str(r.id).begins_with("D08_directory_03_"):regions.append(r)
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"ExactRetainedThermalCompilerFloors");record("four_original_floor_owners",floors.get_child_count()==4)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor)
	var entries:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"));var supports:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_SUPPORT_CONTRACT.json"));var rooms:Array=[]
	for i in range(2):
		var entry:Dictionary=entries.rooms[i];var room:Node3D=load("res://"+str(entry.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(entry.programme_key);room.set_meta("programme_key",str(entry.programme_key));host.add_child(room)
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
		load("res://scripts/group6_completion/thermal_entries.gd").build(room);var addition:Node3D=load("res://scripts/group6_completion/thermal_support.gd").build(room);record(str(entry.programme_key)+"_support_build",addition!=null);rooms.append(room)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();host.add_child(budget);budget.set_process(false);budget.configure(host,actor)
	for i in range(2):
		await thermal_checks(rooms[i],actor,entries.rooms[i]);await support_checks(host,rooms[i],actor,supports.rooms[i],budget)
		if not errors.is_empty():break
	record("four_entry_and_support_approaches_exercised",legs.size()==16 and support_evidence.size()==4)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"entry_motion":thermal_motion,"support_motion":support_motion,"support_evidence":support_evidence,"supported_independent_fixtures":8,"traversal_position_velocity_writes":0,"scope":"Exact original received thermal exports/four floor owners, preserved r003 entries, four fixed dry support stations/task lights and original player. Turn capsule is a geometry proposal; occupied hoist/water/chair/gravity/species, hardware and final art held."}
	FileAccess.open("res://docs/group6_completion/THERMAL_SUPPORT_LOCAL001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 THERMAL SUPPORT LOCAL ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
