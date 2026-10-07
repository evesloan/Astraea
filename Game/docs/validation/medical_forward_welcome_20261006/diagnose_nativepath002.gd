extends "res://tests/validate_medical_structure.gd"
# Scratch-only comparator diagnosis on the actual installed world.
func _initialize() -> void:
	test_name="medical_structure_nativepath_trial";call_deferred("run")

func triangle_multiset(faces: PackedVector3Array, pose: Transform3D=Transform3D.IDENTITY) -> Dictionary:
	var result: Dictionary={}
	if not require(faces.size()%3==0,"Complete triangle triples required"): return {}
	for i in range(0,faces.size(),3):
		var vertices: Array[String]=[]
		for j in range(3):
			var point: Vector3=pose*faces[i+j]
			vertices.append(var_to_bytes(point).hex_encode())
		vertices.sort()
		var key: String="|".join(PackedStringArray(vertices))
		result[key]=int(result.get(key,0))+1
	return result

func record_top_faces(triangles: Array, y: float) -> PackedVector3Array:
	var result: PackedVector3Array=[]
	for triangle in triangles:
		for point in triangle: result.append(Vector3(float(point[0]),y,float(point[1])))
	return result

func render_input_faces(mesh: Mesh) -> PackedVector3Array:
	var result: PackedVector3Array=[]
	for surface in range(mesh.get_surface_count()):
		var arrays: Array=mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: Variant=arrays[Mesh.ARRAY_INDEX]
		if indices!=null and indices.size()>0:
			for index in indices: result.append(vertices[index])
		else: result.append_array(vertices)
	return result

func verify_actual_slab(record: Dictionary) -> bool:
	var owner: Node3D=floors.get_node(str(record.id)) as Node3D
	var y: float=float(record.floor_y);var depth: float=float(record.thickness)
	var top: PackedVector3Array=record_top_faces(record.triangles,y)
	var edges: PackedVector3Array=[]
	for point in top: edges.append(point-Vector3.UP*depth)
	for ring in record.rings:
		for i in range(ring.size()):
			var p: Array=ring[i];var q: Array=ring[(i+1)%ring.size()]
			var a: Vector3=Vector3(float(p[0]),y,float(p[1]));var b: Vector3=Vector3(float(q[0]),y,float(q[1]))
			var bottom_a: Vector3=a-Vector3.UP*depth;var bottom_b: Vector3=b-Vector3.UP*depth
			for vertex in [a,b,bottom_b,a,bottom_b,bottom_a]: edges.append(vertex)
	var complete: PackedVector3Array=top.duplicate();complete.append_array(edges)
	var contacts: Array=owner.find_children("*","CollisionShape3D",true,false)
	if not require(contacts.size()==1,"One exact compiled medical collision shape required"): return false
	var contact: CollisionShape3D=contacts[0] as CollisionShape3D
	if not require(contact.shape is ConcavePolygonShape3D,"Medical floor must keep its faithful concave slab contact"): return false
	var actual: PackedVector3Array=(contact.shape as ConcavePolygonShape3D).get_faces()
	# Production creates its contact through ArrayMesh/TriangleMesh. This exact
	# native path has a float32 codec step; raw render inputs are checked separately.
	var expected_arrays: Array=[];expected_arrays.resize(Mesh.ARRAY_MAX)
	expected_arrays[Mesh.ARRAY_VERTEX]=complete
	var expected_mesh: ArrayMesh=ArrayMesh.new()
	expected_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,expected_arrays)
	var expected_contact: ConcavePolygonShape3D=expected_mesh.create_trimesh_shape()
	var native_expected: PackedVector3Array=expected_contact.get_faces()
	if not require(triangle_multiset(actual,contact.global_transform)==triangle_multiset(native_expected),"Actual medical collision triangles differ from the complete compiled slab"): return false
	var visuals: Array=owner.find_children("*","MeshInstance3D",true,false)
	if not require(visuals.size()==record.render_chunks.size()+1,"Exact bounded render chunks and edge mesh required"): return false
	for chunk in record.render_chunks:
		var visual: MeshInstance3D=owner.get_node(str(chunk.id)) as MeshInstance3D
		if not require(triangle_multiset(render_input_faces(visual.mesh),visual.global_transform)==triangle_multiset(record_top_faces(chunk.triangles,y)),"Actual render chunk differs from compiled triangles: "+str(chunk.id)): return false
	var side: MeshInstance3D=owner.get_node("StructuralSidesAndUnderside") as MeshInstance3D
	if not require(triangle_multiset(render_input_faces(side.mesh),side.global_transform)==triangle_multiset(edges),"Actual underside/closure geometry differs from compiled slab"): return false
	metrics["exact_actual_contact_triangles"]=actual.size()/3
	metrics["exact_actual_render_chunks"]=record.render_chunks.size()
	return true

