extends RefCounted
# UNRUN scratch draft. Test helpers only; never build/repair the venue in a test.
const CONTRACT := "res://data/architecture/THEATER_RUNTIME_STAGE001.json"
const FIXTURES := "res://tests/fixtures/THEATER_TEST_FIXTURES.json"
const FLOOR := 69.5
const NATIVE_INSTANCE_QA := "res://docs/THEATER_NATIVE_INSTANCE_QA.json"
const NATIVE_INSTANCE_QA_SHA := "59d8c3f4e4b2bf85ae82ab798088197b05c1baddd376f50a73fcb1f730f494ad"
const OPTIC = preload("res://tests/court_a_aimed_optic_probe.gd")
const ENTRY = preload("res://tests/theater_d11_entry_probe.gd")
var data: Dictionary
var fixture: Dictionary
var ship: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var venue: Node3D
var shell: Node3D
var bridge: Node3D
var motion: Node3D
var assembly: Node3D
var floors: Node3D
var budget: Node
var space: PhysicsDirectSpaceState3D
var floor_samples := 0
var light_samples: Array = []
var held_poses: Dictionary = {}

func configure(current_ship: Node3D) -> void:
	ship = current_ship
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	cart = ship.find_child("CustodialCart", true, false) as RigidBody3D
	venue = ship.find_child("GrandLanternTheater_ConnectedStaticStage_WIP", true, false)
	assert(venue != null, "Theater must already be integrated into the actual main scene")
	assert(venue.global_transform.is_equal_approx(Transform3D.IDENTITY))
	shell = venue.get_node("TheaterSourceArchitecture")
	bridge = venue.get_node("TheaterReceivingPortico")
	motion = venue.get_node("TheaterUnpoweredDoorLiftAssemblies")
	assembly = venue.get_node("RetainedAuthoredInstances")
	floors = ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	budget = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	space = ship.get_world_3d().direct_space_state
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	fixture = JSON.parse_string(FileAccess.get_file_as_string(FIXTURES))
	assert(FileAccess.get_sha256(CONTRACT) == str(fixture.runtime_contract_sha256))
	assert(FileAccess.get_sha256("res://scripts/grand_lantern_theater_section.gd") == str(fixture.runtime_builder_sha256))
	for path in fixture.retained_runtime_pins:
		assert(FileAccess.get_sha256("res://" + str(path)) == str(fixture.retained_runtime_pins[path]), "Unchanged runtime dependency required: " + str(path))
	assert(load("res://scripts/lighting_budget.gd").MAX_VISIBILITY_CANDIDATES == 32)
	assert(budget.shadow_source_budget == 8)
	assert(cart != null and cart.products.size() == 4)
	OPTIC.check_installation(ship)
	ENTRY.check_installation(ship)

func xyz(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))

func matrix(a: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(a[0][0],a[1][0],a[2][0]),Vector3(a[0][1],a[1][1],a[2][1]),Vector3(a[0][2],a[1][2],a[2][2])),Vector3(a[0][3],a[1][3],a[2][3]))

func relative(node: Node3D, ancestor: Node3D) -> Transform3D:
	var result := node.transform
	var cursor := node.get_parent()
	while cursor != ancestor:
		assert(cursor != null and cursor is Node3D)
		result = (cursor as Node3D).transform * result
		cursor = cursor.get_parent()
	return result

func assert_transform(actual: Transform3D, expected: Transform3D, label: String) -> void:
	assert(actual.origin.distance_to(expected.origin) < .0001, label + " origin differs")
	for axis in range(3):
		assert(actual.basis[axis].distance_to(expected.basis[axis]) < .00001, label + " basis differs")

func exclusions() -> Array[RID]:
	var result: Array[RID] = [actor.get_rid(), cart.get_rid()]
	for product in cart.products: result.append(product.get_rid())
	return result

func ray(a: Vector3, b: Vector3, excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a, b, 1)
	query.hit_back_faces = true
	query.exclude = excluded
	return space.intersect_ray(query)

