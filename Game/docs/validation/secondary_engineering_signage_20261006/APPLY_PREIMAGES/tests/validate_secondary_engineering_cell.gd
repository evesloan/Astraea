extends SceneTree
# SCRATCH DRAFT. Never executed by its author. Run only in the explicitly
# integrated project, through the normal fresh-import validation workflow.
# Uses the unchanged real player, physical cart/bottles, service-door state and
# light selector. Diagnostic arrivals are not an external staff connection.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_CELL_RUNTIME.json"
const RECEIPT := "res://artifacts/secondary_engineering_cell_validation.json"
const UPPER_OWNER := "D02_secondary_engineering_floor"
const LOWER_OWNER := "D02_secondary_engineering_workbay_cell_lower"
const SOURCE_GROUPS := 153
const PARK := Vector3(30, 6.04, -405)
const PARK_YAW := -PI / 2.0
const OUTSIDE := Vector3(20.85, 6, -405.23)
const INSIDE := Vector3(23.3, 5.55, -404.5)
const MAX_FRAMES := 30000
const WALL_WATCHDOG_MSEC := 600000
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var tool: RigidBody3D
var built: Node3D
var visual: Node3D
var gate: Node3D
var floors: Node3D
var budget: Node
var space: PhysicsDirectSpaceState3D
var data: Dictionary
var checks: Dictionary
var failed := false
var checkpoint := "unrun"
var started := 0
var frames := 0
var walked_frames := 0
var support_samples := 0
var leaf_motion_samples := 0
var leaf_pose_checked := false
var last_checked_leaf_pose: Transform3D
var verified_bearing_rids: Dictionary = {}
var verified_fixed_shapes: Array = []
var verified_leaf_sweep: AABB
var verified_leaf_size: Vector3
var verified_leaf_basis: Basis
var bearing_records: Array = []
var descent_frames := 0
var ascent_frames := 0
var parked := false
var parked_transform: Transform3D
var tool_home_local: Vector3
var first_hit_records: Array = []
var light_records: Array = []
var selection_records: Array = []

func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if not failed and Time.get_ticks_msec() - started > WALL_WATCHDOG_MSEC:
		require(false, "600-second watchdog at " + checkpoint)
	return false

func require(ok: bool, detail: String) -> bool:
	if ok and not failed: return true
	if not failed:
		failed = true
		release_inputs()
		write_receipt("FAIL", detail)
		push_error("SECONDARY ENGINEERING CELL: " + detail + " at " + checkpoint)
		quit(1)
	return false

func write_receipt(status: String, detail: String = "") -> void:
	if failed and status != "FAIL": return
	var record := {
		"test": "secondary_engineering_cell", "status": status,
		"checkpoint": checkpoint, "detail": detail,
		"runtime_contract_sha256": FileAccess.get_sha256(CONTRACT),
		"test_sha256": FileAccess.get_sha256("res://tests/validate_secondary_engineering_cell.gd"),
		"frames": frames, "ordinary_player_movement_frames": walked_frames,
		"support_samples": support_samples, "leaf_motion_samples": leaf_motion_samples,
		"descent_frames": descent_frames, "ascent_frames": ascent_frames,
		"exact_gate_first_hits": first_hit_records, "light_receivers": light_records,
		"imported_bearing_face_classification": bearing_records,
		"light_selection": selection_records,
		"cart_initial_fixture_placements": 1 if parked else 0,
		"scope": "Focused runtime geometry, ordinary player/input, portable cleaner carry/return and source-light checks. Cart remains upstairs. No cleaning task, cart stair traversal, external staff connection, visual acceptance, target-device performance or aggregate pass is claimed."
	}
	if is_instance_valid(actor): record["actor_xyz"] = array_xyz(actor.global_position)
	if is_instance_valid(cart): record["cart_xyz"] = array_xyz(cart.global_position)
	if is_instance_valid(tool):
		record["tool_xyz"] = array_xyz(tool.global_position)
		record["tool_cart_local"] = array_xyz(cart.to_local(tool.global_position))
		record["tool_held"] = tool.driver==actor
		record["tool_velocity"] = array_xyz(tool.linear_velocity)
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(record, "  ") + "\n")
		file.close()
	else:
		push_error("Cannot write cell validation receipt: " + str(FileAccess.get_open_error()))
		failed = true
		quit(1)

func mark(label: String) -> bool:
	if failed: return false
	checkpoint = label
	write_receipt("RUNNING")
	print("SECONDARY ENGINEERING CELL CHECKPOINT: ", label)
	return not failed

func xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]), float(value[1]), float(value[2]))

func array_xyz(value: Vector3) -> Array:
	return [value.x, value.y, value.z]

func bounds(value: Array) -> AABB:
	var low := Vector3(float(value[0]), float(value[1]), float(value[2]))
	return AABB(low, Vector3(float(value[3]), float(value[4]), float(value[5])) - low)

func world_bounds(mesh: MeshInstance3D) -> AABB:
	var box := mesh.get_aabb()
	var result := AABB(mesh.global_transform * box.position, Vector3.ZERO)
	for corner in range(8): result = result.expand(mesh.global_transform * box.get_endpoint(corner))
	return result

func controlled_exclusions() -> Array[RID]:
	var result: Array[RID] = [actor.get_rid(), cart.get_rid()]
	for product in cart.products: result.append(product.get_rid())
	return result

func ray(a: Vector3, b: Vector3, excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a, b, 1)
	query.exclude = excluded
	query.hit_back_faces = true
	return space.intersect_ray(query)

func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)

