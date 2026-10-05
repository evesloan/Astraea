extends RefCounted
# Explicit opt-in for the immutable AST-DIN-002 chair. Contacts and identities
# remain on the original part nodes; only draw geometry is joined by material.
# Each chair keeps its own culling/light bounds. No cross-room batching.
static var cached: WeakRef

static func relative_transform(part: Node3D, wrapper: Node3D) -> Transform3D:
	var result := part.transform
	var parent := part.get_parent() as Node3D
	while parent != wrapper:
		assert(parent != null)
		result = parent.transform * result
		parent = parent.get_parent() as Node3D
	return result

static func apply(wrapper: Node3D) -> MeshInstance3D:
	assert(wrapper.get_meta("catalogue_file", "") == "AST-DIN-002.glb")
	assert(not wrapper.has_node("JoinedChairVisual"))
	var parts := wrapper.find_children("*", "MeshInstance3D", true, false)
	assert(parts.size() == 10, "Changed chair source needs a new visual/contact review")
	var joined: ArrayMesh = cached.get_ref() if cached != null else null
	if joined == null:
		var groups: Dictionary = {}
		for part: MeshInstance3D in parts:
			assert(part.mesh != null and part.mesh.get_blend_shape_count() == 0)
			assert(part.skin == null and part.material_overlay == null)
			assert(part.visible and part.mesh.get_surface_count() == 1)
			var material := part.get_active_material(0)
			assert(material != null)
			var key := material.get_instance_id()
			if not groups.has(key): groups[key] = {"material": material, "parts": []}
			groups[key].parts.append(part)
		joined = ArrayMesh.new()
		for group in groups.values():
			var surface := SurfaceTool.new()
			surface.begin(Mesh.PRIMITIVE_TRIANGLES)
			for part: MeshInstance3D in group.parts:
				surface.append_from(part.mesh, 0, relative_transform(part, wrapper))
			surface.set_material(group.material)
			surface.commit(joined)
		assert(joined.get_surface_count() == 2)
		cached = weakref(joined)
	var visual := MeshInstance3D.new()
	visual.name = "JoinedChairVisual"
	visual.mesh = joined
	wrapper.add_child(visual)
	for part: MeshInstance3D in parts:
		assert(part.has_node("StaticContact/SharedShape"))
		part.hide()
	return visual