func all_hits(a: Vector3, b: Vector3) -> Array:
	var excluded := exclusions()
	var hits: Array = []
	for index in range(64):
		var hit := ray(a, b, excluded)
		if hit.is_empty(): return hits
		hits.append(hit)
		excluded.append(hit.collider.get_rid())
	assert(false, "Unsaturated exact-owner ray required")
	return hits

func clear_box(low: Vector3, high: Vector3, label: String) -> void:
	var box := BoxShape3D.new()
	box.size = high - low
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = box
	query.margin = .001
	query.transform.origin = (low + high) * .5
	query.exclude = exclusions()
	query.collision_mask = 1
	var hits := space.intersect_shape(query, 128)
	assert(hits.size() < 128)
	for hit in hits: print("THEATER CLEARANCE BLOCK: ", label, " ", hit.collider.get_path())
	assert(hits.is_empty(), label)

func floor_at(point: Vector3, exact_owner: String = "") -> void:
	var hit := ray(point + Vector3.UP * .20, point - Vector3.UP * .20, exclusions())
	assert(not hit.is_empty(), "No real support at " + str(point))
	assert(absf(hit.position.y - FLOOR) < .015, "Wrong deck support at " + str(point))
	var expected := exact_owner
	if expected.is_empty():
		# The external spine, new bridge, and approved D11 flat partition own the
		# route. No furniture, cabin, wall, or generic cover may substitute.
		expected = "D11_fore_route" if point.x > -4.0 else ("D11_theater_receiving_bridge" if point.x > -34.0 else "D11_theater_flat_00")
	var owner := floors.get_node_or_null(NodePath(expected))
	assert(owner != null and owner.is_ancestor_of(hit.collider), "Wrong walking owner at %s: %s, expected %s" % [point, hit.collider.get_path(), expected])
	floor_samples += 1

func check_exact_contact(mesh: MeshInstance3D, expected: bool = true) -> void:
	var body := mesh.get_node_or_null("SourceStaticContact") as StaticBody3D
	if not expected:
		assert(body == null and mesh.find_children("*", "CollisionObject3D", true, false).is_empty(), "Visual cabin must have no collider")
		return
	assert(body != null and body.collision_layer == 1)
	assert(body.transform.is_equal_approx(Transform3D.IDENTITY))
	var shape := body.get_node("ExactSourceTriangles") as CollisionShape3D
	assert(not shape.disabled and shape.transform.is_equal_approx(Transform3D.IDENTITY))
	assert(shape.shape is ConcavePolygonShape3D and absf(shape.shape.margin - .001) < .000001)
	var actual: PackedVector3Array = shape.shape.get_faces()
	var original: PackedVector3Array = mesh.mesh.get_faces()
	assert(actual.size() == original.size() and actual.size() > 0)
	for index in range(actual.size()): assert(actual[index].distance_to(original[index]) < .000001)