func focus(pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	Input.parse_input_event(event)

func release_inputs() -> void:
	for code in [KEY_W, KEY_S, KEY_A, KEY_D, KEY_E]: key(code, false)
	focus(false)

func aim(point: Vector3) -> void:
	var delta: Vector3 = point - actor.camera.global_position
	actor.rotation.y = atan2(-delta.x, -delta.z)
	actor.pitch = atan2(delta.y, Vector2(delta.x, delta.z).length())
	actor.camera.rotation.x = actor.pitch

func advance(count: int, inspect_leaf := true) -> bool:
	for frame in range(count):
		if failed: return false
		await physics_frame
		frames += 1
		if not require(frames <= MAX_FRAMES, "Derived 30000-frame route/control allowance exceeded"): return false
		if inspect_leaf and is_instance_valid(gate) and not leaf_clear(): return false
		if parked and not parked_cart_state(): return false
	return true

func tap_e() -> bool:
	key(KEY_E, true)
	if not await advance(2): return false
	key(KEY_E, false)
	return await advance(2)

func check_pins() -> bool:
	if not require(data.has("runtime_checks"), "Missing explicit runtime_checks proof; source proposals are not runtime evidence"): return false
	checks = data.runtime_checks
	for field in ["lighting_selection_views", "opaque_light_probes", "gate_bearing_contact_proof"]:
		if not require(checks.has(field), "Missing runtime_checks." + field): return false
	for path in data.retained_runtime_pins:
		if not require(FileAccess.get_sha256("res://" + str(path)) == str(data.retained_runtime_pins[path]), "Retained runtime bytes changed: " + str(path)): return false
	for required_path in ["scripts/player.gd", "scripts/service_door.gd", "scripts/lighting_budget.gd", "scripts/guest_entry_door.gd", "scripts/physics_tether.gd", "scripts/cleaning_cart.gd", "scripts/cleaning_bottle.gd"]:
		if not require(data.retained_runtime_pins.has(required_path), "Missing unchanged-controller pin: " + required_path): return false
	var model := "res://assets/models/" + str(data.model_file)
	if not require(FileAccess.get_sha256(model) == str(data.model_sha256), "Frozen workbay export hash mismatch"): return false
	var settings := ConfigFile.new()
	if not require(settings.load(model + ".import") == OK, "Workbay import descriptor missing"): return false
	if not require(settings.get_value("params", "meshes/force_disable_compression", false), "Submillimetre source controls require lossless imported positions"): return false
	var imported: String = settings.get_value("remap", "path", "")
	if not require(not imported.is_empty() and FileAccess.file_exists(imported), "Imported workbay scene missing"): return false
	var cache := ConfigFile.new()
	if not require(cache.load(imported.get_basename() + ".md5") == OK, "Workbay source import digest missing"): return false
	if not require(cache.get_value("", "source_md5", "") == FileAccess.get_md5(model), "Stale workbay import; refresh through approved validation workflow"): return false
	return true

func mesh_and_contact_census() -> bool:
	# The reviewed grounded triangular wedge may remove degenerate end faces
	# from the earlier 47910-triangle draft. Require the exact final frozen
	# contract count and model hash, never a >= comparison or skipped group.
	var source_triangles := int(data.source_triangles)
	if not require(data.mesh_group_count == SOURCE_GROUPS and source_triangles > 0, "Frozen 153-group source census missing"): return false
	var meshes := built.find_children("*", "MeshInstance3D", true, false)
	if not require(meshes.size() == SOURCE_GROUPS, "Imported source group census differs from 153"): return false
	var seen: Dictionary = {}
	var triangles := 0
	var proxies := 0
	var actuators := 0
	var control_actuators := 0
	var workbay_actuators := 0
	var counts: Dictionary = {}
	for node in meshes:
		var mesh := node as MeshInstance3D
		var name := str(mesh.name)
		if not require(data.groups.has(name) and not seen.has(name), "Unknown/duplicate source group: " + name): return false
		seen[name] = true
		var expected: Dictionary = data.groups[name]
		var role := str(expected.collision_contract)
		counts[role] = int(counts.get(role, 0)) + 1
		if not require(mesh.mesh != null and mesh.material_override == null, "Source mesh/material replacement: " + name): return false
		var faces := mesh.mesh.get_faces()
		if not require(faces.size() == int(expected.triangles) * 3, "Source triangle count changed: " + name): return false
		triangles += int(faces.size() / 3)
		if not require(mesh.visible == bool(expected.visible), "Source visual/contact visibility mismatch: " + name): return false
		var actual := world_bounds(mesh)
		var expected_box := bounds(expected.bounds_xyz)
		if not require(actual.position.distance_to(expected_box.position) < .001 and actual.end.distance_to(expected_box.end) < .001, "Source world bounds changed: " + name): return false
		var materials: Array[String] = []
		for surface in range(mesh.mesh.get_surface_count()):
			if not require(mesh.get_surface_override_material(surface) == null, "Per-surface replacement: " + name): return false
			var material := mesh.get_active_material(surface)
			if not require(material != null, "Missing original source material: " + name): return false
			materials.append(str(material.resource_name))
		materials.sort()
		var expected_materials: Array = expected.materials.duplicate()
		expected_materials.sort()
		if not require(materials == expected_materials, "Original material identities changed: " + name): return false
		var contacts := mesh.find_children("*", "CollisionShape3D", true, false)
		if role in ["static_surface", "stair_flight_contact", "contact_only_glass_26mm"]:
			if not require(contacts.size() == 1, "One exact source contact required: " + name): return false
			var contact := contacts[0] as CollisionShape3D
			if not require(not contact.disabled and contact.get_parent() is StaticBody3D and not contact.get_parent() is AnimatableBody3D, "Invalid fixed contact: " + name): return false
			if contact.shape is ConcavePolygonShape3D:
				if not require(contact.transform.is_equal_approx(Transform3D.IDENTITY) and contact.get_parent().transform.is_equal_approx(Transform3D.IDENTITY), "Trimesh must preserve mesh-local source frame: " + name): return false
				var contact_faces := (contact.shape as ConcavePolygonShape3D).get_faces()
				if not require(contact_faces.size() == faces.size(), "Contact triangle census changed: " + name): return false
				for index in range(faces.size()):
					if not require(faces[index].distance_to(contact_faces[index]) < .00001, "Contact must retain each source vertex: " + name): return false
			else:
				if not require(role == "contact_only_glass_26mm" and contact.shape is BoxShape3D, "No convex cavity fill or invented contact: " + name): return false
				var box_shape := contact.shape as BoxShape3D
				var box_world := AABB(contact.global_transform * (-box_shape.size * .5), Vector3.ZERO)
				for corner in range(8): box_world = box_world.expand(contact.global_transform * AABB(-box_shape.size * .5, box_shape.size).get_endpoint(corner))
				if not require(box_world.position.distance_to(expected_box.position) < .001 and box_world.end.distance_to(expected_box.end) < .001, "Pane box must equal this proxy only: " + name): return false
			if role == "contact_only_glass_26mm":
				proxies += 1
				var axis := 0 if expected_box.size.x < expected_box.size.z else 2
				if not require(absf(expected_box.size[axis] - .026) < .0001, "Pane thickness is not 26 mm: " + name): return false
				var normal := Vector3.RIGHT if axis == 0 else Vector3.BACK
				var centre := expected_box.get_center()
				for sign_value in [-1.0, 1.0]:
					var hit := ray(centre + normal * .06 * sign_value, centre - normal * .06 * sign_value, controlled_exclusions())
					if not require(not hit.is_empty() and mesh.is_ancestor_of(hit.collider), "Exact hidden-pane physical first hit missing: " + name): return false
		elif role == "moving_door_leaf":
			if not require(contacts.is_empty() and gate.leaves.size() == 1 and gate.leaves[0].is_ancestor_of(mesh), "Leaf must have only its one source-bound dynamic fitting"): return false
		else:
			if not require(contacts.is_empty(), "Non-contact source group received invented body/target: " + name): return false
		if name.begins_with("ACT_ENG2_"): actuators += 1
		if name.begins_with("ACT_ENG2_CONTROL_"): control_actuators += 1
		if name.begins_with("ACT_ENG2_WORKBAY_"): workbay_actuators += 1
		if not require(not "PREVIEW" in name and actual.position.y >= 5.309, "Preview floor or intrusion below D01 underside reservation: " + name): return false
	if not require(triangles == source_triangles and proxies == 10 and actuators == 120, "Exact final frozen triangle/proxy/actuator census failed"): return false
	if not require(control_actuators==72 and workbay_actuators==48, "All 120 calibration IDs must retain their 72 control / 48 workbay allocation"): return false
	if not require(counts.get("static_surface") == 13 and counts.get("stair_flight_contact") == 1 and counts.get("visual_only_stair_tread") == 1, "Fixed/stair contact roles changed"): return false
	return require(built.find_children("*", "Light3D", true, false).size() == 4, "Exactly four new source-backed lights required")

func floor_hit(point: Vector3, owner: String) -> bool:
	var hit := ray(point + Vector3.UP * .10, point - Vector3.UP * .10, controlled_exclusions())
	if not require(not hit.is_empty() and absf(hit.position.y - point.y) < .003 and hit.normal.y > .99, "Actual floor support absent at " + str(point)): return false
	if not require(floors.is_ancestor_of(hit.collider) and str(hit.collider.get_parent().name) == owner, "Support must belong to explicit compiler owner " + owner): return false
	support_samples += 1
	return true

func floor_topology_and_stair() -> bool:
	var compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	# Reuse the reviewed, hash-pinned successor proof. A failed helper must not
	# allow this caller to reach PASS, even if its internal assert aborts early.
	var guard := load("res://tests/secondary_engineering_additive_guard.gd")
	var preserved: Variant = guard.validate(compiled)
	if not require(preserved is Dictionary and preserved.size() == 4 and preserved.has(LOWER_OWNER), "Exact old258/unchanged260/current engineering four/theater271 preservation helper did not complete"): return false
	var chain: Variant = guard.section_proof()
	if not require(chain is Dictionary and chain.has("original_host_record"), "Reviewed floor successor proof is missing"): return false
	if not require(compiled.regions.size() == 271 and floors.get_child_count() == 271, "Actual compiled/runtime floor owner counts differ"): return false
	var current: Dictionary = {}
	for region in compiled.regions:
		if not require(not current.has(str(region.id)), "Duplicate compiler owner"): return false
		current[str(region.id)] = region
	var old_upper: Dictionary = chain.original_host_record
	if not require(not old_upper.is_empty() and current.has(LOWER_OWNER), "Explicit upper/lower owners missing"): return false
	var upper: Dictionary = current[UPPER_OWNER]
	var lower: Dictionary = current[LOWER_OWNER]
	if not require(absf(float(upper.floor_y) - 6) < .00001 and absf(float(lower.floor_y) - 5.55) < .00001 and absf(float(lower.thickness) - .24) < .00001, "Upper/lower slab datums changed"): return false
	if not require(upper.rings.size() == 2 and lower.rings.size() == 1 and upper.rings[0] == old_upper.rings[0], "Only the exact interior cell cut may change upper ownership"): return false
	if not require(absf(float(old_upper.structural_area_m2) - float(upper.structural_area_m2) - 15.34) < .00001 and absf(float(lower.structural_area_m2) - 15.34) < .00001, "Exact 15.34 m² slab cut required"): return false
	if not require(data.has("D01_vertical_reservation"), "Explicit future D01 programme reservation missing"): return false
	var reservation: Dictionary = data.D01_vertical_reservation
	if not require(str(reservation.programme_key)=="D01_directory_02" and str(reservation.name)=="Cold provisions" and absf(float(reservation.cell_slab_underside_y)-5.31)<.00001 and not reservation.room_completion_or_below_fit_accepted, "D01 future Cold provisions reservation was silently accepted or changed"): return false
	var expected_vertices: Array = [[21.9,-406.6],[27.1,-406.6],[27.1,-403.65],[21.9,-403.65]]
	for ring in [upper.rings[1], lower.rings[0]]:
		if not require(ring.size() == 4, "Cell floor boundary gained a vertex"): return false
		for point in expected_vertices:
			if not require(ring.has(point), "Exact cell hole vertex missing: " + str(point)): return false
	var cut := PackedVector2Array([Vector2(21.90001,-406.59999), Vector2(27.09999,-406.59999), Vector2(27.09999,-403.65001), Vector2(21.90001,-403.65001)])
	for triangle in upper.triangles:
		var polygon := PackedVector2Array()
		for point in triangle: polygon.append(Vector2(point[0], point[1]))
		if not require(Geometry2D.intersect_polygons(polygon, cut).is_empty(), "Upper compiler triangle bridges the cell cut"): return false
	for point in [Vector3(21.5,6,-404.5), Vector3(27.4,6,-404.5), Vector3(24.5,6,-403.4), Vector3(24.5,6,-406.85), Vector3(30,6,-405)]:
		if not floor_hit(point, UPPER_OWNER): return false
	for x in [23.3,24.5,26.5]:
		var point := Vector3(x,5.55,-404.4)
		var cut_ray := ray(point + Vector3.UP * .52, point - Vector3.UP * .04, controlled_exclusions())
		if not require(not cut_ray.is_empty() and floors.is_ancestor_of(cut_ray.collider) and str(cut_ray.collider.get_parent().name) == LOWER_OWNER and absf(cut_ray.position.y - 5.55) < .003, "Real cell ray still hits upper floor or non-floor slab"): return false
		if not floor_hit(point, LOWER_OWNER): return false
		var underside := ray(Vector3(x,5.20,-404.4),Vector3(x,5.40,-404.4),controlled_exclusions())
		if not require(not underside.is_empty() and floors.is_ancestor_of(underside.collider) and str(underside.collider.get_parent().name) == LOWER_OWNER and absf(underside.position.y - 5.31) < .003 and underside.normal.y < -.99, "Lower compiler underside/D01 headroom datum missing"): return false
		if not require(ray(Vector3(x,5.02,-404.4),Vector3(x,5.305,-404.4),controlled_exclusions()).is_empty(), "New intrusion immediately below retained D01 ceiling reservation"): return false
	for x in [21.95,22.05,22.20,22.35,22.50,22.70,22.78]:
		for z in [-404.9,-404.5,-404.1]:
			var y: float = 6.0 - (float(x) - 21.9) * .5
			var top := ray(Vector3(x,y+.03,z),Vector3(x,y-.03,z),controlled_exclusions())
			if not require(not top.is_empty() and str(top.collider.get_parent().name) == "CONTACT_CellStairFlight" and absf(top.position.y-y) < .003 and top.normal.y > .88, "Actual bounded flight contact missing; no ramp bridge substitute"): return false
			# The earlier 0.12 m thin prism admitted a real lying bottle below the
			# visually solid treads. The corrected closed wedge must seat at Y5.55.
			# Only exclude the coincident lower slab for this ownership-specific
			# underside ray; actual player/bottle queries retain all collisions.
			var excluded := controlled_exclusions()
			for body in floors.get_node(LOWER_OWNER).find_children("*","StaticBody3D",true,false): excluded.append(body.get_rid())
			var bottom := ray(Vector3(x,5.525,z),Vector3(x,5.575,z),excluded)
			if not require(not bottom.is_empty() and str(bottom.collider.get_parent().name) == "CONTACT_CellStairFlight" and absf(bottom.position.y-5.55)<.003 and bottom.normal.y<-.99, "Corrected closed source stair must seat directly on lower floor Y5.55"): return false
	return true

func under_tread_loose_bottle() -> bool:
	# Reproduce the independently reported gap with the production cylinder,
	# lying lengthwise along Z. Initial test-fixture placement only; afterward
	# ordinary collision and applied physical force determine the result.
	var bottle: RigidBody3D = (load("res://scripts/cleaning_bottle.gd") as GDScript).new()
	bottle.name = "CellUnderTreadBottleTestOnly"
	bottle.persistent_id = &"cell_under_tread_bottle_test_only"
	ship.get_node("ShipSpace/PersistentActors").add_child(bottle)
	bottle.rotation = Vector3(PI/2,0,0)
	var centre := Vector3(22.19,5.61,-405.45)
	bottle.global_position = centre-bottle.global_basis*Vector3(0,.125,0)
	var shapes := bottle.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CylinderShape3D and absf(shapes[0].shape.radius-.057)<.00001 and absf(shapes[0].shape.height-.25)<.00001, "Under-tread witness must use unchanged actual cleaner contact"): return false
	if not await advance(8): return false
	var shape := shapes[0] as CollisionShape3D
	var excluded := controlled_exclusions()
	excluded.append(bottle.get_rid())
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape.shape
	# Raise the witness 3 mm above the lower floor so a floor contact cannot
	# masquerade as the wanted vertical stair-side obstruction in cast_motion.
	query.transform = shape.global_transform.translated(Vector3.UP*.003)
	query.motion = Vector3(0,0,.75)
	query.margin = .001
	query.exclude = excluded
	var fractions := space.cast_motion(query)
	if not require(fractions.size()==2 and fractions[0]>.05 and fractions[0]<.45, "Actual lying-bottle sweep still fits below the visual treads"): return false
	var side := ray(Vector3(22.19,5.61,-405.3),Vector3(22.19,5.61,-404.9),excluded)
	if not require(not side.is_empty() and str(side.collider.get_parent().name)=="CONTACT_CellStairFlight" and absf(side.position.z+405.1)<.003, "Grounded flight side must physically close the retained gap witness"): return false
	var initial_centre: Vector3 = shape.global_position
	for frame in range(150):
		bottle.apply_central_force(Vector3(0,0,5.0))
		if not await advance(1): return false
		if not require(bottle.global_position.is_finite() and bottle.linear_velocity.length()<3, "Under-tread bottle force witness became unstable"): return false
		if not require(shape.global_position.z < -405.20, "Actual loose bottle crossed into under-tread gap"): return false
	if not require(shape.global_position.z-initial_centre.z>.02 and shape.global_position.z<-405.20, "Loose bottle must actually advance and stop on real grounded stair side"): return false
	bottle.queue_free()
	return await advance(4)

