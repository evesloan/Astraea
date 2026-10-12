extends RefCounted
# Unplaced construction kits. The shared ship root does not call this module.
static func build_source_fixture(parent: Node3D, kit: String) -> Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"),"Actual receiving commons/roof/support adoption is held")
	assert(kit in ["TIDAL","QUIET"])
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_vip_pavilions/KITS_r003.json"))
	var section := Node3D.new()
	section.name = "VIP_SourceKit_" + kit
	parent.add_child(section)
	var visual: Node3D = (load("res://assets/group2_vip_pavilions/VIP_"+kit+"_r003.glb") as PackedScene).instantiate()
	section.add_child(visual)
	var contacts: Array[Node] = []
	for mesh in visual.find_children("*","MeshInstance3D",true,false):
		if "Water_Illustrative" not in str(mesh.name): contacts.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,contacts)
	for row in data.doors:
		if row.kit != kit: continue
		var door: Node3D = load("res://scripts/group2_vip_pavilions/privacy_door.gd").new()
		door.name = row.name
		door.persistent_id = StringName(row.persistent_id)
		door.position = Vector3(row.local_xyz[0],row.local_xyz[1],row.local_xyz[2])
		door.rotation.y = row.yaw
		section.add_child(door)
	for row in data.lights:
		if row.kit != kit: continue
		assert(visual.find_child(str(row.source_mesh).validate_node_name(),true,false) != null)
		var light := OmniLight3D.new()
		light.name = "Fixture_" + str(row.source_mesh)
		light.position = Vector3(row.local_xyz[0],row.local_xyz[1],row.local_xyz[2])
		light.light_color = Color(1,.86,.68)
		light.light_energy = row.energy
		light.omni_range = row.range
		light.shadow_enabled = true
		light.visible = false
		section.add_child(light)
	section.set_meta("production_adoption",false)
	section.set_meta("unresolved_shared_interfaces",data.unresolved_shared_interfaces)
	return section
