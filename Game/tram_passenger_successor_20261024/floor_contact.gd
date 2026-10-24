extends RefCounted
# Unselected exact primitive successor for the proved eight-corner source floor.
# Apply only during fresh empty construction, before any passenger/cart enters.
const P := "res://tram_passenger_successor_20261024/"

static func apply_to_empty_vehicle(body: AnimatableBody3D) -> Dictionary:
	var report := {"status":"HELD", "changed_contacts":0, "visuals_changed":false}
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P + "SOURCE_PROOF.json"))
	if FileAccess.get_sha256(proof.vehicle_source) != proof.vehicle_sha256:
		report.reason = "Exact retained source024 bytes differ"
		return report
	if body.has_meta("exact_floor_primitive_successor") or body.has_meta("group4_source_actuator"):
		report.reason = "Only a fresh unmotorized empty source vehicle may receive this contact representation"
		return report
	var meshes: Array[Node] = body.find_children("V2__Tram_Floor", "MeshInstance3D", true, false)
	if meshes.size() != 1:
		report.reason = "Expected exactly one original source floor mesh"
		return report
	var floor_mesh: MeshInstance3D = meshes[0]
	var expected_lo := Vector3(proof.floor_min[0], proof.floor_min[1], proof.floor_min[2])
	var expected_hi := Vector3(proof.floor_max[0], proof.floor_max[1], proof.floor_max[2])
	var local_pose := body.global_transform.affine_inverse() * floor_mesh.global_transform
	var selected: CollisionShape3D
	var original_points := PackedVector3Array()
	for child: Node in body.get_children():
		if not child is CollisionShape3D:
			continue
		var col: CollisionShape3D = child
		if not col.shape is ConvexPolygonShape3D:
			continue
		if not col.transform.is_equal_approx(local_pose):
			continue
		var points: PackedVector3Array = col.shape.points
		if points.size() != 8:
			continue
		var exact := true
		for x in [expected_lo.x, expected_hi.x]:
			for y in [expected_lo.y, expected_hi.y]:
				for z in [expected_lo.z, expected_hi.z]:
					if not points.has(Vector3(x,y,z)):
						exact = false
		if exact:
			if selected != null:
				report.reason = "Ambiguous duplicate original floor contacts"
				return report
			selected = col
			original_points = points
	if selected == null:
		report.reason = "Imported convex floor does not have all eight exact source corners; no approximation applied"
		return report
	var primitive := BoxShape3D.new()
	primitive.size = expected_hi - expected_lo
	primitive.margin = selected.shape.margin
	var center := (expected_lo + expected_hi) * .5
	for point: Vector3 in original_points:
		var reproduced := center + Vector3(signf(point.x-center.x),signf(point.y-center.y),signf(point.z-center.z)) * primitive.size * .5
		if reproduced != point:
			report.reason = "Primitive corner would not be bit-exact with the existing source floor"
			return report
	var original_transform := selected.transform
	var new_transform := original_transform * Transform3D(Basis.IDENTITY, center)
	# One collision node/owner/index retained. No mesh, actor, joint, contact layer,
	# friction, bounce, caster geometry, mass, CCD or physics setting is changed.
	selected.shape = primitive
	selected.transform = new_transform
	selected.set_meta("exact_source_floor_primitive", true)
	body.set_meta("exact_floor_primitive_successor", "20261024/r001_unaccepted")
	report.status = "APPLIED_EXACT_PRIMITIVE_UNACCEPTED"
	report.changed_contacts = 1
	report.size = primitive.size
	report.center = center
	report.margin = primitive.margin
	report.same_eight_corners = true
	report.original_collision_node = str(body.get_path_to(selected))
	return report
