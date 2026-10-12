extends RefCounted
# Original seven gallery fixtures,two supported recess fixtures and an existing-opening slider.
static func build(ship:Node3D)->Node3D:
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/MAKER_CONSTRUCTION.json"))
	assert(FileAccess.get_sha256(str(spec.original_model))==str(spec.original_model_sha256))
	assert(FileAccess.get_sha256(str(spec.foyer_source.model_path))==str(spec.foyer_source.model_sha256))
	assert(FileAccess.get_sha256(str(spec.door.model_path))==str(spec.door.model_sha256))
	var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,str(spec.programme_key))
	assert(owner!=null and owner.position==Vector3.ZERO)
	if owner.has_node("Group5MakerConstruction"):return owner.get_node("Group5MakerConstruction")
	var root:=Node3D.new();root.name="Group5MakerConstruction";owner.add_child(root)
	if spec.has("ceiling_enclosure"):
		var enclosure:Dictionary=spec.ceiling_enclosure
		assert(FileAccess.get_sha256(str(enclosure.model_path))==str(enclosure.model_sha256))
		var ceiling:Node3D=load(str(enclosure.model_path)).instantiate();ceiling.name="AuthoredMakerCeilingEnclosure";root.add_child(ceiling)
		ceiling.position=Vector3(enclosure.origin_world_xyz[0],enclosure.origin_world_xyz[1],enclosure.origin_world_xyz[2])
		ship._static_contacts(ceiling)
	var foyer:Node3D=load(str(spec.foyer_source.model_path)).instantiate();foyer.name="AuthoredMakerFoyerSources";root.add_child(foyer)
	foyer.position=Vector3(spec.foyer_source.origin_world_xyz[0],spec.foyer_source.origin_world_xyz[1],spec.foyer_source.origin_world_xyz[2])
	ship._static_contacts(foyer)
	var door:=Node3D.new();door.name=str(spec.door.door_name);door.set_script(load("res://scripts/group5_retail_slider.gd"))
	door.persistent_id=StringName(str(spec.door.physical_id));door.width=float(spec.door.width);door.height=float(spec.door.height)
	door.model_path=str(spec.door.model_path);door.controls=spec.door.controls
	door.position=Vector3(spec.door.world_xyz[0],spec.door.world_xyz[1],spec.door.world_xyz[2]);door.rotation.y=float(spec.door.rotation_y);root.add_child(door)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	for item in spec.fixtures:
		var lens:MeshInstance3D=owner.find_child(str(item.source_mesh),true,false);assert(lens!=null)
		var light:=OmniLight3D.new();light.name=str(item.name);root.add_child(light)
		light.position=Vector3(item.world_xyz[0],item.world_xyz[1],item.world_xyz[2])
		light.light_color=Color(item.color[0],item.color[1],item.color[2]);light.light_energy=float(item.energy);light.omni_range=float(item.range_m)
		light.omni_attenuation=1.2;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;light.shadow_bias=.03;light.shadow_normal_bias=.3
		light.visible=false;light.shadow_enabled=false;light.set_meta("fixture_powered",true);light.set_meta("source_fixture",str(item.source_mesh));light.set_meta("calibration","first_pass_unaccepted")
		budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
	ship.set_meta("group5_maker_construction_attached",true)
	return root
