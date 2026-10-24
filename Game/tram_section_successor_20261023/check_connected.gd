extends SceneTree
# Bounded static connection fixture. Root is the sole engine owner.
# No live ship, actor, controller, admission mutation or moving-passenger claim.
const PACKAGE := "res://../recovery/tram_section_successor_20261023/"
const ORIGINAL := "res://source_derivatives/group4_completion_20261011/"
var world: Node3D
var checks := 0
var plan: Dictionary

func _initialize() -> void:
	call_deferred("run")

func require(value: bool, message: String) -> void:
	if not value:
		push_error("TRAM_SECTION_CONNECTED_FAIL: " + message)
		quit(1)
		assert(value, message)
	checks += 1

func read_json(path: String) -> Variant:
	return JSON.parse_string(FileAccess.get_file_as_string(path))

func raw_model(path: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	# Required operation is unconditional in debug and release.
	var error := document.append_from_file(ProjectSettings.globalize_path(path), state)
	require(error == OK, "GLTF bytes readable: " + path)
	var instance := document.generate_scene(state)
	require(instance != null, "GLTF scene generated: " + path)
	return instance

func contacts(owner: Node3D, policies: Dictionary = {}) -> void:
	var faces := PackedVector3Array()
	for mesh: MeshInstance3D in owner.find_children("*", "MeshInstance3D", true, false):
		if policies.get(str(mesh.name), "contact") == "no_collision_detail":
			continue
		var transform := owner.global_transform.affine_inverse() * mesh.global_transform
		faces.append_array(transform * mesh.mesh.get_faces())
	var body := StaticBody3D.new()
	var collider := CollisionShape3D.new()
	var shape := ConcavePolygonShape3D.new()
	shape.set_faces(faces)
	collider.shape = shape
	body.add_child(collider)
	owner.add_child(body)

func retained(name: String, remove_names: Array[String]) -> Node3D:
	var node := raw_model(ORIGINAL + name)
	world.add_child(node)
	var models: Array = read_json("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json").models
	var policies := {}
	for item: Dictionary in models:
		if item.file == name:
			for source_name: String in item.policies:
				policies[source_name.validate_node_name()] = item.policies[source_name]
	for name_to_remove in remove_names:
		var removed := node.find_child(name_to_remove.validate_node_name(), true, false)
		require(removed != null, "exact replaced source member " + name_to_remove)
		removed.free()
	contacts(node, policies)
	return node

func floor_hit(xz: Vector2, expected_y: float) -> bool:
	var query := PhysicsRayQueryParameters3D.create(Vector3(xz.x, expected_y + .12, xz.y), Vector3(xz.x, expected_y - .12, xz.y))
	var hit := world.get_world_3d().direct_space_state.intersect_ray(query)
	return not hit.is_empty() and absf(hit.position.y - expected_y) < .003

func require_floor_segment(a: Vector2, b: Vector2, label: String) -> void:
	var count := maxi(2, ceili(a.distance_to(b) / .08))
	for i in range(count + 1):
		require(floor_hit(a.lerp(b, float(i) / count), 56.1), label + " sample " + str(i))

func clear_band(point: Vector2, bottom: float) -> bool:
	var shape := CylinderShape3D.new()
	shape.radius = 2.0
	shape.height = 4.0
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.margin = 0.0
	query.transform = Transform3D(Basis.IDENTITY, Vector3(point.x, bottom + 2.0, point.y))
	return world.get_world_3d().direct_space_state.intersect_shape(query, 64).is_empty()

func run() -> void:
	plan = read_json(PACKAGE + "candidate_r002/CANDIDATE.json")
	require(not plan.active and not plan.integration_motion_admitted and not plan.integration_boarding_admitted and not plan.integration_joint_admitted, "all admission remains false")
	var receipt: Dictionary = read_json(PACKAGE + "runtime_r002/EXPORT_RECEIPT.json")
	for file: String in receipt.files:
		require(FileAccess.get_sha256(PACKAGE + "runtime_r002/" + file) == receipt.files[file].sha256, "exact candidate bytes " + file)
	world = Node3D.new()
	world.name = "TramSectionBoundedConnectionFixture_UNADOPTED"
	root.add_child(world)
	var section := raw_model(PACKAGE + "runtime_r002/AST-TRM-SECTION-20261023-r002.glb")
	world.add_child(section)
	contacts(section)
	retained("AST-TRM-G4-014_central_source.glb", ["V2_Central_NorthEnd_infill", "V2_Central_NorthEnd_rail", "V2__CENTRAL__Boarding_Post_-73.2", "V2__CENTRAL__Boarding_Post_-70.8", "V2__CENTRAL__Boarding_Header"])
	retained("AST-TRM-G4-018_central_stair_receiving.glb", [])
	await physics_frame
	await physics_frame
	# Source triangle gate separately covers the core/atrium/eight bearings.
	# This fixture checks candidate self-clearance and retained CENTRAL contacts.
	for p: Array in plan.protected_route_xz:
		require(clear_band(Vector2(p[0], p[1]), 52.55), "retained lower four-metre cylinder " + str(p))
	var total := 0.0
	var route: Array = plan.route_points_xz
	for i in range(route.size() - 1):
		var a := Vector2(route[i][0], route[i][1])
		var b := Vector2(route[i + 1][0], route[i + 1][1])
		var distance := a.distance_to(b)
		if total >= float(plan.central_interval_m[0]) - .00001 and total <= float(plan.central_interval_m[1]) + .00001:
			var count := maxi(1, ceili(distance / 1.0))
			for j in range(count):
				require(clear_band(a.lerp(b, float(j) / count), 56.10001), "upper four-metre cylinder segment " + str(i) + ":" + str(j))
		total += distance
	var center := Vector2(-5.6, -71.5)
	var join := Vector2((float(plan.central.join_to_retained_floor_x[0]) + float(plan.central.join_to_retained_floor_x[1])) * .5, -75.0)
	var origin := Vector2(plan.central.bridge_origin_xyz[0], plan.central.bridge_origin_xyz[2])
	require_floor_segment(Vector2(-8.5, -70.5), center, "unchanged stair return to platform")
	require_floor_segment(center, join, "retained platform to apron join")
	require_floor_segment(join, origin, "new apron to bridge hinge")
	# Static deployed panel and exact slotted source body prove connection only;
	# no gate/motor/cart/controller is instantiated or readiness manufactured.
	var bridge := raw_model(PACKAGE + "runtime_r002/AST-TRM-BRIDGE-20261023-r002.glb")
	bridge.position = Vector3(origin.x, 56.1, origin.y)
	bridge.rotation.y = plan.central.bridge_yaw
	world.add_child(bridge)
	contacts(bridge)
	var body := raw_model("res://source_derivatives/group4_boarding_safety_20261011/AST-TRM-G4-024_powered_portal_body_r001.glb")
	body.position = Vector3(plan.central.new_pose[1], 56.1, plan.central.new_pose[2])
	body.rotation.y = plan.central.new_pose[3]
	world.add_child(body)
	contacts(body)
	await physics_frame
	await physics_frame
	var right := Vector2(cos(plan.central.bridge_yaw), -sin(plan.central.bridge_yaw))
	require_floor_segment(origin, origin + right * (float(plan.central.bridge_reach_m) + .08), "deployed bridge to real body floor")
	print(JSON.stringify({"status":"PASS_STATIC_CONNECTION_ONLY", "checks":checks, "source_candidate":"r002", "motion_admitted":false, "boarding_admitted":false, "joint_admitted":false, "not_tested":["moving passenger", "controller/gate interlocks", "actual installed later neighbours", "caster/joint", "visual scenic route", "performance"]}))
	world.free()
	quit(0)
