extends RefCounted

static func build(parent: Node3D, top_material: Material, side_material: Material) -> Node3D:
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
		top.set_material(top_material)
		edges.set_material(side_material)
		var mesh: ArrayMesh = top.commit()
		edges.commit(mesh)
		var instance := MeshInstance3D.new()
		instance.name = region.id
		instance.mesh = mesh
		instance.set_meta("region_id",region.id)
		instance.set_meta("coverage","structural_only")
		group.add_child(instance)
		instance.create_trimesh_collision()
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
