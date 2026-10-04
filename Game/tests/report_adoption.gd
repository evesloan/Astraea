extends SceneTree
var instances: Dictionary = {}
func _initialize() -> void: call_deferred("run")
func visit(node: Node) -> void:
	if node.has_meta("catalogue_file"):
		var file: String = node.get_meta("catalogue_file")
		instances[file] = instances.get(file,0)+1
	for child in node.get_children(): visit(child)
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	await process_frame
	visit(main)
	var total := 0
	for count in instances.values(): total += int(count)
	var report := {"source":"Instantiated main scene, not imported-file count", "unique_source_files_instantiated":instances.size(), "instances":total,"by_file":instances,"static_contact_placements":load("res://scripts/static_contact_cache.gd").contacts_created,"shared_static_contact_shapes":load("res://scripts/static_contact_cache.gd").live_shape_count(),"acceptance":"Presence only; does not establish finished rooms, asset quality, or gameplay acceptance"}
	DirAccess.make_dir_recursive_absolute("res://artifacts")
	var file := FileAccess.open("res://artifacts/asset_adoption.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print(JSON.stringify(report))
	main.queue_free()
	await process_frame
	quit(0)
