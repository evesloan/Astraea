extends RefCounted
# Material-only successor on the existing compiler-owned top surfaces.
static func build(ship: Node3D, data: Dictionary) -> void:
	var spec: Dictionary=data.floor_finish
	assert(FileAccess.get_sha256(str(spec.shader))==str(spec.shader_sha256))
	assert(FileAccess.get_sha256(str(spec.finish_texture))==str(spec.finish_texture_sha256))
	var floor:=ship.get_node(NodePath("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/"+str(spec.owner))) as Node3D
	assert(floor!=null and not floor.has_meta("gallery_finish_before"))
	var material:=ShaderMaterial.new()
	material.shader=load(str(spec.shader))
	material.set_shader_parameter("retained_stone",ship.stone.albedo_texture)
	material.set_shader_parameter("finish_mineral",load(str(spec.finish_texture)))
	var b: Array=spec.bounds_xz
	material.set_shader_parameter("finish_bounds",Vector4(b[0],b[1],b[2],b[3]))
	material.set_shader_parameter("finish_enabled",true)
	assert(ship.stone.albedo_color==Color.WHITE and is_equal_approx(ship.stone.roughness,.83) and ship.stone.metallic==0 and ship.stone.metallic_specular==.5)
	assert(ship.stone.texture_filter==BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS)
	var before: Dictionary={}
	var selected: Array[String]=[]
	for node in floor.get_children():
		if not node is MeshInstance3D:continue
		var mesh:=node as MeshInstance3D
		assert(mesh.transform==Transform3D.IDENTITY and mesh.mesh.get_surface_count()==1)
		var arrays: Array=mesh.mesh.surface_get_arrays(0)
		before[str(mesh.name)]={"mesh":mesh.mesh,"arrays":arrays.duplicate(true),"material":mesh.get_active_material(0),"override":mesh.get_surface_override_material(0)}
		if str(mesh.name)=="StructuralSidesAndUnderside":continue
		assert(mesh.get_active_material(0)==ship.stone and mesh.get_surface_override_material(0)==null)
		var box: AABB=mesh.mesh.get_aabb()
		if box.end.x<=float(b[0]) or box.position.x>=float(b[1]) or box.end.z<=float(b[2]) or box.position.z>=float(b[3]):continue
		for vertex in arrays[Mesh.ARRAY_VERTEX]:assert(absf(vertex.y-float(spec.floor_y))<.00001)
		mesh.set_surface_override_material(0,material)
		selected.append(str(mesh.name))
	assert(not selected.is_empty())
	var contacts: Dictionary={}
	for shape in floor.find_children("*","CollisionShape3D",true,false):
		assert(shape.shape is ConcavePolygonShape3D)
		contacts[str(floor.get_path_to(shape))]=shape.shape.get_faces()
	floor.set_meta("gallery_finish_before",before)
	floor.set_meta("gallery_finish_contacts",contacts)
	floor.set_meta("gallery_finish_selected",selected)
	floor.set_meta("gallery_finish_material",material)
	floor.set_meta("gallery_finish_bounds",spec.bounds_xz)
