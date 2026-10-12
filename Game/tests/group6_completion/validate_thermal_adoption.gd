extends "res://tests/group6_completion/validate_local.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var space_root:=Node3D.new();space_root.name="ShipSpace";host.add_child(space_root)
	var districts:=Node3D.new();districts.name="Districts";space_root.add_child(districts)
	var rooms:=Node3D.new();rooms.name="ReceivedSections";districts.add_child(rooms)
	var actors:=Node3D.new();actors.name="PersistentActors";space_root.add_child(actors)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.name="Player";actor.spawn_position=Vector3(38.5,44.93,-430.15);actors.add_child(actor);actor.global_position=actor.spawn_position;actor.set_controls_enabled(false);actor.set_physics_process(false)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.set_process(false);budget.configure(host,actor)
	var floors_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for region in floors_data.regions:
		if str(region.id).begins_with("D08_directory_02_") or str(region.id).begins_with("D08_directory_03_"):regions.append(region)
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(space_root,host.stone,host.ivory,regions,{},"OriginalThermalCompilerFloors");var floor_id:=floors.get_instance_id()
	var predecessors:Array=[];var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"))
	for spec in data.rooms:
		var room:Node3D=load("res://"+str(spec.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(spec.programme_key);room.set_meta("programme_key",str(spec.programme_key));room.set_meta("persistent_id",str(spec.programme_key));rooms.add_child(room)
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
		var entry:Node3D=load("res://scripts/group6_completion/thermal_entries.gd").build(room);var support:Node3D=load("res://scripts/group6_completion/thermal_support.gd").build(room);predecessors.append([entry,entry.get_instance_id(),support,support.get_instance_id()])
		var source_lights:Array[Light3D]=[]
		for light:Light3D in support.find_children("*","Light3D",true,false):source_lights.append(light)
		load("res://scripts/receiving_source_lights.gd").register(source_lights,host)
	for i in range(3):await physics_frame
	var before:int=budget.sources.size();var installed:Dictionary=load("res://scripts/group6_completion/thermal_integration.gd").finish(host)
	for i in range(3):await process_frame
	var north:Node3D=rooms.get_node("D08_directory_02");var mineral:Node3D=rooms.get_node("D08_directory_03");var chamber:Node3D=north.get_node("Group6TidalNorthRoom")
	record("current_Group1_predecessor_registration_order",before==4 and budget.sources.size()==before+int(installed.new_registered_sources))
	var ids:Dictionary={}
	for light:Light3D in budget.sources:record("unique_source_"+str(light.get_instance_id()),not ids.has(light.get_instance_id()));ids[light.get_instance_id()]=true
	for old in predecessors:record("predecessor_instances_retained_"+str(old[1]),old[0].get_instance_id()==old[1] and old[2].get_instance_id()==old[3])
	record("both_recoveries_one_north_successor",north.get_node_or_null("Group6ThermalRecovery")!=null and mineral.get_node_or_null("Group6ThermalRecovery")!=null and mineral.get_node_or_null("Group6TidalNorthRoom")==null)
	record("same_four_compiler_floor_owners",floors.get_instance_id()==floor_id and floors.get_child_count()==4)
	record("reflection_automatically_waits_for_real_budget",chamber.get_node("TidalActualRoomReflection").visible and chamber.get_node("AfterBudgetLocalReflection").get_meta("admitted_room_sources_at_capture",0)>0)
	var active:=0
	for light:Light3D in budget.sources:
		if not light.get_meta("fixture_powered",true):record("inactive_successor_source_"+str(light.name),not light.visible and not light.shadow_enabled)
		elif light.visible:active+=1;record("source_has_real_shadow_"+str(light.name),light.shadow_enabled)
	record("same_eight_shadow_limit",active>0 and active<=8)
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/TIDAL_NORTH_ROOM_CONTRACT.json"))
	for name in spec.original_runtime_exclusions+spec.prior_recovery_runtime_exclusions:
		var mesh:MeshInstance3D=north.find_child(str(name),true,false);record("old_visual_contact_cleanup_"+str(name),not mesh.visible and mesh.get_node_or_null("StaticContact")==null)
	var occlusion:Dictionary=load("res://scripts/static_room_occlusion.gd").install(host);record("occlusion_installed_after_successors",occlusion.source_meshes>0)
	var residency:Node=load("res://scripts/received_room_residency.gd").new();residency.name="ReceivedRoomResidency";systems.add_child(residency);residency.setup(host);record("current_Group1_residency_sees_both_rooms",residency.entries.size()==2)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"installation":installed,"registered_sources":budget.sources.size(),"active_sources":active,"occlusion":occlusion,"scope":"Exact retained Group1 bootstrap predecessor order and existing registry/occlusion/residency APIs in the isolated two-room/four-floor context. No combined ship startup, traversal, hardware or occupied-water acceptance. Existing 22-leg room receipt is separate."}
	FileAccess.open("res://docs/group6_completion/THERMAL_ADOPTION_LOCAL002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 THERMAL ADOPTION ",result.status," ",errors);quit(0 if errors.is_empty() else 1)
