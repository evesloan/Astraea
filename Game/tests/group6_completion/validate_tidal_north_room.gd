extends "res://tests/group6_completion/validate_water_care.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for region in data.regions:
		if str(region.id).begins_with("D08_directory_02_"):regions.append(region)
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"OriginalTidalCompilerFloors");var floor_id:=floors.get_instance_id()
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/TIDAL_NORTH_ROOM_CONTRACT.json"))
	var room:Node3D=load("res://"+str(spec.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(spec.programme_key);room.set_meta("programme_key",str(spec.programme_key));room.set_meta("persistent_id",str(spec.programme_key));host.add_child(room)
	for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/group6_completion/thermal_entries.gd").build(room);load("res://scripts/group6_completion/thermal_support.gd").build(room);load("res://scripts/group6_completion/thermal_recovery.gd").build(room,true)
	var addition:Node3D=load("res://scripts/group6_completion/tidal_north_room.gd").build(room)
	record("same_programme_and_two_floor_owners",room.get_meta("programme_key")=="D08_directory_02" and floors.get_instance_id()==floor_id and floors.get_child_count()==2)
	record("exact_room_mesh_roles",addition.find_children("*","MeshInstance3D",true,false).size()==spec.new_meshes.size())
	for name in spec.original_runtime_exclusions:
		var mesh:MeshInstance3D=room.find_child(str(name),true,false);record("scoped_successor_"+str(name),not mesh.visible and mesh.get_node_or_null("StaticContact")==null)
	var reflection:ReflectionProbe=addition.get_node("TidalActualRoomReflection");record("bounded_actual_room_reflection_without_ambient",reflection.ambient_mode==ReflectionProbe.AMBIENT_DISABLED and reflection.update_mode==ReflectionProbe.UPDATE_ONCE and reflection.size==Vector3(24,8,30) and reflection.interior and reflection.enable_shadows and not reflection.visible)
	record("floor_piers_removed_and_glazed_guards_have_real_contact",addition.find_child("G6_TIDAL__cove_pier_0",true,false)==null and addition.find_child("G6_TIDAL__gallery_guard_glass_0",true,false).get_node_or_null("StaticContact")!=null)
	var water:MeshInstance3D=addition.find_child("G6_TIDAL__water_face",true,false);var wa:AABB=water.global_transform*water.get_aabb()
	record("same_water_height_boundary_and_no_hidden_collision",absf(wa.position.y-44.9)<.0001 and absf(wa.position.x-29.2)<.0001 and absf(wa.end.x-40.8)<.0001 and absf(wa.position.z+427.8)<.0001 and absf(wa.end.z+408.2)<.0001 and water.get_node_or_null("StaticContact")==null)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.spawn_position=Vector3(38.5,44.93,-430.15);host.add_child(actor);actor.global_position=actor.spawn_position;actor.set_controls_enabled(true);var actor_id:=actor.get_instance_id()
	var budget:Node=load("res://scripts/lighting_budget.gd").new();host.add_child(budget);budget.set_process(false)
	for i in range(20):await physics_frame
	budget.configure(host,actor);load("res://scripts/group6_completion/tidal_north_room.gd").activate_reflection(room,budget);record("reflection_enabled_after_shared_budget",reflection.visible and reflection.get_meta("captured_after_shared_budget"));record("supported_original_wet_landing_start",actor.is_on_floor() and absf(actor.global_position.y-44.9)<.01)
	var optics:Array=[]
	for fitting in spec.fittings:
		var light:SpotLight3D=addition.get_node(str(fitting.id)+"_PhysicalSource");var target:=vec(fitting.target_xyz)
		record(str(fitting.id)+"_mounted_source_cone_path",light.global_position.distance_to(vec(fitting.source_xyz))<.0001 and light.global_position.distance_to(target)<light.spot_range and (-light.global_basis.z).dot((target-light.global_position).normalized())>.999 and budget._clear_sample(light.global_position,target))
		if not budget._clear_sample(light.global_position,target):
			var obstruction:Dictionary=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(light.global_position,target));print("TIDAL OPTICAL HOLD ",fitting.id," ",obstruction)
		var probe_end:Vector3=target+Vector3.UP*.15 if "vault_uplight" in str(fitting.id) else target+Vector3.DOWN*.75
		var receiver_hit:Dictionary=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(target,probe_end));record(str(fitting.id)+"_real_receiver_geometry",not receiver_hit.is_empty())
		optics.append({"id":fitting.id,"source":fitting.source_xyz,"receiver":fitting.receiver,"target":fitting.target_xyz,"actual_receiver_geometry":str(receiver_hit.collider.get_path()) if not receiver_hit.is_empty() else "missing"})
	var witness:=MotionWitness.new();witness.process_physics_priority=1000;host.add_child(witness);witness.reset(actor)
	var goals:Array=[Vector3(42.5,44.9,-430.15),Vector3(42.05,44.9,-423),Vector3(42.05,44.9,-417.5),Vector3(43.65,44.9,-417.5),Vector3(43.65,44,-406.7),Vector3(45,44,-406.7),Vector3(45,44,-412),Vector3(46,44,-412),Vector3(45,44,-412),Vector3(45,44,-432),Vector3(46,44,-432),Vector3(45,44,-432),Vector3(45,44,-406.7),Vector3(43.65,44,-406.7),Vector3(43.65,44.9,-417.5),Vector3(42.05,44.9,-417.5),Vector3(42.05,44.9,-430.15),Vector3(38.5,44.9,-430.15),Vector3(34,44.9,-430.2),Vector3(34,44.3,-424.4),Vector3(34,44.9,-430.2),Vector3(38.5,44.9,-430.15)]
	var lamp_states:Array=[]
	for goal in goals:
		var walk:Dictionary=await walk_to(actor,goal);legs.append(walk);record("continuous_gallery_ramp_recovery_leg_"+str(legs.size()),walk.reached and walk.floor_contact)
		budget.refresh();var active:Array=[]
		for light:Light3D in budget.sources:
			if light.visible and budget.requested_shadow.get(light.get_instance_id(),false):active.append(str(light.name));record("active_source_keeps_shadow_"+str(light.name),light.shadow_enabled)
		record("unchanged_eight_shadow_cap_leg_"+str(legs.size()),active.size()>0 and active.size()<=8);lamp_states.append({"stance":str(actor.global_position),"active":active})
		if not errors.is_empty():break
	witness.active=false;physical_key(false)
	record("same_player_continuous_supported_motion",actor.get_instance_id()==actor_id and witness.maximum_step<.12 and witness.minimum_y>43.95 and witness.samples>100)
	record("all_room_round_trip_legs_exercised",legs.size()==goals.size());record("no_gameplay_or_shared_adoption_claim",not addition.get_meta("swimming_implemented") and addition.get_meta("shared_roof_adoption_pending") and addition.get_meta("new_room_capacity_or_floor_owner")==0)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":{"samples":witness.samples,"maximum_frame_step_m":witness.maximum_step,"minimum_y":witness.minimum_y},"lights":optics,"budget_stances":lamp_states,"supported_initial_fixture_starts":1,"traversal_position_or_velocity_writes":0,"scope":"One coherent Tidal north room candidate; exact original room/two floor owners, retained entries/support, scoped recovery successor and original player/shared lighting budget. Focused wet gallery, return ramp, original east dry route, recovery approach, reverse traversal and preserved northern basin entry/bed/return. Bath entry uses grounded foot movement; visual water only. Shared consolidated roof/adoption, occupied recovery/hoist, swimming/fluid/species/hardware and complete group acceptance remain separate."}
	FileAccess.open("res://docs/group6_completion/TIDAL_NORTH_ROOM_LOCAL010.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 TIDAL NORTH ROOM ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
