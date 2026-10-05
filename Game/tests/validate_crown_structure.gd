extends SceneTree
# Actual main-scene construction contacts, not structural/load certification.
# Imported parts are material/spatial batches; ties are identified by real triangles.
const CONTRACT := "res://data/architecture/CENTRAL_CROWN_RUNTIME.json"
const ASSET := "res://assets/models/AST-CMD-001.glb"
const SOURCE_EXPORT_SHA256 := "fd23668ccfe850409708b6e18a1a483f28ba4f7091e4c417069fc9f0e182b604"
const MAX_RESULTS := 256
const EPS := 0.001
var failures: Array[String] = []
var space: PhysicsDirectSpaceState3D
var ship: Node3D
var crown: Node3D
var shell: Node3D
var crown_exclusions: Array[RID] = []
var dynamic_exclusions: Array[RID] = []
var mesh_records: Array[Dictionary] = []
var support_count := 0
var opening_count := 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, detail: String) -> bool:
	if not condition:
		failures.append(detail)
		push_error("CROWN STRUCTURE FAIL: " + detail)
	return condition

func ray(start: Vector3, finish: Vector3, excluded: Array[RID]) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(start, finish)
	query.exclude = excluded
	return space.intersect_ray(query)

func box_hits(bounds: AABB, excluded: Array[RID], label: String) -> Array[Dictionary]:
	var shape := BoxShape3D.new()
	shape.size = bounds.size
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.margin = 0.0005
	query.transform.origin = bounds.get_center()
	query.exclude = excluded
	var hits := space.intersect_shape(query, MAX_RESULTS)
	check(hits.size() < MAX_RESULTS, label + ": collision result capacity saturated")
	return hits

func owner(hit: Dictionary) -> String:
	return "<no contact>" if hit.is_empty() else str(hit.collider.get_path())

func region_id(body: Node) -> String:
	var node := body
	while node != null:
		if node.has_meta("region_id"):
			return str(node.get_meta("region_id"))
		node = node.get_parent()
	return ""

func contract_box(values: Array) -> AABB:
	return AABB(Vector3(values[0], values[2], values[4]),
		Vector3(values[1] - values[0], values[3] - values[2], values[5] - values[4]))

func validate_meshes() -> void:
	var minimum := Vector3(INF, INF, INF)
	var maximum := Vector3(-INF, -INF, -INF)
	var triangle_count := 0
	var meshes := shell.find_children("CMD_CELL_*", "MeshInstance3D", true, false)
	check(meshes.size() == 634, "Expected 634 source/export-verified architecture batches")
	for node in meshes:
		var mesh := node as MeshInstance3D
		if not check(mesh.mesh != null and mesh.is_visible_in_tree(), "Missing/hidden batch " + str(mesh.name)):
			continue
		var local_faces := mesh.mesh.get_faces()
		var faces := PackedVector3Array()
		var bounds: AABB = mesh.global_transform * mesh.get_aabb()
		for vertex in local_faces:
			var world_vertex: Vector3 = mesh.global_transform * vertex
			faces.append(world_vertex)
			minimum = minimum.min(world_vertex)
			maximum = maximum.max(world_vertex)
		triangle_count += local_faces.size() / 3
		var contact := mesh.get_node_or_null("StaticContact/SharedShape") as CollisionShape3D
		if check(contact != null and not contact.disabled, "Missing collision for " + str(mesh.name)):
			check(contact.shape is ConcavePolygonShape3D, "Architecture must keep concave surface contacts: " + str(mesh.name))
			if contact.shape is ConcavePolygonShape3D:
				check(contact.shape.get_faces() == local_faces, "Mesh/collision triangle disagreement: " + str(mesh.name))
		mesh_records.append({"bounds": bounds, "faces": faces, "name": str(mesh.name)})
	check(triangle_count == 32604, "Imported architecture must retain all 32604 verified source triangles")
	check(minimum.y >= -3.2 - EPS and absf(minimum.y + 3.2) < EPS,
		"Actual crown base must remain on keel top -3.2, observed %.5f" % minimum.y)
	check(maximum.y <= 114.5 + EPS and maximum.y > 114.0,
		"Actual roof must exist within 114.5 height limit, observed %.5f" % maximum.y)

