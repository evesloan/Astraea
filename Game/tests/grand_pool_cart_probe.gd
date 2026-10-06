extends RefCounted
# Queries exclude only the five controlled loose rigid bodies and capsule.
# Every wall, gate, door pocket and other active collider remains in the queries.
signal failed(message: String)
var wheel_specs: Array = []
var sampled_poses := 0
var floor_rays := 0
var sill_bridge_rays := 0

func require(condition: bool, message: String = "Grand Pool cart probe assertion failed") -> void:
	if condition: return
	failed.emit(message)
	var tree := Engine.get_main_loop() as SceneTree
	if tree != null: tree.quit(1)
	assert(condition, message)

func _init() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	wheel_specs = data.wheel_contacts
	require(wheel_specs.size() == 4)

func controlled_exclusions(actor: CharacterBody3D, cart: RigidBody3D) -> Array[RID]:
	var excluded: Array[RID] = [actor.get_rid(), cart.get_rid()]
	require(cart.products.size() == 4)
	for product in cart.products: excluded.append(product.get_rid())
	return excluded

func clear_shape(space: PhysicsDirectSpaceState3D, shape: Shape3D, transform: Transform3D, excluded: Array[RID], label: String) -> void:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = transform
	query.margin = .001
	query.exclude = excluded
	var hits := space.intersect_shape(query, 128)
	require(hits.size() < 128, "Unsaturated Grand Pool cart query required")
	for hit in hits: print("GRAND POOL CART POSE BLOCK: ", label, " ", hit.collider.get_path())
	require(hits.is_empty(), label)

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
			require(not side.is_empty() and absf(side.position.y - floor_y) < .015, "Unsupported staff sill bearing: " + label)
			sill_bridge_rays += 1
	else:
		require(not hit.is_empty(), "Unsupported actual wheel/operator: %s at %s" % [label, point])
		require(absf(hit.position.y - floor_y) < .015, "Wrong-level Grand Pool support: " + label)
		if cabin != null: require(hit.collider == cabin, "Loaded transfer must bear on the actual moving cabin: " + label)
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
	clear_shape(space, capsule, Transform3D(basis, position + basis * Vector3(0, .91, 1.62)), excluded, "Actual operator envelope")
	for index in range(wheel_specs.size()):
		var centre: Array = wheel_specs[index].center
		floor_at(space, transform * Vector3(centre[0], 0, centre[2]), floor_y, excluded, "planned wheel " + str(index), at_lift)
	floor_at(space, position + basis * Vector3(0, 0, 1.62), floor_y, excluded, "planned operator foot", at_lift)
	sampled_poses += 1