func check_import_and_scene_census() -> void:
	for kind in fixture.models:
		var spec: Dictionary = fixture.models[kind]
		var path := "res://assets/models/" + str(spec.file)
		assert(FileAccess.get_sha256(path) == str(spec.sha256))
		var config := ConfigFile.new()
		assert(config.load(path + ".import") == OK)
		assert(config.get_value("params", "meshes/force_disable_compression", false), "Exact source positions require lossless import")
		var cache := str(config.get_value("remap", "path", ""))
		assert(not cache.is_empty() and FileAccess.file_exists(cache))
		var digest := ConfigFile.new()
		assert(digest.load(cache.get_basename() + ".md5") == OK)
		assert(digest.get_value("", "source_md5", "") == FileAccess.get_md5(path), "Fresh import required: " + path)
		var imported := (load(path) as PackedScene).instantiate() as Node3D
		var meshes := imported.find_children("*", "MeshInstance3D", true, false)
		assert(meshes.size() == int(spec.mesh_count))
		var total := 0
		var seen: Dictionary = {}
		for item in meshes:
			var mesh := item as MeshInstance3D
			var name := str(mesh.name)
			assert(not seen.has(name) and spec.batches.has(name))
			seen[name] = true
			var faces: PackedVector3Array = mesh.mesh.get_faces()
			assert(faces.size() == int(spec.batches[name]) * 3, "Imported triangle census: " + name)
			total += int(faces.size() / 3)
		assert(total == int(spec.triangles))
		if kind in ["static", "bridge"]:
			var built: Node3D = shell if kind == "static" else bridge
			assert(built.find_children("*", "MeshInstance3D", true, false).size() == meshes.size())
			for item in meshes:
				var actual := built.find_child(str(item.name), true, false) as MeshInstance3D
				assert(actual != null)
				assert_transform(relative(actual,built), relative(item,imported), str(item.name))
				if kind == "static" and str(item.name) == "C005_S_0326":
					OPTIC.check_replacement(actual,item)
				else:
					assert(actual.mesh == item.mesh)
					check_exact_contact(actual)
		imported.free()
	assert(shell.find_children("*", "MeshInstance3D", true, false).size() == 747)
	assert(bridge.find_children("*", "MeshInstance3D", true, false).size() == 83)
	assert(motion.find_children("*", "MeshInstance3D", true, false).size() == 120)

func check_instances() -> void:
	var dummy_readback := DisplayServer.get_name() == "headless" and RenderingServer.get_video_adapter_name().is_empty()
	if dummy_readback: assert(require_retained_native_readback(), "Native readback evidence validator must complete")
	var template := (load("res://assets/models/" + str(data.prototype_file)) as PackedScene).instantiate() as Node3D
	var local_parts: Dictionary = {}
	var prototype_faces: Dictionary = {}
	var records: Dictionary = {}
	var expected_pairs: Dictionary = {}
	var expected_groups: Dictionary = {}
	var expected_contacts := 0
	var chair_ids: Dictionary = {}
	var chair_poses: Dictionary = {}
	for identity in data.prototypes:
		var definition: Dictionary = data.prototypes[identity]
		var anchor := template.find_child(str(definition.root_node), true, false) as Node3D
		assert(anchor != null)
		var faces := PackedVector3Array()
		for name in definition.batches:
			var part := anchor.find_child(str(name), true, false) as MeshInstance3D
			assert(part != null)
			var transform := relative(part, anchor)
			local_parts[name] = {"transform":transform, "mesh":part.mesh}
			for p in part.mesh.get_faces(): faces.append(transform * p)
		prototype_faces[identity] = faces
	for record in data.instances:
		var identity := str(record.id)
		assert(not records.has(identity), "Repeated source ID")
		records[identity] = record
		var transform := matrix(record.native_matrix)
		var group := str(record.definition) + "|%d|%d|%d" % [floori(transform.origin.x/16.0), floori(transform.origin.y/6.0), floori(transform.origin.z/16.0)]
		for part in data.prototypes[record.definition].batches:
			expected_pairs[identity + "|" + str(part)] = true
			expected_groups[group + "|" + str(part)] = true
		if data.prototypes[record.definition].collides: expected_contacts += 1
		if record.audience_chair:
			chair_ids[identity] = true
			var key := "%.5f|%.5f|%.5f" % [transform.origin.x,transform.origin.y,transform.origin.z]
			assert(not chair_poses.has(key), "Duplicate chair placement")
			chair_poses[key] = true
	assert(records.size() == 2494 and chair_ids.size() == 2200 and chair_poses.size() == 2200)
	var seen_pairs: Dictionary = {}
	var seen_contacts: Dictionary = {}
	var checked_shapes: Dictionary = {}
	var views := assembly.find_children("*", "MultiMeshInstance3D", true, false)
	assert(views.size() == expected_groups.size(), "Actual spatial rendering batch census differs")
	for item in views:
		var view := item as MultiMeshInstance3D
		var ids: Array = view.get_meta("source_instance_ids")
		var part := str(view.get_meta("source_prototype_batch"))
		assert(local_parts.has(part) and view.multimesh.mesh == local_parts[part].mesh)
		assert(view.multimesh.instance_count == ids.size() and view.multimesh.visible_instance_count == -1)
		assert(view.transform.is_equal_approx(Transform3D.IDENTITY))
		for index in range(ids.size()):
			var identity := str(ids[index])
			var key := identity + "|" + part
			assert(expected_pairs.has(key) and not seen_pairs.has(key), "Missing/duplicate/wrong prototype part " + key)
			seen_pairs[key] = true
			if not dummy_readback:
				assert_transform(view.multimesh.get_instance_transform(index), matrix(records[identity].native_matrix) * local_parts[part].transform, key)
	assert(seen_pairs.size() == expected_pairs.size())
	var contacts := assembly.find_children("*", "StaticBody3D", true, false)
	assert(contacts.size() == expected_contacts)
	for node in contacts:
		var body := node as StaticBody3D
		var identity := str(body.get_meta("source_instance_id"))
		assert(records.has(identity) and not seen_contacts.has(identity))
		seen_contacts[identity] = true
		var definition := str(records[identity].definition)
		assert(data.prototypes[definition].collides and str(body.get_meta("source_definition")) == definition)
		assert_transform(body.transform, matrix(records[identity].native_matrix), identity)
		assert(body.get_child_count() == 1 and body.get_child(0) is CollisionShape3D)
		var collider := body.get_child(0) as CollisionShape3D
		assert(not collider.disabled and collider.shape is ConcavePolygonShape3D)
		assert(collider.transform.is_equal_approx(Transform3D.IDENTITY) and body.collision_layer == 1)
		var shape_id := collider.shape.get_instance_id()
		if not checked_shapes.has(shape_id):
			var actual: PackedVector3Array = collider.shape.get_faces()
			var expected: PackedVector3Array = prototype_faces[definition]
			assert(actual.size() == expected.size())
			for i in range(actual.size()): assert(actual[i].distance_to(expected[i]) < .000001)
			checked_shapes[shape_id] = definition
		assert(checked_shapes[shape_id] == definition)
	for identity in chair_ids: assert(seen_contacts.has(identity), "Every one of 2200 chairs needs its actual contact")
	template.free()
	print("THEATER INSTANCE CENSUS: unique chairs=",chair_ids.size()," unique placements=",records.size()," contact bodies=",contacts.size()," visual parts=",seen_pairs.size()," spatial batches=",views.size())

