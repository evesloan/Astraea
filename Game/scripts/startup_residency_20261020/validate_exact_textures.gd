extends SceneTree
func _initialize() -> void: call_deferred("run")
func digest(texture: Texture2D) -> String:
	var image := texture.get_image()
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(image.get_data())
	return "%s:%d:%d:%d:%d:%d:%s:%s:%s" % [texture.get_class(),texture.get_width(),texture.get_height(),image.get_width(),image.get_height(),image.get_format(),str(image.has_mipmaps()),str(texture.has_alpha()),hash.finish().hex_encode()]
func material_state(material: Material) -> Dictionary:
	var state: Dictionary = {}
	for property in material.get_property_list():
		if not (int(property.usage) & PROPERTY_USAGE_STORAGE): continue
		var value = material.get(str(property.name))
		if value is Texture2D: continue
		state[str(property.name)] = value
	return state
func run() -> void:
	var interner = load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
	var instances: Array[Node3D] = []
	var rows: Array[Dictionary] = []
	var old_textures: Dictionary = {}
	for file in ["AST-DOR-001.glb","AST-DOR-002.glb","AST-CIR-003_three_stop.glb"]:
		var packed := load("res://assets/models/"+file) as PackedScene
		var instance := packed.instantiate() as Node3D
		instances.append(instance)
		root.add_child(instance)
		for mesh: MeshInstance3D in instance.find_children("*","MeshInstance3D",true,false):
			interner.pending.append(weakref(mesh))
			for surface in range(mesh.mesh.get_surface_count()):
				var material := mesh.get_active_material(surface)
				if not material is BaseMaterial3D: continue
				for property in material.get_property_list():
					if int(property.type) != TYPE_OBJECT or not (int(property.usage) & PROPERTY_USAGE_STORAGE): continue
					var value = material.get(str(property.name))
					if not (value is ImageTexture or value is CompressedTexture2D): continue
					old_textures[value.get_instance_id()] = weakref(value)
					rows.append({"mesh":weakref(mesh),"mesh_id":mesh.mesh.get_instance_id(),"transform":mesh.transform,"surface":surface,"material_id":material.get_instance_id(),"material_state":material_state(material),"property":str(property.name),"digest":digest(value),"texture_id":value.get_instance_id(),"path":value.resource_path})
		packed = null
	var before := OS.get_static_memory_usage()
	interner.flush()
	var changed := 0
	for row in rows:
		var mesh := row.mesh.get_ref() as MeshInstance3D
		assert(mesh.mesh.get_instance_id() == row.mesh_id and mesh.transform == row.transform)
		var material := mesh.get_active_material(row.surface)
		assert(material.get_instance_id() == row.material_id)
		assert(material_state(material) == row.material_state,"Non-texture material/UV/sampling properties changed")
		var texture := material.get(row.property) as Texture2D
		assert(digest(texture) == row.digest, "Texture semantic payload changed")
		if texture.get_instance_id() != row.texture_id: changed += 1
	await process_frame
	var released := 0
	for reference in old_textures.values():
		if reference.get_ref() == null: released += 1
	print("EXACT_TEXTURE_INTERN_VALIDATION ",JSON.stringify({"slots_checked":rows.size(),"changed_slots":changed,"original_textures_released":released,"before_static":before,"after_static":OS.get_static_memory_usage(),"statistics":interner.statistics(),"sample_paths":rows.slice(0,3).map(func(row): return row.path)}))
	assert(changed > 0 and released > 0,"No proven texture release")
	for instance in instances: instance.free()
	quit()
