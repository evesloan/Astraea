extends RefCounted
# Bounded D14 house-side service receiving. Staff shaft/upper stops remain closed.
const DATA := "res://data/architecture/TIDAL_D14_SERVICE_RECEIVING.json"

static func build(ship: Node3D, house: Node3D) -> Node3D:
	var existing := house.get_node_or_null("TidalD14ServiceReceiving") as Node3D
	if existing != null: return existing
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	assert(FileAccess.get_sha256("res://assets/models/"+str(d.original_street_file)) == str(d.original_street_sha256))
	for item in d.model_bindings:
		assert(FileAccess.get_sha256("res://assets/models/"+str(item.file)) == str(item.sha256))
	var group := Node3D.new()
	group.name = str(d.root_name)
	group.set_meta("persistent_id",str(d.persistent_id))
	group.set_meta("acceptance","installed_d14_receiving_wip")
	group.set_meta("upper_staff_lift_enabled",false)
	group.set_meta("abandoned_west_mouths_physically_closed",true)
	group.set_meta("flow_use","sequential_sealed_load_shared_portal")
	group.set_meta("simultaneous_segregation_accepted",false)
	group.set_meta("structural_load_capacity_accepted",false)
	house.add_child(group)
	var corridor: Node3D = load("res://assets/models/"+str(d.corridor_file)).instantiate()
	corridor.name = "RetainedD14CorridorClosedShaft"
	group.add_child(corridor)
	var visual: Node3D = load("res://assets/models/"+str(d.receiver_file)).instantiate()
	visual.name = "D14SharedHouseReceiver"
	group.add_child(visual)
	# The source patch has world-baked vertices. Copy both mesh and actual world
	# transform so the translated street endguard is not translated a second time.
	var patch: Node3D = load("res://assets/models/"+str(d.patch_file)).instantiate()
	patch.name = "TemporaryExactNamedPatch"
	group.add_child(patch)
	for item in d.named_replacements:
		var owner: Node3D = corridor if str(item.owner) == "new_d14_corridor" else ship.get_node("ShipSpace/Districts/TidalD14SouthStreetExtension")
		var target := owner.find_child(str(item.mesh),true,false) as MeshInstance3D
		var replacement := patch.find_child(str(item.mesh),true,false) as MeshInstance3D
		assert(target != null and replacement != null)
		var old := target.get_node_or_null("StaticContact")
		if str(item.owner) == "existing_d14_street": assert(old != null)
		if old != null:
			target.remove_child(old)
			old.free()
		target.mesh = replacement.mesh
		target.global_transform = replacement.global_transform
		target.set_meta("tidal_d14_shared_service_opening",true)
		if str(item.owner) == "existing_d14_street": load("res://scripts/static_contact_cache.gd").attach(target)
	patch.free()
	var corridor_meshes := corridor.find_children("*","MeshInstance3D",true,false)
	var receiver_meshes := visual.find_children("*","MeshInstance3D",true,false)
	assert(corridor_meshes.size() == int(d.corridor_mesh_count) and receiver_meshes.size() == int(d.receiver_mesh_count))
	for mesh: MeshInstance3D in corridor_meshes+receiver_meshes:
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	# The compact receiver export owns its missing-only link floor. Only the
	# separate retained approach is generated here, with no duplicated link floor.
	load("res://scripts/structural_floor_builder.gd").build_regions(group,ship.stone,ship.ivory,d.approach_floor_regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"D14MissingOnlyServiceApproach")
	var item: Dictionary = d.door
	var door: Node3D = load("res://scripts/service_door.gd").new()
	door.name = str(item.name)
	door.persistent_id = StringName(str(item.persistent_id))
	door.position = Vector3(item.position[0],item.position[1],item.position[2])
	door.rotation.y = float(item.yaw)
	group.add_child(door)
	assert(door.scale == Vector3.ONE and door.leaves.size() == 2)
	var lights: Array[Light3D] = []
	for fixture in d.fixtures:
		var source: Node3D = corridor if str(fixture.visual_owner) == "corridor" else visual
		var marker := source.find_child(str(fixture.marker),true,false) as Node3D
		assert(marker != null)
		var light := OmniLight3D.new()
		light.name = str(fixture.name)
		group.add_child(light)
		light.global_position = marker.global_position
		light.light_color = Color(fixture.color[0],fixture.color[1],fixture.color[2])
		light.light_energy = float(fixture.energy)
		light.omni_range = float(fixture.range_m)
		light.omni_attenuation = 1.0
		light.shadow_enabled = true
		light.set_meta("fixture_powered",true)
		light.set_meta("source_marker",str(fixture.marker))
		light.set_meta("source_visual_owner",str(fixture.visual_owner))
		light.set_meta("calibration","bounded_initial_unaccepted")
		lights.append(light)
	assert(lights.size() == 8)
	var budget := ship.get_node("ShipSystems/LocalShadowSourceBudget")
	if is_instance_valid(budget.actor): load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	group.set_meta("physical_fixture_light_count",lights.size())
	group.set_meta("corridor_mesh_count",corridor_meshes.size())
	group.set_meta("receiver_mesh_count",receiver_meshes.size())
	group.set_meta("named_replacement_count",d.named_replacements.size())
	return group
