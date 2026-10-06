extends SceneTree
# Future read-only imported-array probe plus optional isolated sibling build.
# Not run. Requires the separately authorized new-only installation first.
var output := ""
var unit_build := false
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()):
		if args[i] == "--output" and i + 1 < args.size(): output = args[i + 1]
		if args[i] == "--unit-build": unit_build = true
	assert(output.begins_with("/workspace/scratch/375c2e438292/theater_resume/"))
	assert(not FileAccess.file_exists(output + ".json") and not FileAccess.file_exists(output + ".bin"))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/COURT_A_RUNTIME_INCREMENT004.json"))
	var builder = load("res://scripts/court_a_increment004.gd")
	var records: Array = []
	var imports: Dictionary = {}
	var binary := FileAccess.open(output + ".bin", FileAccess.WRITE)
	assert(binary != null)
	for kind in ["authored", "prototype"]:
		var spec: Dictionary = data.files[kind]
		var path := "res://assets/models/" + str(spec.filename)
		assert(FileAccess.get_sha256(path) == str(spec.sha256))
		var policy := ConfigFile.new()
		assert(policy.load(path + ".import") == OK and policy.get_value("params", "meshes/force_disable_compression", false))
		var cache := str(policy.get_value("remap", "path", ""))
		var cache_hash := ConfigFile.new()
		assert(cache_hash.load(cache.get_basename() + ".md5") == OK)
		assert(str(cache_hash.get_value("", "source_md5", "")) == FileAccess.get_md5(path))
		imports[kind] = {"filename": spec.filename, "source_sha256": spec.sha256, "compression_disabled": true, "cache": cache}
		var scene := (load(path) as PackedScene).instantiate() as Node3D
		for item in scene.find_children("*", "MeshInstance3D", true, false):
			var mesh := item as MeshInstance3D
			var local: Transform3D = builder.relative_transform(mesh, scene)
			var normal_basis := local.basis.inverse().transposed()
			for surface in range(mesh.mesh.get_surface_count()):
				var arrays := mesh.mesh.surface_get_arrays(surface)
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
				var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
				var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
				assert(vertices.size() == normals.size() and vertices.size() == uv.size())
				if indices.is_empty():
					for index in range(vertices.size()): indices.append(index)
				assert(indices.size() % 3 == 0)
				var values := PackedFloat32Array()
				for index in indices:
					var p := local * vertices[index]
					var n := (normal_basis * normals[index]).normalized()
					values.append_array(PackedFloat32Array([p.x, p.y, p.z, uv[index].x, uv[index].y, n.x, n.y, n.z]))
				var material := mesh.mesh.surface_get_material(surface)
				var material_record := {"class": material.get_class(), "name": material.resource_name}
				if material is StandardMaterial3D:
					var mat := material as StandardMaterial3D
					material_record["albedo"] = [mat.albedo_color.r, mat.albedo_color.g, mat.albedo_color.b, mat.albedo_color.a]
					material_record["roughness"] = mat.roughness
					material_record["metallic"] = mat.metallic
					material_record["metallic_specular"] = mat.metallic_specular
					material_record["transparency"] = mat.transparency
					material_record["cull_mode"] = mat.cull_mode
				records.append({"kind": kind, "node": str(mesh.name), "surface": surface, "corners": indices.size(), "offset_bytes": binary.get_position(), "material": material_record})
				binary.store_buffer(values.to_byte_array())
		scene.free()
	binary.close()
	var unit: Dictionary = {"run": false}
	if unit_build:
		var parent := Node3D.new()
		root.add_child(parent)
		builder.build(parent, null)
		var court := parent.get_node(str(data.root_name)) as Node3D
		assert(court.get_meta("authored_batches") == 123 and court.get_meta("authored_contacts") == 98 and court.get_meta("furniture_contacts") == 3)
		assert(court.get_meta("source_instance_ids").size() == 24)
		assert(court.find_children("*", "Light3D", true, false).is_empty())
		assert(court.find_children("*", "MeshInstance3D", true, false).size() == 123)
		var faces: Array = []
		for node in court.find_children("*", "CollisionShape3D", true, false):
			var shape := (node as CollisionShape3D).shape as ConcavePolygonShape3D
			assert(shape != null)
			var returned := shape.get_faces() # Deliberate PHYSICS storage readback, not render/source extraction.
			var digest := HashingContext.new()
			digest.start(HashingContext.HASH_SHA256)
			digest.update(returned.to_byte_array())
			var actual := digest.finish().hex_encode()
			faces.append({"identity": node.get_parent().get_meta("court_source_identity"), "input_corners": shape.get_meta("court_raw_input_corners"), "returned_corners": returned.size(), "input_sha256": shape.get_meta("court_raw_input_sha256"), "returned_sha256": actual, "exact_input_storage": actual == shape.get_meta("court_raw_input_sha256")})
		assert(faces.size() == 101)
		unit = {"run": true, "placements": 24, "authored_batches": 123, "contact_bodies": 101, "shape_storage": faces, "actual_rays_routes_and_old_subtree_preservation_tested": false}
		parent.free()
	var result := {"status": "CAPTURED_IMPORT_ARRAYS_REQUIRES_INDEPENDENT_CHECK", "imports": imports, "records": records, "binary_sha256": FileAccess.get_sha256(output + ".bin"), "court_origin_native": data.court_origin_native, "unit_build": unit, "native_art_lighting_acceptance": false}
	var receipt := FileAccess.open(output + ".json", FileAccess.WRITE)
	receipt.store_string(JSON.stringify(result, "\t"))
	receipt.close()
	print("COURT IMPORT PROBE: ", records.size(), " surfaces; no route/lighting acceptance")
	quit(0)
