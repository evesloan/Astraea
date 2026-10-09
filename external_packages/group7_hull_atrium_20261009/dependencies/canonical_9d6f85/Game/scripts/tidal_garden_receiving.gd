extends RefCounted

# Retained source architecture only. Explicitly invoked for receiving validation;
# not enabled in the main ship until adjacent support and route gates pass.
static func build(ship: Node3D, definition_path: String = "res://data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json") -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(definition_path))
	var path := "res://assets/models/" + str(definition.model_file)
	assert(FileAccess.get_sha256(path) == str(definition.source_sha256))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == str(definition.preserved_compiled_floor_sha256))
	var parent := ship.get_node("ShipSpace/Districts")
	assert(parent.get_node_or_null("TidalGardenReceivingCandidate") == null)
	var house := Node3D.new()
	house.name = "TidalGardenReceivingCandidate"
	house.set_meta("source_only_interiors", 85)
	house.set_meta("installed_guest_units", 0)
	house.set_meta("acceptance", "receiving_validation_pending")
	parent.add_child(house)
	var visual := (load(path) as PackedScene).instantiate()
	house.add_child(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_specialty.gd").patch_frontage(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_specialty_batch.gd").patch_frontage(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_aquatic_singles.gd").patch_frontage(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_aquatic_double.gd").patch_frontage(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_low_nest_singles.gd").patch_frontage(visual)
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")!="1":load("res://scripts/tidal_quiet_doubles.gd").patch_frontage(visual)
	var meshes := visual.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == int(definition.mesh_count))
	var contacts := 0
	for part: MeshInstance3D in meshes:
		var source: Dictionary = part.get_meta("extras", {})
		assert(source.has("category") and source.has("runtime_collision"), "Retain source collision semantics")
		assert(str(source.source_plan_sha256) == str(definition.plan_sha256))
		if bool(source.runtime_collision):
			load("res://scripts/static_contact_cache.gd").attach(part)
			contacts += 1
	house.set_meta("source_contact_count", contacts)
	var transfer: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_HORIZON_TRANSFER_CANDIDATE.json"))
	var transfer_path := "res://assets/models/" + str(transfer.model_file)
	assert(FileAccess.get_sha256(transfer_path) == str(transfer.export_sha256))
	assert(FileAccess.get_sha256("res://assets/models/SOL_D12_directory_01_entry001.glb") == str(transfer.source_pins["Game/assets/models/SOL_D12_directory_01_entry001.glb"]))
	var receiving: Node3D = (load(transfer_path) as PackedScene).instantiate()
	receiving.name = "HorizonTransferCandidate"
	house.add_child(receiving)
	var transfer_meshes := receiving.find_children("*", "MeshInstance3D", true, false)
	assert(transfer_meshes.size() == int(transfer.source_part_count))
	for part: MeshInstance3D in transfer_meshes:
		load("res://scripts/static_contact_cache.gd").attach(part)
	house.set_meta("horizon_contact_geometry", "48 source contact checks passed; no load certification")
	house.set_meta("listening_transfer", "pending")
	var source_assets := Node3D.new()
	source_assets.name = "RetainedLandscapeAndSeating"
	house.add_child(source_assets)
	var asset_scenes: Dictionary = {}
	for catalogue_id in definition.retained_asset_definitions:
		var asset: Dictionary = definition.retained_asset_definitions[catalogue_id]
		var asset_path := "res://assets/models/"+str(asset.model_file)
		assert(FileAccess.get_sha256(asset_path)==str(asset.sha256))
		asset_scenes[catalogue_id] = load(asset_path) as PackedScene
	for item in definition.retained_asset_instances:
		var placed := Node3D.new()
		placed.name = str(item.name)
		var p: Array = item.world_xyz
		placed.position = Vector3(p[0],p[1],p[2])
		placed.rotation.y = deg_to_rad(float(item.yaw))
		placed.scale = Vector3.ONE * float(item.scale)
		placed.set_meta("catalogue_id",item.catalogue_id)
		placed.set_meta("source_purpose",item.purpose)
		source_assets.add_child(placed)
		var asset_visual: Node3D = (asset_scenes[item.catalogue_id] as PackedScene).instantiate()
		placed.add_child(asset_visual)
		# Preserve the production model builder's botanical collision policy.
		if not str(item.catalogue_id).begins_with("AST-BOT"):
			for mesh: MeshInstance3D in asset_visual.find_children("*","MeshInstance3D",true,false):
				load("res://scripts/static_contact_cache.gd").attach(mesh)
	assert(source_assets.get_child_count()==81)
	return house
