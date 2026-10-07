extends RefCounted
# DRAFT: source/binary checked; actual Godot parsing/import/physics tests pending.
# New sibling only. No old theater mutation, floor ownership, light or exposure code.
const CONTRACT := "res://data/architecture/COURT_A_RUNTIME_INCREMENT004.json"

static func vector(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))

static func transform(a: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(a[0][0], a[1][0], a[2][0]), Vector3(a[0][1], a[1][1], a[2][1]), Vector3(a[0][2], a[1][2], a[2][2])), Vector3(a[0][3], a[1][3], a[2][3]))

static func relative_transform(node: Node3D, root: Node3D) -> Transform3D:
	var result := node.transform
	var cursor := node.get_parent()
	while cursor != root:
		assert(cursor != null and cursor is Node3D)
		result = (cursor as Node3D).transform * result
		cursor = cursor.get_parent()
	return root.transform * result

static func exact_transform(a: Transform3D, b: Transform3D) -> void:
	for axis in range(3):
		assert(abs(a.origin[axis] - b.origin[axis]) <= 0.000001)
		for row in range(3):
			assert(abs(a.basis[axis][row] - b.basis[axis][row]) <= 0.000001)

static func raw_faces(mesh: Mesh, placement: Transform3D = Transform3D.IDENTITY) -> PackedVector3Array:
	# Read raw surface arrays. Mesh.get_faces() is intentionally forbidden here.
	assert(mesh is ArrayMesh)
	var resource := mesh as ArrayMesh
	var faces := PackedVector3Array()
	for surface in range(mesh.get_surface_count()):
		assert(resource.surface_get_primitive_type(surface) == Mesh.PRIMITIVE_TRIANGLES)
		var arrays := mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		assert(not vertices.is_empty())
		if indices.is_empty():
			assert(vertices.size() % 3 == 0)
			for v in vertices:
				faces.append(placement * v)
		else:
			assert(indices.size() % 3 == 0)
			for index in indices:
				assert(index >= 0 and index < vertices.size())
				faces.append(placement * vertices[index])
	assert(faces.size() % 3 == 0 and not faces.is_empty())
	return faces

static func shape_from_raw(faces: PackedVector3Array) -> ConcavePolygonShape3D:
	var shape := ConcavePolygonShape3D.new()
	var digest := HashingContext.new()
	digest.start(HashingContext.HASH_SHA256)
	digest.update(faces.to_byte_array())
	shape.set_meta("court_raw_input_sha256", digest.finish().hex_encode())
	shape.set_meta("court_raw_input_corners", faces.size())
	shape.set_faces(faces)
	shape.margin = 0.001 # Existing theater policy; no fit tuning.
	return shape

static func add_contact(parent: Node3D, shape: Shape3D, identity: String, placement: Transform3D = Transform3D.IDENTITY) -> void:
	var body := StaticBody3D.new()
	body.name = "CourtContact_" + identity
	body.transform = placement
	body.set_meta("court_source_identity", identity)
	body.set_meta("contact_source", "raw_lod0_vertex_index_arrays")
	var collider := CollisionShape3D.new()
	collider.name = "SourceTriangles"
	collider.shape = shape
	body.add_child(collider)
	parent.add_child(body)

static func load_template(spec: Dictionary) -> Node3D:
	var path := "res://assets/models/" + str(spec.filename)
	assert(FileAccess.get_sha256(path) == str(spec.sha256))
	var policy := ConfigFile.new()
	assert(policy.load(path + ".import") == OK)
	assert(policy.get_value("params", "meshes/force_disable_compression", false))
	var resource := load(path) as PackedScene
	assert(resource != null)
	return resource.instantiate() as Node3D

