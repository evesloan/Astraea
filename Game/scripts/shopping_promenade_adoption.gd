extends RefCounted
# Construction-only adoption; immutable footprint IDs preserve unresolved address mappings.
static func build(ship:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHOPPING_PROMENADE.json"))
	var root:=Node3D.new()
	root.name="ShoppingPromenadeChunks"
	ship.get_node("ShipSpace/Districts").add_child(root)
	var regions:Array=[]
	for record in d.floor_proposals:
		var rings:Array=[record.boundary]
		rings.append_array(record.holes)
		regions.append({"id":record.id,"deck":"D09","floor_y":52.5,"thickness":record.thickness,"triangles":record.triangles_xz,"rings":rings,"render_chunks":record.render_chunks})
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,regions,{},"ShoppingPromenadeOwnedFloors")
	var opaque_faces:Dictionary={}
	for face in d.opaque_surfaces:
		if not opaque_faces.has(str(face.chunk_id)):opaque_faces[str(face.chunk_id)]=[]
		var vertices:Array=face.local_vertices_godot
		for index in face.triangles:
			var v:Array=vertices[index]
			opaque_faces[str(face.chunk_id)].append(Vector3(v[0],v[1],v[2]))
	var by_id:Dictionary={}
	var proven:=0
	for row in d.chunks:
		var chunk:=Node3D.new()
		chunk.name=str(row.chunk_id)
		chunk.position=Vector3(row.position[0],row.position[1],row.position[2])
		root.add_child(chunk)
		chunk.set_meta("source_chunk_id",row.chunk_id)
		chunk.set_meta("finished",false)
		if row.get("stable_room_id")!=null:
			chunk.set_meta("stable_room_id",row.stable_room_id)
			proven+=1
		if row.get("proposed_room_id")!=null:chunk.set_meta("unapproved_address_proposal",row.proposed_room_id)
		for layer in row.layers:
			assert(FileAccess.get_sha256(str(row.layers[layer].path))==str(row.layers[layer].sha256))
		var bounds:=AABB()
		var first:=true
		for layer in ["shell","fitout"]:
			var key:String=str(row.chunk_id)+"__"+layer
			if not d.local_bounds.has(key):continue
			var box:Dictionary=d.local_bounds[key]
			var low:=Vector3(box.min[0],box.min[1],box.min[2])
			var high:=Vector3(box.max[0],box.max[1],box.max[2])
			var part:=AABB(low,high-low)
			bounds=part if first else bounds.merge(part)
			first=false
		assert(not first)
		chunk.set_meta("deferred_visual_path",row.visual_scene)
		chunk.set_meta("deferred_visual_bounds",bounds)
		chunk.set_meta("deferred_visual_meshes",row.visual_mesh_count)
		chunk.set_meta("deferred_visual_collision_policy",d.node_policy)
		if opaque_faces.has(str(row.chunk_id)):
			var occluder:OccluderInstance3D=load("res://scripts/architectural_occlusion.gd").from_faces(ship.get_node("ShipSpace"),PackedVector3Array(opaque_faces[str(row.chunk_id)]),str(row.chunk_id)+"_RetainedOpaqueOccluder")
			occluder.position=chunk.position
		by_id[str(row.chunk_id)]=chunk
	assert(root.get_child_count()==177 and proven==15)
	var lights:Array[Light3D]=[]
	for spec in d.lights:
		assert(by_id.has(str(spec.chunk_id)))
		var light:Light3D
		if spec.kind=="SpotLight3D":
			var spot:=SpotLight3D.new()
			spot.spot_range=minf(float(spec.range_m),8.0)
			spot.spot_angle=float(spec.angle_deg)
			spot.rotation_degrees.x=-90
			light=spot
		else:
			var omni:=OmniLight3D.new()
			omni.omni_range=minf(float(spec.range_m),8.0)
			light=omni
		light.name=str(spec.id)
		light.position=Vector3(spec.local_xyz[0],spec.local_xyz[1],spec.local_xyz[2])
		light.light_color=Color(spec.colour[0],spec.colour[1],spec.colour[2])
		light.light_energy=float(spec.energy)
		light.visible=false
		light.shadow_enabled=false
		by_id[str(spec.chunk_id)].add_child(light)
		lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	root.set_meta("new_shops",99)
	root.set_meta("unresolved_address_joins",84)
	root.set_meta("final_art_accepted",false)
	return root
