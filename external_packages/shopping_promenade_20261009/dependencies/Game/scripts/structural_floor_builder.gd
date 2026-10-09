extends RefCounted

static func build(parent: Node3D, top_material: Material, side_material: Material, materials: Dictionary = {}) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var group := Node3D.new()
	group.name = "CompiledStructuralFloors_NotFinishedRooms"
	parent.add_child(group)
	for region in definition.regions:
		var y := float(region.floor_y)
		var thickness := float(region.thickness)
		var top := SurfaceTool.new()
		top.begin(Mesh.PRIMITIVE_TRIANGLES)
		var edges := SurfaceTool.new()
		edges.begin(Mesh.PRIMITIVE_TRIANGLES)
		for triangle in region.triangles:
			var a := Vector3(triangle[0][0],y,triangle[0][1])
			var b := Vector3(triangle[1][0],y,triangle[1][1])
			var c := Vector3(triangle[2][0],y,triangle[2][1])
			face(top,a,b,c,Vector3.UP)
			face(edges,a-Vector3.UP*thickness,b-Vector3.UP*thickness,c-Vector3.UP*thickness,Vector3.DOWN)
		for ring in region.rings:
			for index in range(ring.size()):
				var p = ring[index]
				var q = ring[(index+1)%ring.size()]
				var a := Vector3(p[0],y,p[1])
				var b := Vector3(q[0],y,q[1])
				var bottom_a := a-Vector3.UP*thickness
				var bottom_b := b-Vector3.UP*thickness
				var direction := b-a
				var normal := Vector3(direction.z,0,-direction.x).normalized()
				face(edges,a,b,bottom_b,normal)
				face(edges,a,bottom_b,bottom_a,normal)
		top.set_material(materials.get(region.get("material_role","guest_floor"),top_material))
		edges.set_material(side_material)
		var mesh: ArrayMesh = top.commit()
		edges.commit(mesh)
		var instance := Node3D.new()
		instance.name = region.id
		instance.set_meta("region_id",region.id)
		instance.set_meta("coverage","structural_only")
		group.add_child(instance)
		load("res://scripts/architectural_occlusion.gd").from_mesh(instance,mesh,"ActualOpaqueSlabOccluder")
		# Physics stays continuous; rendering is spatially bounded for local light limits.
		var body := StaticBody3D.new()
		var contact := CollisionShape3D.new()
		contact.shape = mesh.create_trimesh_shape()
		body.add_child(contact)
		instance.add_child(body)
		var chunks: Array = region.get("render_chunks",[])
		if chunks.is_empty():
			var visual := MeshInstance3D.new()
			visual.mesh = mesh
			instance.add_child(visual)
		else:
			for chunk in chunks:
				var tool := SurfaceTool.new()
				tool.begin(Mesh.PRIMITIVE_TRIANGLES)
				for triangle in chunk.triangles:
					face(tool,Vector3(triangle[0][0],y,triangle[0][1]),Vector3(triangle[1][0],y,triangle[1][1]),Vector3(triangle[2][0],y,triangle[2][1]),Vector3.UP)
				tool.set_material(materials.get(region.get("material_role","guest_floor"),top_material))
				var visual := MeshInstance3D.new()
				visual.name = chunk.id
				visual.mesh = tool.commit()
				instance.add_child(visual)
			var underside := MeshInstance3D.new()
			underside.name = "StructuralSidesAndUnderside"
			var edge_mesh := ArrayMesh.new()
			edge_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,mesh.surface_get_arrays(1))
			edge_mesh.surface_set_material(0,side_material)
			underside.mesh = edge_mesh
			instance.add_child(underside)

	return group

static func face(tool: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, normal: Vector3) -> void:
	if (b-a).cross(c-a).dot(normal)>0.0:
		var swap := b
		b = c
		c = swap
	for vertex in [a,b,c]:
		tool.set_normal(normal)
		tool.set_uv(Vector2(vertex.x*.3,vertex.z*.3) if absf(normal.y)>.9 else Vector2((vertex.x+vertex.z)*.3,vertex.y*.3))
		tool.add_vertex(vertex)
