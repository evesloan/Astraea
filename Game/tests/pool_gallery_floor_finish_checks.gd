extends RefCounted
static func check(owner: RefCounted) -> void:
	var spec: Dictionary=owner.data.floor_finish
	var floor:=owner.ship.get_node(NodePath("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/"+str(spec.owner))) as Node3D
	var before: Dictionary=floor.get_meta("gallery_finish_before")
	var selected: Array=floor.get_meta("gallery_finish_selected")
	var material: ShaderMaterial=floor.get_meta("gallery_finish_material")
	assert(FileAccess.get_sha256(str(spec.shader))==str(spec.shader_sha256) and material.shader==load(str(spec.shader)))
	assert(material.get_shader_parameter("retained_stone")==owner.ship.stone.albedo_texture)
	assert(material.get_shader_parameter("finish_mineral")==load(str(spec.finish_texture)))
	assert(material.get_shader_parameter("finish_enabled")==true)
	var bounds: Array=spec.bounds_xz
	assert(material.get_shader_parameter("finish_bounds")==Vector4(bounds[0],bounds[1],bounds[2],bounds[3]))
	var unchanged_surfaces:=0;var finished_surfaces:=0;var vertices:=0
	for name in before:
		var mesh:=floor.get_node(NodePath(str(name))) as MeshInstance3D
		var old: Dictionary=before[name]
		assert(mesh.mesh==old.mesh and mesh.transform==Transform3D.IDENTITY)
		assert(mesh.mesh.surface_get_arrays(0)==old.arrays,"Floor finish changed a vertex, index, normal or UV")
		assert(mesh.mesh.surface_get_material(0)==old.material and mesh.material_override==null and mesh.material_overlay==null)
		vertices+=old.arrays[Mesh.ARRAY_VERTEX].size()
		if str(name) in selected:
			assert(str(name)!="StructuralSidesAndUnderside" and mesh.get_surface_override_material(0)==material)
			finished_surfaces+=1
		else:
			assert(mesh.get_surface_override_material(0)==old.override and mesh.get_active_material(0)==old.material)
			unchanged_surfaces+=1
	var contacts: Dictionary=floor.get_meta("gallery_finish_contacts")
	for path in contacts:
		var shape:=floor.get_node(NodePath(str(path))) as CollisionShape3D
		assert(shape.shape.get_faces()==contacts[path],"Floor finish changed the retained collider")
	assert(finished_surfaces==selected.size() and unchanged_surfaces>0)
	# Boundary semantics: no new mesh/pass; shader remains exactly retained stone outside.
	for p in [[-17.81,-448],[-8.14,-448],[-13,-461.11],[-13,-435.39]]:
		assert(not(float(p[0])>=float(bounds[0])and float(p[0])<=float(bounds[1])and float(p[1])>=float(bounds[2])and float(p[1])<=float(bounds[3])))
	owner.records["gallery_floor_finish"]={"owner":spec.owner,"retained_vertices_indices_normals_uvs_exact":vertices,"retained_colliders_exact":contacts.size(),"top_chunks_material_only":finished_surfaces,"untouched_surfaces":unchanged_surfaces,"bounds_xz":bounds,"outside_material_inputs_unchanged":true,"outside_native_pixel_comparison_pending":true,"new_floor_owners":0}
	print("POOL GALLERY FLOOR FINISH PASS: exact existing mesh/UV/collider resources, bounded top material only, original sides and outside material inputs retained")
