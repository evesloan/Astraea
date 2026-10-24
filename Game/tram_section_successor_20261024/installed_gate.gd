extends RefCounted
# Caller-owned connected-world test; no vehicle/passenger transform is written.
# This cannot turn a bounded source fixture into a whole selected-ship receipt.
const P := "res://tram_section_successor_20261024/"

static func audit(assembly: Node3D, selected_ship: Node3D) -> Dictionary:
	var report := {"status":"HELD", "queries":0, "hits":[], "source_scope":"actual caller-supplied installed world", "motion_admitted":false}
	if not is_instance_valid(selected_ship) or not selected_ship.is_ancestor_of(assembly):
		report.reason = "Supply the actual selected ship with this named empty assembly; a fixture is not installed context"
		return report
	if not assembly.has_node("Group4LoadedSourceTravelActuator") or not assembly.has_node("Group4SourceOperatingControls"):
		report.reason = "Original loaded motor, articulated bogies, portals, restraint and mounted console must all exist before complete moving-assembly audit"
		return report
	var body: AnimatableBody3D = assembly.get_node("Group4OwnedTram_Source024")
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var motor: Node3D = assembly.get_node("Group4LoadedSourceTravelActuator")
	if motor.moving or safety.phase != "secured" or not safety.unloaded_clear_to_depart():
		report.reason = "Closed, stowed, stationary physical assembly required; never alter an occupied live tram for a test"
		return report
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P + "section_plan_r002.json"))
	var excludes: Array[RID] = [body.get_rid()]
	for child: CollisionObject3D in body.find_children("*", "CollisionObject3D", true, false):
		excludes.append(child.get_rid())
	# Deliberate rolling wheel/rail contact only. Shoes, hangers, panels, other
	# stations, hull, floors and every selected-world neighbor remain queryable.
	var rolling: Node3D = assembly.get_node("NamedSectionReceiving20261024/RollingGuidewayContacts")
	for child: CollisionObject3D in rolling.find_children("*", "CollisionObject3D", true, false):
		excludes.append(child.get_rid())
	var components: Array[Dictionary] = []
	for col: CollisionShape3D in body.find_children("*", "CollisionShape3D", true, false):
		if col.disabled or col.shape == null:
			continue
		var shape_owner: Node3D = col.get_parent()
		var bogie := -1
		for i in range(motor.bogies.size()):
			if shape_owner == motor.bogies[i] or motor.bogies[i].is_ancestor_of(col):
				bogie = i
				break
		var relative: Transform3D = body.global_transform.affine_inverse() * col.global_transform
		if bogie >= 0:
			relative = motor.bogies[bogie].global_transform.affine_inverse() * col.global_transform
		components.append({"name":str(body.get_path_to(col)), "shape":col.shape, "relative":relative, "bogie":bogie})
	var original_pose := body.global_transform
	var original_cursor: float = motor.cursor
	# Actual contact shapes, not a cylinder proof. This is a dense discrete gate;
	# the separate source interval-envelope proof covers between sampled poses.
	for pose: Array in motor.poses:
		if pose[0] < plan.central_interval_m[0] or pose[0] > plan.central_interval_m[1]:
			continue
		var proposed := Transform3D(Basis(Vector3.UP, float(pose[3])), Vector3(pose[1], 56.1, pose[2]))
		for component: Dictionary in components:
			var relative: Transform3D = component.relative
			if component.bogie >= 0:
				var i: int = component.bogie
				var column := 4 + i * 3
				relative = Transform3D(Basis(Vector3.UP, float(pose[column + 1])), Vector3(pose[column], -.2, -1.5 if i == 0 else 1.5)) * relative
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = component.shape
			query.transform = proposed * relative
			query.margin = 0.0
			query.exclude = excludes
			var hits: Array[Dictionary] = body.get_world_3d().direct_space_state.intersect_shape(query, 64)
			report.queries += 1
			if not hits.is_empty():
				var owners: Array[String] = []
				for hit: Dictionary in hits:
					owners.append(str(hit.collider.get_path()))
				report.hits.append({"cursor":pose[0], "component":component.name, "installed_owners":owners})
				if report.hits.size() >= 16:
					report.reason = "First sixteen actual installed contact conflicts; no readiness admission"
					report.status = "FAIL_INSTALLED_CONTACTS"
					return report
	if body.global_transform != original_pose or motor.cursor != original_cursor:
		report.reason = "Unexpected external owner moved during read-only query gate"
		return report
	report.status = "PASS_SAMPLED_INSTALLED_CONTACTS" if report.hits.is_empty() else "FAIL_INSTALLED_CONTACTS"
	report.components = components.size()
	report.remaining = ["visual-only installed geometry coverage", "moving passenger", "loaded cart/caster physical run", "structural capacity", "scenic and performance acceptance"]
	return report
