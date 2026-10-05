extends SceneTree
# Runtime corroboration, not a replacement for the complete source triangle/cone proof.
# Glass stays physically collidable. Only verified visible glass is optically transparent.
const CONTRACT := "res://data/architecture/UPPER_HORIZON_ENCLOSURE_RUNTIME.json"
const GLASS_SHADER := "res://shaders/hospitality_glass.gdshader"
const GLASS_SHA256 := "d65f946db48a7242020d6bba54d576dc8d927c62835dc872a0e9f9ac63a3fb4a"
const SKY_SHA256 := "08f0ec4c92b7de0c45afa539f8d9abdd65ec00c3d4af1831548f0ec24d485b2d"
var failures: Array[String] = []
var space: PhysicsDirectSpaceState3D
var shell: Node3D
var physical_exclusions: Array[RID] = []
var optical_exclusions: Array[RID] = []
var contacts := 0
var view_pairs := 0
var screens := 0
var supported_eyes := 0
var hull := PackedVector2Array()

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, detail: String) -> bool:
	if not ok:
		failures.append(detail)
		push_error(detail)
	return ok

func ray(a: Vector3, b: Vector3, optical := false) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a, b)
	query.exclude = optical_exclusions if optical else physical_exclusions
	return space.intersect_ray(query)

func describe(hit: Dictionary) -> String:
	return "clear" if hit.is_empty() else "%s at %s" % [hit.collider.get_path(), hit.position]

func exact_numeric_pair(values: Array, low: float, high: float) -> bool:
	# JSON numbers are floats in Godot; Array equality distinguishes integer
	# literals from floats. Compare coordinates exactly after numeric conversion.
	return values.size() == 2 and float(values[0]) == low and float(values[1]) == high

func glass_mesh(body: Node) -> MeshInstance3D:
	var mesh := body.get_parent() as MeshInstance3D
	if mesh == null or not "glass" in str(mesh.name).to_lower():
		return null
	if not mesh.material_override is ShaderMaterial:
		return null
	var material := mesh.material_override as ShaderMaterial
	if material.shader == null or material.shader.resource_path != GLASS_SHADER:
		return null
	return mesh

func glass_contact(hit: Dictionary, label: String) -> bool:
	if not check(not hit.is_empty(), "Missing physical pane: " + label):
		return false
	var mesh := glass_mesh(hit.collider)
	if not check(mesh != null and shell.is_ancestor_of(hit.collider), "Expected enclosure pane, found " + describe(hit) + ": " + label):
		return false
	check(mesh.is_visible_in_tree(), "Invisible glass: " + label)
	var material := mesh.material_override as ShaderMaterial
	var opacity: Variant = material.get_shader_parameter("face_opacity")
	# Headless rendering reports Nil for an unset uniform. The exact checked
	# shader below declares face_opacity=0.23; explicit overrides still win.
	if opacity == null:
		opacity = 0.23
	check(opacity != null and float(opacity) > 0.0 and float(opacity) < 0.65, "Opaque or invisible glass material: " + label)
	check(hit.collider is StaticBody3D, "Pane must be a static protective barrier: " + label)
	contacts += 1
	return true

func validate_windows(data: Dictionary) -> void:
	check(data.windows.size() == 28, "Expected 28 logical single-plane windows")
	var ids: Dictionary = {}
	var low_count := 0
	for window in data.windows:
		var label := str(window.id)
		check(not ids.has(label), "Duplicate window: " + label)
		ids[label] = true
		check(bool(window.single_plane), "Layered pane contract: " + label)
		var a: Vector3
		var b: Vector3
		if window.has("glass_aabb"):
			low_count += 1
			var bounds: Array = window.glass_aabb
			a = Vector3((float(bounds[0]) + float(bounds[1])) * 0.5, 0, float(bounds[4]))
			b = Vector3(a.x, 0, float(bounds[5]))
			check(absf(float(window.opaque_top_above_floor) - 0.92) < 0.001, "Low sill finished height changed")
		else:
			a = Vector3(float(window.a_xz[0]), 0, float(window.a_xz[1]))
			b = Vector3(float(window.b_xz[0]), 0, float(window.b_xz[1]))
		var tangent := (b-a).normalized()
		var normal := Vector3(tangent.z, 0, -tangent.x)
		var y0 := float(window.clear_aperture_y[0])
		var y1 := float(window.clear_aperture_y[1])
		for t in [0.2, 0.5, 0.8]:
			for y in [y0 + 0.12, (y0+y1)*0.5, y1 - 0.12]:
				var p: Vector3 = a.lerp(b, t)
				p.y = y
				var front := ray(p + normal*0.12, p - normal*0.12)
				var back := ray(p - normal*0.12, p + normal*0.12)
				if glass_contact(front, label) and glass_contact(back, label):
					check(absf(front.position.distance_to(back.position) - 0.06) < 0.006, "Both faces must bound the physical 60mm pane: " + label)
	check(low_count == 2, "Exactly two lowered observation bays required")
	check(contacts == 504, "All 504 bidirectional distributed pane contacts must execute")