func check_floor_owners() -> void:
	assert(FileAccess.get_sha256("res://data/architecture/packages/theater/SOURCE_SURFACE_MANIFEST_003.json") == str(fixture.source_manifest_sha256))
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var actual: Dictionary = {}
	for row in layout.regions:
		assert(not actual.has(str(row.id)))
		actual[str(row.id)] = row
	var compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var compiled_ids: Dictionary = {}
	for row in compiled.regions:
		assert(not compiled_ids.has(str(row.id)))
		compiled_ids[str(row.id)] = row
	var allowed: Dictionary = {}
	for expected in fixture.expected_regions:
		var identity := str(expected.id)
		assert(actual.has(identity), "Missing precise source owner " + identity)
		var row: Dictionary = actual[identity]
		for field in ["deck","boundary","holes","owner","provided_by_asset","kind","void_exemptions","source_surface_manifest_sha256","source_static_export_sha256","source_blend_sha256","source_partition_sha256","walkable","thickness"]:
			assert(row.get(field) == expected.get(field), "Changed exact theater owner " + identity + ": " + field)
		allowed[identity] = true
		if expected.get("provided_by_asset", false):
			assert(not compiled_ids.has(identity) and floors.get_node_or_null(NodePath(identity)) == null, "Source upper floor must not acquire a duplicate compiler slab")
		else:
			assert(compiled_ids.has(identity) and floors.get_node_or_null(NodePath(identity)) != null)
	for row in layout.regions:
		if row.get("owner", "") == "grand_lantern_theater" or "theater_upper_volume" in row.get("void_exemptions", []):
			assert(allowed.has(str(row.id)), "Unapproved generic theater or cabin walking credit")
	assert(allowed.size() == 17 and fixture.source_owner_batches.size() == 8)
	# Structural foundations retain physical support but never gain walking,
	# navigation or public walking-area credit. Require explicit false metadata.
	var foundation_count := 0
	for index in range(7):
		var identity := "D11_theater_foundation_%02d" % index
		assert(allowed.has(identity) and compiled_ids.has(identity))
		var foundation := floors.get_node_or_null(NodePath(identity)) as Node3D
		assert(foundation != null)
		for key in ["walkable", "navigation_surface", "walking_area_credit"]:
			assert(foundation.has_meta(key) and typeof(foundation.get_meta(key)) == TYPE_BOOL and foundation.get_meta(key) == false, "Foundation must explicitly reject " + key + ": " + identity)
		var bodies := foundation.find_children("*", "StaticBody3D", true, false)
		assert(not bodies.is_empty(), "Nonwalking foundation must retain real structural collision: " + identity)
		var live_shapes := 0
		for item in bodies:
			var body := item as StaticBody3D
			assert((body.collision_layer & 1) != 0)
			for node in body.find_children("*", "CollisionShape3D", true, false):
				var collider := node as CollisionShape3D
				assert(not collider.disabled and collider.shape is ConcavePolygonShape3D)
				assert(collider.shape.get_faces().size() > 0)
				live_shapes += 1
		assert(live_shapes > 0, "Metadata cannot replace foundation collision: " + identity)
		foundation_count += 1
	assert(foundation_count == 7)
	assert(absf(float(compiled_ids["D11_theater_foundation_00"].structural_area_m2) - 504.0) < .000001, "Only the exact approved 504m2 stage foundation is permitted")
	var stage_foundation_samples := 0
	for sample in fixture.source_floor_probes:
		var p := xyz(sample.point)
		var hits := all_hits(p + Vector3.UP*.018, p - Vector3.UP*.018)
		var exact: Dictionary = {}
		for hit in hits:
			assert(not floors.is_ancestor_of(hit.collider), "Compiler duplicates actual source floor at " + str(sample))
			if shell.is_ancestor_of(hit.collider) and str(hit.collider.get_parent().name) in fixture.source_walkable_batches:
				var batch := str(hit.collider.get_parent().name)
				assert(batch in sample.batches and not exact.has(batch), "Wrong/duplicate source-floor batch at " + str(sample))
				assert(absf(hit.position.y-p.y) < .003)
				exact[batch] = true
		assert(exact.size() == sample.batches.size(), "Missing exact source owner " + str(sample))
		# Only stage_36x14 has an approved structural foundation below its
		# Y70.1 source floor. Every other lower projection forbids compiler hits.
		if sample.get("lower_projection",false):
			var is_stage: bool = str(sample.owner) == "stage_36x14"
			var supporting_hits := 0
			for hit in all_hits(Vector3(p.x,FLOOR+.018,p.z),Vector3(p.x,FLOOR-.018,p.z)):
				if not floors.is_ancestor_of(hit.collider): continue
				assert(is_stage, "Compiler retained under a non-stage source-owned lower projection: " + str(sample.owner))
				var approved := floors.get_node("D11_theater_foundation_00")
				assert(approved.is_ancestor_of(hit.collider), "Stage support must be only its exact approved foundation00")
				assert(absf(hit.position.y-FLOOR) < .003 and hit.normal.y > .99, "Stage foundation must physically support at Y69.5")
				supporting_hits += 1
			if is_stage:
				assert(absf(p.y-70.1) < .003 and supporting_hits == 1, "Stage sample requires its one actual supporting foundation")
				stage_foundation_samples += 1
			else:
				assert(supporting_hits == 0, "No compiler-slab allowance beneath ramps, sill, stair start or rake")
		floor_samples += 1
	assert(stage_foundation_samples == 1, "Retain the exact stage_36x14 source sample and its supporting-foundation witness")
	for a in fixture.open_void_points:
		var p := xyz(a)
		assert(all_hits(p+Vector3.UP*.018,p-Vector3.UP*.018).is_empty(), "Authored open volume has been capped at " + str(p))
	# All three future moving-cabin stops remain non-walkable empty shaft space.
	for y in [69.5,78.0,84.0]:
		for x in [-43.5,-41.5,-39.5]:
			for z in [-123.0,-121.0,-119.0]:
				assert(all_hits(Vector3(x,y+.018,z),Vector3(x,y-.018,z)).is_empty(), "Static cabin floor credit is forbidden")

