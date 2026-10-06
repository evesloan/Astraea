extends SceneTree
# Parent serial slot only. Read actual retained main ship before theater adoption.
# No source import/export/copy, registry/controller changes or render. Output only
# to an explicitly supplied package/scratch JSON path.
var started := 0
var target: AABB
var mesh_count := 0
var mesh_candidates := 0
var triangle_count := 0
var collision_count := 0
var failures: Array[Dictionary] = []
var collision_candidates: Array[Dictionary] = []
var unhandled_geometry: Array[Dictionary] = []
var import_pins: Dictionary = {}
var import_failures: Array[Dictionary] = []
var package_dir := "/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section"
var output_path := ""

func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec() - started > 180000:
		push_error("Theater retained-neighbour census exceeded180-second watchdog")
		quit(1)
	return false

func values(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func bbox(a: AABB) -> Dictionary:
	return {"min": values(a.position), "max": values(a.end)}

func world_bounds(local: AABB, transform: Transform3D) -> AABB:
	var a := AABB(transform * local.get_endpoint(0), Vector3.ZERO)
	for i in range(1, 8):
		a = a.expand(transform * local.get_endpoint(i))
	return a

func census_mesh(mesh: Mesh, transform: Transform3D, path: String) -> void:
	mesh_count += 1
	if mesh == null:
		unhandled_geometry.append({"node": path, "issue": "Missing mesh"})
		return
	var bounds := world_bounds(mesh.get_aabb(), transform)
	if not target.intersects(bounds):
		return
	mesh_candidates += 1
	var faces: PackedVector3Array = mesh.get_faces()
	triangle_count += int(faces.size() / 3)
	var candidates := 0
	var exact_triangles: Array = []
	for i in range(0, faces.size(), 3):
		var tri := AABB(transform * faces[i], Vector3.ZERO)
		tri = tri.expand(transform * faces[i + 1])
		tri = tri.expand(transform * faces[i + 2])
		if target.intersects(tri.grow(0.00001)):
			candidates += 1
			exact_triangles.append([values(transform * faces[i]), values(transform * faces[i + 1]), values(transform * faces[i + 2])])
	if candidates > 0:
		failures.append({"node": path, "world_bounds": bbox(bounds), "triangle_aabb_candidates": candidates, "exact_candidate_triangles_world": exact_triangles, "meaning": "Candidate requires exact contact review; not an automatic confirmed collision"})

func pin_import(node: Node) -> void:
	if not node.has_meta("catalogue_file"):
		return
	var filename := str(node.get_meta("catalogue_file"))
	if import_pins.has(filename):
		return
	var path := "res://assets/models/" + filename
	var config := ConfigFile.new()
	if config.load(path + ".import") != OK:
		import_failures.append({"file": filename, "reason": "Missing import receipt"})
		return
	var imported: String = config.get_value("remap", "path", "")
	var cache := ConfigFile.new()
	if imported.is_empty() or cache.load(imported.get_basename() + ".md5") != OK:
		import_failures.append({"file": filename, "reason": "Missing imported resource/source md5"})
		return
	var expected := FileAccess.get_md5(path)
	var actual := str(cache.get_value("", "source_md5", ""))
	if actual != expected:
		import_failures.append({"file": filename, "reason": "Stale geometry import", "source_md5": expected, "cache_source_md5": actual})
	import_pins[filename] = {"source_sha256": FileAccess.get_sha256(path), "cache_source_md5": actual, "current_source_md5": expected}

func visit(node: Node) -> void:
	pin_import(node)
	if node is MeshInstance3D:
		var item := node as MeshInstance3D
		census_mesh(item.mesh, item.global_transform, str(item.get_path()))
	elif node is MultiMeshInstance3D:
		var item := node as MultiMeshInstance3D
		if item.multimesh != null and item.multimesh.mesh != null:
			var count := item.multimesh.instance_count
			if item.multimesh.visible_instance_count >= 0:
				count = mini(count, item.multimesh.visible_instance_count)
			for i in range(count):
				census_mesh(item.multimesh.mesh, item.global_transform * item.multimesh.get_instance_transform(i), str(item.get_path()) + "::instance_" + str(i))
		else:
			unhandled_geometry.append({"node": str(item.get_path()), "issue": "Missing MultiMesh resource"})
	elif node is CSGShape3D:
		unhandled_geometry.append({"node": str(node.get_path()), "issue": "CSG needs separate final mesh census"})
	if node is CollisionShape3D:
		var item := node as CollisionShape3D
		if not item.disabled and item.shape != null:
			collision_count += 1
			var debug_mesh: ArrayMesh = item.shape.get_debug_mesh()
			if debug_mesh != null:
				var bounds := world_bounds(debug_mesh.get_aabb(), item.global_transform)
				if target.intersects(bounds):
					var hits := -1
					var exact_collision_triangles: Array = []
					if item.shape is ConcavePolygonShape3D:
						hits = 0
						var faces: PackedVector3Array = (item.shape as ConcavePolygonShape3D).get_faces()
						for i in range(0, faces.size(), 3):
							var tri := AABB(item.global_transform * faces[i], Vector3.ZERO)
							tri = tri.expand(item.global_transform * faces[i + 1])
							tri = tri.expand(item.global_transform * faces[i + 2])
							if target.intersects(tri.grow(0.00001)):
								hits += 1
								exact_collision_triangles.append([values(item.global_transform * faces[i]), values(item.global_transform * faces[i + 1]), values(item.global_transform * faces[i + 2])])
					if hits != 0:
						collision_candidates.append({"node": str(item.get_path()), "shape_class": item.shape.get_class(), "world_bounds": bbox(bounds), "triangle_aabb_candidates": hits, "exact_candidate_triangles_world": exact_collision_triangles, "meaning": "Conservative bound candidate; require exact shape/triangle reconciliation"})
	for child in node.get_children():
		visit(child)

func run() -> void:
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()):
		if args[i] == "--package" and i + 1 < args.size():
			package_dir = args[i + 1]
		if args[i] == "--output" and i + 1 < args.size():
			output_path = args[i + 1]
	assert(not output_path.is_empty(), "Explicit output path required; no default shared write")
	assert(not FileAccess.file_exists(output_path), "Preserve earlier census output")
	var source_path := package_dir + "/source/geometry.json"
	var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source_path))
	var first := true
	for item in geometry.objects:
		if str(item.role) == "preview_only":
			continue
		for point in item.vertices_world:
			var v := Vector3(point[0], point[1], point[2])
			if first:
				target = AABB(v, Vector3.ZERO)
				first = false
			else:
				target = target.expand(v)
	# Include the approved fixed foundation depth without adding a floor.
	target = target.expand(Vector3(target.position.x, minf(target.position.y, 69.26), target.position.z))
	# Bounded receiving route plus fore-spine terminal bearing/guard context.
	target = AABB(Vector3(-34.02, 68.50, -129.10), Vector3(31.22, 5.35, 6.20))
	var ship: Node3D = load("res://scenes/ship.tscn").instantiate()
	root.add_child(ship)
	await process_frame
	await physics_frame
	await physics_frame
	visit(ship)
	var pins: Dictionary = {}
	for filename in DirAccess.get_files_at("res://scripts"):
		if filename.ends_with(".gd"):
			pins["scripts/" + filename] = FileAccess.get_sha256("res://scripts/" + filename)
	var report := {"status": "Actual D11 receiving-bridge and fore-spine terminal candidate geometry; intended contacts still require exact classification", "geometry_sha256": FileAccess.get_sha256(source_path), "compiled_slabs_sha256": FileAccess.get_sha256("res://data/generated/structural_meshes.json"), "runtime_script_pins": pins, "model_import_pins": import_pins, "stale_or_missing_imports": import_failures, "theater_query_bounds": bbox(target), "meshes_checked": mesh_count, "mesh_aabb_candidates": mesh_candidates, "candidate_mesh_triangles_checked": triangle_count, "render_triangle_candidates": failures, "collision_shapes_checked": collision_count, "collision_bound_candidates": collision_candidates, "unhandled_geometry": unhandled_geometry, "no_theater_import_or_install": true, "limits": ["Zero candidates establish exclusion at this recorded state only", "Nonempty bounds need exact contact classification", "No future cabin/gate sweep, exterior connector, structural or route acceptance"]}
	var file := FileAccess.open(output_path, FileAccess.WRITE)
	assert(file != null)
	file.store_string(JSON.stringify(report, "\t") + "\n")
	print("THEATER D11 BRIDGE RECEIVER CENSUS: meshes=", mesh_count, " render_candidates=", failures.size(), " collision_candidates=", collision_candidates.size(), " unhandled=", unhandled_geometry.size())
	quit(0 if failures.is_empty() and collision_candidates.is_empty() and unhandled_geometry.is_empty() and import_failures.is_empty() else 1)