func target_directions(side: String, full_port := false) -> Array[Vector3]:
	var result: Array[Vector3] = []
	var centre: Vector3 = Vector3(0.9354072, -0.2923717, 0.1988269).normalized() if side == "starboard" else Vector3(-0.9871089, 0.1045285, -0.1212017).normalized()
	var radius := deg_to_rad(29.85) if side == "starboard" else acos(cos(deg_to_rad(7.0)) - 0.0006)
	var u: Vector3 = centre.cross(Vector3.UP).normalized()
	var v: Vector3 = u.cross(centre)
	# Actual angular cap boundaries, solid disc rim, and interior rays. Never use
	# independent rectangular slope extrema as if they were genuine sky directions.
	var radii: Array[float] = [radius * 0.5, radius]
	if side == "starboard":
		radii.append(deg_to_rad(29.0))
	for rho in radii:
		for i in range(24):
			var theta := TAU * float(i) / 24.0
			var direction: Vector3 = (centre*cos(rho) + (u*cos(theta)+v*sin(theta))*sin(rho)).normalized()
			if direction.y >= 0.0 or full_port:
				result.append(direction)
	if centre.y >= 0.0:
		result.append(centre)
	if side == "starboard":
		var azimuth := atan2(centre.z, centre.x)
		var delta := acos(cos(radius)/Vector2(centre.x, centre.z).length())
		for i in range(9):
			var angle := lerpf(azimuth-delta, azimuth+delta, float(i)/8.0)
			result.append(Vector3(cos(angle), 0, sin(angle)))
		result.append(Vector3(0.9477884152696088, 0.22168947715789528, 0.22923982114410868))
	else:
		result.append(Vector3(-0.9655845226301824, 0.22960219762916861, -0.12218576226753684))
		result.append(Vector3(-0.963547882386675, 0.10537718641845417, -0.24590877766091357))
		result.append(Vector3(-0.994417109075425, 0.10537719153601907, 0.0055009710102196935))
		if full_port:
			result.append(Vector3(-0.9922571597550345, -0.02227932341788251, -0.12218576293052029))
	return result

func eye_samples(box: Dictionary, heights: Array) -> Array[Vector3]:
	var result: Array[Vector3] = []
	for y in heights:
		for x in box.x:
			for z in box.z:
				result.append(Vector3(float(x), float(y), float(z)))
		result.append(Vector3((float(box.x[0])+float(box.x[1]))*0.5, float(y), (float(box.z[0])+float(box.z[1]))*0.5))
	return result

func future_clear(eye: Vector3, direction: Vector3, massing: Dictionary, label: String) -> void:
	check(direction.y >= -0.000001, "Future upper-target promise includes a negative ray: " + label)
	var side := signf(direction.x)
	for spec in [[massing.central_upper_pavilions_abs_x, massing.central_upper_pavilions_z], [massing.aft_upper_pavilions_abs_x, massing.aft_upper_pavilions_z], [[63,100], [massing.aft_courts_start_z,491.123]]]:
		# XZ rejection is independent of the unfinished future buildings' height.
		var z0 := eye.z + (float(spec[0][0])-absf(eye.x))*direction.z/absf(direction.x)
		var z1 := eye.z + (float(spec[0][1])-absf(eye.x))*direction.z/absf(direction.x)
		check(maxf(z0,z1) < float(spec[1][0]) or minf(z0,z1) > float(spec[1][1]), "Future fixed envelope intersects target on side %s: %s" % [side,label])

