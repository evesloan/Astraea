extends RefCounted
# Queries exclude only the five controlled loose rigid bodies and capsule.
# Every wall, gate, door pocket and other active collider remains in the queries.
signal failed(message: String)
var wheel_specs: Array = []
var sampled_poses := 0
var floor_rays := 0
var sill_bridge_rays := 0

func require(condition: bool, message: String = "Grand Pool cart probe assertion failed") -> bool:
	if condition: return true
	failed.emit(message)
	var tree := Engine.get_main_loop() as SceneTree
	if tree != null: tree.quit(1)
	return false

func _init() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	wheel_specs = data.wheel_contacts
	if not require(wheel_specs.size() == 4): return

func controlled_exclusions(actor: CharacterBody3D, cart: RigidBody3D) -> Array[RID]:
	var excluded: Array[RID] = [actor.get_rid(), cart.get_rid()]
	if not require(cart.products.size() == 4): return []
	for product in cart.products: excluded.append(product.get_rid())
	return excluded

func clear_shape(space: PhysicsDirectSpaceState3D, shape: Shape3D, transform: Transform3D, excluded: Array[RID], label: String) -> void:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = transform
	query.margin = .001
	query.exclude = excluded
	var hits := space.intersect_shape(query, 128)
	if not require(hits.size() < 128, "Unsaturated Grand Pool cart query required"): return
	for hit in hits: print("GRAND POOL CART POSE BLOCK: ", label, " query_origin:", transform.origin, " ", hit.collider.get_path())
	if not require(hits.is_empty(), label): return

func raw_support(space: PhysicsDirectSpaceState3D, point: Vector3, floor_y: float, excluded: Array[RID]) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(Vector3(point.x, floor_y + .20, point.z), Vector3(point.x, floor_y - .20, point.z), 1)
	query.exclude = excluded
	return space.intersect_ray(query)

func floor_at(space: PhysicsDirectSpaceState3D, point: Vector3, floor_y: float, excluded: Array[RID], label: String, at_lift := false, cabin: Node3D = null) -> void:
	var hit := raw_support(space, point, floor_y, excluded)
	if hit.is_empty() and at_lift and point.x > -23.205 and point.x < -23.185 and absf(point.z + 490) < 1.2:
		# The retained 10mm platform/sill seam is bridged by a real wheel/capsule.
		# Demand actual same-level bearing on BOTH sides, never exclude a gate.
		for direction in [-1.0, 1.0]:
			var side := raw_support(space, point + Vector3.RIGHT * .02 * direction, floor_y, excluded)
			if not require(not side.is_empty() and absf(side.position.y - floor_y) < .015, "Unsupported staff sill bearing: " + label): return
			sill_bridge_rays += 1
	else:
		if not require(not hit.is_empty(), "Unsupported actual wheel/operator: %s at %s" % [label, point]): return
		if not require(absf(hit.position.y - floor_y) < .015, "Wrong-level Grand Pool support: " + label): return
		if cabin != null:
			if not require(hit.collider == cabin, "Loaded transfer must bear on the actual moving cabin: " + label): return
	floor_rays += 1

func check_pose(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, position: Vector3, yaw: float, floor_y: float, at_lift := false) -> void:
	var excluded := controlled_exclusions(actor, cart)
	var space := ship.get_world_3d().direct_space_state
	var basis := Basis(Vector3.UP, yaw)
	var transform := Transform3D(basis, position)
	for child in cart.get_children():
		if child is CollisionShape3D: clear_shape(space, child.shape, transform * child.transform, excluded, "Cart part " + str(child.name))
	var load_shape := BoxShape3D.new()
	load_shape.size = Vector3(.65, .26, .96)
	clear_shape(space, load_shape, transform * Transform3D(Basis.IDENTITY, Vector3(0, 1.05, 0)), excluded, "Four loose products' tray envelope")
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	clear_shape(space, capsule, Transform3D(basis, position + basis * Vector3(0, .91, 1.62)), excluded, "Actual operator envelope at cart%s yaw%s" % [position,yaw])
	for index in range(wheel_specs.size()):
		var centre: Array = wheel_specs[index].center
		floor_at(space, transform * Vector3(centre[0], 0, centre[2]), floor_y, excluded, "planned wheel " + str(index), at_lift)
	floor_at(space, position + basis * Vector3(0, 0, 1.62), floor_y, excluded, "planned operator foot", at_lift)
	sampled_poses += 1

func shape_world_x_bounds(contact: CollisionShape3D) -> Vector2:
	# Exact projected active shape geometry, including the actual body tilt/yaw.
	var transform := contact.global_transform
	var shape := contact.shape
	var radius_x := 0.0
	if shape is BoxShape3D:
		var half: Vector3 = shape.size * .5
		radius_x = absf(transform.basis.x.x)*half.x + absf(transform.basis.y.x)*half.y + absf(transform.basis.z.x)*half.z
	elif shape is SphereShape3D:
		radius_x = shape.radius * Vector3(transform.basis.x.x,transform.basis.y.x,transform.basis.z.x).length()
	elif shape is CylinderShape3D:
		radius_x = shape.height*.5*absf(transform.basis.y.x) + shape.radius*sqrt(transform.basis.x.x*transform.basis.x.x + transform.basis.z.x*transform.basis.z.x)
	elif shape is ConcavePolygonShape3D or shape is ConvexPolygonShape3D:
		var points: PackedVector3Array = (shape as ConcavePolygonShape3D).get_faces() if shape is ConcavePolygonShape3D else (shape as ConvexPolygonShape3D).points
		var bounds := Vector2(INF,-INF)
		for point in points:
			var world: Vector3 = transform * point
			bounds.x = minf(bounds.x,world.x)
			bounds.y = maxf(bounds.y,world.x)
		return bounds
	else:
		print("GRAND POOL X-BOUNDS UNSUPPORTED SHAPE: ",contact.get_path()," ",shape)
		return Vector2(NAN,NAN)
	return Vector2(transform.origin.x-radius_x,transform.origin.x+radius_x)

func collision_world_x_bounds(node: Node3D) -> Vector2:
	var bounds := Vector2(INF,-INF)
	for contact in node.find_children("*","CollisionShape3D",true,false):
		var body := contact.get_parent() as CollisionObject3D
		if contact.disabled or body == null or (body.collision_layer & 1) == 0: continue
		var part := shape_world_x_bounds(contact)
		if not part.is_finite(): return part
		bounds.x = minf(bounds.x,part.x)
		bounds.y = maxf(bounds.y,part.y)
	return bounds

func actual_loaded_cart_x_bounds(cart: RigidBody3D) -> Vector2:
	var bounds := collision_world_x_bounds(cart)
	for product in cart.products:
		var part := collision_world_x_bounds(product)
		if not part.is_finite(): return part
		bounds.x = minf(bounds.x,part.x)
		bounds.y = maxf(bounds.y,part.y)
	return bounds