func validate_piers(data: Dictionary) -> void:
	var centres: Array = data.support.pier_centres_xz
	check(centres.size() == 4, "Exactly four crown piers required")
	var unique: Dictionary = {}
	for centre in centres:
		var x := float(centre[0])
		var z := float(centre[1])
		check(absf(absf(x) - 51.5) < EPS and absf(absf(z) - 71.0) < EPS, "Pier centre changed: " + str(centre))
		var key := "X%s_Z%s" % ["M" if x < 0 else "P", "M" if z < 0 else "P"]
		check(not unique.has(key), "Duplicate pier " + key)
		unique[key] = true
		for datum in [["base", -3.2], ["top", 114.0]]:
			var marker := shell.find_child("DATUM_pier_%s_%s" % [datum[0], key], true, false) as Node3D
			if check(marker != null, "Missing actual pier marker " + key + "/" + str(datum[0])):
				check(marker.global_position.distance_to(Vector3(x, datum[1], z)) < EPS,
					"Pier marker differs from authored bearing datum: " + str(marker.name))
		# 16 overlapping-free vertical slices avoid truncation by many nearby bodies.
		# Begin 1cm above the intentional foundation contact; preserve full X/Z envelope.
		for segment in range(16):
			var low := lerpf(-3.19, 114.0, segment / 16.0)
			var high := lerpf(-3.19, 114.0, (segment + 1) / 16.0)
			var label := "%s segment %d [%.3f, %.3f]" % [key, segment, low, high]
			var bounds := AABB(Vector3(x - 0.4, low, z - 0.6), Vector3(0.8, high - low, 1.2))
			for hit in box_hits(bounds, crown_exclusions, label):
				check(false, "Pier intersects OTHER permanent architecture: " + label + " -> " + owner(hit))
			# A hypothetical empty pier envelope cannot pass without actual built material.
			var y := (low + high) * 0.5
			var witness := ray(Vector3(x - 1.0, y, z), Vector3(x + 1.0, y, z), dynamic_exclusions)
			if check(not witness.is_empty(), "Missing built pier material: " + label):
				check(shell.is_ancestor_of(witness.collider) and absf(witness.position.z - z) < EPS,
					"Pier witness hit wrong owner: " + label + " -> " + owner(witness))
		for offset in [Vector2.ZERO, Vector2(-0.4, -0.6), Vector2(-0.4, 0.6), Vector2(0.4, -0.6), Vector2(0.4, 0.6)]:
			var start := Vector3(x + offset.x, -3.0, z + offset.y)
			var hit := ray(start, start - Vector3.UP * 0.4, crown_exclusions)
			if check(not hit.is_empty(), "Keel support absent: " + key + " " + str(offset)):
				check("HUL_KeelPan" in owner(hit) and absf(hit.position.y + 3.2) < 0.002,
					"Support must hit actual HUL_KeelPan top -3.2: " + key + " -> " + owner(hit))
			support_count += 1
	check(support_count == 20, "All four centre/corner support sets must run")

func validate_tie_mesh(bounds: AABB, label: String) -> void:
	var count := 0
	var corners: Dictionary = {}
	var padded := bounds.grow(0.0003)
	for record in mesh_records:
		if not padded.intersects(record.bounds):
			continue
		var faces: PackedVector3Array = record.faces
		for index in range(0, faces.size(), 3):
			if not (padded.has_point(faces[index]) and padded.has_point(faces[index + 1]) and padded.has_point(faces[index + 2])):
				continue
			count += 1
			for vertex in [faces[index], faces[index + 1], faces[index + 2]]:
				var corner := Vector3i()
				for axis in range(3):
					var is_min: bool = absf(vertex[axis] - bounds.position[axis]) < 0.0003
					var is_max: bool = absf(vertex[axis] - bounds.end[axis]) < 0.0003
					check(is_min or is_max, "Tie contains a vertex off its exact authored AABB: " + label)
					corner[axis] = 1 if is_max else 0
				corners[corner] = true
	check(count == 12 and corners.size() == 8,
		"Actual batched tie mesh must retain 12 triangles/eight corners: %s observed %d/%d" % [label, count, corners.size()])

