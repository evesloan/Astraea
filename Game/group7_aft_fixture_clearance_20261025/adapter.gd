extends RefCounted
const BASE="res://group7_aft_fixture_clearance_20261025/"
const ROOT="ShipSpace/Districts/AftCrownPlatform_WIP"
static func digest(mesh:Mesh)->String:
	var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256)
	for surface in mesh.get_surface_count():h.update(var_to_bytes(mesh.surface_get_arrays(surface)))
	return h.finish().hex_encode()
static func meshes(packed:PackedScene)->Dictionary:
	var state:=packed.get_state();var result:Dictionary={}
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)==&"mesh":result[str(state.get_node_name(n))]=state.get_node_property_value(n,p)
	return result
static func selected(p:Vector3)->bool:
	return absf(p.x)<=.721 and p.y>=110.469 and p.y<=111.241 and p.z>=193.479 and p.z<=193.921
static func partition_indices(bytes:PackedByteArray,stride:int,vertices:PackedVector3Array,wanted:bool)->PackedByteArray:
	var result:=PackedByteArray()
	for at in range(0,bytes.size(),stride*3):
		var matches:=0
		for j in 3:
			var i:int=bytes.decode_u16(at+j*stride) if stride==2 else bytes.decode_u32(at+j*stride)
			if selected(vertices[i]):matches+=1
		if matches!=0 and matches!=3:push_error("Fixture intersects a retained triangle");return PackedByteArray()
		if (matches==3)==wanted:result.append_array(bytes.slice(at,at+stride*3))
	return result
static func partition(source:ArrayMesh,wanted:bool)->ArrayMesh:
	# Copy encoded vertex/attribute bytes and their decoding AABB verbatim.
	# Only triangle indices change; no normal, tangent or UV re-encoding.
	var surfaces:Array=source.get("_surfaces").duplicate(true)
	for s in surfaces.size():
		var d:Dictionary=surfaces[s]
		var vertices:PackedVector3Array=source.surface_get_arrays(s)[Mesh.ARRAY_VERTEX]
		var stride:int=RenderingServer.mesh_surface_get_format_index_stride(int(d.format),int(d.vertex_count))
		d.index_data=partition_indices(d.index_data,stride,vertices,wanted)
		d.index_count=d.index_data.size()/stride
		if d.index_count==0:return null
		# The source LOD removes this tiny housing entirely in one level.
		# Keep full original triangles for these two 24-triangle batches;
		# do not fabricate a mixed LOD or make the required fixture disappear.
		d.erase("lods")
	var result:=ArrayMesh.new();result.set("_surfaces",surfaces)
	# The main exact triangles cast shadows. The old fused shadow mesh spans
	# both partitions and must not be attached to either subset.
	return result
static func build(ship:Node3D)->bool:
	var owner:=ship.get_node_or_null(ROOT)
	if owner==null or owner.has_meta("fixture_clearance_r002"):
		push_error("Missing or already revised aft fixture owner");return false
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(BASE+"BUILD_RECEIPT.json"))
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(BASE+"RESOURCE_PROOF.json"))
	if FileAccess.get_sha256("res://assets/models/AST-CMD-005.glb")!=str(receipt.baseline_model_sha256) or FileAccess.get_sha256(BASE+"AST-CMD-005_fixture_clearance_r002.glb")!=str(receipt.successor_model_sha256):
		push_error("Aft fixture source bytes changed");return false
	var changes:Array=[]
	for row:Dictionary in proof.batches:
		var node:=owner.find_child(str(row.name),true,false) as MeshInstance3D
		if node==null or digest(node.mesh)!=str(row.before_sha256):push_error("Aft fixture preimage differs");return false
		var contacts:=node.find_children("*","CollisionShape3D",true,false)
		if contacts.size()!=1 or not contacts[0].shape is ConcavePolygonShape3D:push_error("Aft fixture contact ownership differs");return false
		var shape:CollisionShape3D=contacts[0]
		if shape.shape.get_faces()!=node.mesh.get_faces():push_error("Aft fixture contacts differ from source triangles");return false
		var moved:ArrayMesh=node.mesh if row.whole_batch else partition(node.mesh,true)
		var retained:ArrayMesh=null if row.whole_batch else partition(node.mesh,false)
		if moved==null or digest(moved)!=str(row.moved_sha256) or (not row.whole_batch and (retained==null or digest(retained)!=str(row.retained_sha256))):push_error("Aft fixture successor differs");return false
		changes.append({"node":node,"shape":shape,"moved":moved,"retained":retained})
	var marker:=owner.find_child(str(receipt.fixture_marker),true,false) as Node3D
	var light:=owner.get_node_or_null("AftPlatformSource_"+str(receipt.fixture_marker)) as SpotLight3D
	if marker==null or light==null or marker.global_position.distance_to(Vector3(0,110.46,193.7))>.0001 or light.global_position.distance_to(marker.global_position)>.0001:
		push_error("Aft fixture marker/light preimage differs");return false
	# Preserve the lens nodes/resources. Split only the two housing batches;
	# duplicated physical bodies retain layers/masks and all collision settings.
	for row:Dictionary in changes:
		if row.retained==null:
			row.node.position.y+=float(receipt.delta_y_m)
			continue
		var moved:MeshInstance3D=row.node.duplicate(0)
		moved.name=str(row.node.name)+"_Fixture50mm"
		moved.mesh=row.moved
		var moved_contact:CollisionShape3D=moved.find_children("*","CollisionShape3D",true,false)[0]
		var moving_shape:ConcavePolygonShape3D=row.moved.create_trimesh_shape()
		moving_shape.margin=row.shape.shape.margin;moving_shape.backface_collision=row.shape.shape.backface_collision
		moved_contact.shape=moving_shape
		var retained_shape:ConcavePolygonShape3D=row.retained.create_trimesh_shape()
		retained_shape.margin=row.shape.shape.margin;retained_shape.backface_collision=row.shape.shape.backface_collision
		row.node.mesh=row.retained;row.shape.shape=retained_shape
		moved.position.y+=float(receipt.delta_y_m);row.node.get_parent().add_child(moved)
	marker.position.y+=float(receipt.delta_y_m);light.position.y+=float(receipt.delta_y_m)
	owner.set_meta("fixture_clearance_r002",true)
	owner.set_meta("fixture_clearance_source",str(receipt.successor_model_sha256))
	return true
