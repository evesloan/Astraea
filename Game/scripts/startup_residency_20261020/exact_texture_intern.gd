extends RefCounted
# Identical immutable imported texture payloads share their existing Texture2D.
# No recompression, resizing, material substitution, geometry or identity changes.
var pending: Array[WeakRef] = []
var materials: Dictionary = {}
var textures: Dictionary = {}
var canonical: Dictionary = {}
var examined := 0
var replacements := 0
var duplicate_payload_bytes := 0
func observe(node: Node) -> void:
	if node is MeshInstance3D:
		pending.append(weakref(node))
		intern_mesh(node)
func intern_mesh(mesh: MeshInstance3D) -> void:
	if mesh == null or mesh.mesh == null: return
	for surface in range(mesh.mesh.get_surface_count()):
		intern_material(mesh.mesh.surface_get_material(surface))
		intern_material(mesh.get_active_material(surface))
	intern_material(mesh.material_overlay)
func flush() -> void:
	for reference in pending:
		intern_mesh(reference.get_ref() as MeshInstance3D)
	pending.clear()
func intern_material(material: Material) -> void:
	if material == null: return
	var identity := material.get_instance_id()
	if materials.has(identity) and materials[identity].get_ref() == material: return
	materials[identity] = weakref(material)
	if material is BaseMaterial3D:
		for property in material.get_property_list():
			if int(property.type) != TYPE_OBJECT or not (int(property.usage) & PROPERTY_USAGE_STORAGE): continue
			var value = material.get(str(property.name))
			if not (value is ImageTexture or value is CompressedTexture2D): continue
			var path := str(value.resource_path)
			if not (path.begins_with("res://assets/models/") or path.begins_with("res://assets/runtime/startup_residency_20261020/") or path.begins_with("res://.godot/imported/")): continue
			var shared := intern_texture(value)
			if shared != value:
				material.set(str(property.name),shared)
				replacements += 1
	intern_material(material.next_pass)
func intern_texture(texture: Texture2D) -> Texture2D:
	var identity := texture.get_instance_id()
	if textures.has(identity) and textures[identity].original.get_ref() == texture:
		return textures[identity].shared
	var pixels := texture.get_image()
	if pixels == null or pixels.is_empty(): return texture
	var bytes := pixels.get_data()
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	var key := "%s:%d:%d:%d:%d:%d:%s:%s:%s" % [texture.get_class(),texture.get_width(),texture.get_height(),pixels.get_width(),pixels.get_height(),pixels.get_format(),str(pixels.has_mipmaps()),str(texture.has_alpha()),hash.finish().hex_encode()]
	var shared: Texture2D = canonical.get(key,texture)
	if shared == texture:
		canonical[key] = texture
	else:
		duplicate_payload_bytes += bytes.size()
	textures[identity] = {"original":weakref(texture),"shared":shared}
	examined += 1
	return shared
func statistics() -> Dictionary:
	return {"examined_textures":examined,"unique_payloads":canonical.size(),"material_slot_replacements":replacements,"duplicate_payload_bytes":duplicate_payload_bytes,"policy":"identical format, dimensions, mipmaps and complete payload; original material objects retained"}

func prune_expired_references() -> void:
	for identity in textures.keys():
		if textures[identity].original.get_ref()==null:textures.erase(identity)
	for identity in materials.keys():
		if materials[identity].get_ref()==null:materials.erase(identity)
