extends RefCounted
# Bounded source-backed optic adoption. Original assets and shared resources stay immutable.
const CONTRACT := "res://data/architecture/COURT_A_AIMED_OPTIC008.json"
const SOURCE_SHA256 := "c252539361fa2454e919b85cb5e357eb75a329b8724f2c311101a936206996b8"
const GLB_SHA256 := "9e62faa88311b58c644c77b2008c0728b25ab6c370c8cdb5f9159692e2940bca"

static func _vector(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))

static func _sha(bytes: PackedByteArray) -> String:
	var digest := HashingContext.new()
	var status := digest.start(HashingContext.HASH_SHA256)
	assert(status == OK)
	status = digest.update(bytes)
	assert(status == OK)
	return digest.finish().hex_encode()

static func _native_transform(node: Node3D, parent: Node3D) -> Transform3D:
	# The contract uses Districts-local ship coordinates, independent of ship world pose.
	var result := node.transform
	var cursor := node.get_parent()
	while cursor != parent:
		assert(cursor != null and cursor is Node3D)
		result = (cursor as Node3D).transform * result
		cursor = cursor.get_parent()
	return result

static func _in_lens(point: Vector3, spec: Dictionary) -> bool:
	var lo := _vector(spec.bounds_min_native)
	var hi := _vector(spec.bounds_max_native)
	var epsilon: float = spec.selection_epsilon_m
	return point.x >= lo.x - epsilon and point.y >= lo.y - epsilon and point.z >= lo.z - epsilon and point.x <= hi.x + epsilon and point.y <= hi.y + epsilon and point.z <= hi.z + epsilon

static func _raw_faces(mesh: Mesh) -> PackedVector3Array:
	assert(mesh is ArrayMesh)
	var faces := PackedVector3Array()
	for surface in range(mesh.get_surface_count()):
		assert((mesh as ArrayMesh).surface_get_primitive_type(surface) == Mesh.PRIMITIVE_TRIANGLES)
		var arrays: Array = mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		assert(not vertices.is_empty())
		if indices.is_empty():
			assert(vertices.size() % 3 == 0)
			faces.append_array(vertices)
		else:
			assert(indices.size() % 3 == 0)
			for index in indices:
				assert(index >= 0 and index < vertices.size())
				faces.append(vertices[index])
	return faces

