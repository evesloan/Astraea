extends RefCounted

# Retained authored homes, using the existing door controllers and immutable
# contact cache. This candidate is not enabled in the default ship.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_UNIT_CANDIDATES.json"))
	var parent := ship.get_node("ShipSpace/Districts")
	assert(parent.get_node_or_null("TidalRoomCandidates") == null)
	var root := Node3D.new()
	root.name = "TidalRoomCandidates"
	root.set_meta("default_scene_enabled", false)
	parent.add_child(root)
	var prototypes: Dictionary = {}
	var scenes: Dictionary = {}
	var local_bounds:Dictionary={}
	for prototype in definition.prototypes:
		var path := "res://assets/models/"+str(prototype.model_file)
		assert(FileAccess.get_sha256(path)==str(prototype.sha256))
		prototypes[str(prototype.key)] = prototype
		scenes[str(prototype.key)] = load(path) as PackedScene
		local_bounds[str(prototype.key)]=load("res://scripts/deferred_home_visual.gd").bounds(scenes[str(prototype.key)])
	var indices: Dictionary = {}
	var identities: Dictionary = {}
	var rest_slots := 0
	for unit in definition.units:
		assert(not indices.has(unit.census_source_index) and not identities.has(unit.rebuild_identity))
		indices[unit.census_source_index] = true
		identities[unit.rebuild_identity] = true
		var room := Node3D.new()
		room.name = str(unit.rebuild_identity)
		var origin: Array = unit.source_origin_world_xyz
		room.position = Vector3(origin[0],origin[1],origin[2])
		room.rotation.y = float(unit.source_yaw_godot)
		room.set_meta("census_source_index",unit.census_source_index)
		room.set_meta("source_identity_status",unit.identity_status)
		room.set_meta("source_recipe",unit.source_recipe_key)
		room.set_meta("source_rest_slots",unit.anchor_bindings)
		room.set_meta("finished",false)
		root.add_child(room)
		var prototype: Dictionary = prototypes[str(unit.source_recipe_key)]
		room.set_meta("deferred_visual_scene",scenes[str(unit.source_recipe_key)])
		load("res://scripts/deferred_home_visual.gd").install_occluder(ship,room,scenes[str(unit.source_recipe_key)])
		room.set_meta("deferred_visual_bounds",local_bounds[str(unit.source_recipe_key)])
		room.set_meta("deferred_visual_meshes",int(prototype.mesh_batches))
		for binding in prototype.doors:
			var entry := str(binding.label)=="EntryDoor"
			assert(str(binding.catalogue_source).ends_with("AST-DOR-002.blend") if entry else str(binding.catalogue_source).ends_with("AST-DOR-001.blend"))
			var door: Node3D = load("res://scripts/guest_entry_door.gd" if entry else "res://scripts/guest_privacy_door.gd").new()
			door.name = str(binding.label)
			door.persistent_id = StringName(str(unit.entry_persistent_id if entry else unit.bath_persistent_id))
			var p: Array = binding.source_xyz
			door.position = Vector3(p[0],p[2],-p[1])
			door.rotation.y = float(binding.source_yaw)
			room.add_child(door)
		rest_slots += unit.anchor_bindings.size()
	assert(root.get_child_count()==85 and rest_slots==221)
	root.set_meta("source_candidate_units",85)
	root.set_meta("source_rest_slots",rest_slots)
	return root
