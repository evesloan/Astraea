extends RefCounted
const P := "res://orchard_tram_interior_20261025/integration/"

static func apply(ship: Node3D) -> bool:
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P+"PIT_AND_BINDING.json"))
	if FileAccess.get_sha256("res://data/generated/structural_meshes.json") != proof.compiled_source_sha256:
		push_error("Orchard pit source mismatch");return false
	var parent := ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	var original: Node3D = parent.get_node(proof.before.id)
	if original.has_meta("orchard_pit_successor"):
		push_error("Duplicate Orchard floor receiving");return false
	var actual: Array = []
	for shape: CollisionShape3D in original.find_children("*","CollisionShape3D",true,false):
		if not shape.shape is ConcavePolygonShape3D:return false
		var faces: PackedVector3Array = shape.shape.get_faces()
		for i in range(0,faces.size(),3):
			var tri: Array = []
			for j in range(3):tri.append(shape.global_transform*faces[i+j])
			if absf(tri[0].y-52.5)<.00002 and absf(tri[1].y-52.5)<.00002 and absf(tri[2].y-52.5)<.00002:actual.append(tri)
	if actual.size()!=proof.before.triangles.size():
		push_error("Orchard original floor triangle count differs");return false
	for i in range(actual.size()):
		for point: Vector3 in actual[i]:
			var matched := false
			for p: Array in proof.before.triangles[i]:
				if point.distance_to(Vector3(p[0],52.5,p[1]))<.00002:matched=true
			if not matched:push_error("Orchard original floor triangle differs");return false
	# Stage the exact replacement with inherited materials; keep the floor owner ID.
	var material: Material = null
	var side: Material = null
	for visual: MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
		if visual.mesh.get_surface_count()==2:
			material=visual.get_active_material(0);side=visual.get_active_material(1);break
	if material==null or side==null:push_error("Original retail floor materials unavailable");return false
	var builder = load("res://scripts/structural_floor_builder.gd")
	var staged: Node3D = builder.build_regions(ship.get_node("ShipSpace"),material,side,[proof.after],{"guest_floor":material},"OrchardFloorReceivingStaging")
	var replacement: Node3D = staged.get_node(proof.after.id)
	for key: StringName in original.get_meta_list():replacement.set_meta(key,original.get_meta(key))
	original.free()
	replacement.reparent(parent,true)
	replacement.name=proof.after.id
	replacement.set_meta("orchard_pit_successor",true)
	replacement.set_meta("pit_removed_m2",proof.removed_m2)
	staged.free()
	var infill: Node3D=builder.build_regions(ship.get_node("ShipSpace"),material,side,[proof.old_pit_infill],{"guest_floor":material},"RetiredForemidPitClosure")
	infill.set_meta("new_room_or_capacity",false)
	return true
