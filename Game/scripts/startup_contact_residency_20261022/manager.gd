extends Node
# Candidate: release exact opaque triangle resources, never visual nodes or controllers.
# Adoption is permitted only after the original package has completed all source cuts.
const ENTER := 24.0
const KEEP := 36.0
var host: Node3D
var entries: Array[Dictionary] = []
var elapsed := 0.0
var rejected := 0
var loads := 0
var releases := 0
var shape_cache: Dictionary = {}

func setup(ship: Node3D) -> void:
	host = ship
	process_physics_priority = -220

func _digest(faces: PackedVector3Array) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(faces.to_byte_array())
	return hash.finish().hex_encode()

func adopt(root: Node3D) -> void:
	for mesh: MeshInstance3D in root.find_children("*", "MeshInstance3D", true, false):
		var body := mesh.get_node_or_null("StaticContact") as StaticBody3D
		if body == null: continue
		var collider := body.get_node_or_null("SharedShape") as CollisionShape3D
		if not _eligible(mesh, body, collider):
			rejected += 1
			continue
		var shape := collider.shape as ConcavePolygonShape3D
		var digest := _digest(mesh.mesh.get_faces())
		# Exact triangle ordering as well as geometry must match the retained source.
		if digest != _digest(shape.get_faces()):
			rejected += 1
			continue
		entries.append({"mesh":weakref(mesh), "collider":weakref(collider),
			"mesh_id":mesh.mesh.get_instance_id(), "sha256":digest,
			"margin":shape.margin, "backface":shape.backface_collision,
			"bounds":mesh.global_transform * mesh.get_aabb()})

func _eligible(mesh: MeshInstance3D, body: StaticBody3D, collider: CollisionShape3D) -> bool:
	if mesh.mesh == null or collider == null or not collider.shape is ConcavePolygonShape3D: return false
	if body.get_script() != null or collider.get_script() != null: return false
	if not body.get_meta_list().is_empty() or not collider.get_meta_list().is_empty(): return false
	if body.collision_layer != 1 or body.collision_mask != 1 or body.get_child_count() != 1: return false
	if body.constant_linear_velocity != Vector3.ZERO or body.constant_angular_velocity != Vector3.ZERO: return false
	if body.transform != Transform3D.IDENTITY or collider.transform != Transform3D.IDENTITY or collider.disabled: return false
	var ancestor: Node = mesh
	while ancestor != host:
		if ancestor == null or ancestor.get_script() != null or ancestor is CollisionObject3D: return false
		ancestor = ancestor.get_parent()
	for surface in mesh.mesh.get_surface_count():
		var material := mesh.get_active_material(surface)
		if not material is StandardMaterial3D: return false
		if material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a < .999: return false
	return true

func _near(point: Vector3, bounds: AABB, radius: float) -> bool:
	return point.distance_squared_to(point.clamp(bounds.position, bounds.end)) <= radius * radius

func _load_entry(entry: Dictionary) -> void:
	var collider: CollisionShape3D = entry.collider.get_ref()
	var mesh: MeshInstance3D = entry.mesh.get_ref()
	if collider == null or mesh == null or collider.shape != null: return
	assert(mesh.mesh.get_instance_id() == entry.mesh_id, "Contact source changed after adoption")
	var key: String = str(entry.mesh_id) + ":" + str(entry.margin) + ":" + str(entry.backface)
	var reference: WeakRef = shape_cache.get(key)
	var shape: ConcavePolygonShape3D = reference.get_ref() if reference != null else null
	if shape == null:
		assert(_digest(mesh.mesh.get_faces()) == entry.sha256, "Contact triangles changed after adoption")
		shape = mesh.mesh.create_trimesh_shape()
		shape.margin = entry.margin
		shape.backface_collision = entry.backface
		shape_cache[key] = weakref(shape)
	collider.shape = shape
	loads += 1

func prepare_position(position: Vector3) -> void:
	for entry in entries:
		var mesh: MeshInstance3D = entry.mesh.get_ref()
		if mesh != null and mesh.is_inside_tree(): entry.bounds = mesh.global_transform * mesh.get_aabb()
		if _near(position, entry.bounds, ENTER): _load_entry(entry)

func refresh() -> void:
	var actors := host.get_node_or_null("ShipSpace/PersistentActors")
	var player := host.get_node_or_null("ShipSpace/PersistentActors/Player") as Node3D
	if actors == null or player == null: return
	var positions: Array[Vector3] = [player.global_position]
	for body: RigidBody3D in actors.find_children("*", "RigidBody3D", true, false): positions.append(body.global_position)
	for entry in entries:
		var collider: CollisionShape3D = entry.collider.get_ref()
		var mesh: MeshInstance3D = entry.mesh.get_ref()
		if collider == null or mesh == null: continue
		if mesh.is_inside_tree(): entry.bounds = mesh.global_transform * mesh.get_aabb()
		var wanted := false
		for position in positions:
			if _near(position, entry.bounds, KEEP if collider.shape != null else ENTER):
				wanted = true
				break
		if wanted: _load_entry(entry)
		elif collider.shape != null:
			collider.shape = null
			releases += 1

func _physics_process(delta: float) -> void:
	elapsed += delta
	if elapsed >= .2:
		elapsed = 0.0
		refresh()

func statistics() -> Dictionary:
	var active := 0
	for entry in entries:
		var collider: CollisionShape3D = entry.collider.get_ref()
		if collider != null and collider.shape != null: active += 1
	return {"registered":entries.size(), "active":active, "rejected":rejected,
		"loads":loads, "releases":releases, "visual_nodes_removed":0}