func validate_screen(data: Dictionary, side: String, heights: Array, full_port := false) -> void:
	var box: Dictionary = data.standing_eye_boxes[side]
	var directions := target_directions(side, full_port)
	var label := side + (" local full port footprint" if full_port else " above-horizon target") + " eyes=" + str(heights)
	for eye in eye_samples(box, heights):
		var floor_hit := ray(Vector3(eye.x,106.65,eye.z), Vector3(eye.x,106.25,eye.z))
		check(not floor_hit.is_empty() and absf(float(floor_hit.get("position",Vector3.ZERO).y)-106.5)<0.015, "Optical eye lacks supported D18 floor: " + str(eye))
		supported_eyes += 1
		for direction in directions:
			var sign_x := signf(direction.x)
			var outer: Vector3 = eye + direction*((35.95-absf(eye.x))/absf(direction.x))
			var entry := ray(eye, outer)
			if glass_contact(entry, label + " " + str(eye)):
				check(absf(absf(entry.position.x)-35.67)<0.006, "Wrong low-bay inner face: " + describe(entry))
				var exit_hit := ray(outer, eye)
				if glass_contact(exit_hit, label + " outer face"):
					check(absf(absf(exit_hit.position.x)-35.73)<0.006, "Wrong low-bay outer face: " + describe(exit_hit))
			for plane in [35.52,35.88]:
				var point: Vector3 = eye + direction*((float(plane)-absf(eye.x))/absf(direction.x))
				check(point.y > float(data.bays.clear_aperture_y[0]) and point.y < float(data.bays.clear_aperture_y[1]) and point.z > 160.1 and point.z < 163.9, "Ray misses actual deep reveal opening: " + label)
			var end: Vector3 = eye + direction*((120.0-absf(eye.x))/absf(direction.x))
			var obstruction := ray(eye,end,true)
			check(obstruction.is_empty(), "Opaque view obstruction " + describe(obstruction) + ": " + label + " eye=" + str(eye) + " ray=" + str(direction))
			# Beyond the intended outer face there must be no second glass layer
			# or other solid before the historical hull edge in this bounded cone.
			var exterior := ray(outer,end)
			check(exterior.is_empty(), "Extra pane/exterior obstruction " + describe(exterior) + ": " + label)
			if direction.y >= 0.0:
				future_clear(eye,direction,data.future_massing,label)
			var at_shoulder: Vector3 = eye + direction*((52.0-absf(eye.x))/absf(direction.x))
			check(at_shoulder.y < float(data.shoulder_minimum_new_underside_y), "Target exceeds shoulder underside: " + label)
			check(sign_x*eye.x > 32.69, "Out-of-contract inboard eye")
			view_pairs += 1
	screens += 1

func validate_limits(data: Dictionary) -> void:
	check(absf(float(data.bays.sill_top_y)-107.42)<0.001, "Reviewed finished sill top must be Y107.42")
	check(absf(float(data.bays.old_cap_cover_clearance_m)-0.02)<0.001, "Reviewed proud sill interface changed")
	check(data.seated_diagnostic_eye_y == [107.55,107.65,107.75], "All three reviewed seated eye heights required")
	check(data.standing_eye_boxes.starboard.x == [32.7,33.1] and data.standing_eye_boxes.port.x == [-33.1,-32.7], "Deliberate close viewing stations changed")
	check(data.standing_eye_boxes.starboard.y == [107.95,108.35] and data.standing_eye_boxes.port.y == [107.95,108.35], "Standing eye-height ranges changed")
	check(data.standing_eye_boxes.starboard.z == [161.05,161.35] and data.standing_eye_boxes.port.z == [162.1,162.6], "Bounded longitudinal viewing stations changed")
	check(bool(data.future_massing.unchanged) and float(data.future_massing.D17_roof_y)==106.5, "Future roof/massing contract changed")
	check(exact_numeric_pair(data.future_massing.central_upper_pavilions_abs_x,94.0,118.0) and exact_numeric_pair(data.future_massing.central_upper_pavilions_z,22.0,54.0), "Central future pavilions were moved")
	check(exact_numeric_pair(data.future_massing.aft_upper_pavilions_abs_x,73.0,104.0) and exact_numeric_pair(data.future_massing.aft_upper_pavilions_z,400.0,436.0) and float(data.future_massing.aft_courts_start_z) == 250.0, "Aft future pavilions/courts were moved")
	for side in [-1.0,1.0]:
		# Low horizontal seated rays pass the bay; adjacent untouched high guard
		# still blocks the same eye height. This meaningfully tests the lowering.
		for y in data.seated_diagnostic_eye_y:
			var eye: Vector3 = Vector3(side*32.9,float(y),162)
			check(ray(eye,Vector3(side*36.1,float(y),162),true).is_empty(), "Low sill does not release seated horizontal ray")
			var old_guard := ray(Vector3(side*34.9,float(y),165),Vector3(side*36.1,float(y),165),true)
			check(not old_guard.is_empty(), "Unchanged adjacent guard no longer bounds seated view")
		var sill := ray(Vector3(side*35.55,107.6,162),Vector3(side*35.55,107.2,162),true)
		check(not sill.is_empty() and absf(float(sill.get("position",Vector3.ZERO).y)-107.42)<0.006, "Physical finished sill is not Y107.42")
	# High-angle stars remain clipped by retained frame, even with clear glass.
	var high_eye: Vector3 = Vector3(32.9,108.15,161.2)
	var high_direction: Vector3 = (Vector3(35.7,111.05,162)-high_eye).normalized()
	check(not ray(high_eye,high_eye+high_direction*20.0,true).is_empty(), "Expected high-angle frame limitation disappeared")
	# Finite future D17 reservation, NOT current installed roof or infinite-plane proof.
	for y in data.seated_diagnostic_eye_y:
		var eye: Vector3 = Vector3(-32.9,float(y),162.35)
		var direction: Vector3 = Vector3(-0.9922571597550345,-0.02227932341788251,-0.12218576293052029)
		var roof_point: Vector3 = eye+direction*((106.5-eye.y)/direction.y)
		check(Geometry2D.is_point_in_polygon(Vector2(roof_point.x,roof_point.z),hull), "Seated port fringe finite-roof limitation changed")
	var direction: Vector3 = Vector3(cos(deg_to_rad(5.0))*cos(deg_to_rad(12.0)),-sin(deg_to_rad(5.0)),cos(deg_to_rad(5.0))*sin(deg_to_rad(12.0)))
	var eye: Vector3 = Vector3(32.9,108.15,161.2)
	var roof_point: Vector3 = eye+direction*((106.5-eye.y)/direction.y)
	check(Geometry2D.is_point_in_polygon(Vector2(roof_point.x,roof_point.z),hull), "Lower planet future-roof crop changed")

