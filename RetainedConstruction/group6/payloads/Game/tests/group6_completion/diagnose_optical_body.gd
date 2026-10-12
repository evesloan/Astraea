extends "res://tests/group6_completion/validate_water_care.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host);var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host);var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,host)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor);actor.set_physics_process(false)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();host.add_child(budget);budget.set_process(false);actor.global_position=Vector3(59.4,45.48,231)
	for i in range(3):await physics_frame
	budget.configure(host,actor);var rows:Array=[]
	for id in ["rinse_task_0","rinse_task_1"]:
		var light:SpotLight3D=addition.get_node(id+"_PhysicalSource");var target:=actor.global_position+Vector3.UP*.8;var q:=PhysicsRayQueryParameters3D.create(light.global_position,target);q.exclude=[actor.get_rid()];var hit:=host.get_world_3d().direct_space_state.intersect_ray(q)
		rows.append({"id":id,"source":[light.global_position.x,light.global_position.y,light.global_position.z],"active":light.visible,"visible_sample":budget._has_visible_sample(light),"reach":light.spot_range,"cone_degrees":light.spot_angle,"cos_to_body":(-light.global_basis.z).dot((target-light.global_position).normalized()),"blocked":not hit.is_empty(),"blocker":str(hit.collider.get_path()) if not hit.is_empty() else "","block_xyz":[hit.position.x,hit.position.y,hit.position.z] if not hit.is_empty() else []})
	FileAccess.open("res://docs/group6_completion/OPTICAL_BODY_DIAGNOSTIC001.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print(rows);quit()
