extends SceneTree
# Architectural geometry/contact regression, not structural or pressure certification.
# Read raw, hash-pinned GLB accessors without invoking the Godot importer, then
# match every imported triangle one-to-one with tolerant corners and winding.
const CONTRACT := "res://data/architecture/BRIDGE_ENCLOSURE_RUNTIME.json"
const ASSET := "res://assets/models/AST-CMD-004.glb"
const AUDIT := "res://docs/BRIDGE_ENCLOSURE_SOURCE_CONTACT_AUDIT.json"
const ROUNDTRIP := "res://docs/BRIDGE_ENCLOSURE_SOURCE_ROUNDTRIP.json"
const EXPORT_SHA := "0c6d37681d76909ce14f8526b7f6bfadd10b8114b39d11cd12ba29a7e9970dbf"
const AUDIT_SHA := "a204d808f5fe3d428cc5f4b7a76e7d61fa51ed3fb7a4449e86ddbf72b8218128"
const EPS := 0.001
var failures: Array[String] = []
var ship: Node3D
var shell: Node3D
var platform: Node3D
var space: PhysicsDirectSpaceState3D
var dynamic_exclusions: Array[RID] = []
var shell_exclusions: Array[RID] = []
var gltf: Dictionary
var binary: PackedByteArray
var matched_triangles := 0
var maximum_corner_error := 0.0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, detail: String) -> bool:
	if not ok:
		failures.append(detail)
		push_error(detail)
	return ok

func read_json(path: String) -> Dictionary:
	var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not check(value is Dictionary, "Missing/malformed JSON: " + path):
		return {}
	return value

func v3(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

func ray(a: Vector3, b: Vector3, exclusions: Array[RID]) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a,b)
	q.exclude = exclusions
	return space.intersect_ray(q)

func accessor(index: int) -> Array:
	var a: Dictionary = gltf.accessors[index]
	var view: Dictionary = gltf.bufferViews[int(a.bufferView)]
	var width := 3 if str(a.type) == "VEC3" else 1
	var component := int(a.componentType)
	var size := 2 if component == 5123 else 4
	check(component in [5123,5125,5126] and not a.has("sparse"),"Unsupported raw GLB accessor")
	var start := int(view.get("byteOffset",0))+int(a.get("byteOffset",0))
	var stride := int(view.get("byteStride",width*size))
	var result: Array = []
	for i in range(int(a.count)):
		var offset := start+i*stride
		if width == 3:
			result.append(Vector3(binary.decode_float(offset),binary.decode_float(offset+4),binary.decode_float(offset+8)))
		else:
			result.append(binary.decode_u16(offset) if component == 5123 else binary.decode_u32(offset))
	return result

func raw_batches() -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(ASSET)
	if not check(bytes.size() > 28 and bytes.decode_u32(0) == 0x46546c67 and bytes.decode_u32(4) == 2,"Invalid GLB container"):
		return {}
	var length := int(bytes.decode_u32(12))
	gltf = JSON.parse_string(bytes.slice(20,20+length).get_string_from_utf8())
	var bin_start := 20+length
	check(bytes.decode_u32(bin_start+4) == 0x004e4942,"Expected GLB binary chunk")
	binary = bytes.slice(bin_start+8,bin_start+8+int(bytes.decode_u32(bin_start)))
	var result: Dictionary = {}
	for node in gltf.nodes:
		if not node.has("mesh"):
			continue
		# Reviewed export bakes world transforms. Refuse a changed hierarchy rather
		# than silently comparing local coordinates to world-space runtime data.
		check(not node.has("matrix") and not node.has("translation") and not node.has("rotation") and not node.has("scale") and not node.has("children"),"Unreviewed GLB transform/hierarchy")
		var faces := PackedVector3Array()
		for primitive in gltf.meshes[int(node.mesh)].primitives:
			check(int(primitive.get("mode",4)) == 4,"GLB primitive is not triangles")
			var positions := accessor(int(primitive.attributes.POSITION))
			var indices := accessor(int(primitive.indices))
			for index in indices:
				faces.append(positions[int(index)])
		result[str(node.name)] = faces
	return result