static func _prepare_replacement(old_node: MeshInstance3D, parent: Node3D, spec: Dictionary) -> Dictionary:
	# Proven triangle-only filter: never write into the imported shared Mesh or Shape.
	assert(old_node != null and old_node.mesh is ArrayMesh)
	var original := old_node.mesh as ArrayMesh
	assert(original.get_surface_count() == 1 and original.surface_get_primitive_type(0) == Mesh.PRIMITIVE_TRIANGLES)
	var original_arrays: Array = original.surface_get_arrays(0)
	var original_bytes := var_to_bytes(original_arrays)
	var indices: PackedInt32Array = original_arrays[Mesh.ARRAY_INDEX]
	var vertices: PackedVector3Array = original_arrays[Mesh.ARRAY_VERTEX]
	assert(indices.size() == int(spec.original_triangles) * 3)
	var placement := _native_transform(old_node, parent)
	var kept := PackedInt32Array()
	var removed := PackedVector3Array()
	for triangle in range(int(spec.original_triangles)):
		var belongs := true
		for corner in range(3):
			belongs = belongs and _in_lens(placement * vertices[indices[triangle * 3 + corner]], spec)
		for corner in range(3):
			var index: int = indices[triangle * 3 + corner]
			if belongs:
				removed.append(placement * vertices[index])
			else:
				kept.append(index)
	assert(removed.size() == int(spec.removed_triangles) * 3 and kept.size() == int(spec.retained_triangles) * 3)
	var filtered: Array = original_arrays.duplicate(true)
	filtered[Mesh.ARRAY_INDEX] = kept
	var replacement := ArrayMesh.new()
	replacement.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, filtered)
	replacement.surface_set_material(0, original.surface_get_material(0))
	replacement.surface_set_name(0, original.surface_get_name(0))
	var stored: Array = replacement.surface_get_arrays(0)
	assert(stored[Mesh.ARRAY_INDEX].to_byte_array() == kept.to_byte_array())
	for slot in range(Mesh.ARRAY_MAX):
		if slot != Mesh.ARRAY_INDEX:
			assert(var_to_bytes(stored[slot]) == var_to_bytes(original_arrays[slot]), "Unchanged old render attribute differs")
	assert(var_to_bytes(original.surface_get_arrays(0)) == original_bytes)
	var collider := old_node.get_node(str(spec.contact_path)) as CollisionShape3D
	assert(collider != null and collider.shape is ConcavePolygonShape3D)
	assert((collider.get_parent() as Node3D).transform == Transform3D.IDENTITY and collider.transform == Transform3D.IDENTITY)
	var original_shape := collider.shape as ConcavePolygonShape3D
	var original_faces: PackedVector3Array = original_shape.get_faces()
	assert(original_faces.size() == int(spec.original_triangles) * 3)
	var retained_faces := PackedVector3Array()
	var removed_contacts := 0
	for triangle in range(int(spec.original_triangles)):
		var belongs := true
		for corner in range(3):
			belongs = belongs and _in_lens(placement * original_faces[triangle * 3 + corner], spec)
		if belongs:
			removed_contacts += 1
		else:
			for corner in range(3):
				retained_faces.append(original_faces[triangle * 3 + corner])
	assert(removed_contacts == int(spec.removed_triangles) and retained_faces.size() == int(spec.retained_triangles) * 3)
	var shape := ConcavePolygonShape3D.new()
	shape.set_faces(retained_faces)
	shape.margin = original_shape.margin
	shape.backface_collision = original_shape.backface_collision
	assert(shape.get_faces().to_byte_array() == retained_faces.to_byte_array())
	assert(original_shape.get_faces().to_byte_array() == original_faces.to_byte_array())
	var witness := {
		"old_batch": str(spec.batch), "removed_semantic": str(spec.semantic),
		"original_render_triangles": int(spec.original_triangles), "removed_named_lens_triangles": int(spec.removed_triangles), "remaining_render_triangles": int(spec.retained_triangles),
		"remaining_vertex_uv_normal_tangent_arrays_exact": true, "remaining_physics_faces_exact": true,
		"original_arrays_sha256": _sha(original_bytes), "retained_indices_sha256": _sha(kept.to_byte_array()),
		"removed_render_faces_native_sha256": _sha(removed.to_byte_array()), "original_contact_faces_sha256": _sha(original_faces.to_byte_array()), "retained_contact_faces_sha256": _sha(retained_faces.to_byte_array()),
		"original_shared_resources_unchanged": true, "source_sha256": SOURCE_SHA256, "glb_sha256": GLB_SHA256
	}
	return {"mesh": replacement, "collider": collider, "shape": shape, "witness": witness}

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema == "astraea.court_a.aimed_optic008")
	assert(data.source.sha256 == SOURCE_SHA256 and data.asset.sha256 == GLB_SHA256)
	assert(data.mesh_count == 7 and data.triangles == 116 and data.contacts == 7 and data.lights_added == 0)
	assert(data.replacement.batch == "C005_S_0326" and data.replacement.original_triangles == 112 and data.replacement.removed_triangles == 28 and data.replacement.retained_triangles == 84)
	assert(parent == ship.get_node(str(data.parent_path)) and not parent.has_node(str(data.root_name)))
	var court := parent.get_node("CourtACompletion004") as Node3D
	assert(court.get_meta("authored_batches") == 123 and court.get_meta("authored_contacts") == 98 and court.get_meta("furniture_contacts") == 3)
	for path in data.retained_originals.runtime_sha256:
		assert(FileAccess.get_sha256("res://" + str(path)) == str(data.retained_originals.runtime_sha256[path]))
	var asset_path := "res://assets/models/" + str(data.asset.filename)
	assert(FileAccess.get_sha256(asset_path) == GLB_SHA256)
	var policy := ConfigFile.new()
	var import_status := policy.load(asset_path + ".import")
	assert(import_status == OK and policy.get_value("params", "meshes/force_disable_compression", false))
	var packed := load(asset_path) as PackedScene
	assert(packed != null)
	var root := packed.instantiate() as Node3D
	assert(root != null and root.transform == Transform3D.IDENTITY)
	assert(root.find_children("*", "MeshInstance3D", true, false).size() == 7)
	assert(root.find_children("*", "Light3D", true, false).is_empty() and root.find_children("*", "CollisionShape3D", true, false).is_empty())
	root.name = str(data.root_name)
	root.position = _vector(data.origin_native)
	var triangles := 0
	var seen: Array[String] = []
	for part in data.parts:
		var mesh := root.find_child(str(part.node), true, false) as MeshInstance3D
		assert(mesh != null and not seen.has(str(mesh.name)) and mesh.mesh != null)
		seen.append(str(mesh.name))
		assert(_native_transform(mesh, root) == Transform3D.IDENTITY)
		var faces := _raw_faces(mesh.mesh)
		assert(faces.size() == int(part.triangles) * 3)
		triangles += faces.size() / 3
		var lo := Vector3(INF, INF, INF)
		var hi := Vector3(-INF, -INF, -INF)
		for point in faces:
			lo = lo.min(root.position + point)
			hi = hi.max(root.position + point)
		assert(lo.distance_to(_vector(part.bounds_native[0])) < 0.00006 and hi.distance_to(_vector(part.bounds_native[1])) < 0.00006)
		mesh.set_meta("source_semantic_id", str(part.semantic))
		mesh.set_meta("source_blend_sha256", SOURCE_SHA256)
		var body := StaticBody3D.new()
		body.name = "SourceStaticContact"
		body.set_meta("contact_source", "raw_lod0_vertex_index_arrays")
		body.set_meta("source_semantic_id", str(part.semantic))
		var collider := CollisionShape3D.new()
		collider.name = "ExactSourceTriangles"
		var shape := ConcavePolygonShape3D.new()
		shape.set_faces(faces)
		shape.margin = 0.001
		shape.set_meta("raw_input_sha256", _sha(faces.to_byte_array()))
		assert(shape.get_faces().to_byte_array() == faces.to_byte_array())
		collider.shape = shape
		body.add_child(collider)
		mesh.add_child(body)
	assert(seen.size() == 7 and triangles == 116 and root.find_children("*", "CollisionShape3D", true, false).size() == 7)
	var marker := root.find_child(str(data.marker.node), true, false) as Node3D
	assert(marker != null and _native_transform(marker, root) == Transform3D.IDENTITY)
	# The editor PackedScene preserves glTF custom properties in the extras dictionary.
	assert(marker.has_meta("extras") and marker.get_meta("extras") is Dictionary)
	var marker_extras: Dictionary = marker.get_meta("extras")
	assert(marker_extras.has("source_id") and marker_extras.has("optical_axis_native"))
	assert(str(marker_extras.source_id) == str(data.fixture.id))
	assert(_vector(marker_extras.optical_axis_native).distance_to(_vector(data.fixture.aim_native)) < 0.000001)
	var theater := parent.get_node("GrandLanternTheater_ConnectedStaticStage_WIP") as Node3D
	var old_node := theater.get_node("TheaterSourceArchitecture").find_child(str(data.replacement.batch), true, false) as MeshInstance3D
	assert(old_node != null and not old_node.has_meta("court_a_optic_replacement"))
	var derivative := _prepare_replacement(old_node, parent, data.replacement)
	var lamp := theater.get_node(str(data.fixture.id)) as SpotLight3D
	assert(lamp != null and _native_transform(theater, parent) == Transform3D.IDENTITY)
	assert(lamp.get_meta("source_fixture_semantic_id") == data.fixture.original_semantic and lamp.get_meta("source_blend_sha256") == data.fixture.original_source_sha256)
	assert(lamp.position.distance_to(_vector(data.fixture.position_native)) < 0.0001)
	assert((-lamp.basis.z).distance_to(_vector(data.fixture.before_aim_native).normalized()) < 0.0001)
	assert(absf(lamp.spot_range - float(data.fixture.range_m)) < 0.00001 and absf(lamp.light_energy - float(data.fixture.energy)) < 0.00001 and absf(lamp.spot_angle * 2.0 - float(data.fixture.full_cone_degrees)) < 0.00001)
	assert(data.fixture.shadow_source_budget == 8 and data.fixture.candidate_cap == 32)
	var light_count := ship.find_children("*", "Light3D", true, false).size()
	# Apply only after every source, import, geometry, contact and target-light gate.
	parent.add_child(root)
	old_node.mesh = derivative.mesh
	(derivative.collider as CollisionShape3D).shape = derivative.shape
	old_node.set_meta("court_a_optic_replacement", derivative.witness)
	lamp.basis = Basis.looking_at(_vector(data.fixture.aim_native).normalized(), Vector3.UP)
	lamp.set_meta("source_fixture_semantic_id", str(data.fixture.new_semantic))
	lamp.set_meta("source_blend_sha256", SOURCE_SHA256)
	lamp.set_meta("court_a_optic_contract", CONTRACT)
	root.set_meta("source_sha256", SOURCE_SHA256)
	root.set_meta("glb_sha256", GLB_SHA256)
	root.set_meta("source_contract", CONTRACT)
	root.set_meta("source_contract_sha256", FileAccess.get_sha256(CONTRACT))
	root.set_meta("authored_meshes", 7)
	root.set_meta("authored_triangles", 116)
	root.set_meta("authored_contacts", 7)
	root.set_meta("lights_added", 0)
	root.set_meta("fixture_id", str(data.fixture.id))
	root.set_meta("replacement_witness", derivative.witness)
	assert(root.get_parent() == parent and root.get_parent() == court.get_parent())
	assert(ship.find_children("*", "Light3D", true, false).size() == light_count)
	assert(court.find_children("*", "MeshInstance3D", true, false).size() == 123 and court.find_children("*", "CollisionShape3D", true, false).size() == 101)
	# Ship constructs its existing 8-shadow/32-candidate budget after this builder.
	# Final budget behavior is checked independently after ship initialization.
