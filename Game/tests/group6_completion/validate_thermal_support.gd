extends "res://tests/group6_completion/validate_thermal_targets.gd"
var support_motion:Array=[]
var support_evidence:Array=[]
var unoccupied_envelopes:Array=[]
func support_checks(host:Node3D,room:Node3D,actor:CharacterBody3D,spec:Dictionary,budget:Node)->void:
	var addition:Node3D=room.get_node("Group6ThermalSupport");var space:=room.get_world_3d().direct_space_state
	record(str(spec.programme_key)+"_fixed_support_no_occupied_gameplay",not addition.get_meta("occupied_hoist_water_species_accepted") and addition.get_meta("new_room_capacity")==0)
	record(str(spec.programme_key)+"_80_source_meshes",addition.find_children("*","MeshInstance3D",true,false).size()==80)
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
		check_unoccupied_envelopes(room,actor,station,addition)
		var back:Dictionary=await walk_to(actor,dry);legs.append(back);record(id+"_normal_return",back.reached and back.floor_contact)
		witness.active=false;record(id+"_continuous_motion",witness.maximum_step<.12 and witness.minimum_y>44.85 and witness.samples>30);support_motion.append({"id":id,"samples":witness.samples,"max_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y});witness.queue_free()
		if not errors.is_empty():break
	physical_key(false)
func check_unoccupied_envelopes(room:Node3D,actor:CharacterBody3D,station:Dictionary,addition:Node3D)->void:
	var space:=room.get_world_3d().direct_space_state;var exclusion:Array[RID]=[actor.get_rid()];var excluded_names:Array=[]
	for name in station.future_carrier_meshes+station.future_flexible_sling_meshes+station.future_arm_meshes+station.fixed_pivot_connector_meshes:
		var mesh:MeshInstance3D=addition.get_node(str(name));var contact:StaticBody3D=mesh.get_node_or_null("StaticContact")
		if contact!=null:exclusion.append(contact.get_rid());excluded_names.append(str(name))
	var carrier:=BoxShape3D.new();carrier.size=Vector3(.95,.67,.85);var arm:=BoxShape3D.new();var mast:=vec(station.mast_anchor_xyz);var parked:=vec(station.seat_top_xyz);var length:float=absf(parked.z-mast.z);arm.size=Vector3(.74,.49,length+.62)
	var q:=PhysicsShapeQueryParameters3D.new();q.exclude=exclusion;q.margin=0;var samples:=0;var failures:Array=[]
	var final_yaw:float=float(station.proposed_yaw_radians);var lift:float=float(station.unoccupied_geometry_lift_m);var lower:float=float(station.proposed_lower_from_parked_m);var radial:=Vector3(0,0,parked.z-mast.z)
	# Conservative pose reservations only. The original actor, production contacts
	# and every original obstacle stay untouched. Fixed docking legs stay active.
	for phase in ["lift_from_dock","arm_yaw","carrier_yaw","wet_lower"]:
		var count:=512 if phase in ["arm_yaw","carrier_yaw"] else 320
		for k in range(count+1):
			var t:float=float(k)/count;var yaw:float=final_yaw*t if phase in ["arm_yaw","carrier_yaw"] else final_yaw if phase=="wet_lower" else 0.0;var basis:=Basis(Vector3.UP,yaw)
			if phase=="arm_yaw":q.shape=arm;q.transform=Transform3D(basis,Vector3(mast.x,46.90,mast.z)+basis*(radial*.5+radial.normalized()*.21))
			else:
				q.shape=carrier;var delta:float=.04+(lift-.04)*t if phase=="lift_from_dock" else lift+(lower-lift)*t if phase=="wet_lower" else lift
				q.transform=Transform3D(basis,Vector3(mast.x,45.60+delta,mast.z)+basis*radial)
			var hits:=space.intersect_shape(q,64);samples+=1
			if not hits.is_empty():failures.append({"phase":phase,"fraction":t,"collider":str(hits[0].collider.get_path())});break
		record(str(station.id)+"_unoccupied_"+phase+"_reservation_clear",failures.is_empty())
		if not failures.is_empty():break
	var water:=vec(station.proposed_water_seat_xyz);record(str(station.id)+"_geometric_arm_reaches_pinned_water_target",absf(Vector2(water.x-mast.x,water.z-mast.z).length()-length)<.0001)
	unoccupied_envelopes.append({"id":station.id,"samples":samples,"failures":failures,"water_seat_target":station.proposed_water_seat_xyz,"carrier_box_m":[.95,.67,.85],"arm_box_m":[.74,.49,length+.62],"excluded_only_own_future_moving_parts_and_fixed_pivot_connectors":excluded_names,"fixed_docking_legs_and_all_original_contacts_retained":true,"initial_0_to_0_04m_dock_departure_not_certified":true,"dynamic_occupied_motion_or_load_accepted":false})
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
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"entry_motion":thermal_motion,"support_motion":support_motion,"support_evidence":support_evidence,"unoccupied_geometry_envelopes":unoccupied_envelopes,"supported_independent_fixtures":8,"traversal_position_velocity_writes":0,"scope":"Exact original received thermal exports/four floor owners, preserved r003 entries, four fixed dry support stations/task lights and original player. Turn capsule is a geometry proposal; occupied hoist/water/chair/gravity/species, hardware and final art held."}
	FileAccess.open("res://docs/group6_completion/THERMAL_SUPPORT_LOCAL003.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 THERMAL SUPPORT LOCAL ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