func check_motion_poses_and_barriers() -> void:
	assert(data.held_open_groups == ["THEATER_D11_MAIN_LEAF_LEFT","THEATER_D11_MAIN_LEAF_RIGHT"])
	ENTRY.check_installation(ship)
	assert(data.motion_groups.size() == 39)
	var fully_open := true
	var active_groups := 0
	var template := (load("res://assets/models/" + str(data.moving_file)) as PackedScene).instantiate() as Node3D
	for identity in data.motion_groups:
		var spec: Dictionary = data.motion_groups[identity]
		var node := motion.find_child(str(data.motion_node_names[identity]),true,false) as Node3D
		var original := template.find_child(str(data.motion_node_names[identity]),true,false) as Node3D
		assert(node != null and original != null)
		var expected := relative(original,template)
		var held: bool = identity in data.held_open_groups
		if held:
			# Only the two original D11 main groups are operational. The entry
			# probe verifies their six retained Mesh/Shape resources and carriers.
			var fraction := float(node.get_meta("current_pose_fraction"))
			assert(is_finite(fraction) and fraction >= 0.0 and fraction <= 1.0)
			expected.origin += xyz(spec.axis_world) * float(spec.travel_m) * fraction
			assert_transform(relative(node,motion),expected,str(identity))
			assert(node.get_meta("operation_enabled") == true and not node.has_meta("locked_pose_fraction"))
			assert(node.find_children("*","Area3D",true,false).is_empty())
			assert(identity not in data.visual_only_motion_groups)
			fully_open = fully_open and fraction == 1.0
			active_groups += 1
			continue
		assert_transform(relative(node,motion),expected,str(identity))
		assert(node.get_meta("operation_enabled") == false and not node.has_method("interact"))
		assert(float(node.get_meta("locked_pose_fraction")) == (1.0 if held else 0.0))
		assert(node.find_children("*","Area3D",true,false).is_empty())
		if held_poses.has(identity): assert_transform(node.global_transform,held_poses[identity],"Fixed pose drift " + str(identity))
		else: held_poses[identity] = node.global_transform
		var visual_only: bool = identity in data.visual_only_motion_groups
		for mesh in node.find_children("*","MeshInstance3D",true,false): check_exact_contact(mesh,not visual_only)
		if not held and not visual_only:
			# Interior leaf centre ray, avoiding millimetre centre seams. The test
			# asks for the exact retained leaf contact, not a nearby wall hit.
			var centre := xyz(spec.closed_root_world) + Vector3.UP*1.2
			var normal := Vector3.FORWARD if "LANDING_GATE" in str(identity) else Vector3.RIGHT
			var found := false
			for hit in all_hits(centre-normal*.45,centre+normal*.45):
				if node.is_ancestor_of(hit.collider): found = true
			assert(found, "Closed retained exit/gate has no physical barrier: " + str(identity))
	template.free()
	assert(active_groups == 2)
	assert(motion.get_meta("cabin_static_floor_credit") == false)
	if fully_open:
		clear_box(Vector3(-35.0,69.51,-128.59),Vector3(-33.95,72.50,-123.41),"D11 5.2m held-open aperture and 3m route headroom")
	clear_box(Vector3(-33.95,69.51,-128.59),Vector3(-4.01,72.50,-123.41),"Bridge full 5.2m clear lane and 3m headroom")

