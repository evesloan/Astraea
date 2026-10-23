extends RefCounted
static func attach_group(root:Node3D,source_meshes:Array[Node])->void:
	var cache=load("res://scripts/static_contact_cache.gd")
	if OS.get_environment("ASTRAEA_PACKED_CONTACT_FACES")!="1":
		cache.attach_group(root,source_meshes);return
	var meshes:Array[Node]=[]
	for instance:MeshInstance3D in source_meshes:
		if instance.mesh==null:continue
		var opaque:=true
		for surface in range(instance.mesh.get_surface_count()):
			var material:Material=instance.get_active_material(surface)
			if not material is BaseMaterial3D or material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:opaque=false
		if opaque:meshes.append(instance)
		else:cache.attach(instance) # Preserve per-mesh glass identification by light visibility queries.
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
	var reference:WeakRef=cache.shapes.get(key)
	var shape:Shape3D=reference.get_ref() if reference!=null else null
	if shape==null:
		var packed:=PackedVector3Array()
		if OS.get_environment("ASTRAEA_PACKED_CONTACT_FACES")=="1":
			# Native packed-array transform; same ordered mesh-local triangles and poses.
			for i in range(meshes.size()):
				var instance:MeshInstance3D=meshes[i]
				packed.append_array(transforms[i]*instance.mesh.get_faces())
		else:
			var faces:Array[Vector3]=[]
			for i in range(meshes.size()):
				var instance:MeshInstance3D=meshes[i]
				for vertex in instance.mesh.get_faces():faces.append(transforms[i]*vertex)
			packed=PackedVector3Array(faces)
		var triangles:=ConcavePolygonShape3D.new()
		triangles.set_faces(packed)
		shape=triangles
		cache.shapes[key]=weakref(shape)
	else:cache.shapes_reused+=1
	var body:=StaticBody3D.new()
	body.name="RoomStaticContacts"
	root.add_child(body)
	var collider:=CollisionShape3D.new()
	collider.name="SharedRoomTriangles"
	collider.shape=shape
	body.add_child(collider)
	cache.contacts_created+=1
