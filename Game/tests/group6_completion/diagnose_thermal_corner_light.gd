extends "res://tests/group6_completion/validate_water_care.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host);var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for region in data.regions:
		if str(region.id).begins_with("D08_directory_03_"):regions.append(region)
	load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"OriginalMineralFloors")
	var room:Node3D=load("res://assets/models/SOL_D08_directory_03_entry001.glb").instantiate();host.add_child(room);room.set_meta("programme_key","D08_directory_03")
	for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/group6_completion/thermal_entries.gd").build(room);load("res://scripts/group6_completion/thermal_support.gd").build(room);load("res://scripts/group6_completion/thermal_recovery.gd").build(room,true)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor);actor.set_physics_process(false);actor.global_position=Vector3(-25,44.03,-241.5)
	for k in range(3):await physics_frame
	var budget:Node=load("res://scripts/lighting_budget.gd").new();host.add_child(budget);budget.set_process(false);budget.configure(host,actor)
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_RECOVERY_CONTRACT.json"));var matches:Array=definition.rooms[1].optional_existing_fixture_bindings.filter(func(f):return str(f.original_source_mesh).ends_with("spring_light2_lens"))
	if matches.size()!=1:
		print("THERMAL CORNER DIAGNOSTIC HOLD: original fixture identity unresolved");quit(1);return
	var fitting:Dictionary=matches[0];var source:=vec(fitting.source_xyz);var rows:Array=[]
	for target in [vec(fitting.target_xyz),Vector3(source.x,44.04,-239),Vector3(-47,44.04,-241),Vector3(-47,44.04,-239)]:
		var q:=PhysicsRayQueryParameters3D.create(source,target);q.exclude=[actor.get_rid()];var hit:=host.get_world_3d().direct_space_state.intersect_ray(q);var row:Dictionary={"source":fitting.source_xyz,"target":[target.x,target.y,target.z],"clear_by_original_budget":budget._clear_sample(source,target)}
		if not hit.is_empty():
			row["hit"]=str(hit.collider.get_path());row["position"]=[hit.position.x,hit.position.y,hit.position.z];var mesh:MeshInstance3D=hit.collider.get_parent() as MeshInstance3D
			if mesh!=null:
				var m:Material=mesh.get_active_material(0);row["material"]=str(m.resource_name);row["material_class"]=m.get_class();row["transparency"]=m.transparency if m is StandardMaterial3D else -1
		rows.append(row)
	FileAccess.open("res://docs/group6_completion/THERMAL_CORNER_DIAGNOSTIC003.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print("THERMAL CORNER DIAGNOSTIC ",rows);quit()
