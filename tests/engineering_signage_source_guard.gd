extends RefCounted
# Test-only actual imported backing/ink proof; original gate collision stays authoritative.
static func _xyz(row: Array) -> Vector3:
	return Vector3(float(row[0]),float(row[1]),float(row[2]))
static func validate(cell: Node3D) -> bool:
	assert(load("res://scripts/engineering_cell_signage.gd").live_binding_valid(cell))
	var data: Dictionary=cell.get_meta("signage_contract")
	var fixed := cell.get_meta("signage_fixed") as MeshInstance3D
	var ink := cell.get_meta("signage_print") as MeshInstance3D
	var leaf := cell.get_meta("signage_original_leaf") as MeshInstance3D
	var backing := cell.find_child("SectionStatic_0_WORKBAY",true,false) as MeshInstance3D
	assert(backing!=null and leaf.name=="LEAF_WORKBAY_CELL")
	var scene_space := cell.get_world_3d().direct_space_state
	var support_hits: Array=[]
	for y in [8.65,8.715,8.78]:
		for z in [-406.42,-405.8,-405.125,-404.45,-403.83]:
			var hit := scene_space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(27.18,y,z),Vector3(27.13,y,z),1))
			assert(not hit.is_empty() and backing.is_ancestor_of(hit.collider))
			assert(absf(hit.position.x-27.15)<.00005 and hit.normal.x>.99)
			support_hits.append([hit.position.x,hit.position.y,hit.position.z])
	var glass := PackedVector3Array()
	for surface in range(leaf.mesh.get_surface_count()):
		if str(leaf.get_active_material(surface).resource_name)!="ASTRAEA_bridge_pressure_glass": continue
		var arrays := leaf.mesh.surface_get_arrays(surface)
		glass=arrays[Mesh.ARRAY_VERTEX]
	assert(glass.size()>=4)
	var glass_box := AABB(glass[0],Vector3.ZERO)
	for p in glass:glass_box=glass_box.expand(p)
	assert(glass_box.size.x<.00001 and glass_box.size.y>2.29 and glass_box.size.z>1.19)
	var minimum_gap := INF
	var maximum_gap := -INF
	for point in load("res://scripts/engineering_cell_signage.gd").raw_render_faces(ink.mesh):
		var local: Vector3=ink.transform*point
		var gap: float=glass_box.position.x-local.x
		minimum_gap=minf(minimum_gap,gap);maximum_gap=maxf(maximum_gap,gap)
		assert(gap>.00015 and gap<.00025,"Imported ink must remain ahead of actual source glass, not quantized into it")
		assert(local.y>glass_box.position.y+.04 and local.y<glass_box.end.y-.04)
		assert(local.z>glass_box.position.z+.04 and local.z<glass_box.end.z-.04)
	var geometry := PackedFloat32Array()
	var uvs := PackedFloat32Array()
	var groups: Array=[]
	for value in [fixed,ink]:
		var mesh := value as MeshInstance3D
		var label := str(mesh.name)
		var expected: Dictionary=data.groups[label]
		var faces: PackedVector3Array=load("res://scripts/engineering_cell_signage.gd").raw_render_faces(mesh.mesh)
		var box := AABB(mesh.global_transform*faces[0],Vector3.ZERO)
		for p in faces:box=box.expand(mesh.global_transform*p)
		assert(box.position.distance_to(_xyz(expected.bounds_xyz.slice(0,3)))<.001 and box.end.distance_to(_xyz(expected.bounds_xyz.slice(3,6)))<.001)
		var surfaces: Array=[]
		for surface in range(mesh.mesh.get_surface_count()):
			var arrays: Array = mesh.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
			var texcoords: PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV]
			var indices := PackedInt32Array()
			if arrays[Mesh.ARRAY_INDEX]!=null: indices=arrays[Mesh.ARRAY_INDEX]
			if indices.is_empty():
				for vertex_index in range(vertices.size()):indices.append(vertex_index)
			assert(texcoords.size()==vertices.size() and not indices.is_empty() and indices.size()%3==0)
			var offset := geometry.size()/9
			for index in indices:
				var p: Vector3=mesh.global_transform*vertices[index]
				geometry.append(p.x);geometry.append(p.y);geometry.append(p.z)
				uvs.append(texcoords[index].x);uvs.append(texcoords[index].y)
			surfaces.append({"material":str(mesh.get_active_material(surface).resource_name),"triangle_offset":offset,"triangles":indices.size()/3})
		groups.append({"name":label,"surfaces":surfaces})
	assert(geometry.size()/9==6672)
	var raw := FileAccess.open("res://artifacts/engineering_signage_triangles.float32",FileAccess.WRITE)
	assert(raw!=null);raw.store_buffer(geometry.to_byte_array());raw.close()
	var texture_dump := FileAccess.open("res://artifacts/engineering_signage_uv.float32",FileAccess.WRITE)
	assert(texture_dump!=null);texture_dump.store_buffer(uvs.to_byte_array());texture_dump.close()
	var file := FileAccess.open("res://artifacts/engineering_signage_imported_source.json",FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify({"status":"IMPORTED_CONTACT_GATE_PASS_REQUIRES_OFFLINE_EQUIVALENCE","model_sha256":data.model_sha256,"groups":groups,"header_source_contacts":support_hits,"minimum_ink_glass_gap_m":minimum_gap,"maximum_ink_glass_gap_m":maximum_gap,"triangles":6672,"uv_coordinate_order":"Godot native imported UV","scope":"Actual backing and source-glass relation. Triangle/UV comparison and normal-view reading remain separate."},"  ")+"\n");file.close()
	return true