func expected_floor_y(position: Vector3) -> float:
	if position.x >= 21.9 and position.x <= 22.8 and position.z > -405.1 and position.z < -403.9:
		return 6.0 - (position.x - 21.9) * .5
	if position.x > 21.9 and position.x < 27.1 and position.z > -406.6 and position.z < -403.65: return 5.55
	return 6.0

func actual_player_support() -> bool:
	var point := actor.global_position
	var expected_y := expected_floor_y(point)
	if not require(point.is_finite() and absf(point.y - expected_y) < .14, "Original capsule lost supported route/fell/recovered: " + str(point)): return false
	var hit := ray(point + Vector3.UP*.10, point-Vector3.UP*.25, controlled_exclusions())
	if not require(not hit.is_empty() and absf(hit.position.y-expected_y)<.003 and hit.normal.y>.88, "Actual capsule foot has no expected floor/flight contact: " + str(point)): return false
	if not require(floors.is_ancestor_of(hit.collider) or str(hit.collider.get_parent().name) == "CONTACT_CellStairFlight", "No machinery/tread substitute may support the route"): return false
	if point.x > 21.95 and point.x < 22.75 and point.z > -405.05 and point.z < -403.95:
		if actor.velocity.x > .1: descent_frames += 1
		elif actor.velocity.x < -.1: ascent_frames += 1
	support_samples += 1
	return true

func held_tool_state() -> bool:
	if tool == null or actor.held_interaction != tool: return true
	if not require(tool.driver == actor and tool.get_parent() == cart.get_parent(), "Portable tool lost its real tether or was reparented"): return false
	if not require(tool.global_position.is_finite() and tool.linear_velocity.length() < 8 and tool.global_position.distance_to(actor.camera.global_position) < 2.1, "Portable tool escaped bounded physical carry"): return false
	return require(tool.global_position.y > expected_floor_y(actor.global_position) + .12, "Carried tool dragged through floor/steps")

func face_heading(yaw: float) -> bool:
	key(KEY_W, false)
	if not await advance(16): return false
	for frame in range(240):
		var error := wrapf(yaw - actor.rotation.y, -PI, PI)
		if absf(error) < .005: return true
		actor.rotation.y += clampf(error, -1.2/60.0, 1.2/60.0)
		if not await advance(1): return false
		if not actual_player_support() or not held_tool_state(): return false
	return require(false, "Bounded on-foot turn failed")

func walk_to(destination: Vector2) -> bool:
	focus(false)
	actor.pitch = 0
	actor.camera.rotation.x = 0
	var delta := destination - Vector2(actor.global_position.x, actor.global_position.z)
	if delta.length() < .13: return actual_player_support()
	if not await face_heading(atan2(-delta.x, -delta.y)): return false
	var allowance := ceili(delta.length()/3.1*60) + 180
	var reached := false
	for frame in range(allowance):
		delta = destination - Vector2(actor.global_position.x, actor.global_position.z)
		var horizontal := Vector2(actor.velocity.x, actor.velocity.z)
		if delta.length() < .14 and horizontal.length() < .06:
			reached = true
			break
		var braking_distance := horizontal.length_squared()/32.0 + .06
		key(KEY_W, delta.length() > braking_distance)
		if delta.length() > .15: actor.rotation.y = atan2(-delta.x, -delta.y)
		if not await advance(1): return false
		walked_frames += 1
		if not actual_player_support() or not held_tool_state(): return false
	key(KEY_W, false)
	return require(reached, "Ordinary original-player W route stalled at %s toward %s" % [actor.global_position,destination])

func walk_path(points: Array) -> bool:
	for point in points:
		if not await walk_to(point): return false
	return true

func arrive(point: Vector3) -> bool:
	release_inputs()
	if not require(actor.held_interaction == null, "Diagnostic arrival may not transport a held object"): return false
	if not require(ship.arrive_at(point + Vector3.UP*.10, 0), "Supported diagnostic arrival refused: " + str(point)): return false
	if not await advance(24): return false
	return actual_player_support()

func retained_routes() -> bool:
	if not await arrive(Vector3(6,6,-432)): return false
	if not await walk_path([Vector2(12,-432),Vector2(6,-432)]): return false
	# Preserved diagnostic internal staff route, not an invented exterior entry.
	if not await arrive(Vector3(30,6,-459)): return false
	var route := [Vector2(30,-459),Vector2(30,-452.8),Vector2(38,-452.8),Vector2(38,-445),Vector2(45.5,-445),Vector2(45.5,-432),Vector2(51,-432),Vector2(51,-411.2),Vector2(30,-411.2),Vector2(30,-405)]
	if not await walk_path(route): return false
	for pair in [[Vector3(16.5,7.6,-432),Vector3(17.5,7.6,-432)], [Vector3(20.5,7.6,-432),Vector3(21.5,7.6,-432)]]:
		if not require(not ray(pair[0],pair[1],controlled_exclusions()).is_empty(), "Original visitor/hall glass separation removed"): return false
	return true

func contact_box_world(shape: BoxShape3D, pose: Transform3D) -> AABB:
	var local := AABB(-shape.size*.5,shape.size)
	var result := AABB(pose*local.position,Vector3.ZERO)
	for corner in range(8): result=result.expand(pose*local.get_endpoint(corner))
	return result

