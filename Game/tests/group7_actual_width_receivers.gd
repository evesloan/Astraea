extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r008/"
	var paths: Array = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/OCCLUDER_PATHS.json"))
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var rows: Array = []
	var missing: Array = []
	for i in range(paths.size()):
		var node: Node = root.get_node_or_null(NodePath(paths[i]))
		if not node is MeshInstance3D:
			missing.append(paths[i])
			continue
		var mesh: MeshInstance3D = node
		var local_faces: PackedVector3Array = mesh.mesh.get_faces()
		var faces := PackedVector3Array()
		faces.resize(local_faces.size())
		for j in range(local_faces.size()): faces[j] = mesh.global_transform * local_faces[j]
		var filename: String = "mesh_%04d.tri.f32" % i
		FileAccess.open(directory + "qa/occluders/" + filename, FileAccess.WRITE).store_buffer(faces.to_byte_array())
		var ancestors: Array = []
		var parent: Node = mesh.get_parent()
		for j in range(3):
			if parent == null: break
			ancestors.append({"name": str(parent.name), "scene_file_path": parent.scene_file_path, "extras": parent.get_meta("extras", {})})
			parent = parent.get_parent()
		rows.append({"path": paths[i], "filename": filename, "triangles": faces.size() / 3, "mesh_resource_path": mesh.mesh.resource_path, "extras": mesh.get_meta("extras", {}), "ancestors": ancestors, "visible": mesh.visible, "world_transform": str(mesh.global_transform)})
	var report: Dictionary = {"status": "PASS" if missing.is_empty() else "HOLD_MISSING_TARGETS", "meshes": rows, "missing": missing, "geometry_format": "little-endian float32 XYZ, three vertices per triangle", "baseline": "affc5c807087ff87da29f3642c2d6e418241b896", "read_only_source_scene": true, "group7_candidate_instantiated": false, "protected_sources_edited": false}
	FileAccess.open(directory + "qa/ACTUAL_OCCLUDERS.json", FileAccess.WRITE).store_string(JSON.stringify(report, "  ") + "\n")
	print(JSON.stringify({"status": report.status, "meshes": rows.size(), "missing": missing}))
	quit(0 if missing.is_empty() else 1)
