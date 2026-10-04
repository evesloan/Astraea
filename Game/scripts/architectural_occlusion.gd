extends RefCounted
# Occlusion geometry is copied from actual opaque static surfaces, preserving holes.
static func from_mesh(parent: Node3D, mesh: Mesh, label: String) -> OccluderInstance3D:
	var vertices := mesh.get_faces()
	return from_faces(parent,vertices,label)
static func from_faces(parent: Node3D, vertices: PackedVector3Array, label: String) -> OccluderInstance3D:
	if vertices.is_empty(): return null
	var indices := PackedInt32Array()
	indices.resize(vertices.size())
	for i in range(vertices.size()): indices[i] = i
	var shape := ArrayOccluder3D.new()
	shape.set_arrays(vertices,indices)
	var instance := OccluderInstance3D.new()
	instance.name = label
	instance.occluder = shape
	parent.add_child(instance)
	return instance
static func salon_shell(shell: Node3D) -> void:
	var faces := PackedVector3Array()
	for part in shell.find_children("*","MeshInstance3D",true,false):
		var accepted := false
		for prefix in ["SAL_StonePlinth","SAL_WalnutDado","SAL_UpperWall","SAL_SectionalCeiling","SAL_PortalTransom"]:
			if part.name.begins_with(prefix): accepted = true
		if not accepted or part.mesh == null: continue
		var relative: Transform3D = shell.global_transform.affine_inverse()*part.global_transform
		for p in part.mesh.get_faces(): faces.append(relative*p)
	from_faces(shell,faces,"OpaqueSalonSurfaces_KeepWindowsAndPortalOpen")