func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	var ship := main.get_node("World360/Astraea") as Node3D
	shell = ship.get_node_or_null("ShipSpace/Districts/UpperHorizonEnclosure_WIP/UpperHorizonEnclosureArchitecture") as Node3D
	if not check(shell != null and FileAccess.file_exists(CONTRACT), "Upper Horizon enclosure or contract missing"):
		quit(1)
		return
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:
			physical_exclusions.append(body.get_rid())
	optical_exclusions.assign(physical_exclusions)
	for body in ship.find_children("*","StaticBody3D",true,false):
		if glass_mesh(body) != null and glass_mesh(body).is_visible_in_tree():
			optical_exclusions.append(body.get_rid())
	check(FileAccess.get_sha256("res://shaders/astraea_space.gdshader")==SKY_SHA256,"Unchanged world sky shader was edited")
	check(FileAccess.get_sha256(GLASS_SHADER)==GLASS_SHA256,"Reviewed glass shader/default opacity changed")
	var environment: Environment = ship.get_node("WorldEnvironment").environment
	check(environment.sky_rotation.is_equal_approx(Vector3.ZERO),"Sky rotation changed to manufacture a vista")
	var sky_material := environment.sky.sky_material as ShaderMaterial
	if check(sky_material != null and sky_material.shader.resource_path == "res://shaders/astraea_space.gdshader", "Runtime sky material differs from reviewed source"):
		# Unset parameters use the shader defaults, fixed by SKY_SHA256 above.
		# ship.gd sets only use_radiance_cache; the headless backend returns Nil
		# rather than evaluating declarations for the remaining uniforms.
		var defaults: Dictionary = {"starboard_direction": Vector3(0.9354072,-0.2923717,0.1988269), "port_direction": Vector3(-0.9871089,0.1045285,-0.1212017), "starboard_radius_degrees": 29.0, "port_radius_degrees": 7.0}
		for parameter in defaults:
			var override_value: Variant = sky_material.get_shader_parameter(parameter)
			check(override_value == null or override_value == defaults[parameter], "Runtime target override differs from exact reviewed shader default: " + str(parameter))
		check(sky_material.get_shader_parameter("use_radiance_cache") == false, "Reviewed direct world-sky mode changed")
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	check(str(data.catalogue_id)=="AST-CMD-006" and str(data.programme_key)=="D18_directory_09", "Wrong enclosure identity")
	var hull_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/hull_envelope.json"))
	for point in hull_data.plan_xz_m:
		hull.append(Vector2(float(point[0]),float(point[1])))
	validate_windows(data)
	for side in ["starboard","port"]:
		var box: Dictionary = data.standing_eye_boxes[side]
		var heights: Array = [float(box.y[0]),(float(box.y[0])+float(box.y[1]))*0.5,float(box.y[1])]
		validate_screen(data,side,heights)
		if side == "port":
			validate_screen(data,side,heights,true)
		for y in data.seated_diagnostic_eye_y:
			validate_screen(data,side,[float(y)])
			if side == "port":
				validate_screen(data,side,[float(y)],true)
	validate_limits(data)
	check(screens == 12 and supported_eyes == 90 and view_pairs > 1000, "Representative screen coverage incomplete")
	print(("UPPER HORIZON ENCLOSURE WINDOWS PASS: " if failures.is_empty() else "UPPER HORIZON ENCLOSURE WINDOWS FAILED: ")+"%d pane contacts, %d ray pairs, %d screens; %d failures. Bounded standing/seated cap-halo/crescent only. Shared ribbon is not an all-eye panorama; finite future roof crops negative targets. No full planet, court, pressure, species-fit or visual-art acceptance." % [contacts,view_pairs,screens,failures.size()])
	main.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
