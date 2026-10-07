extends RefCounted
# Existing retained counter and workbench, original scale, on the D09 floor.
static func build(parent: Node3D, ship: Node3D, data: Dictionary) -> void:
	assert(data.connected_gallery.length_m == 25.7 and data.furniture.size() == 2)
	assert(parent.get_node_or_null("ConnectedGalleryFurniture") == null)
	var root := Node3D.new()
	root.name = "ConnectedGalleryFurniture"
	parent.add_child(root)
	for entry in data.furniture:
		var spec: Dictionary = data.models[str(entry.asset)]
		assert(spec.existing_retained_runtime_model == true)
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file)) == str(spec.sha256))
		var p: Array = entry.position_xyz
		var item: Node3D = ship.model(root, str(spec.file), str(entry.name), Vector3(p[0],p[1],p[2]), float(entry.yaw_radians))
		assert(item.scale == Vector3.ONE)
		item.set_meta("placement_support", entry.floor_owner)
		item.set_meta("parent_design_id", entry.asset)
		item.set_meta("source_assembly_sha256", data.connected_gallery.source_sha256)
		item.set_meta("static_service_fit_only", true)
	parent.set_meta("scope", "Connected25.7m D09 gallery: orientation garden, curved rest group and market receiving; native art review pending")
	assert(root.get_child_count() == 2)
	load("res://scripts/grand_pool_receiving_stock.gd").build(root,ship,data)
	load("res://scripts/grand_pool_gallery_floor_finish.gd").build(ship,data)