func check_lights(label: String) -> void:
	assert(budget.shadow_source_budget == 8 and load("res://scripts/lighting_budget.gd").MAX_VISIBILITY_CANDIDATES == 32)
	var enabled: Dictionary = {}
	for entry in data.fixtures:
		if entry.enabled:
			var identity := str(entry.id).validate_node_name()
			assert(not enabled.has(identity), "Source fixture names must map bijectively to native node names")
			enabled[identity] = entry
	var actual := venue.find_children("*","Light3D",true,false)
	assert(actual.size() == enabled.size())
	for item in actual:
		var light := item as Light3D
		assert(enabled.has(str(light.name)) and light in budget.sources)
		assert(budget.requested_shadow.get(light.get_instance_id(),false), "No extra unshadowed fill light")
		assert(light.get_meta("fixture_powered",false))
		var entry: Dictionary = enabled[str(light.name)]
		assert(light.global_position.distance_to(xyz(entry.position_world)) < .0001)
		assert(absf(light.light_energy-float(entry.initial_native_energy)) < .00001)
		if entry.type == "SPOT":
			assert(light is SpotLight3D)
			assert(absf(light.spot_angle-float(entry.full_cone_degrees)*.5) < .00001)
			assert((-light.global_basis.z).distance_to(OPTIC.expected_aim(light,entry)) < .00001)
	budget.refresh()
	var selected: Array[String] = []
	for light in budget.sources:
		if not budget.requested_shadow[light.get_instance_id()]: continue
		assert(light.visible == light.shadow_enabled, "No wall-leaking unshadowed fallback")
		if light.visible:
			assert(light.get_meta("fixture_powered",true) and budget._has_visible_sample(light))
			selected.append(str(light.name))
	assert(selected.size() <= 8, "Actual world selection exceeds eight sources")
	light_samples.append({"label":label,"actor_xyz":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"selected":selected})
	print("THEATER ACTUAL LIGHT SELECTION: ",label," ",selected)