func triangle_clip_box(a: Vector3, b: Vector3, c: Vector3, box: AABB, inset: float) -> Array:
	# Float64 scalar clipping keeps the <=1 micrometre interior test separate
	# from both world Vector3 float32 ULPs and the 1 mm receiver tolerance.
	var polygon: Array = [array_xyz(a),array_xyz(b),array_xyz(c)]
	for axis in range(3):
		for lower in [true,false]:
			var edge := float(box.position[axis])+inset if lower else float(box.end[axis])-inset
			var output: Array = []
			for index in range(polygon.size()):
				var p: Array = polygon[index]
				var q: Array = polygon[(index+1)%polygon.size()]
				var inside_p := float(p[axis])>=edge if lower else float(p[axis])<=edge
				var inside_q := float(q[axis])>=edge if lower else float(q[axis])<=edge
				if inside_p: output.append(p)
				if inside_p!=inside_q:
					var amount := (edge-float(p[axis]))/(float(q[axis])-float(p[axis]))
					output.append([float(p[0])+(float(q[0])-float(p[0]))*amount,float(p[1])+(float(q[1])-float(p[1]))*amount,float(p[2])+(float(q[2])-float(p[2]))*amount])
			polygon=output
			if polygon.size()<3: return []
	var doubled_area := 0.0
	for index in range(1,polygon.size()-1):
		var ux: float=polygon[index][0]-polygon[0][0]
		var uy: float=polygon[index][1]-polygon[0][1]
		var uz: float=polygon[index][2]-polygon[0][2]
		var vx: float=polygon[index+1][0]-polygon[0][0]
		var vy: float=polygon[index+1][1]-polygon[0][1]
		var vz: float=polygon[index+1][2]-polygon[0][2]
		doubled_area+=sqrt(pow(uy*vz-uz*vy,2)+pow(uz*vx-ux*vz,2)+pow(ux*vy-uy*vx,2))
	return polygon if doubled_area>1e-12 else []

func float32_ulp(value: float) -> float:
	if value==0.0: return pow(2.0,-149.0)
	return pow(2.0,floor(log(absf(value))/log(2.0))-23.0)

func triangle_same_vertices(actual: Array[Vector3], expected_face: Dictionary) -> bool:
	var expected: Array=expected_face.source_triangle_vertices_xyz
	if expected.size()!=3: return false
	var normal := xyz(expected_face.outward_triangle_normal_xyz).abs()
	var normal_axis := normal.max_axis_index()
	if normal[normal_axis]<.999999: return false
	var used: Dictionary = {}
	for point in actual:
		var match_index := -1
		for index in range(3):
			if used.has(index): continue
			var same := true
			for axis in range(3):
				var source_value := float(expected[index][axis])
				# One representable import step only in the face's tangent axes.
				# The actual normal plane and un-grown penetration gate remain <=1um.
				var tolerance := .000001 if axis==normal_axis else maxf(.000001,float32_ulp(source_value))
				if absf(float(point[axis])-source_value)>tolerance+1e-12: same=false
			if same:
				match_index=index
				break
		if match_index<0: return false
		used[match_index]=true
	return used.size()==3

func clipped_inside_band(polygon: Array, band: Dictionary) -> bool:
	var limits: Array=band.margin_clipped_bounds_xyz
	var normal_axis := int(band.get("plane_axis",band.get("contact_plane_axis",-1)))
	if normal_axis<0: return false
	for point in polygon:
		for axis in range(3):
			# Tangential window endpoints are derived from real float32 poses/grow.
			# Keep the physical bearing-plane normal bound strict and unchanged.
			var tolerance := .000001 if axis==normal_axis else maxf(.000001,maxf(float32_ulp(float(limits[axis])),float32_ulp(float(limits[axis+3]))))
			if float(point[axis])<float(limits[axis])-tolerance or float(point[axis])>float(limits[axis+3])+tolerance: return false
	return true

