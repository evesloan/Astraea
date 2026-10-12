extends "res://tests/group6_completion/validate_water_care.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host)
	var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,host)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor);actor.set_physics_process(false)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();host.add_child(budget);budget.set_process(false)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FIT_CONTRACT.json"))
	actor.global_position=Vector3(64,45.48,230.3)
	for i in range(3):await physics_frame
	budget.configure(host,actor)
	var fittings:Array=[]
	for item in plan.additional_lights:
		var light:Light3D=addition.get_node(str(item.id)+"_PhysicalSource")
		var target:Vector3=light.get_meta("illumination_anchor");var q:=PhysicsRayQueryParameters3D.create(light.global_position,target);q.exclude=[actor.get_rid()]
		var hit:=host.get_world_3d().direct_space_state.intersect_ray(q)
		fittings.append({"id":item.id,"source_xyz":[light.global_position.x,light.global_position.y,light.global_position.z],"receiver_xyz":[target.x,target.y,target.z],"distance_m":light.global_position.distance_to(target),"range_m":light.omni_range if light is OmniLight3D else light.spot_range,"physical_receiver_clear":hit.is_empty(),"blocker":str(hit.collider.get_path()) if not hit.is_empty() else "","block_xyz":[hit.position.x,hit.position.y,hit.position.z] if not hit.is_empty() else []})
	var views:Array=[]
	for spec in [["dry_arrival",Vector3(60.6,44.03,240)],["south_boarding",Vector3(76,45.48,239.6)],["west_rest",Vector3(64.8,45.48,220)],["rinse",Vector3(61.6,45.48,231)],["quiet_court",Vector3(76.2,45.48,217)],["water_care",Vector3(96.8,45.48,210.6)],["launch",Vector3(72,49.38,194.4)]]:
		actor.global_position=spec[1];for i in range(2):await physics_frame
		budget.refresh();var active:Array=[]
		for light:Light3D in budget.sources:
			if light.visible:active.append(str(light.name))
		views.append({"name":spec[0],"independent_sample_xyz":[actor.position.x,actor.position.y,actor.position.z],"active_sources":active,"active_count":active.size()})
	var result:Dictionary={"source":"AquaticCompletion_r018.glb","source_count":budget.sources.size(),"fittings":fittings,"views":views,"scope":"Diagnostic actual local annex, unchanged original source locations, contact geometry and shared budget. Independent optical sample fixtures, not player routes, rendered readability or final lighting acceptance."}
	FileAccess.open("res://docs/group6_completion/LIGHT_DIAGNOSTIC002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 LIGHT DIAGNOSTIC ",budget.sources.size());quit()
