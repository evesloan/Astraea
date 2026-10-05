extends RefCounted
# Shared probe for the pending connected D17 route. This is not a passed route test.
var wheel_specs: Array = []
var sampled_poses := 0
var floor_rays := 0

func _init() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	wheel_specs = data.wheel_contacts
	assert(wheel_specs.size() == 4)

func controlled_exclusions(actor: CharacterBody3D, cart: RigidBody3D) -> Array[RID]:
	var result: Array[RID] = [actor.get_rid(), cart.get_rid()]
	assert(cart.products.size() == 4)
	for product in cart.products:
		result.append(product.get_rid())
	return result

func clear_shape(space: PhysicsDirectSpaceState3D, shape: Shape3D, transform: Transform3D, excluded: Array[RID], label: String) -> void:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = transform
	query.margin = .001
	query.exclude = excluded
	var hits := space.intersect_shape(query, 128)
	assert(hits.size() < 128, "Unsaturated route query required")
	for hit in hits:
		print("D17 ROUTE BLOCK: ", label, " ", hit.collider.get_path())
	assert(hits.is_empty(), label)

func floor_at(space: PhysicsDirectSpaceState3D, point: Vector3, floor_y: float, excluded: Array[RID], label: String) -> void:
	var ray := PhysicsRayQueryParameters3D.create(Vector3(point.x, floor_y + .20, point.z), Vector3(point.x, floor_y - .20, point.z), 1)
	ray.exclude = excluded
	var hit := space.intersect_ray(ray)
	assert(not hit.is_empty(), "Unsupported " + label + " at " + str(point))
	assert(abs(hit.position.y - floor_y) < .015, "Wrong-level support for " + label)
	floor_rays += 1

func check_pose(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, position: Vector3, yaw: float, floor_y: float) -> void:
	var excluded := controlled_exclusions(actor, cart)
	var space := ship.get_world_3d().direct_space_state
	var basis := Basis(Vector3.UP, yaw)
	var transform := Transform3D(basis, position)
	for child in cart.get_children():
		if child is CollisionShape3D:
			clear_shape(space, child.shape, transform * child.transform, excluded, "Cart part " + str(child.name))
	var load_shape := BoxShape3D.new()
	load_shape.size = Vector3(.65, .26, .96)
	clear_shape(space, load_shape, transform * Transform3D(Basis.IDENTITY, Vector3(0, 1.05, 0)), excluded, "Loaded upper tray")
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	clear_shape(space, capsule, Transform3D(basis, position + basis * Vector3(0, .91, 1.62)), excluded, "Actual operator envelope")
	for index in range(wheel_specs.size()):
		var centre: Array = wheel_specs[index].center
		var point := transform * Vector3(float(centre[0]), 0, float(centre[2]))
		floor_at(space, point, floor_y, excluded, "wheel " + str(index))
	floor_at(space, position + basis * Vector3(0, 0, 1.62), floor_y, excluded, "operator foot")
	sampled_poses += 1