func dump_imported_source_geometry() -> void:
	var values := PackedFloat32Array()
	var records: Array=[]
	for item in built.find_children("*","MeshInstance3D",true,false):
		var mesh := item as MeshInstance3D
		var first := values.size()/9
		var faces := mesh.mesh.get_faces()
		for vertex in faces:
			var point: Vector3=mesh.global_transform*vertex
			values.append(point.x);values.append(point.y);values.append(point.z)
		var surfaces: Array=[]
		for surface in range(mesh.mesh.get_surface_count()):
			var arrays := mesh.mesh.surface_get_arrays(surface)
			var count := (arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size() if arrays[Mesh.ARRAY_INDEX]!=null else (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
			surfaces.append({"triangles":count/3,"material":str(mesh.get_active_material(surface).resource_name)})
		records.append({"name":str(mesh.name),"triangle_offset":first,"triangles":faces.size()/3,"surfaces":surfaces})
	var binary := FileAccess.open("res://artifacts/cell_imported_triangles.float32",FileAccess.WRITE)
	assert(binary!=null)
	binary.store_buffer(values.to_byte_array());binary.close()
	var metadata := FileAccess.open("res://artifacts/cell_imported_triangles.json",FileAccess.WRITE)
	assert(metadata!=null)
	metadata.store_string(JSON.stringify({"model_sha256":data.model_sha256,"groups":records,"coordinate_order":"Godot world XYZ little-endian float32 triangles","triangles":values.size()/9},"  "));metadata.close()

func classify_imported_gate_bearings() -> bool:
	var proof: Dictionary = checks.gate_bearing_contact_proof
	if not require(str(proof.model_sha256)==str(data.model_sha256) and proof.margin_candidate_fixed_triangle_count==8 and proof.exact_margin_candidate_faces.size()==8 and proof.un_grown_source_interior_triangle_hits.is_empty(), "Exact final eight-face bearing source proof missing"): return false
	if not require(absf(float(proof.runtime_query_margin_m)-.001)<.00000001, "Bearing proof must retain the 1 mm runtime query margin"): return false
	if not require(gate.leaves.size()==1 and gate.open_fraction<.001, "Bearing census requires the actual one-leaf closed rest"): return false
	var leaf: AnimatableBody3D = gate.leaves[0]
	var moving := leaf.find_children("*","CollisionShape3D",true,false)
	if not require(moving.size()==1 and moving[0].shape is BoxShape3D, "Bearing census requires the actual source-bound contact box"): return false
	var contact := moving[0] as CollisionShape3D
	var box := contact.shape as BoxShape3D
	var closed_pose: Transform3D = gate.global_transform*gate.closed_pose*contact.transform
	var open_pose: Transform3D = gate.global_transform*Transform3D(gate.closed_pose.basis,gate.closed_pose.origin+gate.travel_in_gate)*contact.transform
	var closed_box := contact_box_world(box,closed_pose)
	var open_box := contact_box_world(box,open_pose)
	verified_leaf_sweep=closed_box.merge(open_box)
	verified_leaf_size=box.size
	verified_leaf_basis=closed_pose.basis
	if not require(open_pose.basis==verified_leaf_basis, "Reviewed gate travel may not rotate/scale its collider"): return false
	var source_sweep := bounds(proof.full_actual_leaf_swept_bounds_xyz)
	if not require(verified_leaf_sweep.position.distance_to(source_sweep.position)<.001 and verified_leaf_sweep.end.distance_to(source_sweep.end)<.001, "Actual full collider sweep differs from source proof"): return false
	var margin_box := verified_leaf_sweep.grow(.001)
	var query := PhysicsShapeQueryParameters3D.new()
	var broad := BoxShape3D.new()
	broad.size=margin_box.size
	broad.margin=.001
	query.shape=broad
	query.transform.origin=margin_box.get_center()
	query.margin=0
	query.collision_mask=1
	query.collide_with_areas=false
	query.exclude=[leaf.get_rid()]
	var hits := space.intersect_shape(query,128)
	if not require(hits.size()<128, "Whole swept contact census query saturated"): return false
	var seen_bodies: Dictionary = {}
	var matched_faces: Dictionary = {}
	var band_counts: Dictionary = {}
	for hit in hits:
		var body := hit.collider as CollisionObject3D
		if not body is StaticBody3D: continue
		if not require(not body is AnimatableBody3D, "Unreviewed other moving architectural body intersects full gate sweep"): return false
		if seen_bodies.has(body.get_rid()): continue
		seen_bodies[body.get_rid()]=true
		var count_for_body := 0
		for node in body.find_children("*","CollisionShape3D",true,false):
			var fixed := node as CollisionShape3D
			if fixed.disabled: continue
			if not require(fixed.shape is ConcavePolygonShape3D, "Nearby fixed gate-sweep shape lacks reviewed exact source triangles"): return false
			var faces := (fixed.shape as ConcavePolygonShape3D).get_faces()
			var mesh := body.get_parent() as MeshInstance3D
			if mesh!=null:
				if not require(faces==mesh.mesh.get_faces() and fixed.global_transform==mesh.global_transform, "Physical fixed faces must exactly equal their actual imported mesh"): return false
			elif not require(floors.is_ancestor_of(body), "Nearby non-mesh fixed triangles must belong to a hash-pinned compiler slab"): return false
			verified_fixed_shapes.append({"shape":fixed,"shape_resource":fixed.shape,"faces":faces.duplicate(),"shape_pose":fixed.global_transform,"mesh":mesh,"mesh_resource":mesh.mesh if mesh!=null else null,"body":body,"layer":body.collision_layer})
			for index in range(0,faces.size(),3):
				var a: Vector3=fixed.global_transform*faces[index]
				var b: Vector3=fixed.global_transform*faces[index+1]
				var c: Vector3=fixed.global_transform*faces[index+2]
				# Strict overlap prefilter, including axis-aligned planar triangles.
				var low := a.min(b).min(c)
				var high := a.max(b).max(c)
				if high.x<=margin_box.position.x or high.y<=margin_box.position.y or high.z<=margin_box.position.z or low.x>=margin_box.end.x or low.y>=margin_box.end.y or low.z>=margin_box.end.z: continue
				if not require(triangle_clip_box(a,b,c,verified_leaf_sweep,.000001).is_empty(), "Actual fixed triangle penetrates un-grown full leaf sweep beyond <=1 micrometre tangency: " + str(body.get_path())): return false
				var clipped := triangle_clip_box(a,b,c,margin_box,.00000001)
				if clipped.is_empty(): continue
				if not require(mesh!=null, "Unclassified compiler slab face intersects gate margin envelope"): return false
				var actual: Array[Vector3]=[a,b,c]
				var match_index := -1
				for expected_index in range(proof.exact_margin_candidate_faces.size()):
					var expected: Dictionary=proof.exact_margin_candidate_faces[expected_index]
					if str(mesh.name)==str(expected.export_group) and triangle_same_vertices(actual,expected):
						if not require(match_index<0, "Ambiguous reviewed bearing face identity"): return false
						match_index=expected_index
				if match_index<0 or matched_faces.has(match_index):
					print("CELL_UNCLASSIFIED_BEARING_FACE:",JSON.stringify({"body":str(body.get_path()),"mesh":str(mesh.name),"face_index":index/3,"actual_vertices":[array_xyz(a),array_xyz(b),array_xyz(c)],"clipped":clipped,"match_index":match_index,"already_matched":matched_faces,"source_expected":proof.exact_margin_candidate_faces,"actual_sweep_position":array_xyz(verified_leaf_sweep.position),"actual_sweep_end":array_xyz(verified_leaf_sweep.end),"mesh_transform":str(mesh.global_transform)}))
				if not require(match_index>=0 and not matched_faces.has(match_index), "Unclassified or duplicate actual fixed face in 1 mm swept margin"): return false
				var expected: Dictionary=proof.exact_margin_candidate_faces[match_index]
				if not require(mesh.mesh.get_surface_count()==1 and str(mesh.get_active_material(0).resource_name)==str(expected.material), "Bearing face material/source group differs"): return false
				var band_name := ""
				for band in proof.reviewed_bearing_bands:
					if str(band.source_part)==str(expected.source_part) and clipped_inside_band(clipped,band): band_name=str(band.id)
				if not require(not band_name.is_empty(), "Actual clipped contact leaves its precisely reviewed cap/lip bearing band"): return false
				band_counts[band_name]=int(band_counts.get(band_name,0))+1
				matched_faces[match_index]=true
				count_for_body+=1
				bearing_records.append({"body":str(body.get_path()),"rid":str(body.get_rid()),"shape":str(fixed.get_path()),"face_index":index/3,"source_face_index":match_index,"band":band_name,"actual_world_vertices":[array_xyz(a),array_xyz(b),array_xyz(c)],"clipped_polygon":clipped})
		if count_for_body>0: verified_bearing_rids[body.get_rid()]=count_for_body
	if not require(matched_faces.size()==8 and verified_bearing_rids.size()==1, "Complete actual full-sweep contact set must be exactly eight source faces on one immutable RID"): return false
	for band in proof.reviewed_bearing_bands:
		if not require(int(band_counts.get(str(band.id),0))==int(band.expected_face_count), "Exact bearing-band face census differs"): return false
	return true

func leaf_clear() -> bool:
	if not require(gate.leaves.size() == 1, "Source fitting requires exactly one leaf"): return false
	var leaf: AnimatableBody3D = gate.leaves[0]
	var shapes := leaf.find_children("*", "CollisionShape3D", true, false)
	if not require(shapes.size() == 1 and shapes[0].shape is BoxShape3D and not shapes[0].disabled, "One exact active leaf contact required"): return false
	if not require(verified_bearing_rids.size()==1, "Full imported bearing classification must finish before any motion query"): return false
	if not require(shapes[0].shape.size==verified_leaf_size and shapes[0].global_basis==verified_leaf_basis, "Moving shape size/basis changed after exact sweep proof"): return false
	var actual_box := contact_box_world(shapes[0].shape,shapes[0].global_transform)
	for axis in range(3):
		if not require(float(actual_box.position[axis])>=float(verified_leaf_sweep.position[axis])-.000001 and float(actual_box.end[axis])<=float(verified_leaf_sweep.end[axis])+.000001, "Current collider pose escaped exact prevalidated travel bounds"): return false
	# Fixed source geometry never changes during this test. Recheck every actual
	# new moving pose, without repeating a large merged-contact triangle query
	# thousands of times while the player walks elsewhere and the gate rests.
	if leaf_pose_checked and shapes[0].global_transform == last_checked_leaf_pose: return true
	for snapshot in verified_fixed_shapes:
		var fixed: CollisionShape3D=snapshot.shape
		var mesh: MeshInstance3D=snapshot.mesh
		if not require(is_instance_valid(fixed) and not fixed.disabled and fixed.shape==snapshot.shape_resource and fixed.global_transform==snapshot.shape_pose and snapshot.body.collision_layer==snapshot.layer and fixed.shape.get_faces()==snapshot.faces, "Fixed physical face signatures or transforms changed after bearing classification"): return false
		if mesh!=null:
			if not require(is_instance_valid(mesh) and mesh.mesh==snapshot.mesh_resource and mesh.global_transform==snapshot.shape_pose and mesh.mesh.get_faces()==snapshot.faces, "Imported mesh geometry/transform changed after fixed-contact classification"): return false
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shapes[0].shape
	query.transform = shapes[0].global_transform
	query.margin = .001
	query.collision_mask = 1
	query.exclude = [leaf.get_rid()]
	var hits := space.intersect_shape(query, 128)
	if not require(hits.size() < 128, "Leaf query saturated"): return false
	for hit in hits:
		if hit.collider is StaticBody3D:
			if not require(verified_bearing_rids.has(hit.collider.get_rid()), "Unclassified fixed contact at fraction %.5f: %s" % [gate.open_fraction,hit.collider.get_path()]): return false
	last_checked_leaf_pose = shapes[0].global_transform
	leaf_pose_checked = true
	leaf_motion_samples += 1
	return true

func exact_gate_target(side: String) -> Node3D:
	var target := built.find_child("EngineeringCellGateTarget_" + side, true, false) as Node3D
	if not require(target != null, "Missing distinct source gate target: " + side): return null
	var marker := visual.find_child("TARGET_CELL_GATE_" + side, true, false) as Node3D
	if not require(marker != null and target.global_position.distance_to(marker.global_position) < .0001, "Gate target is not at its exact source marker: " + side): return null
	aim(marker.global_position)
	var start: Vector3 = actor.camera.global_position
	var query := PhysicsRayQueryParameters3D.create(start, start-actor.camera.global_basis.z*2.5)
	query.exclude = [actor.get_rid()]
	query.collide_with_areas = true
	var hit := space.intersect_ray(query)
	if not require(not hit.is_empty() and hit.collider is Area3D and target.is_ancestor_of(hit.collider), "Exact first ray hit must be this gate's own area: " + side): return null
	var collider := hit.collider as CollisionObject3D
	var owner_id := collider.shape_find_owner(int(hit.shape))
	var shape_owner := collider.shape_owner_get_owner(owner_id) as CollisionShape3D
	if not require(shape_owner != null and not shape_owner.disabled and shape_owner.shape is SphereShape3D and absf(shape_owner.shape.radius - .026) < .00001, "Exact first-hit target shape is not the bounded source button sphere"): return null
	if not require(actor.target_from_view() == target and target.gate == gate, "Original dispatcher must resolve this fixed button to the one real gate"): return null
	first_hit_records.append({"side":side,"actor_xyz":array_xyz(actor.global_position),"area":str(collider.get_path()),"shape_index":int(hit.shape),"shape_owner":str(shape_owner.get_path()),"leaf_fraction":gate.open_fraction})
	return target

func gate_button(side: String, expected_open: bool) -> bool:
	if exact_gate_target(side) == null: return false
	focus(true)
	if not await tap_e(): return false
	if not require(gate.desired_open == expected_open and not gate.obstructed, "Exact RMB/E gate command did not take effect from " + side): return false
	if not await advance(95): return false
	if not require(absf(gate.open_fraction - (1.0 if expected_open else 0.0)) < .001, "Gate did not finish commanded source-bound travel"): return false
	return aperture_state(expected_open)

func aperture_state(opened: bool) -> bool:
	var leaf: AnimatableBody3D = gate.leaves[0]
	var source := leaf.find_child("LEAF_WORKBAY_CELL", true, false) as MeshInstance3D
	if not require(source != null, "Moving source leaf missing"): return false
	var box := world_bounds(source)
	var expected := bounds(data.gate.open_leaf_bounds_xyz if opened else data.gate.closed_leaf_bounds_xyz)
	if not require(box.position.distance_to(expected.position) < .001 and box.end.distance_to(expected.end) < .001, "Leaf pose does not equal closed/open source bounds"): return false
	for z in [-404.9,-404.5,-404.1]:
		for y in [6.2,7.1,8.2]:
			var hit := ray(Vector3(21.5,y,z),Vector3(22.2,y,z),controlled_exclusions())
			if opened:
				if not require(hit.is_empty(), "Open source aperture retains invisible/fixed contact"): return false
			else:
				if not require(not hit.is_empty() and hit.collider == leaf, "Closed aperture must be obstructed by the actual moving leaf"): return false
	return true

func obstruction_prop(opened: bool) -> bool:
	# A small real loose body occupies the actual next-travel volume. No fixed
	# source contact is disabled; gravity_scale=0 merely holds this test fixture.
	var prop := RigidBody3D.new()
	prop.name = "CellTravelObstructionTestOnly"
	prop.gravity_scale = 0
	var contact := CollisionShape3D.new()
	var shape := SphereShape3D.new()
	shape.radius = .025
	contact.shape = shape
	prop.add_child(contact)
	ship.get_node("ShipSpace/PersistentActors").add_child(prop)
	prop.global_position = Vector3(21.8675,7.2,-404.5 if opened else -405.8)
	var initial := prop.global_position
	if not await advance(5): return false
	if not require(prop.global_position.distance_to(initial) < .003, "Obstruction fixture overlaps pre-existing geometry"): return false
	if exact_gate_target("OUTSIDE") == null: return false
	focus(true)
	var fraction: float = gate.open_fraction
	if not await tap_e(): return false
	if not require(gate.obstructed and gate.desired_open == opened, "Real loose prop must reject travel from both closed and open states"): return false
	if not await advance(12): return false
	if not require(absf(gate.open_fraction-fraction) < .00001, "Obstructed leaf advanced into loose body"): return false
	prop.queue_free()
	if not await advance(4): return false
	return require(not gate.obstructed, "Inherited obstruction clears when actual loose body is removed")

func gate_and_empty_hand_route() -> bool:
	if not require(str(gate.persistent_id) == str(data.gate.persistent_id), "Gate lost stable persistent identity"): return false
	if not require(gate.get_script().get_base_script().resource_path == "res://scripts/service_door.gd", "Gate must inherit existing state/pause/obstruction owner"): return false
	if not await arrive(OUTSIDE): return false
	if not aperture_state(false): return false
	if exact_gate_target("OUTSIDE") == null: return false
	focus(false)
	if not await tap_e(): return false
	if not require(not gate.desired_open and gate.open_fraction < .001, "Unfocused E must not operate gate"): return false
	if not await obstruction_prop(false): return false
	if not await gate_button("OUTSIDE", true): return false
	if not await obstruction_prop(true): return false
	if not await gate_button("OUTSIDE", false): return false
	# Mid-travel reversal uses another ordinary press/release, not state edits.
	if exact_gate_target("OUTSIDE") == null: return false
	focus(true)
	if not await tap_e() or not await advance(20): return false
	if not require(gate.open_fraction > .05 and gate.open_fraction < .6, "Reversal witness must be mid-travel"): return false
	if not await tap_e() or not await advance(95): return false
	if not aperture_state(false): return false
	# Held E is one event, not a per-frame toggle. Directory pause must retain pose.
	key(KEY_E, true)
	if not await advance(20): return false
	var paused_fraction: float = gate.open_fraction
	main._toggle_directory()
	if not require(paused and main.directory_open, "Actual directory must pause the scene"): return false
	for frame in range(12): await process_frame
	if not require(absf(gate.open_fraction-paused_fraction) < .00001, "Gate moved during inherited pause"): return false
	main._toggle_directory()
	if not require(not paused and actor.gameplay_input_enabled, "Directory resume failed"): return false
	if not await advance(100): return false
	key(KEY_E, false)
	if not require(gate.desired_open and gate.open_fraction > .999, "Held key must produce one command and resume travel normally"): return false
	if not await walk_path([Vector2(20.85,-404.5),Vector2(23.3,-404.5)]): return false
	if not require(absf(actor.global_position.y-5.55)<.08 and descent_frames>3, "Real original capsule did not descend actual flight"): return false
	if not await gate_button("INSIDE", false): return false
	if not await gate_button("INSIDE", true): return false
	if not await walk_to(Vector2(21.8675,-404.5)): return false
	if not require(gate._sweep_occupied(), "Actual original capsule in threshold must occupy gate sweep"): return false
	gate.interact(actor)
	if not require(gate.obstructed and gate.desired_open, "Person in real open aperture must prevent closing"): return false
	if not await walk_to(Vector2(20.85,-404.5)): return false
	if not await advance(8): return false
	if not require(not gate.obstructed and ascent_frames>3, "Capsule ascent/obstruction recovery failed"): return false
	return aperture_state(true)

func parked_cart_state() -> bool:
	if not require(cart.driver == null and cart.global_basis.y.dot(Vector3.UP) > .97 and absf(cart.global_position.y-6) < .10, "Actual cart must remain upright, released and upstairs"): return false
	if not require(cart.global_position.distance_to(parked_transform.origin) < .15, "Parked cart moved during on-foot tool route"): return false
	for product in cart.products:
		if product == tool: continue
		var local: Vector3 = cart.to_local(product.global_position)
		if not require(local.y>.85 and local.y<1.15 and absf(local.x)<.4 and absf(local.z)<.58, "Parked cart lost another loose product"): return false
	return true

func park_cart_once() -> bool:
	if not require(not parked and cart.products.size()==4 and cart.driver==null, "Exactly one initial physical cart fixture placement is allowed"): return false
	var locals: Array[Vector3] = []
	for product in cart.products: locals.append(cart.to_local(product.global_position))
	cart.global_position = PARK
	cart.rotation = Vector3(0,PARK_YAW,0)
	cart.linear_velocity = Vector3.ZERO
	cart.angular_velocity = Vector3.ZERO
	cart.sleeping = false
	for index in range(4):
		var product: RigidBody3D = cart.products[index]
		product.global_position = cart.global_transform * locals[index]
		product.linear_velocity = Vector3.ZERO
		product.angular_velocity = Vector3.ZERO
		product.sleeping = false
	if not await advance(90): return false
	parked_transform = cart.global_transform
	parked = true
	# Query every actual cart collider, four-product envelope and the original
	# operator capsule. Keep all source geometry; exclude only controlled bodies.
	var excluded := controlled_exclusions()
	for child in cart.get_children():
		if not child is CollisionShape3D: continue
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = child.shape
		query.transform = child.global_transform.translated(Vector3.UP*.015)
		query.margin = .001
		query.exclude = excluded
		var hits := space.intersect_shape(query,128)
		if not require(hits.size()<128 and hits.is_empty(), "Actual parked cart part intrudes into fixed architecture: " + str(child.name)): return false
	var contacts: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	for wheel in contacts.wheel_contacts:
		var point: Vector3 = cart.global_transform * Vector3(wheel.center[0],0,wheel.center[2])
		if not floor_hit(Vector3(point.x,6,point.z), UPPER_OWNER): return false
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	var operator_point := Vector3(28.38,6,-405)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.transform.origin = operator_point+Vector3.UP*.91
	query.exclude = excluded
	if not require(space.intersect_shape(query,128).is_empty(), "Actual parked operator envelope is obstructed"): return false
	if not floor_hit(operator_point, UPPER_OWNER): return false
	return parked_cart_state()

func pickup_tool() -> bool:
	for candidate in cart.products:
		aim(candidate.global_transform * candidate.grip_local)
		if actor.target_from_view() == candidate:
			tool = candidate
			break
	if not require(tool != null, "No actual loose cleaner can be picked up from parked cart/operator pose"): return false
	tool_home_local = cart.to_local(tool.global_position)
	focus(false)
	if not await tap_e(): return false
	if not require(tool.driver == null and actor.held_interaction == null, "Unfocused E must not pick up cleaner"): return false
	focus(true)
	if not await tap_e(): return false
	if not require(tool.driver == actor and actor.held_interaction == tool, "Ordinary RMB/E must take the real loose cleaning tool"): return false
	actor.pitch = 0
	actor.camera.rotation.x = 0
	if not await advance(70): return false
	return held_tool_state()

func held_priority_at_gate() -> bool:
	# Aim and press before the tether drifts into the sight line. The expected
	# action is release of the held bottle, even while the gate button is visible.
	var prior: bool = gate.desired_open
	var fraction: float = gate.open_fraction
	if exact_gate_target("OUTSIDE") == null: return false
	focus(true)
	if not await tap_e(): return false
	if not require(actor.held_interaction == null and tool.driver == null and gate.desired_open == prior and absf(gate.open_fraction-fraction)<.00001, "Held-object priority must release tool without operating gate"): return false
	if not await advance(60): return false
	aim(tool.global_transform*tool.grip_local)
	if not require(actor.target_from_view()==tool, "Released portable tool must be safely recoverable by its real first hit"): return false
	if not await tap_e(): return false
	if not require(tool.driver==actor and actor.held_interaction==tool, "Actual released tool recovery failed"): return false
	actor.pitch = 0
	actor.camera.rotation.x = 0
	return await advance(50)

func return_tool_to_cart() -> bool:
	# No product/cart transform, velocity, freeze or parent edits after parking.
	# Approach the empty tray slot, aim the ordinary 1.35 m physical tether,
	# release with RMB/E, and demand a real stable four-product return.
	# Return within the same empty slot, with a30mm inward aiming allowance
	# from the real end rim. Keep the existing strict .45m pre-release bound.
	var safe_home := tool_home_local
	safe_home.z = move_toward(safe_home.z,0.0,.03)
	var home: Vector3 = cart.global_transform * safe_home
	# Hold the real bottle above the1.01m tray rim, then release and let gravity
	# seat it. Aiming directly at its resting point while the spring sags pushes
	# the returning bottle into the solid rim instead of over the open mouth.
	var grip_y := home.y + .125 + .50
	var eye_y := 7.65
	var horizontal := sqrt(maxf(0.0,1.35*1.35-pow(eye_y-grip_y,2)))
	# The selected bottle's original slot is on the cart's far/east end.
	# Walk around its actual body in the supported upper service square instead
	# of asking the capsule to enter the cart from the west. No contact disabled.
	if not await walk_path([Vector2(28.38,-403.65),Vector2(31.55,-403.65),Vector2(31.55,home.z),Vector2(home.x+horizontal,home.z)]): return false
	# Do not reverse a held physical object180degrees in one frame through the
	# original capsule. Turn on foot at the same bounded rate used on this route.
	var toward_slot := Vector2(home.x-actor.global_position.x,home.z-actor.global_position.z)
	if not await face_heading(atan2(-toward_slot.x,-toward_slot.y)): return false
	if not require(absf(actor.camera.global_position.distance_to(Vector3(home.x,grip_y,home.z))-tool.hold_distance)<.015,"Actual standing pose must place the drop target on the original physical tether reach sphere"): return false
	aim(Vector3(home.x,grip_y,home.z))
	if not await advance(100): return false
	var local: Vector3 = cart.to_local(tool.global_position)
	print("CELL_CART_RETURN_STATE:",JSON.stringify({"actor_xyz":array_xyz(actor.global_position),"tool_xyz":array_xyz(tool.global_position),"tool_cart_local":array_xyz(local),"home_xyz":array_xyz(home),"grip_aim_xyz":[home.x,grip_y,home.z],"tool_grip_xyz":array_xyz(tool.global_transform*tool.grip_local),"velocity":array_xyz(tool.linear_velocity),"tool_basis_y":array_xyz(tool.global_basis.y)}))
	if not require(tool.driver==actor and absf(local.x)<.30 and absf(local.z)<.45 and local.y>.88 and local.y<1.35, "Original tether must place tool over the real tray before release"): return false
	focus(true)
	if not await tap_e(): return false
	if not require(actor.held_interaction==null and tool.driver==null, "Ordinary E must release returned tool"): return false
	if not await advance(150): return false
	for product in cart.products:
		var returned: Vector3 = cart.to_local(product.global_position)
		if not require(returned.y>.85 and returned.y<1.1 and absf(returned.x)<.4 and absf(returned.z)<.58 and product.linear_velocity.length()<.15, "Every loose product must finish safely settled in actual upper cart"): return false
	return parked_cart_state()

func portable_tool_route() -> bool:
	# Travel to the cart on foot first; placing it afterward avoids using the
	# parked fixture to mask the unchanged old engineering route test.
	if not await walk_path([Vector2(20.85,-402.95),Vector2(28.38,-402.95),Vector2(28.38,-405)]): return false
	if not await park_cart_once() or not await pickup_tool(): return false
	if not await walk_path([Vector2(28.38,-402.95),Vector2(20.85,-402.95),Vector2(20.85,-405.23)]): return false
	if not await held_priority_at_gate(): return false
	var prior_descent := descent_frames
	var prior_ascent := ascent_frames
	if not await walk_path([Vector2(20.85,-404.5),Vector2(23.3,-404.5),Vector2(24.5,-404.5)]): return false
	if not require(actor.held_interaction==tool and descent_frames>prior_descent+3 and absf(actor.global_position.y-5.55)<.08, "Actual tool carry did not reach lower service face through the three-step flight"): return false
	if not await sample_lighting_view("lower_live", false): return false
	if not await walk_path([Vector2(23.3,-404.5),Vector2(20.85,-404.5),Vector2(20.85,-402.95),Vector2(28.38,-402.95),Vector2(28.38,-405)]): return false
	if not require(actor.held_interaction==tool and ascent_frames>prior_ascent+3 and absf(actor.global_position.y-6)<.08, "Actual carried tool did not return upstairs"): return false
	return await return_tool_to_cart()

func light_proofs() -> bool:
	if not require(data.local_light_trial.size()==4 and budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32, "Source/candidate limits must remain exactly 4 new / 8 active / 32 candidates"): return false
	for item in data.local_light_trial:
		for field in ["first_receiver_group", "first_receiver_xyz", "receiver_tolerance_m", "receiver_source_sha256"]:
			if not require(item.has(field), "Unresolved source-backed receiver proof for " + str(item.marker) + ": " + field): return false
		if not require(not item.get("receiver_proof_pending",true), "Receiver proof is still explicitly pending: " + str(item.marker)): return false
		if not require(str(item.receiver_source_sha256)==str(data.model_sha256), "Receiver evidence must be recomputed against the exact final source export"): return false
		var light := built.find_child(str(item.light_name),true,false) as SpotLight3D
		var marker := visual.find_child(str(item.marker),true,false) as Node3D
		if not require(light!=null and marker!=null and budget.sources.has(light), "Source marker/emitter/selector binding missing: " + str(item.marker)): return false
		if not require(light.global_position.distance_to(xyz(item.expected_emitter_xyz))<.0001 and marker.global_position.distance_to(light.global_position)<.0001, "Emitter moved off exact source marker"): return false
		var direction := (xyz(item.aim_xyz)-light.global_position).normalized()
		if not require((-light.global_basis.z).dot(direction)>.99999 and is_equal_approx(light.spot_range,float(item.range_m)) and is_equal_approx(light.light_energy,float(item.energy)) and is_equal_approx(light.spot_angle,float(item.spot_angle)), "Local runtime trial differs from explicit source-bound values"): return false
		if not require(budget.requested_shadow.get(light.get_instance_id(),false), "New task light cannot become a wall-leaking unshadowed fallback"): return false
		if item.has("illumination_anchor_xyz"):
			if not require(str(item.marker)=="DATUM_CELL_LIGHT", "Only the specifically reviewed cell source may use a receiver anchor"): return false
			if not anchor_surface_proof(item,light): return false
		else:
			if not require(not light.has_meta("illumination_anchor"), "Unreviewed receiver anchor added to another source"): return false
		if not require(ray(light.global_position,light.global_position+direction*.10,controlled_exclusions()).is_empty(), "Source emitter exit trapped in fixture housing"): return false
		var expected := xyz(item.first_receiver_xyz)
		var tolerance := float(item.receiver_tolerance_m)
		if not require(tolerance>0 and tolerance<=.001 and expected.distance_to(light.global_position)<light.spot_range, "Receiver must be independently pinned within actual source range at <=1 mm tolerance"): return false
		# Aim is directional, not assumed to be the receiving surface. Ray extends
		# to full real light range; compare the first physics contact to source proof.
		var hit := ray(light.global_position,light.global_position+direction*light.spot_range,controlled_exclusions())
		if not require(not hit.is_empty() and hit.position.distance_to(expected)<=tolerance, "First actual source receiver position mismatch: " + str(item.marker)): return false
		if not require(str(hit.collider.get_parent().name)==str(item.first_receiver_group), "First receiver source/compiler owner mismatch: " + str(item.marker)): return false
		light_records.append({"marker":item.marker,"first_receiver":str(hit.collider.get_path()),"receiver_xyz":array_xyz(hit.position),"range_m":light.spot_range})
	if not require(checks.opaque_light_probes.size()>=4, "At least one physical opaque-wall/slab rejection witness per new light is required"): return false
	var proved: Dictionary = {}
	for probe in checks.opaque_light_probes:
		var start := xyz(probe.from_xyz)
		var finish := xyz(probe.to_xyz)
		var light: SpotLight3D
		for item in data.local_light_trial:
			if str(item.marker)==str(probe.marker): light=built.find_child(str(item.light_name),true,false) as SpotLight3D
		if not require(light!=null and start.distance_to(light.global_position)<.0001, "Opaque-ray witness must start at named real emitter"): return false
		var segment := finish-start
		if not require(segment.length()>.1 and segment.length()<=light.spot_range+.00001 and segment.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)), "Opaque-barrier witness must lie inside the actual light cone and range"): return false
		var hit := ray(start,finish,controlled_exclusions())
		if not require(not hit.is_empty() and str(probe.first_owner_contains) in str(hit.collider.get_path()), "Expected actual opaque barrier absent"): return false
		var receiver_mesh := hit.collider.get_parent() as MeshInstance3D
		if receiver_mesh != null:
			var material := receiver_mesh.get_active_material(0)
			if material is BaseMaterial3D:
				if not require(material.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED, "Opaque proof cannot use a transparent pane as its first barrier"): return false
			elif material is ShaderMaterial:
				if not require(material.shader!=null and not "glass" in material.shader.resource_path, "Opaque proof cannot use shared glass shader"): return false
		else:
			if not require(floors.is_ancestor_of(hit.collider), "Non-mesh opaque first contact must be a real compiler slab"): return false
		if not require(not budget._clear_sample(start,finish), "Unchanged selector incorrectly admits through-wall source sample"): return false
		proved[str(probe.marker)] = true
	return require(proved.size()==4, "Opaque barrier proofs must cover all four real light sources")

