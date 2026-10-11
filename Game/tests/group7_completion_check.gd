extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var sample_checks := 0
var route_legs: Array = []
func snap(node: Node, out: Dictionary) -> void:
	if node is MeshInstance3D:
		out[str(node.get_path())]=[node.mesh,node.transform,node.visible]
	elif node is MultiMeshInstance3D:
		out[str(node.get_path())]=[node.multimesh,node.transform,node.visible]
	for child in node.get_children(): snap(child,out)
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D=main.get_node("World360/Astraea")
	var player: CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/docs/PLAN.json"))
	var before: Dictionary={};snap(ship,before)
	var budget: Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var old_sources: int=budget.sources.size()
	var candidate: Node3D=load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	record("candidate_idempotent",load("res://scripts/group7_completion.gd").build(ship)==candidate)
	record("lights_append_only",budget.sources.size()==old_sources+data.lights.size())
	record("shadow_budget_preserved",budget.shadow_source_budget==8)
	for path in before:
		var node: Node3D=ship.get_node(NodePath(path))
		record("retained_local_geometry_transform_"+path,node!=null and node.transform==before[path][1])
		if node is MeshInstance3D:record("retained_mesh_"+path,node.mesh==before[path][0])
		elif node is MultiMeshInstance3D:record("retained_multimesh_"+path,node.multimesh==before[path][0])
	record("aft_crown_sitting_bays_preserved",ship.find_child("AftCrownSittingBays",true,false)!=null)
	record("aft_crown_sitting_lights_preserved",ship.find_child("AftCrownSittingLighting",true,false)!=null)
	for row in data.models:
		record("export_hash_"+str(row.cell),FileAccess.get_sha256("res://assets/models/"+str(row.file))==row.sha256)
		var visual: Node3D=candidate.get_node(str(row.cell))
		for mesh: MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			var category: String=str(mesh.get_meta("extras",{}).get("contact_category",""))
			if category.begins_with("solid_"):record("actual_contact_"+str(mesh.get_path()),mesh.has_node("StaticContact"))
			elif category=="visual_lens":record("optical_exit_shadow_"+str(mesh.get_path()),mesh.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	var space: PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	# D18 original terminal routes keep their floor; new overhead roof clears it.
	for sign_z in [-1,1]:
		for z in range(511,531,2):
			for x in [-3.0,0.0,3.0]:
				var at:=Vector3(x,106.5,float(z)*sign_z)
				var floor_hit: Dictionary=ray(space,at+Vector3.UP*.05,at-Vector3.UP*.05)
				record("d18_original_floor_"+str(at),not floor_hit.is_empty() and absf(floor_hit.position.y-106.5)<.002)
				record("d18_worker_capsule_"+str(at),capsule_clear(space,at))
				var roof_hit: Dictionary=ray(space,at+Vector3.UP*2.5,at+Vector3.UP*5)
				record("d18_raised_roof_"+str(at),not roof_hit.is_empty() and roof_hit.position.y>=110.1)
				sample_checks+=3
	# All botanical courts contact existing floors and leave their inner bypass open.
	for pocket in plan.botanical_pockets:
		var at:=vec(pocket.origin)
		var side: float=-1.0 if at.x<0 else 1.0
		var route_at:=at-Vector3(side*2.2,0,0)
		var hit: Dictionary=ray(space,route_at+Vector3.UP*.04,route_at-Vector3.UP*.04)
		record("court_retained_floor_"+str(pocket.id),not hit.is_empty() and absf(hit.position.y-at.y)<.002)
		record("court_inner_bypass_capsule_"+str(pocket.id),capsule_clear(space,route_at))
	# One fixture per disconnected terminal; subsequent walking uses the original controller.
	for sign_z in [-1,1]:
		player.global_position=Vector3(0,106.53,511.0*sign_z);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
		for i in range(15):await physics_frame
		for goal in [Vector3(0,106.5,525.0*sign_z),Vector3(0,106.5,511.0*sign_z)]:
			var result: Dictionary=await walk_to(player,goal);route_legs.append(result);record("terminal_original_player_walk_"+str(route_legs.size()),result.reached and result.floor_contact)
	# Existing door family, default closed; normal RMB/E selects and operates each pair.
	var operations: Array=[]
	for row in data.doors:
		var door: Node3D=candidate.get_node(str(row.id));var origin:=vec(row.origin)
		record("door_retained_family_"+str(row.id),door.get_script().resource_path=="res://scripts/service_door.gd" and door.persistent_id==StringName(row.id))
		record("door_closed_default_"+str(row.id),door.open_fraction==0.0 and not door.desired_open)
		var side: float=signf(origin.x)
		player.global_position=Vector3(side*4.7,69.53,origin.z);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
		for i in range(10):await physics_frame
		await aim(player,origin+Vector3(0,2.7,0));record("door_normal_focus_"+str(row.id),player.interaction_target==door)
		await aim(player,origin+Vector3(0,2.7,0))
		await key_e()
		for i in range(90):await physics_frame
		record("door_opened_"+str(row.id),door.desired_open and door.open_fraction>.99)
		await key_e()
		for i in range(90):await physics_frame
		record("door_closed_again_"+str(row.id),not door.desired_open and door.open_fraction<.01)
		operations.append({"id":row.id,"closed_fraction":door.open_fraction,"normal_input":true})
	physical_key(false)
	var light_results: Array=[]
	for row in data.lights:
		var emitter:=vec(row.position)
		var receiver: Vector3
		if str(row.id).contains("Court"):
			var side: float=signf(emitter.x)
			receiver=Vector3(emitter.x-side*.7,emitter.y-1.94,emitter.z)
		elif str(row.id).contains("G7C3_"):
			receiver=Vector3(.6,106.5,emitter.z)
		else:
			receiver=Vector3(emitter.x+signf(emitter.x)*.9,69.5,emitter.z)
		player.global_position=receiver+Vector3.UP*.03;player.velocity=Vector3.ZERO
		for i in range(8):await physics_frame
		var floor_hit: Dictionary=ray(space,receiver+Vector3.UP*.05,receiver-Vector3.UP*.05)
		record("fixture_receiver_floor_"+str(row.id),not floor_hit.is_empty() and absf(floor_hit.position.y-receiver.y)<.003)
		# A straight optical exit from the actual source emitter must reach its
		# retained floor, without hitting its own metal post/housing first.
		var down: Dictionary=ray(space,emitter,Vector3(emitter.x,receiver.y-.05,emitter.z))
		record("fixture_downward_optical_exit_"+str(row.id),not down.is_empty() and absf(down.position.y-receiver.y)<.003)
		budget.refresh()
		var light: SpotLight3D=candidate.get_node(str(row.id))
		record("fixture_actual_budget_admission_"+str(row.id),light.visible and light.shadow_enabled)
		record("fixture_normal_downward_cone_"+str(row.id),(-light.global_basis.z).dot(Vector3.DOWN)>.999)
		light_results.append({"id":row.id,"receiver":str(receiver),"admitted":light.visible and light.shadow_enabled,"down_hit":str(down.get("position",Vector3.INF))})
	var out: Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"retained_mesh_instances_checked":before.size(),"new_models":data.models.size(),"new_lights":data.lights.size(),"door_operations":operations,"terminal_headroom_floor_capsule_samples":sample_checks,"actual_original_player_legs":route_legs,"fixture_light_admission":light_results,"fixture_seeds":6+data.lights.size(),"route_teleports_between_walking_legs":0,"baseline":data.baseline,"acceptance_limits":"Scoped opt-in actual ship candidate. Static worker clearance, normal-input doors and source light exit/admission; no largest-species/cart/permissions/engineering/biology/full-enclosure/final-art/hardware acceptance."}
	FileAccess.open("res://../external_packages/group7_completion_20261011/qa/RUNTIME_CHECK.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  ")+"\n")
	print(JSON.stringify({"status":out.status,"checks":out.checks,"errors":errors,"legs":route_legs.size()}))
	quit(0 if errors.is_empty()else 1)