func triangle_error(source: PackedVector3Array, a: int, imported: PackedVector3Array, b: int) -> float:
	var best := INF
	# glTF CCW -> Godot clockwise conversion; cyclic permutations preserve the
	# required orientation. A reflected/reversed triangle is never accepted.
	for rotation in range(3):
		var error := 0.0
		for corner in range(3):
			error = maxf(error,source[a+corner].distance_to(imported[b+(rotation-corner+3)%3]))
		best = minf(best,error)
	return best

func validate_meshes(roundtrip: Dictionary) -> void:
	var batches := raw_batches()
	var meshes := shell.find_children("*","MeshInstance3D",true,false)
	check(meshes.size() == batches.size() and meshes.size() > 300 and meshes.size() < 500,"Exact bounded source batch census differs")
	var minimum := Vector3(INF,INF,INF)
	var maximum := Vector3(-INF,-INF,-INF)
	for item in meshes:
		var mesh := item as MeshInstance3D
		if not check(batches.has(str(mesh.name)) and mesh.mesh != null and mesh.is_visible_in_tree(),"Missing source batch or invisible runtime mesh: "+str(mesh.name)):
			continue
		var source: PackedVector3Array = batches[str(mesh.name)]
		batches.erase(str(mesh.name))
		var local_faces := mesh.mesh.get_faces()
		var faces := PackedVector3Array()
		for vertex in local_faces:
			var point: Vector3 = mesh.global_transform*vertex
			faces.append(point)
			minimum = minimum.min(point)
			maximum = maximum.max(point)
		var contact := mesh.get_node_or_null("StaticContact/SharedShape") as CollisionShape3D
		if check(contact != null and not contact.disabled,"Missing active collision: "+str(mesh.name)):
			check(contact.shape is ConcavePolygonShape3D and contact.get_parent() is StaticBody3D and contact.get_parent().collision_layer != 0,"Wrong static collision type/layer")
			if contact.shape is ConcavePolygonShape3D:
				check(contact.shape.get_faces() == local_faces and contact.global_transform.is_equal_approx(mesh.global_transform),"Exact imported render/collision mismatch: "+str(mesh.name))
		if not check(source.size() == faces.size(),"Source/runtime triangle multiplicity differs: "+str(mesh.name)):
			continue
		var used: Dictionary = {}
		for a in range(0,source.size(),3):
			var found := -1
			var best := EPS
			for b in range(0,faces.size(),3):
				if used.has(b):
					continue
				var error := triangle_error(source,a,faces,b)
				if error < best:
					best = error
					found = b
			if check(found >= 0,"No one-to-one oriented source triangle: %s/%d" % [mesh.name,a/3]):
				used[found] = true
				matched_triangles += 1
				maximum_corner_error = maxf(maximum_corner_error,best)
	check(batches.is_empty(),"Source batches absent from runtime")
	check(matched_triangles == int(roundtrip.get("triangles",-1)),"Full immutable source triangle coverage incomplete")
	check(absf(minimum.y-106.5)<EPS and absf(maximum.y-114.32)<EPS,"Enclosure must not add underfloor geometry or exceed the existing roof")

func validate_source_contacts(audit: Dictionary, proof: Dictionary) -> void:
	check(FileAccess.get_sha256(AUDIT)==AUDIT_SHA and bool(audit.get("pass",false)),"Immutable independent contact proof changed/failed")
	var hashes: Dictionary = audit.get("hashes",{})
	check(str(hashes.get("assets/bridge_enclosure/exports/AST-CMD-004.glb",""))==EXPORT_SHA,"Contact proof refers to another shell export")
	check(str(hashes.get("assets/bridge_enclosure/source/AST-CMD-004.blend",""))==str(proof.get("source_sha256","")),"Contact proof and roundtrip refer to different editable source")
	check(FileAccess.get_sha256("res://assets/models/AST-CMD-003.glb")==str(hashes.get("assets/bridge_platform/exports/AST-CMD-003.glb","")),"Actual supporting platform differs from reviewed geometry")
	check(FileAccess.get_sha256("res://assets/models/AST-CIR-005.glb")==str(hashes.get("installed:assets/models/AST-CIR-005.glb","")),"Actual core cover differs from reviewed geometry")
	check(int(audit.get("enclosure_part_count",0))==963 and audit.parts.size()==963 and audit.contact_network.size()==963,"All963 source parts need a positive contact path")
	var parents: Dictionary = {}
	for contact in audit.contact_network:
		check(not parents.has(str(contact.part)),"Duplicate support graph node")
		parents[str(contact.part)] = contact
		check(float(contact.contact_surface_m2)>0.000001 or float(contact.contact_volume_m3)>0.000000001,"Point/line contact cannot support an architectural component")
	for part in audit.parts:
		var current := str(part.name)
		var seen: Dictionary = {}
		var anchored := false
		while parents.has(current) and not seen.has(current):
			seen[current] = true
			var edge: Dictionary = parents[current]
			if str(edge.support_asset)=="AST-CMD-003":
				anchored = true
				break
			current = str(edge.support_part)
		check(anchored,"Disconnected/cyclic source support path: "+str(part.name))
	check(int(audit.perimeter.gap_count)==0 and audit.perimeter.height_slices.size()==145,"Exact critical-height source perimeter coverage failed")
	check(int(audit.guard_preservation.changed_part_count)==32 and int(audit.guard_preservation.unchanged_part_count)==3362 and bool(audit.guard_preservation.all_other_full_records_exact),"Bounded003 guard-only preservation failed")
	check(audit.fixtures.new_geometry_intersecting_lens_vertical_exit_columns.is_empty(),"Source fixture exit columns blocked")