func anchor_surface_proof(item: Dictionary, light: SpotLight3D) -> bool:
	if not require(item.has("illumination_anchor_surface"), "Receiver anchor lacks independently pinned surface proof"): return false
	var proof: Dictionary = item.illumination_anchor_surface
	if not require(str(proof.source_sha256)==str(data.model_sha256) and not proof.source_receiver_proof_pending, "Anchor patch must be recomputed against the exact final frozen export"): return false
	var anchor := xyz(item.illumination_anchor_xyz)
	var point := xyz(proof.position_xyz)
	var tolerance := float(proof.tolerance_m)
	if not require(tolerance>0 and tolerance<=.001 and absf(float(proof.source_path_offset_m)-.025)<.00001, "Reviewed patch requires <=1 mm source match and exactly 25 mm toward-source offset"): return false
	if not require(light.get_meta("illumination_anchor") is Vector3 and light.get_meta("illumination_anchor").distance_to(anchor)<.00001, "Runtime light does not use the exact approved receiver anchor"): return false
	var direction := (point-light.global_position).normalized()
	if not require(anchor.distance_to(point-direction*.025)<.00001 and anchor.distance_to(light.global_position)<light.spot_range and (anchor-light.global_position).normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)), "Anchor must sit ahead of its real illuminated patch inside the unchanged cone/range"): return false
	var hit := ray(light.global_position,point+direction*.04,controlled_exclusions())
	if not require(not hit.is_empty() and str(hit.collider.get_parent().name)==str(proof.group) and hit.position.distance_to(point)<=tolerance, "Actual imported first-hit anchor patch differs from independent source proof"): return false
	var mesh := visual.find_child(str(proof.group),true,false) as MeshInstance3D
	if not require(mesh!=null and proof.triangle_xyz.size()==3, "Pinned anchor triangle/source group missing"): return false
	var faces := mesh.mesh.get_faces()
	var found := false
	for index in range(0,faces.size(),3):
		var all_vertices := true
		for source_vertex in proof.triangle_xyz:
			var matched := false
			for corner in range(3):
				if (mesh.global_transform*faces[index+corner]).distance_to(xyz(source_vertex))<=tolerance: matched=true
			all_vertices = all_vertices and matched
		if all_vertices:
			found = true
			break
	if not require(found, "Independent anchor triangle is absent from actual imported mesh"): return false
	if not require(ray(light.global_position,anchor,controlled_exclusions()).is_empty() and budget._clear_sample(light.global_position,anchor), "Actual source-to-anchor optical path is not clear"): return false
	return true