static func build(parent: Node3D, _ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema == "astraea.court_a.increment004")
	assert(data.source_sha256 == "7456c069315f3ed1f74c327ba0af53a90942cd1549b6905d3abe58ba76633c49")
	assert(data.authored_meshes == 157 and data.prototype_meshes == 120 and data.placement_count == 24)
	assert(not parent.has_node(str(data.root_name)))
	var root := Node3D.new()
	root.name = str(data.root_name)
	root.position = vector(data.court_origin_native)
	root.set_meta("persistent_id", str(data.persistent_id))
	root.set_meta("source_sha256", str(data.source_sha256))
	root.set_meta("source_instance_ids", [])
	root.set_meta("native_acceptance", false)
	root.set_meta("lights_added", 0)
	parent.add_child(root)
	var source := load_template(data.files.authored)
	var prototype := load_template(data.files.prototype)
	assert(source.find_children("*", "MeshInstance3D", true, false).size() == 123)
	assert(prototype.find_children("*", "MeshInstance3D", true, false).size() == 18)
	var definitions: Dictionary = {}
	var shapes: Dictionary = {}
	var authored_count := 0
	var authored_contacts := 0
	for spec in data.batches:
		var template := source if spec.kind == "authored" else prototype
		var found := template.find_child(str(spec.name), true, false) as MeshInstance3D
		assert(found != null and found.mesh != null)
		var local := relative_transform(found, template)
		exact_transform(local, transform(spec.native_local_matrix))
		if spec.kind == "authored":
			var view := MeshInstance3D.new()
			view.name = str(spec.name)
			view.mesh = found.mesh
			view.transform = local
			view.set_meta("source_semantic_ids", spec.semantic_ids)
			view.set_meta("court_collides", bool(spec.collides))
			view.set_meta("source_role", str(spec.role))
			root.add_child(view)
			authored_count += 1
			if spec.collides:
				add_contact(view, shape_from_raw(raw_faces(view.mesh)), str(spec.name))
				authored_contacts += 1
		else:
			var identity := str(spec.definition)
			if not definitions.has(identity):
				definitions[identity] = []
			definitions[identity].append({"name": str(spec.name), "mesh": found.mesh, "transform": local, "collides": bool(spec.collides)})
	assert(authored_count == 123 and authored_contacts == 98 and definitions.size() == 4)
	for identity in definitions:
		var collides: bool = data.prototype_definitions[identity].collides
		if collides:
			var faces := PackedVector3Array()
			for part in definitions[identity]:
				assert(part.collides)
				faces.append_array(raw_faces(part.mesh, part.transform))
			shapes[identity] = shape_from_raw(faces)
		else:
			for part in definitions[identity]:
				assert(not part.collides)
	var groups: Dictionary = {}
	var identities: Array = []
	var contacts := 0
	for record in data.instances:
		var id := str(record.id)
		assert(not identities.has(id))
		identities.append(id)
		var placement := transform(record.court_local_matrix)
		exact_transform(root.transform * placement, transform(record.native_matrix))
		var identity := str(record.definition)
		assert(definitions.has(identity))
		var cell := Vector3(floor(placement.origin.x / 4.0), floor(placement.origin.y / 4.0), floor(placement.origin.z / 4.0)) * 4.0
		var key := identity + "|" + str(cell)
		if not groups.has(key):
			groups[key] = {"definition": identity, "origin": cell, "entries": []}
		groups[key].entries.append({"id": id, "transform": placement})
		assert(bool(record.collides) == shapes.has(identity))
		if record.collides:
			add_contact(root, shapes[identity], id, placement)
			contacts += 1
	assert(identities.size() == 24 and contacts == 3)
	var batch_number := 0
	for key in groups:
		var group: Dictionary = groups[key]
		var offset := Transform3D(Basis.IDENTITY, group.origin)
		for part in definitions[group.definition]:
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = part.mesh
			mm.instance_count = group.entries.size()
			var ids: Array = []
			for i in range(group.entries.size()):
				var entry: Dictionary = group.entries[i]
				mm.set_instance_transform(i, offset.affine_inverse() * entry.transform * part.transform)
				ids.append(entry.id)
			var view := MultiMeshInstance3D.new()
			view.name = "CourtRetainedVisual_%03d" % batch_number
			view.transform = offset
			view.multimesh = mm
			view.set_meta("source_instance_ids", ids)
			view.set_meta("source_definition", group.definition)
			view.set_meta("source_prototype_batch", part.name)
			root.add_child(view)
			batch_number += 1
	root.set_meta("source_instance_ids", identities)
	root.set_meta("authored_batches", authored_count)
	root.set_meta("authored_contacts", authored_contacts)
	root.set_meta("furniture_contacts", contacts)
	root.set_meta("retained_visual_batches", batch_number)
	# Templates were never added to the scene tree: no hidden prototype duplicates.
	source.free()
	prototype.free()
	load("res://scripts/court_a_aimed_optic008.gd").build(parent, _ship)
	load("res://scripts/theater_d11_entry.gd").build(parent, _ship)