func validate_perimeter(data: Dictionary) -> void:
	var boundary: Array = data.boundary_xz
	var samples := 0
	for edge in range(boundary.size()):
		var a := Vector3(float(boundary[edge][0]),0,float(boundary[edge][1]))
		var b := Vector3(float(boundary[(edge+1)%boundary.size()][0]),0,float(boundary[(edge+1)%boundary.size()][1]))
		var tangent := (b-a).normalized()
		var normal := Vector3(tangent.z,0,-tangent.x)
		var count := ceili(a.distance_to(b)/0.25)
		for i in range(count+1):
			var p := a.lerp(b,float(i)/count)
			for y in [106.55,107.05,107.3,108.1,109.3,109.5,110.5]:
				p.y = y
				if edge in [0,3] and absf(p.x) < 1.375 and y < 109.315:
					continue # Actual controlled door leaf/frame tested separately.
				for direction in [-1.0,1.0]:
					var hit := ray(p+normal*direction*0.5,p-normal*direction*0.5,dynamic_exclusions)
					check(not hit.is_empty(),"Open physical perimeter: edge%d at%s" % [edge,p])
					samples += 1
	check(samples>10000,"Perimeter sampling unexpectedly incomplete")
	# Both sides of the old spine remain an open connected fan interior.
	for z in [-165.0,-145.0,-125.0]:
		for y in [107.2,108.2,109.2]:
			check(ray(Vector3(-3.8,y,z),Vector3(3.8,y,z),dynamic_exclusions).is_empty(),"Old spine divides the new fan interior")

func validate_retained_lights() -> void:
	var old := read_json("res://data/architecture/BRIDGE_PLATFORM_RUNTIME.json")
	check(old.light_markers.size() == 20,"Original20 fixture identities changed")
	check(shell.find_children("*","Light3D",true,false).is_empty(),"Unsource-backed enclosure lights added")
	var old_shell := platform.get_node("BridgePlatformArchitecture")
	for item in old.light_markers:
		var marker := old_shell.find_child(str(item.name),true,false) as Node3D
		var light := platform.find_child("BridgePlatformSource_"+str(item.name),true,false) as SpotLight3D
		var p := v3(item.position)
		if not check(marker != null and light != null,"Original fixture disappeared"):
			continue
		check(marker.global_position.distance_to(p)<EPS and light.global_position.distance_to(p)<EPS,"Original fixture moved")
		for offset in [Vector3.ZERO,Vector3(-0.05,0,0),Vector3(0.05,0,0),Vector3(0,0,-0.05),Vector3(0,0,0.05)]:
			check(ray(p+offset,p+offset+Vector3.DOWN*0.25,dynamic_exclusions).is_empty(),"Original fixture optical exit obstructed: "+str(item.name))
			var lens := ray(p+offset,p+offset+Vector3.UP*0.08,dynamic_exclusions)
			check(not lens.is_empty() and old_shell.is_ancestor_of(lens.collider),"Original lens contact lost")
			# Receiver cone witnesses, not just a short lens-exit test.
			check(ray(p+offset,p+Vector3(offset.x*8,-3.7,offset.z*8),dynamic_exclusions).is_empty(),"Fixture receiver column obstructed")

