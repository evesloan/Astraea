extends RefCounted
# Keep original render objects and therefore original per-object light selection.
# Only the separately verified exact opaque contacts use bounded residency.
static func instantiate_visual(file: String, manifest: Dictionary) -> Node3D:
	var visual := (load("res://assets/models/"+file) as PackedScene).instantiate() as Node3D
	assert(visual != null)
	assert(visual.find_children("*","CollisionShape3D",true,false).is_empty(),"Unexpected imported contacts would duplicate exact cells")
	var policy: Dictionary = manifest.get("source_collision_policy",{})
	if not policy.is_empty():
		for mesh: MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			assert(policy.has(str(mesh.name)))
			var spec: Dictionary = policy[str(mesh.name)]
			if str(spec.get("role","")) == "hospitality_glass":
				var glass := ShaderMaterial.new()
				glass.shader = load("res://shaders/hospitality_glass.gdshader")
				mesh.material_override = glass
			if str(spec.get("category","")) == "light_source":
				mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for row in manifest.get("retained_transparent_contacts",[]):
		var mesh := visual.get_node(str(row.source_path)) as MeshInstance3D
		assert(mesh != null)
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	return visual