func bounded_selector_trace(start: Vector3, finish: Vector3) -> Dictionary:
	# Mirror the original selector's exact six-query bound and transparency rule
	# as evidence only. Do not change the selector, masks or source collisions.
	var query := PhysicsRayQueryParameters3D.create(start,finish)
	query.exclude = [actor.get_rid()]
	var crossed: Array = []
	for crossing in range(6):
		var hit := space.intersect_ray(query)
		if hit.is_empty(): return {"clear":true,"crossings":crossed}
		var body := hit.collider as CollisionObject3D
		var transparent := body is RigidBody3D or body is CharacterBody3D
		var mesh := body.get_parent() as MeshInstance3D
		if mesh!=null:
			var material := mesh.get_active_material(0)
			if material is ShaderMaterial and material.shader!=null and "glass" in material.shader.resource_path: transparent=true
			elif material is StandardMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED: transparent=true
		crossed.append({"body":str(body.get_path()),"transparent_under_existing_rule":transparent})
		if not transparent: return {"clear":false,"crossings":crossed}
		var excluded := query.exclude
		excluded.append(body.get_rid())
		query.exclude = excluded
	return {"clear":false,"crossings":crossed}

func anchor_view_proof(label: String) -> bool:
	for item in data.local_light_trial:
		if not item.has("illumination_anchor_surface") or str(item.illumination_anchor_surface.required_view)!=label: continue
		var light := built.find_child(str(item.light_name),true,false) as SpotLight3D
		var anchor := xyz(item.illumination_anchor_xyz)
		var visible := false
		var traces: Array = []
		for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1.0,0),Vector3(-.65,1.0,0)]:
			var end: Vector3 = actor.global_position+offset
			var trace := bounded_selector_trace(anchor,end)
			if not require(bool(trace.clear)==bool(budget._clear_sample(anchor,end)) and trace.crossings.size()<=6, "Anchor visibility evidence disagrees with unchanged bounded transparent handling"): return false
			trace["end_xyz"] = array_xyz(end)
			traces.append(trace)
			visible = visible or bool(trace.clear)
		if not require(visible and budget._has_visible_sample(light) and light.visible and light.shadow_enabled, "Actual illuminated patch must be visible/selected from required original player view"): return false
		selection_records.append({"view":label,"anchor_marker":item.marker,"anchor_xyz":array_xyz(anchor),"bounded_visibility_traces":traces})
	return true

