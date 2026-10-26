extends RefCounted
# Mesh-local immutable contacts shared by repeated authored model instances.
static var shapes: Dictionary = {}
static var prune_keys: Array = []
static var prune_registered: Dictionary = {}
static var prune_cursor := 0
static var last_prune_checks := 0
static func remember(key: Variant, shape: Shape3D) -> void:
	shapes[key] = weakref(shape)
	if not prune_registered.has(key):
		prune_registered[key] = true
		prune_keys.append(key)
static func prune_expired(limit: int = 128) -> int:
	last_prune_checks = 0
	var removed := 0
	var budget := mini(maxi(limit,0),prune_keys.size())
	while last_prune_checks < budget and not prune_keys.is_empty():
		prune_cursor %= prune_keys.size()
		var key: Variant = prune_keys[prune_cursor]
		var reference: WeakRef = shapes.get(key)
		last_prune_checks += 1
		if reference == null or reference.get_ref() == null:
			shapes.erase(key)
			prune_registered.erase(key)
			prune_keys[prune_cursor] = prune_keys.back()
			prune_keys.pop_back()
			removed += 1
		else: prune_cursor += 1
	return removed
static var contacts_created := 0
static var shapes_reused := 0
static func attach(instance: MeshInstance3D) -> void:
	if instance.mesh == null: return
	var key := instance.mesh.get_instance_id()
	var reference: WeakRef = shapes.get(key)
	var shape: Shape3D = reference.get_ref() if reference != null else null
	if shape == null:
		shape = preload("res://visible_resource_budget_20261026/exact_contact_pool.gd").intern(preload("res://visible_resource_budget_20261026/transient_contact_faces.gd").get_faces(instance.mesh))
		remember(key,shape)
	else: shapes_reused += 1
	# Expired WeakRefs do not own collision resources. Sweep periodically instead
	# of rescanning every live shape for every attached ship mesh.
	if contacts_created % 256 == 0: prune_expired()
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

# Exact immutable room triangles share one physics shape and one body per prototype instance.
# This avoids one broadphase shape proxy per material batch while preserving triangle contacts.
static func attach_group(root:Node3D,source_meshes:Array[Node])->void:
	var meshes:Array[Node]=[]
	for instance:MeshInstance3D in source_meshes:
		if instance.mesh==null:continue
		var opaque:=true
		for surface in range(instance.mesh.get_surface_count()):
			var material:Material=instance.get_active_material(surface)
			if not material is BaseMaterial3D or material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:opaque=false
		if opaque:meshes.append(instance)
		else:attach(instance) # Preserve per-mesh glass identification by light visibility queries.
	if meshes.is_empty():return
	var key:="room:"
	var transforms:Array[Transform3D]=[]
	for instance:MeshInstance3D in meshes:
		var pose:Transform3D=instance.transform
		var parent:Node3D=instance.get_parent()
		while parent!=root:
			assert(parent!=null)
			pose=parent.transform*pose
			parent=parent.get_parent()
		transforms.append(pose)
		key+=str(instance.mesh.get_instance_id())+":"+var_to_bytes(pose).hex_encode()+";"
	var reference:WeakRef=shapes.get(key)
	var shape:Shape3D=reference.get_ref() if reference!=null else null
	if shape==null:
		var faces:Array[Vector3]=[]
		for i in range(meshes.size()):
			var instance:MeshInstance3D=meshes[i]
			for vertex in preload("res://visible_resource_budget_20261026/transient_contact_faces.gd").get_faces(instance.mesh):faces.append(transforms[i]*vertex)
		var triangles:=preload("res://visible_resource_budget_20261026/exact_contact_pool.gd").intern(PackedVector3Array(faces))
		shape=triangles
		remember(key,shape)
	else:shapes_reused+=1
	var body:=StaticBody3D.new()
	body.name="RoomStaticContacts"
	root.add_child(body)
	var collider:=CollisionShape3D.new()
	collider.name="SharedRoomTriangles"
	collider.shape=shape
	body.add_child(collider)
	contacts_created+=1
