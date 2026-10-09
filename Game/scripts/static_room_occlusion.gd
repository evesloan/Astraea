extends RefCounted
# Conservative actual-face occluders. Never fill an AABB, portal or window.
# Only large triangles of verified opaque, unmoving mesh surfaces qualify.
static func install(source: Node3D) -> Dictionary:
	if source.has_meta("static_occlusion_registered"): return source.get_meta("static_occlusion_registered")
	var groups: Dictionary = {}
	var accepted_meshes := 0
	var triangle_count := 0
	var rejected_dynamic := 0
	for part: MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
		if not part.mesh is ArrayMesh or not part.is_visible_in_tree(): continue
		var size: Vector3 = part.mesh.get_aabb().size
		if size.x*size.y+size.x*size.z+size.y*size.z < 4.0: continue
		var ancestor: Node = part
		var unsafe := false
		while ancestor != source and ancestor != null:
			if ancestor is RigidBody3D or ancestor is CharacterBody3D or ancestor is AnimatableBody3D or ancestor.has_meta("region_id"):
				unsafe = true
				break
			# Animated doors/lifts keep their openings; their meshes are excluded.
			if ancestor.has_method("interact") or ancestor.has_method("_apply_pose"):
				unsafe = true
				break
			ancestor = ancestor.get_parent()
		if unsafe:
			rejected_dynamic += 1
			continue
		var transform: Transform3D = source.global_transform.affine_inverse()*part.global_transform
		var used := false
		for surface in range(part.mesh.get_surface_count()):
			var material: Material = part.get_active_material(surface)
			if not material is BaseMaterial3D: continue
			if material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED: continue
			if material.albedo_color.a < .999: continue
			if part.mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES: continue
			var arrays: Array = part.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var count: int = indices.size() if not indices.is_empty() else vertices.size()
			for i in range(0,count-2,3):
				var a: Vector3 = transform*vertices[indices[i] if not indices.is_empty() else i]
				var b: Vector3 = transform*vertices[indices[i+1] if not indices.is_empty() else i+1]
				var c: Vector3 = transform*vertices[indices[i+2] if not indices.is_empty() else i+2]
				if (b-a).cross(c-a).length()*.5 < 2.0: continue
				var center: Vector3 = (a+b+c)/3.0
				var key := Vector3i(floori(center.x/48),floori(center.y/16),floori(center.z/48))
				if not groups.has(key): groups[key] = PackedVector3Array()
				var faces: PackedVector3Array = groups[key]
				faces.append_array(PackedVector3Array([a,b,c]))
				groups[key] = faces
				triangle_count += 1
				used = true
		if used: accepted_meshes += 1
	var root := Node3D.new()
	root.name = "VerifiedStaticOpaqueFaceOccluders"
	source.add_child(root)
	for key in groups:
		load("res://scripts/architectural_occlusion.gd").from_faces(root,groups[key],"Cell_%s_%s_%s"%[key.x,key.y,key.z])
	var result := {"source_meshes":accepted_meshes,"triangles":triangle_count,"cells":groups.size(),"excluded_dynamic_meshes":rejected_dynamic,"policy":"Exact opaque static triangles of at least2m2; no envelope fill or simplification; doors, moving objects, glass, shaders and existing slab owners excluded."}
	source.set_meta("static_occlusion_registered",result)
	return result