func sample_lighting_view(label: String, use_expected: bool) -> bool:
	budget.refresh()
	var active := 0
	var selected: Array = []
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active += 1
	if not require(active<=8 and budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32, "Unchanged 8/32 selector exceeded during actual route"): return false
	for item in data.local_light_trial:
		var light := built.find_child(str(item.light_name),true,false) as SpotLight3D
		if not require(light.visible==light.shadow_enabled, "New source became visible without its required shadow"): return false
		if light.visible:
			if not require(budget._has_visible_sample(light), "Selected source has no permitted visible sample"): return false
			selected.append(str(item.marker))
	selection_records.append({"view":label,"actor_xyz":array_xyz(actor.global_position),"active_ship_sources":active,"selected_new_markers":selected})
	if use_expected:
		for view in checks.lighting_selection_views:
			if str(view.label)!=label: continue
			if not require(view.selected_markers.size()>0, "Lighting witness cannot pass with every new source absent"): return false
			for marker in view.selected_markers:
				if not require(selected.has(str(marker)), "Required source is starved at " + label + ": " + str(marker)): return false
		if not anchor_view_proof(label): return false
	return true

func light_selection_routes() -> bool:
	var upper := false
	var lower := false
	var covered: Dictionary = {}
	if not require(checks.lighting_selection_views.size()>=2, "Explicit upper/lower lighting view proofs required"): return false
	# One initial arrival. Each explicit witness route continues from the prior
	# real player location; no viewpoint teleport may hide a blocked approach.
	if not await arrive(OUTSIDE): return false
	for view in checks.lighting_selection_views:
		if not require(view.has("route_xz"), "Lighting selection witness needs a continuous outside-to-view route"): return false
		var foot := xyz(view.foot_xyz)
		for point in view.route_xz:
			if not await walk_to(Vector2(point[0],point[1])): return false
			if not await sample_lighting_view(str(view.label)+"_route",false): return false
		if not require(Vector2(actor.global_position.x,actor.global_position.z).distance_to(Vector2(foot.x,foot.z))<.15 and absf(actor.global_position.y-foot.y)<.14, "Selection view is not physically reached at its declared deck/position"): return false
		if not await advance(15): return false
		if not await sample_lighting_view(str(view.label),true): return false
		upper = upper or absf(foot.y-6)<.0001
		lower = lower or absf(foot.y-5.55)<.0001
		for marker in view.selected_markers: covered[str(marker)] = true
	if not require(upper and lower and covered.size()==4, "Upper/lower selection witnesses must require all four new sources at their relevant views"): return false
	if not require(absf(actor.global_position.y-5.55)<.14, "Declared source-light witness sequence must end at the lower service face"): return false
	return await walk_path([Vector2(23.3,-404.5),Vector2(20.85,-404.5)])

func run() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not require(parsed is Dictionary, "Runtime contract missing or invalid JSON"): return
	data = parsed
	if not check_pins(): return
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	cart = ship.find_child("CustodialCart",true,false) as RigidBody3D
	built = ship.find_child("SecondaryEngineeringWorkbayCell",true,false) as Node3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	budget = ship.find_child("LocalShadowSourceBudget",true,false)
	if not require(cart!=null and built!=null and floors!=null and budget!=null, "Integrated original scene is missing required real actors/owners"): return
	if not require(built.get_meta("first_pass_quality_accepted",true)==false and not data.first_pass_accepted, "Focused test may not silently certify first-pass completion"): return
	gate = built.find_child("EngineeringCellGate",true,false) as Node3D
	if not require(gate!=null, "Actual source-bound gate missing"): return
	visual = gate.authored_visual
	if not require(visual!=null and visual.global_transform.is_equal_approx(Transform3D.IDENTITY), "New export must retain identity world placement"): return
	space = ship.get_world_3d().direct_space_state
	# Never disable player physics, rescale its capsule, modify floor snap, force
	# move_and_slide externally, or change any shared input/controller setting.
	if not require(actor.is_physics_processing(), "Production original-player physics must remain enabled"): return
	if not mark("source groups, materials and exact contacts") or not mesh_and_contact_census(): return
	dump_imported_source_geometry()
	if not mark("exact imported full-sweep gate bearing face census") or not classify_imported_gate_bearings(): return
	if not mark("compiler cut, lower slab, underside and stair contact") or not floor_topology_and_stair(): return
	if not mark("preserved guest/internal engineering routes") or not await retained_routes(): return
	if not mark("both-side first-hit RMB/E, gate travel, pause and obstruction") or not await gate_and_empty_hand_route(): return
	if not mark("actual loose cleaner cannot enter under-tread gap") or not await under_tread_loose_bottle(): return
	if not mark("source-backed emitter, actual receiver and opaque barrier proofs") or not light_proofs(): return
	if not mark("upper/lower source selection on physical routes") or not await light_selection_routes(): return
	if not mark("upper parked cart, ordinary portable cleaner carry and return") or not await portable_tool_route(): return
	if not check_pins() or failed: return
	release_inputs()
	checkpoint = "complete focused runtime checks"
	write_receipt("PASS")
	if failed: return
	print("SECONDARY ENGINEERING CELL PASS: 153 source groups / ",data.source_triangles," final frozen triangles; 10 exact hidden pane proxies; real compiler cut/lower slab/underside; grounded stair closes actual loose-bottle gap; original player ascent/descent; both-side first-hit RMB/E and source gate travel/obstruction/pause; parked upper cart with physical cleaner carry/return; four source-backed emitters/receivers under unchanged 8/32 selection. Focused proof only: visual, old full regressions and aggregate validation remain separate.")
	main.queue_free()
	await process_frame
	quit(0)