func validate_ties(data: Dictionary) -> void:
	check(data.support.authored_ties.size() == 16, "Expected 16 authored band ties")
	var unique: Dictionary = {}
	for tie in data.support.authored_ties:
		var label := str(tie.name)
		check(not unique.has(label), "Duplicate tie " + label)
		unique[label] = true
		var bounds := contract_box(tie.world_aabb)
		var centre := bounds.get_center()
		var floor_y := float(tie.floor_y)
		var intended := str(tie.deck) + "_atrium_circulation"
		check(str(tie.deck) in ["D06", "D09", "D12", "D16"], "Unexpected tie deck " + label)
		check(absf(bounds.size.x - 0.68) < EPS and absf(bounds.size.y - 0.38) < EPS and absf(bounds.size.z - 0.62) < EPS,
			"Tie dimensions changed: " + label)
		check(absf(bounds.end.y - (floor_y - 0.12)) < EPS, "Tie must remain 0.12m below walking level: " + label)
		check(absf(minf(absf(bounds.position.z), absf(bounds.end.z)) - 69.8) < EPS
			and absf(maxf(absf(bounds.position.z), absf(bounds.end.z)) - 70.42) < EPS,
			"Tie must retain 0.20m slab and 0.02m pier-envelope embed: " + label)
		check(absf(float(tie.intended_slab_overlap_z_m) - 0.2) < EPS
			and absf(float(tie.intended_pier_overlap_z_m) - 0.02) < EPS, "Tie embed contract changed: " + label)
		validate_tie_mesh(bounds, label)
		var contacts := box_hits(bounds, crown_exclusions, label)
		var positive_contact := false
		for hit in contacts:
			var actual := region_id(hit.collider)
			check(actual == intended, "Tie intersects unintended permanent owner: " + label + " -> " + owner(hit))
			positive_contact = positive_contact or actual == intended
		check(positive_contact, "Tie lacks positive intended existing-slab contact: " + label + " -> " + intended)
		# At absZ70.2 the original slab ends at 70 and the pier starts at 70.4.
		# This first hit must therefore be the actual new tie, not either neighbour.
		var witness := Vector3(centre.x, floor_y + 0.1, signf(centre.z) * 70.2)
		var hit := ray(witness, witness - Vector3.UP * 0.8, dynamic_exclusions)
		if check(not hit.is_empty(), "Missing tie witness outside original slab edge: " + label):
			check(shell.is_ancestor_of(hit.collider) and absf(hit.position.y - bounds.end.y) < EPS,
				"Tie top witness must be crown mesh at floor-0.12: " + label + " -> " + owner(hit))
		# Independent top/side witnesses identify the old slab and its actual edge.
		var top := Vector3(centre.x, floor_y + 0.1, signf(centre.z) * 69.9)
		var slab_top := ray(top, top - Vector3.UP * 0.8, crown_exclusions)
		if check(not slab_top.is_empty(), "Missing intended slab top: " + label):
			check(region_id(slab_top.collider) == intended and absf(slab_top.position.y - floor_y) < EPS,
				"Wrong slab-top owner or height: " + label + " -> " + owner(slab_top))
		var side_from := Vector3(centre.x, centre.y, signf(centre.z) * 70.3)
		var side_to := Vector3(centre.x, centre.y, signf(centre.z) * 69.7)
		var slab_side := ray(side_from, side_to, crown_exclusions)
		if check(not slab_side.is_empty(), "Missing intended slab edge: " + label):
			check(region_id(slab_side.collider) == intended and absf(absf(slab_side.position.z) - 70.0) < EPS,
				"Slab edge must provide actual 0.20m tie embed: " + label + " -> " + owner(slab_side))

func geometry_signature(faces: PackedVector3Array) -> String:
	# Frozen pre-crown cover triangles, order/winding independent at 1mm precision.
	var triangles := PackedStringArray()
	for index in range(0, faces.size(), 3):
		var corners := PackedStringArray()
		for offset in range(3):
			var vertex := faces[index + offset]
			corners.append("%d,%d,%d" % [roundi(vertex.x * 1000), roundi(vertex.y * 1000), roundi(vertex.z * 1000)])
		corners.sort()
		triangles.append("|".join(corners))
	triangles.sort()
	return "\n".join(triangles).sha256_text()

