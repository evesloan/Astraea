extends Node
# Visual geometry is always resident. Only exact immutable contact cells stream.
# Cell bounds cover every source triangle, including long walls/floors crossing bins.
const ENTER_METRES := 24.0
const KEEP_METRES := 36.0
var host: Node3D
var entries: Array[Dictionary] = []
var elapsed := 0.0
var loads := 0
var releases := 0
var peak_active_cells := 0
var verified: Dictionary = {}
func setup(ship: Node3D) -> void:
	host = ship
	process_physics_priority = -200
func register_model(wrapper: Node3D, manifest: Dictionary) -> void:
	for cell in manifest.collision_cells:
		var lo: Array = cell.bounds_min
		var hi: Array = cell.bounds_max
		var box := AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
		var entry:Dictionary={"wrapper":weakref(wrapper),"cell":cell,"bounds":wrapper.global_transform*box,"body":null}
		entries.append(entry)
		# Initial hydration visits each new cell once, not every prior model again.
		if _near(Vector3(63.0,52.6,-20.5),entry.bounds,ENTER_METRES):_load_entry(entry)
func _load_entry(entry: Dictionary) -> void:
	if is_instance_valid(entry.body): return
	var wrapper: Node3D = entry.wrapper.get_ref()
	if wrapper == null: return
	var path: String = entry.cell.path
	if not verified.has(path):
		assert(FileAccess.get_sha256(path) == str(entry.cell.sha256), "Exact contact cell hash mismatch: " + path)
		verified[path] = true
	var shape := load(path) as ConcavePolygonShape3D
	assert(shape != null)
	var body := StaticBody3D.new()
	body.name = "ResidentExactContacts_" + str(entry.cell.id)
	body.set_meta("source_contact_sha256",entry.cell.sha256)
	var collider := CollisionShape3D.new()
	collider.name = "ExactSourceTriangles"
	collider.shape = shape
	body.add_child(collider)
	wrapper.add_child(body)
	if body.is_inside_tree(): body.force_update_transform()
	entry.body = body
	loads += 1
func _near(point: Vector3, bounds: AABB, margin: float) -> bool:
	return point.distance_squared_to(point.clamp(bounds.position,bounds.end)) <= margin*margin
func prepare_position(position: Vector3) -> void:
	for entry in entries:
		if _near(position,entry.bounds,ENTER_METRES): _load_entry(entry)
func _physics_process(delta: float) -> void:
	elapsed += delta
	if elapsed < 0.2: return
	elapsed = 0.0
	refresh()
func refresh() -> void:
	var actor := host.get_node_or_null("ShipSpace/PersistentActors/Player") as Node3D
	if actor == null: return
	var positions: Array[Vector3] = [actor.global_position]
	for body in host.get_node("ShipSpace/PersistentActors").find_children("*","RigidBody3D",true,false):
		positions.append(body.global_position)
	var active := 0
	for entry in entries:
		var live := is_instance_valid(entry.body)
		var wanted := false
		for position in positions:
			if _near(position,entry.bounds,KEEP_METRES if live else ENTER_METRES):
				wanted = true
				break
		if wanted:
			_load_entry(entry)
			active += 1
		elif live:
			entry.body.free()
			entry.body = null
			releases += 1
	peak_active_cells = maxi(peak_active_cells,active)
func statistics() -> Dictionary:
	var active := 0
	for entry in entries:
		if is_instance_valid(entry.body): active += 1
	return {"registered_cells":entries.size(),"active_cells":active,"peak_active_cells":peak_active_cells,"loads":loads,"releases":releases,"visual_distance_culling":false,"exact_contact_resources_released":true}
