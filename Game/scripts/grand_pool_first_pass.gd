extends RefCounted
# Additive furnishing only. Existing section geometry, fixtures and routes remain owned.
const CONTRACT := "res://data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json"

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.placements.size() == 51 and data.models.size() == 10)
	assert(parent.get_node_or_null("GrandPoolFirstPassEssentials_WIP") == null)
	for key in data.models:
		var model: Dictionary = data.models[key]
		assert(FileAccess.get_sha256("res://assets/models/" + str(model.file)) == str(model.sha256), "Retained Grand Pool export identity changed: " + str(model.file))
	var root := Node3D.new()
	root.name = "GrandPoolFirstPassEssentials_WIP"
	root.set_meta("persistent_id", "grand_pool_first_pass_essentials_001")
	root.set_meta("programme_keys", data.programme_ids)
	root.set_meta("source_assembly_sha256", data.source_assembly_sha256)
	root.set_meta("scope", "Source-backed static furnishing; wall/ceiling/light/sign completion, operated stock and occupied use unfinished")
	parent.add_child(root)
	for entry in data.placements:
		var p: Array = entry.position_xyz
		var item: Node3D = ship.model(root, str(entry.model_file), str(entry.name), Vector3(p[0],p[1],p[2]), float(entry.yaw_radians))
		item.set_meta("persistent_id", "grand_pool_" + str(entry.name) + "_001")
		item.set_meta("placement_support", entry.support)
		item.set_meta("retained_asset_role", entry.asset)
		item.set_meta("programme_key", "D08_directory_01" if float(p[1]) < 52.5 else "D09_directory_01")
		# The shared model loader gives non-botanical exports cached exact per-mesh
		# concave contacts. Their disconnected semantic pieces remain a compound;
		# never convexify the complete furniture/niche and fill its useful openings.
		# Pots require physical contacts even though foliage intentionally does not.
		if str(entry.asset) == "pot": ship._static_contacts(item)
		item.set_meta("collision_contract", data.models[str(entry.asset)].collision)
	assert(root.get_child_count() == 51)
	assert(root.find_children("*", "Light3D", true, false).is_empty(), "Furnishings do not add uncoordinated light sources")