func validate_portals() -> void:
	for row in [[-118.3,-113.0,109.73],[-173.0,-171.7,111.0]]:
		var z := (float(row[0])+float(row[1]))*0.5
		for x in [-3.8,0.0,3.8]:
			var hit := ray(Vector3(x,float(row[2])-0.13,z),Vector3(x,float(row[2])+0.37,z),shell_exclusions)
			check(not hit.is_empty() and absf(hit.position.y-float(row[2]))<EPS,"Portal roof exact underside missing")
	var core := ship.get_node("ShipSpace/Districts/PrimaryAtriumCore_WIP/PrimaryCoreEnclosure") as Node3D
	var only_core: Array[RID] = []
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not core.is_ancestor_of(body):
			only_core.append(body.get_rid())
	for x in [-3.8,-2.0,0.0,2.0,3.8]:
		var shell_end := ray(Vector3(x,109.80,-112.90),Vector3(x,109.80,-113.10),shell_exclusions)
		var core_end := ray(Vector3(x,109.80,-113.10),Vector3(x,109.80,-112.90),only_core)
		check(not shell_end.is_empty() and absf(shell_end.position.z+112.98)<EPS,"Vestibule roof must enter actual cover by20mm")
		check(not core_end.is_empty() and absf(core_end.position.z+113.0)<EPS,"Original core cover front boundary moved")
		for z in [-113.01,-112.99]:
			var underside := ray(Vector3(x,109.60,z),Vector3(x,109.90,z),dynamic_exclusions)
			check(not underside.is_empty() and absf(underside.position.y-109.73)<EPS,"Actual roof/core join has a gap or changed underside")
	# New shell cannot occupy preserved D17 central route/headroom or core mouth.
	for z in [-170.0,-150.0,-130.0,-115.0,-106.0,-90.0]:
		for x in [-3.9,0.0,3.9]:
			check(ray(Vector3(x,101.5,z),Vector3(x,106.25,z),shell_exclusions).is_empty(),"New enclosure violates D17/core headroom")
	# Demountable future crosslink remains sealed, with no invented exit.
	for x in [-4.0,4.0]:
		check(not ray(Vector3(x-0.3,108,-115),Vector3(x+0.3,108,-115),shell_exclusions).is_empty(),"Future crosslink wrongly left open")

func run() -> void:
	var data := read_json(CONTRACT)
	var proof := read_json(ROUNDTRIP)
	var audit := read_json(AUDIT)
	check(FileAccess.get_sha256(ASSET)==EXPORT_SHA and str(data.get("export_sha256",""))==EXPORT_SHA and str(proof.get("export_sha256",""))==EXPORT_SHA,"Final reviewed source/export identity changed")
	check(bool(proof.get("exact_float32_position_oriented_triangle_uv_material_equality",false)),"Exact source/export proof absent")
	check(not audit.is_empty(),"Independent source contacts missing")
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	var enclosure := ship.get_node_or_null("ShipSpace/Districts/BridgeEnclosure_WIP")
	if not check(enclosure != null,"Enclosure runtime root absent"):
		quit(1)
		return
	shell = enclosure.get_node_or_null("BridgeEnclosureArchitecture") as Node3D
	platform = ship.get_node("ShipSpace/Districts/BridgePlatform_WIP") as Node3D
	if not check(shell != null,"Enclosure architecture absent"):
		quit(1)
		return
	check(shell.global_transform.is_equal_approx(Transform3D.IDENTITY),"Source placement changed")
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:
			dynamic_exclusions.append(body.get_rid())
		if not shell.is_ancestor_of(body):
			shell_exclusions.append(body.get_rid())
	validate_source_contacts(audit,proof)
	validate_meshes(proof)
	validate_perimeter(data)
	validate_retained_lights()
	validate_portals()
	print(("BRIDGE ENCLOSURE STRUCTURE PASS:" if failures.is_empty() else "BRIDGE ENCLOSURE STRUCTURE FAILED:")+" matched %d oriented triangles; max import corner error %.9fm; %d failures. Architectural contact only, no load/pressure certification." % [matched_triangles,maximum_corner_error,failures.size()])
	main.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
