extends RefCounted
# Fitted generic stock/repair furniture under the original shop owner.
static func build(ship:Node3D)->Node3D:
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/THREAD_STOCK_REPAIR.json"))
	assert(FileAccess.get_sha256(str(spec.original_model))==str(spec.original_model_sha256))
	assert(FileAccess.get_sha256(str(spec.model_path))==str(spec.model_sha256))
	var owner:Node3D=ship.find_child("D09_ThreadAndShell_WIP",true,false)
	assert(owner!=null and owner.get_meta("programme_key")==spec.programme_key and owner.get_meta("historical_room_id")==spec.historical_room_id)
	if owner.has_node("Group5ThreadStockAndRepair"):return owner.get_node("Group5ThreadStockAndRepair")
	var root:=Node3D.new();root.name="Group5ThreadStockAndRepair";owner.add_child(root)
	root.set_meta("source_sha256",str(spec.model_sha256))
	root.set_meta("inventory_or_capacity_created",false)
	var model:Node3D=(load(str(spec.model_path)) as PackedScene).instantiate()
	model.name="AuthoredThreadStockRepair";root.add_child(model)
	model.position=Vector3(spec.model_origin_world_xyz[0],spec.model_origin_world_xyz[1],spec.model_origin_world_xyz[2])
	ship._static_contacts(model)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	for item in spec.fixtures:
		var light:=OmniLight3D.new();light.name=str(item.name);root.add_child(light)
		light.global_position=Vector3(item.world_xyz[0],item.world_xyz[1],item.world_xyz[2])
		light.omni_range=float(item.range_m);light.light_energy=float(item.energy)
		light.light_color=Color(item.color[0],item.color[1],item.color[2])
		light.omni_attenuation=1.2;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.shadow_bias=.03;light.shadow_normal_bias=.3
		light.visible=false;light.shadow_enabled=false
		light.set_meta("fixture_powered",true);light.set_meta("source_fixture",str(item.lens))
		light.set_meta("calibration","first_pass_unaccepted")
		budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
	ship.set_meta("group5_thread_stock_attached",true)
	return root