func validate_protected_covers() -> void:
	var definitions := [
		["D18_atrium_structural_cap", "c1a013d8011580177ecc5f06523758ed8e2cff290103ba3cb6c9ae38b02c407b", [Vector2(-47, -63), Vector2(47, -63), Vector2(-47, 63), Vector2(47, 63), Vector2.ZERO]],
		["D18_starboard_house_cover", "d5a53094fad9765f9e90826eb024e6955a43acd37923fc8fafe100a61ca938ee", [Vector2(64, -13), Vector2(64, 13), Vector2(96, -9), Vector2(96, 9), Vector2(78, 0)]]]
	for definition in definitions:
		var name := str(definition[0])
		var slab := ship.find_child(name, true, false)
		if not check(slab != null, "Protected opaque cover missing: " + name):
			continue
		var visual_faces := PackedVector3Array()
		var collision_faces := PackedVector3Array()
		for node in slab.find_children("*", "MeshInstance3D", true, false):
			var mesh := node as MeshInstance3D
			check(mesh.is_visible_in_tree() and mesh.mesh != null, "Protected cover invisible: " + name)
			if mesh.mesh == null:
				continue
			for vertex in mesh.mesh.get_faces():
				visual_faces.append(mesh.global_transform * vertex)
			for surface in range(mesh.mesh.get_surface_count()):
				var material := mesh.get_active_material(surface) as BaseMaterial3D
				check(material != null and material.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED,
					"Protected cover must remain opaque: " + name)
		for node in slab.find_children("*", "CollisionShape3D", true, false):
			var contact := node as CollisionShape3D
			if check(contact.shape is ConcavePolygonShape3D and not contact.disabled, "Protected cover contact changed: " + name):
				for vertex in contact.shape.get_faces():
					collision_faces.append(contact.global_transform * vertex)
		check(geometry_signature(visual_faces) == str(definition[1]), "Protected cover render geometry changed: " + name)
		check(geometry_signature(collision_faces) == str(definition[1]), "Protected cover physical geometry changed: " + name)
		for point in definition[2]:
			var hit := ray(Vector3(point.x, 106.6, point.y), Vector3(point.x, 106.2, point.y), crown_exclusions)
			if check(not hit.is_empty(), "Protected cover support absent: " + name + " " + str(point)):
				check(region_id(hit.collider) == name and absf(hit.position.y - 106.5) < EPS,
					"Protected cover owner/height changed: " + name + " -> " + owner(hit))
	for suffix in ["Fore", "Aft"]:
		var coffer := ship.find_child("ArtificialDaylightCoffer_" + suffix, true, false) as Node3D
		if check(coffer != null, "Protected underside daylight coffer missing: " + suffix):
			check(coffer.get_meta("catalogue_file", "") == "AST-ATR-002.glb"
				and absf(coffer.global_position.y - 106.26) < EPS,
				"Protected coffer identity or mounting height changed: " + suffix)
			check(not coffer.find_children("*", "MeshInstance3D", true, false).is_empty(), "Protected coffer mesh absent: " + suffix)

func validate_core_openings() -> void:
	var floors := ship.find_child("CompiledStructuralFloors_NotFinishedRooms", true, false)
	if not check(floors != null, "Actual compiled floor group absent"):
		return
	# Isolate all compiled slab contacts plus this crown, retaining real floor holes.
	# Existing cabins/stairs are intentionally excluded; their travel is tested separately.
	var exclusions: Array[RID] = []
	for body in ship.find_children("*", "CollisionObject3D", true, false):
		if not floors.is_ancestor_of(body) and not crown.is_ancestor_of(body):
			exclusions.append(body.get_rid())
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var expected := {
		"primary_atrium_core": [-106.0, -90.65, 18], "forward_public_core": [-438.0, -422.65, 17],
		"fore_midship_public_core": [-278.0, -262.65, 17], "aft_midship_public_core": [266.0, 281.35, 17],
		"aft_public_core": [426.0, 441.35, 17], "aft_crown_link": [113.0, 128.35, 2]}
	for prefix in expected:
		for kind in ["lift", "stairs"]:
			var id := str(prefix) + "_" + kind
			var matches: Array = layout.voids.filter(func(item: Dictionary) -> bool: return str(item.id) == id)
			if not check(matches.size() == 1, "Protected core opening missing/duplicated: " + id):
				continue
			var opening: Dictionary = matches[0]
			var centre_z := float(expected[prefix][0 if kind == "lift" else 1])
			var half := Vector2(1.82, 2.02) if kind == "lift" else Vector2(3.1, 5.35)
			var count := int(expected[prefix][2]) - (1 if kind == "stairs" else 0)
			check(opening.decks.size() == count, "Protected core opening deck count changed: " + id)
			var actual := Rect2(Vector2(opening.boundary[0][0], opening.boundary[0][1]), Vector2.ZERO)
			for point in opening.boundary:
				actual = actual.expand(Vector2(point[0], point[1]))
			check(actual.position.distance_to(Vector2(-half.x, centre_z - half.y)) < EPS
				and actual.size.distance_to(half * 2.0) < EPS, "Protected core opening bounds changed: " + id)
			for deck in opening.decks:
				var index := int(str(deck).substr(1)) - 1
				var y := float(ship.deck_y[index])
				var bounds := AABB(Vector3(-half.x + 0.02, y - 0.6, centre_z - half.y + 0.02),
					Vector3(half.x * 2.0 - 0.04, 0.7, half.y * 2.0 - 0.04))
				for hit in box_hits(bounds, exclusions, id + "/" + str(deck)):
					check(false, "Protected core floor opening filled: " + id + "/" + str(deck) + " -> " + owner(hit))
				opening_count += 1
	check(opening_count == 170, "All 170 existing core/deck openings must be checked")