# Dummy renderer deliberately has no MultiMesh readback. It may consume only
# this exact successful native receipt while all relevant construction inputs
# remain identical. Real backends still execute the strict getter above.
func require_retained_native_readback() -> bool:
	assert(FileAccess.get_sha256(NATIVE_INSTANCE_QA) == NATIVE_INSTANCE_QA_SHA, "Missing or unreviewed actual-renderer instance evidence")
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(NATIVE_INSTANCE_QA))
	assert(proof.status == "PASS_RETAINED_NATIVE_INSTANCE_READBACK" and proof.error_count == 0 and proof.source_snapshot_unchanged)
	var engine: Dictionary = Engine.get_version_info()
	for key in ["major","minor","patch","status","hash"]:
		assert(engine[key] == proof.engine[key], "Native readback receipt belongs to another engine")
	var expected_counts := {"chairs":2200,"placements":2494,"contact_bodies":2380,"visual_parts":10018,"spatial_batches":890,"source_floor_probes":6514}
	assert(proof.input_sha256.size() == 11 and proof.counts is Dictionary and proof.counts.size() == expected_counts.size())
	for key in expected_counts:
		assert(proof.counts.has(key) and typeof(proof.counts[key]) in [TYPE_INT,TYPE_FLOAT] and proof.counts[key] == expected_counts[key], "Exact native count required: "+str(key))
	for path in proof.input_sha256:
		assert(FileAccess.get_sha256("res://"+str(path)) == str(proof.input_sha256[path]), "Native instance readback is stale: "+str(path))
	for path in proof.evidence_sha256:
		assert(FileAccess.get_sha256("res://"+str(path)) == str(proof.evidence_sha256[path]), "Retained native evidence changed: "+str(path))
	assert(proof.strict_probe_source_sha256 == "5b682f3fd1dff7765708b0fca48a3e9856416b5eba60bb14161d35a359aeaec4")
	print("THEATER RETAINED NATIVE READBACK: exact actual-renderer receipt consumed; current headless physics/contact/identity/floor checks still execute")
	return true
