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
const CELL := 48.0
const MAX_BINS := 512
var bins: Dictionary = {}
var oversized: Dictionary = {}
var indexed: Dictionary = {}
var resource_owners: Dictionary = {}
var active_entries: Dictionary = {}
var last_candidates := 0
var last_distance_tests := 0
var last_bounds_updates := 0
var last_transform_checks := 0

func _cell(point: Vector3) -> Vector3i:
	return Vector3i(floori(point.x/CELL),floori(point.y/CELL),floori(point.z/CELL))
func _remove_bins(entry: Dictionary) -> void:
	var id: int = entry.index_id
	oversized.erase(id)
	for cell: Vector3i in entry.get("index_cells",[]):
		if bins.has(cell):
			bins[cell].erase(id)
			if bins[cell].is_empty():bins.erase(cell)
	entry.index_cells=[]
func _insert_bins(entry: Dictionary) -> void:
	var lo: Vector3i = _cell(entry.bounds.position)
	var hi: Vector3i = _cell(entry.bounds.end)
	var span: Vector3i = hi-lo+Vector3i.ONE
	if span.x*span.y*span.z > MAX_BINS:
		oversized[entry.index_id]=true
		return
	for x in range(lo.x,hi.x+1):
		for y in range(lo.y,hi.y+1):
			for z in range(lo.z,hi.z+1):
				var cell:=Vector3i(x,y,z)
				if not bins.has(cell):bins[cell]={}
				bins[cell][entry.index_id]=true
				entry.index_cells.append(cell)
func _geometry_changed(resource_id: int) -> void:
	if not resource_owners.has(resource_id):return
	for id: int in resource_owners[resource_id].owners:
		if indexed.has(id):indexed[id].bounds_dirty=true
func _watch_resource(entry: Dictionary, resource: Mesh) -> void:
	var id: int=resource.get_instance_id()
	if not resource_owners.has(id):
		var callback: Callable=_geometry_changed.bind(id)
		resource_owners[id]={"resource":weakref(resource),"owners":{},"callback":callback}
		resource.changed.connect(callback)
	resource_owners[id].owners[entry.index_id]=true
func unregister(entry: Dictionary) -> void:
	_remove_bins(entry)
	indexed.erase(entry.index_id)
	active_entries.erase(entry.index_id)
	if resource_owners.has(entry.mesh_id):
		var owner: Dictionary=resource_owners[entry.mesh_id]
		owner.owners.erase(entry.index_id)
		if owner.owners.is_empty():
			var resource: Mesh=owner.resource.get_ref()
			if resource!=null and resource.changed.is_connected(owner.callback):resource.changed.disconnect(owner.callback)
			resource_owners.erase(entry.mesh_id)
	entries.erase(entry)
func _sync_index() -> void:
	last_bounds_updates=0;last_transform_checks=0
	var expired: Array[Dictionary]=[]
	for entry: Dictionary in entries:
		var mesh: MeshInstance3D=entry.mesh.get_ref()
		if mesh==null:
			expired.append(entry);continue
		last_transform_checks+=1
		# Later retained construction may restore a shape directly. Reconcile its
		# actual state so it cannot escape release merely by missing our load path.
		var collider: CollisionShape3D=entry.collider.get_ref()
		if collider!=null and collider.shape!=null:active_entries[entry.index_id]=true
		else:active_entries.erase(entry.index_id)
		if not mesh.is_inside_tree():continue # Original detached-room bounds remain retained.
		var pose: Transform3D=mesh.global_transform
		if pose==entry.index_pose and not bool(entry.bounds_dirty) and mesh.mesh!=null and mesh.mesh.get_instance_id()==int(entry.mesh_id):continue
		_remove_bins(entry)
		entry.bounds=pose*mesh.get_aabb();entry.index_pose=pose;entry.bounds_dirty=false
		_insert_bins(entry);last_bounds_updates+=1
	for entry: Dictionary in expired:unregister(entry)
func _candidates(positions: Array[Vector3], radius: float) -> Dictionary:
	var result: Dictionary=oversized.duplicate()
	for point: Vector3 in positions:
		var lo: Vector3i=_cell(point-Vector3.ONE*radius)
		var hi: Vector3i=_cell(point+Vector3.ONE*radius)
		for x in range(lo.x,hi.x+1):
			for y in range(lo.y,hi.y+1):
				for z in range(lo.z,hi.z+1):
					var cell:=Vector3i(x,y,z)
					if bins.has(cell):result.merge(bins[cell])
	return result

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
		var entry: Dictionary={"mesh":weakref(mesh), "collider":weakref(collider),
			"mesh_id":mesh.mesh.get_instance_id(), "sha256":digest,
			"margin":shape.margin, "backface":shape.backface_collision,
			"bounds":mesh.global_transform * mesh.get_aabb(),"index_id":mesh.get_instance_id(),
			"index_pose":mesh.global_transform,"bounds_dirty":false,"index_cells":[]}
		assert(not indexed.has(entry.index_id),"One immutable contact owner per mesh")
		_watch_resource(entry,mesh.mesh)
		entries.append(entry);indexed[entry.index_id]=entry;active_entries[entry.index_id]=true
		_insert_bins(entry)

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
	_sync_index()
	var positions: Array[Vector3]=[position]
	var candidates:=_candidates(positions,ENTER)
	last_candidates=candidates.size();last_distance_tests=0
	for id: int in candidates:
		var entry: Dictionary=indexed[id]
		last_distance_tests+=1
		if _near(position,entry.bounds,ENTER):
			_load_entry(entry)
			var collider: CollisionShape3D=entry.collider.get_ref()
			if collider!=null and collider.shape!=null:active_entries[id]=true

func refresh() -> void:
	var actors := host.get_node_or_null("ShipSpace/PersistentActors")
	var player := host.get_node_or_null("ShipSpace/PersistentActors/Player") as Node3D
	if actors == null or player == null: return
	var positions: Array[Vector3] = [player.global_position]
	for body: RigidBody3D in actors.find_children("*", "RigidBody3D", true, false): positions.append(body.global_position)
	_sync_index()
	var candidates:=_candidates(positions,KEEP)
	# Every active contact is checked for release, even after a teleport outside all bins.
	candidates.merge(active_entries)
	last_candidates=candidates.size();last_distance_tests=0
	for id: int in candidates:
		var entry: Dictionary=indexed[id]
		var collider: CollisionShape3D = entry.collider.get_ref()
		var mesh: MeshInstance3D = entry.mesh.get_ref()
		if collider == null or mesh == null:
			active_entries.erase(id);continue
		var wanted := false
		for position in positions:
			last_distance_tests+=1
			if _near(position, entry.bounds, KEEP if collider.shape != null else ENTER):
				wanted = true;break
		if wanted:
			_load_entry(entry)
			if collider.shape!=null:active_entries[id]=true
		elif collider.shape != null:
			collider.shape = null;releases += 1;active_entries.erase(id)

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
		"loads":loads, "releases":releases, "visual_nodes_removed":0,"index_bins":bins.size(),"oversized_entries":oversized.size(),"last_candidates":last_candidates,"last_distance_tests":last_distance_tests,"last_transform_checks":last_transform_checks,"last_bounds_updates":last_bounds_updates}