func validate_fixtures_and_signs(data: Dictionary) -> void:
	check(data.light_markers.size() == 74, "Source contract must retain 74 fixtures")
	check(shell.find_children("DATUM_light_*", "Node3D", true, false).size() == 74, "Actual source must retain 74 light markers")
	check(crown.find_children("CrownSource_*", "SpotLight3D", true, false).size() == 74, "Runtime must retain 74 actual source lights")
	var names: Dictionary = {}
	for item in data.light_markers:
		var name := str(item.name)
		check(not names.has(name), "Duplicate light contract marker " + name)
		names[name] = true
		var marker := shell.find_child(name, true, false) as Node3D
		var light := crown.find_child("CrownSource_" + name, true, false) as SpotLight3D
		if not check(marker != null and light != null, "Missing fixture marker/light: " + name):
			continue
		var expected := Vector3(item.position[0], item.position[1], item.position[2])
		check(marker.global_position.distance_to(expected) < EPS and light.global_position.distance_to(expected) < EPS,
			"Fixture/light differs from source location: " + name)
		check((-light.global_basis.z).dot(Vector3.DOWN) > 0.999, "Fixture must emit downwards: " + name)
		var exit_hit := ray(marker.global_position, marker.global_position + Vector3.DOWN * 0.25, dynamic_exclusions)
		check(exit_hit.is_empty(), "Downward fixture exit blocked: " + name + " -> " + owner(exit_hit))
		# A clear ray alone cannot establish that the corresponding emitting lens exists.
		var backing := ray(marker.global_position, marker.global_position + Vector3.UP * 0.08, dynamic_exclusions)
		check(not backing.is_empty() and shell.is_ancestor_of(backing.collider), "Fixture lacks real source lens above its marker: " + name)
	check(crown.find_children("CrownSign_*", "Label3D", true, false).size() == 6, "Six programme labels must remain mounted")
	for programme in data.programmes:
		var name := "CrownSign_" + str(programme.programme_key)
		var sign := crown.find_child(name, true, false) as Label3D
		if not check(sign != null, "Programme sign missing: " + name):
			continue
		check(absf(sign.global_position.y - 109.65) < EPS, "Sign must remain at authored solid-header level: " + name)
		var direction := Vector3(signf(sign.global_position.x), 0, 0)
		for offset in [-0.5, 0.0, 0.5]:
			var start := sign.global_position + Vector3(0, 0, offset)
			var backing := ray(start, start + direction * 0.08, dynamic_exclusions)
			if check(not backing.is_empty(), "Sign has no physical header backing: " + name):
				check(shell.is_ancestor_of(backing.collider) and absf(absf(backing.position.x) - 10.0) < EPS,
					"Sign backing must be its real room-front header: " + name + " -> " + owner(backing))

func run() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not check(not data.is_empty(), "Runtime construction contract absent/unreadable"):
		quit(1)
		return
	check(FileAccess.get_sha256(ASSET) == SOURCE_EXPORT_SHA256 and str(data.export_sha256) == SOURCE_EXPORT_SHA256,
		"Crown export changed; renew source/frame equivalence evidence before updating this test")
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	crown = ship.get_node_or_null("ShipSpace/Districts/CentralCommandCrown_WIP") as Node3D
	if not check(crown != null, "Actual current main scene has no integrated crown"):
		quit(1)
		return
	shell = crown.get_node_or_null("CentralCrownArchitecture") as Node3D
	if not check(shell != null, "Integrated crown architecture wrapper missing"):
		quit(1)
		return
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*", "CollisionObject3D", true, false):
		var permanent: bool = body is StaticBody3D and not body is AnimatableBody3D
		if not permanent:
			dynamic_exclusions.append(body.get_rid())
		if crown.is_ancestor_of(body) or not permanent:
			crown_exclusions.append(body.get_rid())
	validate_meshes()
	validate_piers(data)
	validate_ties(data)
	validate_protected_covers()
	validate_core_openings()
	validate_fixtures_and_signs(data)
	if not failures.is_empty():
		quit(1)
		return
	print("CROWN STRUCTURE PASS: 4 real piers, 20 keel rays, 16 built ties with intended slab contacts, protected covers/170 core openings, 74 clear fixture exits and 6 backed signs. Architectural contacts only; no load certification.")
	main.queue_free()
	await process_frame
	quit()
