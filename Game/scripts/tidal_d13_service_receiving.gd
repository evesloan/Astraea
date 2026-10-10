extends RefCounted
# Bounded D13 house-side receiving only. No upper staff lift or extra guest units.
const DATA := "res://data/architecture/TIDAL_D13_SERVICE_RECEIVING.json"

static func build(ship: Node3D, house: Node3D) -> Node3D:
	var existing := house.get_node_or_null("TidalD13ServiceReceiving") as Node3D
	if existing != null: return existing
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	assert(FileAccess.get_sha256("res://assets/models/AST-RES-TIDAL_lift_fit_r003.glb") == str(d.original_house_sha256))
	for pair in [[d.model_file,d.model_sha256],[d.guard_patch_file,d.guard_patch_sha256]]:
		assert(FileAccess.get_sha256("res://assets/models/"+str(pair[0])) == str(pair[1]))
	var group := Node3D.new()
	group.name = str(d.root_name)
	group.set_meta("persistent_id",str(d.persistent_id))
	group.set_meta("acceptance","installed_d13_receiving_wip")
	group.set_meta("upper_staff_lift_enabled",false)
	group.set_meta("upper_d14_d17_held",true)
	group.set_meta("no_new_guest_units",true)
	house.add_child(group)
	# Only these two unaffected prior batches are replaced. Refresh their existing
	# static contacts, rather than leaving collisions from the old continuous rail.
	var patch: Node3D = load("res://assets/models/"+str(d.guard_patch_file)).instantiate()
	for item in d.guard_replacement_map:
		var target := house.find_child(str(item.batch),true,false) as MeshInstance3D
		var replacement := patch.find_child(str(item.batch),true,false) as MeshInstance3D
		assert(target != null and replacement != null)
		assert(target.get_meta("extras",{}).category in ["guard","public_glass"])
		var old_contact := target.get_node_or_null("StaticContact")
		assert(old_contact != null)
		target.remove_child(old_contact)
		old_contact.free()
		target.mesh = replacement.mesh
		target.set_meta("tidal_d13_service_guard_openings",2)
		load("res://scripts/static_contact_cache.gd").attach(target)
	patch.free()
	var visual: Node3D = load("res://assets/models/"+str(d.model_file)).instantiate()
	visual.name = "RetainedD13CorridorAndReceiving"
	group.add_child(visual)
	var meshes := visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size() == int(d.mesh_count))
	for mesh: MeshInstance3D in meshes:
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/structural_floor_builder.gd").build_regions(group,ship.stone,ship.ivory,d.floor_regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"D13MissingOnlyApproachAndThresholds")
	for item in d.doors:
		var door: Node3D = load("res://scripts/service_door.gd").new()
		door.name = str(item.name)
		door.persistent_id = StringName(str(item.persistent_id))
		door.position = Vector3(item.position[0],item.position[1],item.position[2])
		door.rotation.y = float(item.yaw)
		group.add_child(door)
		assert(door.scale == Vector3.ONE)
		assert(door.leaves.size() == 2)
	var lights: Array[Light3D] = []
	for item in d.fixtures:
		var marker := visual.find_child(str(item.name),true,false) as Node3D
		assert(marker != null)
		var light := OmniLight3D.new()
		light.name = str(item.name)+"_PhysicalSource"
		group.add_child(light)
		light.global_position = marker.global_position
		light.light_color = Color(item.color[0],item.color[1],item.color[2])
		light.light_energy = float(item.energy)
		light.omni_range = float(item.range_m)
		light.omni_attenuation = 1.0
		light.shadow_enabled = true
		light.set_meta("fixture_powered",true)
		light.set_meta("source_marker",str(item.name))
		light.set_meta("calibration","bounded_initial_unaccepted")
		lights.append(light)
	assert(lights.size() == int(d.fixture_count))
	var budget := ship.get_node("ShipSystems/LocalShadowSourceBudget")
	# During normal adoption the existing configure() below house assembly discovers
	# them once. A later explicit installation uses the established adapter instead.
	if is_instance_valid(budget.actor):
		load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	group.set_meta("physical_fixture_light_count",lights.size())
	group.set_meta("source_mesh_count",meshes.size())
	return group
