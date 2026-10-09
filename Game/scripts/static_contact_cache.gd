extends RefCounted
# Mesh-local immutable contacts shared by repeated authored model instances.
static var shapes: Dictionary = {}
static var contacts_created := 0
static var shapes_reused := 0
static func attach(instance: MeshInstance3D) -> void:
	if instance.mesh == null: return
	var key := instance.mesh.get_instance_id()
	var reference: WeakRef = shapes.get(key)
	var shape: Shape3D = reference.get_ref() if reference != null else null
	if shape == null:
		shape = instance.mesh.create_trimesh_shape()
		shapes[key] = weakref(shape)
	else: shapes_reused += 1
	# Expired WeakRefs do not own collision resources. Sweep periodically instead
	# of rescanning every live shape for every attached ship mesh.
	if shapes.size() > 4096 and contacts_created % 256 == 0:
		for old_key in shapes.keys():
			if shapes[old_key].get_ref() == null: shapes.erase(old_key)
	var body := StaticBody3D.new()
	body.name = "StaticContact"
	var collider := CollisionShape3D.new()
	collider.name = "SharedShape"
	collider.shape = shape
	body.add_child(collider)
	instance.add_child(body)
	contacts_created += 1

static func live_shape_count() -> int:
	var count := 0
	for reference in shapes.values():
		if reference.get_ref() != null: count += 1
	return count
