extends SceneTree
# Actual main-scene capsule/contact coverage. This deliberately makes no claim
# about loaded carts, lift interlocks, water physics or graphical acceptance.
const CONTRACT := "res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json"
const CONTRACT_SHA := "7173bdd7e5213059dcc48b74d596b2589ab805dea5d839ce1e8dda6044b458dd"
const MODEL_PINS := {
	"AST-CIR-005_forward_pool_market_engineering_access.glb": "416ae10ac0e0cbf619e56233136150ded941c5f4c3299da1b95544433f65344b",
	"AST-AQU-016.glb": "95a72a20bd0ed653bb10622ff025b1003386020063587828b29efe5e8e40a481",
	"AST-CIR-005_forward_pool_market.glb": "538f8c6d1a3a075b48cdd63a8cb375c83b07f8100987e193b2efbfd39d134667",
	"AST-STF-009_pool_market.glb": "5e1995b9e0114e8a4f28d9cd5d9c00efbb44ff2fb504d8a965eba613b0e7467a"
}
var walked_frames := 0
var floor_rays := 0
var guard_rays := 0
var interface_rays := 0
var fixture_exits := 0
var pinned_section_fixtures := 0
var wet_receiver_anchors := 0
var ship: Node3D
var actor: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var floors: Node3D
var shell: Node3D
var built: Node3D
var data: Dictionary
var started_msec := 0

func _initialize() -> void:
	started_msec = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec() - started_msec > 230000:
		push_error("Grand Pool access exceeded its 230-second wall-clock watchdog")
		quit(1)
	return false

func xyz(value: Array) -> Vector3:
	return Vector3(value[0], value[1], value[2])

func ray(a: Vector3, b: Vector3, excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a, b, 1)
	query.hit_back_faces = true
	query.exclude = excluded
	return space.intersect_ray(query)

func check_import_pins() -> void:
	assert(FileAccess.get_sha256(CONTRACT) == CONTRACT_SHA, "Test must use the exact frozen source contract")
	for file in MODEL_PINS:
		var path := "res://assets/models/" + str(file)
		assert(FileAccess.get_sha256(path) == MODEL_PINS[file], "Frozen source hash changed: " + str(file))
		var config := ConfigFile.new()
		assert(config.load(path + ".import") == OK, "Missing Godot import: " + str(file))
		var imported: String = config.get_value("remap", "path", "")
		assert(not imported.is_empty() and FileAccess.file_exists(imported))
		var cache := ConfigFile.new()
		assert(cache.load(imported.get_basename() + ".md5") == OK)
		assert(cache.get_value("", "source_md5", "") == FileAccess.get_md5(path), "Stale imported GLB: " + str(file))

func check_floor_owners() -> void:
	var compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var engineering_floors: Dictionary = load("res://tests/secondary_engineering_additive_guard.gd").validate(compiled)
	var baseline: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://docs/GRAND_POOL_PRE_ADOPTION_MESHES.json"))
	assert(compiled.regions.size() == 261 and engineering_floors.size() == 3 and baseline.count == 250)
	assert(floors.get_child_count() == 261, "Exactly one main-scene node per compiler owner")
	var expected: Dictionary = {}
	for entry in data.floor_regions: expected[entry.id] = entry
	assert(expected.size() == 8)
	var prior_found := 0
	var added_found := 0
	# Query exclusions only ignore intervening architecture, never change or
	# disable a floor/contact. Walk tests below use every collision unchanged.
	for region in compiled.regions:
		var owner := floors.get_node_or_null(NodePath(str(region.id))) as Node3D
		assert(owner != null and owner.get_meta("region_id") == region.id)
		var contacts := owner.find_children("*", "StaticBody3D", true, false)
		assert(contacts.size() == 1, "No duplicate local slab owner")
		if expected.has(region.id):
			var original: Dictionary = expected[region.id]
			assert(absf(float(region.floor_y) - float(original.floor_y)) < .00001)
			assert(absf(float(region.thickness) - .24) < .00001)
			assert(absf(float(region.structural_area_m2) - float(original.area_m2)) < .00001)
			for triangle in region.triangles:
				for weights in [Vector3(.34,.33,.33), Vector3(.6,.2,.2), Vector3(.2,.6,.2), Vector3(.2,.2,.6)]:
					check_compiled_sample(region, triangle, weights)
			added_found += 1
		elif engineering_floors.has(region.id):
			assert(region == engineering_floors[region.id], "Approved engineering floor changed")
			check_compiled_sample(region, region.triangles[0], Vector3(.34,.33,.33))
		else:
			assert(baseline.record_sha256.has(region.id), "Unexpected old floor identity")
			# Runtime support on every surviving old owner is separate from the
			# parent's exact Python-canonical 250-record preservation comparison.
			check_compiled_sample(region, region.triangles[0], Vector3(.34,.33,.33))
			prior_found += 1
	assert(prior_found == 250 and added_found == 8)

func check_compiled_sample(region: Dictionary, triangle: Array, weights: Vector3) -> void:
	var p := Vector3(float(triangle[0][0])*weights.x + float(triangle[1][0])*weights.y + float(triangle[2][0])*weights.z, float(region.floor_y), float(triangle[0][1])*weights.x + float(triangle[1][1])*weights.y + float(triangle[2][1])*weights.z)
	var excluded: Array[RID] = [actor.get_rid()]
	var found := false
	for crossing in range(24):
		var hit := ray(p + Vector3.UP * .035, p - Vector3.UP * .035, excluded)
		assert(not hit.is_empty(), "Compiled floor is unsupported: %s at %s" % [region.id, p])
		if floors.is_ancestor_of(hit.collider):
			assert(str(hit.collider.get_parent().name) == str(region.id), "Wrong slab owner under " + str(region.id))
			assert(absf(hit.position.y - p.y) < .002)
			found = true
			break
		excluded.append(hit.collider.get_rid())
	assert(found, "Too many intervening contacts to establish actual compiler support")
	floor_rays += 1

func source_shell_ray(a: Vector3, b: Vector3, initial_exclusions: Array[RID]) -> Dictionary:
	# Coincident core/staff/slab faces are valid assembly joints. Isolate the
	# section's own actual collider without disabling or altering any body.
	var excluded: Array[RID] = initial_exclusions.duplicate()
	for crossing in range(16):
		var hit := ray(a,b,excluded)
		if hit.is_empty() or shell.is_ancestor_of(hit.collider): return hit
		excluded.append(hit.collider.get_rid())
	assert(false, "More than16 intervening bodies prevent source-shell contact proof")
	return {}

func check_source_contacts() -> void:
	# The floor ownership/support checks above test these same bodies separately.
	# Their coincident side faces must not hide the source wall at a real joint.
	var floor_exclusions: Array[RID] = []
	for body in floors.find_children("*", "StaticBody3D", true, false):
		floor_exclusions.append(body.get_rid())
	var builder: GDScript = load("res://scripts/grand_pool_section.gd")
	for name in builder.VISUAL_STAIR_BATCHES:
		var mesh := shell.find_child(name, true, false) as MeshInstance3D
		assert(mesh != null and mesh.find_children("*", "StaticBody3D", true, false).is_empty(), "Visual treads must not regain concave collision")
	assert(built.find_children("GrandPoolStairFlightContact_*", "StaticBody3D", true, false).size() == 3)
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		if str(mesh.name) in builder.VISUAL_STAIR_BATCHES: continue
		assert(mesh.get_node_or_null("StaticContact") != null, "Static shell/guards lost contact: " + str(mesh.name))
		assert(not str(mesh.name).begins_with("PREVIEW_ONLY"), "No compiler floor preview may be instanced")
		if "glass" in str(mesh.name):
			assert(mesh.material_override is ShaderMaterial and mesh.material_override.shader.resource_path == "res://shaders/hospitality_glass.gdshader")
	for part in data.source_parts:
		if part.export_excluded: continue
		var name: String = part.name
		var is_guard: bool = part.role == "glass"
		var is_interface := name.begins_with("GP_PublicPortalDepth") or name.begins_with("GP_BasinWall") or name.begins_with("GP_ServiceVestibuleWall") or name.begins_with("GP_EastWall") or name.begins_with("GP_WestWall")
		if not is_guard and not is_interface: continue
		var vertices: Array = part.world_vertices
		assert(vertices.size() == 8, "Selected source contact must retain its box/prism corners")
		var start_index := 0
		var end_index := 1 if xyz(vertices[0]).distance_to(xyz(vertices[1])) >= xyz(vertices[0]).distance_to(xyz(vertices[3])) else 3
		if name.begins_with("GP_BasinWall"):
			# Sample the exposed water-facing face, not its buried terrace joint.
			var best_distance := INF
			var long_edge := xyz(vertices[start_index]).distance_to(xyz(vertices[end_index]))
			for index in range(4):
				var next := (index+1)%4
				if xyz(vertices[index]).distance_to(xyz(vertices[next])) < long_edge-.01: continue
				var midpoint := (xyz(vertices[index])+xyz(vertices[next]))*.5
				var distance := Vector2(midpoint.x+31,midpoint.z+432).length()
				if distance < best_distance:
					best_distance = distance
					start_index = index
					end_index = next
		var a := xyz(vertices[start_index])
		var b := xyz(vertices[end_index])
		var up := xyz(vertices[start_index+4]) - a
		var normal := (b-a).cross(up).normalized()
		var centre := Vector3.ZERO
		for vertex in vertices: centre += xyz(vertex)/8.0
		# Always begin outside this source solid and cast inward. Starting inside
		# a one-sided concave batch does not establish an exposed contact.
		if normal.dot((a+b)*.5+up*.5-centre) < 0: normal = -normal
		for fraction in [.1, .5, .9]:
			for height in [.15, .5, .85]:
				var p: Vector3 = a.lerp(b, float(fraction)) + up * float(height)
				var hit := source_shell_ray(p + normal*.08, p - normal*.08, floor_exclusions)
				if hit.is_empty() or not shell.is_ancestor_of(hit.collider):
					print("GRAND POOL CONTACT FAILURE: ",name," point:",p," outward:",normal," hit:",hit," collider:",hit.collider.get_path() if not hit.is_empty() else "none")
				assert(not hit.is_empty() and shell.is_ancestor_of(hit.collider), "Missing source guard/wall contact: %s at %s" % [name, p])
				if is_guard: guard_rays += 1
				else: interface_rays += 1
	# Real core apertures, collar closures, retained source return landing and
	# both complete fixed-sill interfaces, with their actual colliders enabled.
	for y in [44.0, 52.5]:
		assert(ray(Vector3(-8.4,y+1.3,-432), Vector3(-7.4,y+1.3,-432)).is_empty(), "Public portal is blocked")
		for z in [-435.08, -428.92]:
			assert(not ray(Vector3(-8.4,y+1.3,z),Vector3(-7.4,y+1.3,z)).is_empty(), "Room/core collar seam is open")
	var landing := ray(Vector3(-14.2,49.5,-417),Vector3(-14.2,49.2,-417))
	assert(not landing.is_empty() and shell.is_ancestor_of(landing.collider) and absf(landing.position.y-49.35)<.002, "Retained source stair return landing missing")
	for y in [46.2, 52.5]:
		for index in range(13):
			var p := Vector3(-13.58 + float(index)*.1, y, -412.4)
			var hit := ray(p+Vector3.UP*.03, p-Vector3.UP*.03)
			assert(not hit.is_empty() and absf(hit.position.y-y)<.003, "Local lift fixed-sill/floor gap at " + str(p))
			interface_rays += 1
	# The central upper void must remain open; no convex-hull floor bridge.
	assert(ray(Vector3(-31,52.6,-432),Vector3(-31,52.4,-432)).is_empty())

func check_section_fixture(light: Light3D, item: Dictionary) -> void:
	var source := light as SpotLight3D
	assert(source != null, "Source-authored pool fixtures must retain their spot cones")
	assert(source.global_position.distance_to(xyz(item.position_xyz)) < .0001, "Fixture position differs from pinned source: " + str(item.name))
	assert(absf(source.light_energy-float(item.suggested_energy)) < .00001, "Do not silently brighten source energy: " + str(item.name))
	assert(absf(source.spot_angle-float(item.suggested_spot_angle_degrees)) < .00001, "Source cone angle changed: " + str(item.name))
	assert((-source.global_basis.z).distance_to(xyz(item.direction).normalized()) < .00001, "Source cone direction changed: " + str(item.name))
	var calibrated_ranges := {"pool_vault":22.0, "wet_terrace":14.0, "market_warm":11.0}
	var expected_range := float(calibrated_ranges.get(str(item.profile), item.suggested_range_m))
	assert(absf(source.spot_range-expected_range) < .00001, "Unexpected range outside bounded profile calibration")
	assert(absf(source.spot_attenuation-1.0) < .00001, "The bounded trial did not authorize a distance-falloff change")
	if item.profile == "wet_terrace":
		assert(source.has_meta("illumination_anchor") and source.get_meta("illumination_anchor") is Vector3, "Wet fixture requires its supported receiver")
		var receiver: Vector3 = source.get_meta("illumination_anchor")
		var expected: Vector3 = xyz(item.position_xyz)
		var surface_y := float(data.section.wet_deck_y)
		if absf(expected.x+16.4) < .001 and absf(expected.z+442.0) < .001:
			surface_y = float(data.section.arrival_y)
		elif absf(expected.x+16.4) < .001 and absf(expected.z+456.0) < .001:
			# Derive the support from the frozen source ramp, not a copied
			# runtime magic height: this marker is over its sloping upper pan.
			var ramp: Dictionary = data.accessible_ramp.upper_run
			var begin: Vector3 = xyz(ramp.start_xyz)
			var end: Vector3 = xyz(ramp.end_xyz)
			var fraction := (expected.z-begin.z)/(end.z-begin.z)
			surface_y = lerpf(begin.y,end.y,fraction)
		expected.y = surface_y+.03
		assert(receiver.distance_to(expected) < .001, "Wet anchor must stay 30 mm above the source-backed receiver")
		var support := ray(receiver+Vector3.UP*.02,receiver-Vector3.UP*.08)
		assert(not support.is_empty() and (floors.is_ancestor_of(support.collider) or shell.is_ancestor_of(support.collider)), "Wet receiver lacks actual compiled-floor or source-ramp support")
		assert(absf(support.position.y-surface_y) < .002 and support.normal.y > .7, "Wet receiver landed on the wrong surface")
		var to_receiver: Vector3 = receiver-source.global_position
		assert(to_receiver.length() < source.spot_range and to_receiver.normalized().dot(-source.global_basis.z) >= cos(deg_to_rad(source.spot_angle)), "Receiver is outside the actual fixture cone/range")
		assert(ray(source.global_position,receiver).is_empty(), "Wet source cannot illuminate its real receiver")
		wet_receiver_anchors += 1
	else:
		assert(not source.has_meta("illumination_anchor"), "Only the eight wet-fixture receivers belong to this bounded trial")
	pinned_section_fixtures += 1

func check_lights_and_identities() -> void:
	assert(built.get_meta("programme_keys") == data.programme_ids)
	for item in [{"name":"GrandPoolProgramme", "key":"D08_directory_01", "alias":"D08_pool0"}, {"name":"OrchardMarketProgramme", "key":"D09_directory_01", "alias":"D09_market0"}]:
		var programme := built.get_node(NodePath(item.name))
		assert(programme.get_meta("programme_key") == item.key and programme.get_meta("historical_room_id") == item.alias)
	var local: Node3D = built.get_node("GrandPoolLocalLift")
	assert(local.get_script().resource_path == "res://scripts/commons_lift.gd")
	assert(local.persistent_id == &"grand_pool_local_lift_001" and local.stop_ids == ["D08_WET", "D09"])
	assert(local.floor_heights == [0.0, 6.3] and local.cabin_file == "AST-CIR-003.glb")
	assert(local.global_position.distance_to(Vector3(-15.4,46.2,-412.4)) < .001 and absf(absf(local.rotation.y)-PI)<.001)
	var staff: Node3D = ship.find_child("ForwardStaffLift", true, false)
	assert(staff.persistent_id == &"forward_staff_lift_001")
	assert(staff.stop_ids == ["D01", "D02", "D03", "D08_WET", "D09"])
	assert(staff.floor_heights == [0.0, 6.0, 12.0, 46.2, 52.5])
	assert(staff.cabin_file == "AST-CIR-003_five_stop.glb" and "wet service" in str(staff.stop_names[3]))
	assert(staff.landing_gates.size() == 5 and local.landing_gates.size() == 2)
	var representations := {"AST-AQU-016.glb":0, "AST-STF-009_pool_market.glb":0, "AST-STF-009.glb":0, "AST-CIR-005_forward_pool_market.glb":0, "AST-CIR-005_forward_core.glb":0, "AST-CIR-005_forward_pool_market_engineering_access.glb":0}
	for node in ship.find_children("*", "Node3D", true, false):
		var file: String = node.get_meta("catalogue_file", "")
		if representations.has(file): representations[file] += 1
	assert(representations.values() == [1,1,0,0,0,1], "New and retained derivative representations must not be doubled")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget == 8 and budget.get_script().resource_path == "res://scripts/lighting_budget.gd")
	assert(budget.MAX_VISIBILITY_CANDIDATES == 32, "Keep the existing bounded shared selector")
	assert(data.fixtures.size() == 25 and built.find_children("GrandPoolSource_*", "SpotLight3D", true, false).size() == 25)
	var source_fixture_ids: Dictionary = {}
	var source_profile_counts: Dictionary = {}
	for item in data.fixtures:
		assert(not source_fixture_ids.has(item.name), "Pinned fixture identifiers must be unique")
		source_fixture_ids[item.name] = true
		source_profile_counts[item.profile] = int(source_profile_counts.get(item.profile,0))+1
	assert(source_profile_counts == {"market_warm":9,"pool_vault":6,"wet_terrace":8,"staff_work":2})
	var staff_shell := ship.find_child("LowerStaffEnclosure", true, false) as Node3D
	var fixture_records: Array = data.fixtures.duplicate()
	fixture_records.append_array(data.staff.upper_light_markers)
	assert(fixture_records.size() == 45)
	for item in fixture_records:
		var owner := staff_shell if str(item.name).begins_with("DATUM_GPM_staff_light_") else shell
		var marker: Node3D = load("res://scripts/grand_pool_section.gd").source_marker(owner, str(item.name))
		assert(marker != null and marker.global_position.distance_to(xyz(item.position_xyz)) < .003, "Stale/moved fixture marker")
		assert(ray(marker.global_position, marker.global_position+Vector3.DOWN*.06).is_empty(), "Fixture light exit blocked: " + str(item.name))
		var matching := 0
		for light in budget.sources:
			if light.get_meta("source_marker", "") == item.name:
				assert(light.global_position.distance_to(marker.global_position)<.001 and budget.requested_shadow[light.get_instance_id()])
				if source_fixture_ids.has(item.name): check_section_fixture(light,item)
				matching += 1
		assert(matching == 1, "Exactly one budgeted source per fixture marker")
		fixture_exits += 1
	assert(pinned_section_fixtures == 25 and wet_receiver_anchors == 8, "Exactly 25 pinned source fixtures and 8 supported wet receivers")
	for entry in data.door_fittings:
		var door := door_for(str(entry.name))
		assert(door.get_script().resource_path == "res://scripts/guest_entry_door.gd")
		assert(door.visual_file == "AST-DOR-002_wide.glb" and door.open_fraction == 0.0 and not door.desired_open)
		assert(door.global_position.distance_to(xyz(entry.root_xyz))<.003)
		assert(absf(door.rotation.y-float(entry.yaw_radians))<.001)
		var a: Vector3 = door.global_transform * Vector3(0,1.2,-.25)
		var b: Vector3 = door.global_transform * Vector3(0,1.2,.25)
		var hit := ray(a,b)
		assert(not hit.is_empty() and door.is_ancestor_of(hit.collider), "Closed environmental door does not actually close its aperture")
	var water := built.get_node("GrandPoolTrialWater_VisualOnly_NoSwimming") as MeshInstance3D
	assert(water != null and water.find_children("*", "CollisionObject3D", true, false).is_empty())
	assert(water.mesh.get_aabb().position.y > 46.049 and water.mesh.get_aabb().position.y < 46.051)

func check_budget() -> void:
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	budget.refresh()
	var active := 0
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active += 1
	assert(active <= 8, "The new section must obey the existing local shadow-source cap")

func door_for(key: String) -> Node3D:
	var door := built.get_node_or_null(NodePath(("GrandPoolDoor_"+key).validate_node_name())) as Node3D
	assert(door != null)
	return door

func set_door(key: String, opened: bool) -> void:
	var door := door_for(key)
	if door.desired_open != opened: door.interact(actor)
	var reached := false
	for frame in range(180):
		await physics_frame
		if (opened and door.open_fraction > .999) or (not opened and door.open_fraction < .001):
			reached = true
			break
	assert(reached, "Existing door failed its bounded requested movement: " + key)

func walk_to(target: Vector3) -> void:
	var start := actor.position
	var a := Vector2(start.x, start.z)
	var b := Vector2(target.x, target.z)
	var span := b-a
	var budget := mini(1800, ceili(span.length()/3.1*60.0)+240)
	var reached := false
	for frame in range(budget):
		var delta := Vector3(target.x-actor.position.x,0,target.z-actor.position.z)
		if delta.length() < .075:
			reached = true
			break
		var movement := delta.normalized()*3.1
		actor.velocity = Vector3(movement.x, -.1 if actor.is_on_floor() else actor.velocity.y-9.8/60, movement.z)
		actor.move_and_slide()
		await physics_frame
		walked_frames += 1
		assert(walked_frames < 28000, "Grand Pool walking exceeded its bounded frame budget")
		var fraction := clampf((Vector2(actor.position.x,actor.position.z)-a).dot(span)/maxf(span.length_squared(),.00001),0,1)
		assert(absf(actor.position.y-lerpf(start.y,target.y,fraction)) < .23, "Player left the intended supported route at " + str(actor.position))
	if not reached:
		for index in range(actor.get_slide_collision_count()):
			print("GRAND POOL WALK BLOCK: ",actor.get_slide_collision(index).get_collider().get_path())
	assert(reached, "Grand Pool walk stalled at %s toward %s" % [actor.position,target])
	assert(absf(actor.position.y-target.y)<.18, "Grand Pool walk reached wrong elevation")

func walk_route(route: Array, reverse: bool = false) -> void:
	var sequence := route.duplicate()
	if reverse: sequence.reverse()
	for point in sequence: await walk_to(xyz(point))
	check_budget()

func run() -> void:
	check_import_pins()
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship = main.get_node("World360/Astraea")
	space = ship.get_world_3d().direct_space_state
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	built = ship.find_child("GrandPoolOrchardSection_WIP",true,false)
	assert(built != null)
	shell = built.get_node("GrandPoolConnectedArchitecture")
	floors = ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	check_floor_owners()
	check_source_contacts()
	check_lights_and_identities()
	actor.position = Vector3(-5.4,44.1,-432)
	actor.velocity = Vector3.ZERO
	await walk_route(data.public_interfaces.D08_route_xyz)
	await walk_route(data.accessible_ramp.route_xyz)
	var wet: Array = [[-20,46.2,-447.8],[-20,46.2,-459.8],[-43,46.2,-459.8],[-45.9,46.2,-458],[-45.9,46.2,-405],[-43,46.2,-400.9],[-20,46.2,-400.9],[-20,46.2,-426.8]]
	await walk_route(wet)
	var lower_lift: Array = [[-20,46.2,-407],[-10.8,46.2,-407],[-10.8,46.2,-412.4],[-12.5,46.2,-412.4]]
	await walk_route(lower_lift)
	await walk_route(lower_lift,true)
	var stair: Array = [[-20,46.2,-426.8],[-15.8,46.2,-426.8],[-15.8,46.2,-423.5],[-15.8,49.35,-418.06],[-15.8,49.35,-417],[-12.6,49.35,-417],[-12.6,49.35,-418.06],[-12.6,52.5,-423.5],[-12.6,52.5,-426.7],[-14.55,52.5,-426.7]]
	await walk_route(stair)
	await set_door("wet_market_stair",true)
	await walk_to(Vector3(-14.55,52.5,-429.5))
	await set_door("wet_market_stair",false)
	await walk_to(Vector3(-15.5,52.5,-432))
	await walk_route(data.public_interfaces.D09_route_xyz,true)
	await walk_route(data.public_interfaces.D09_route_xyz)
	var market: Array = []
	for p in data.market.adopted_dry_loop_centreline_xz: market.append([p[0],52.5,p[1]])
	for entry in data.door_fittings: assert(door_for(str(entry.name)).open_fraction < .001)
	await walk_route(market)
	await walk_route(market,true)
	for entry in data.door_fittings: assert(door_for(str(entry.name)).open_fraction < .001, "Dry circuit must work with all environmental doors closed")
	# Turn aft of GP_UpperPier_5 (Z max -404.102), rather than through it.
	var upper_approach: Array = [[-15.5,52.5,-429.5],[-9.65,52.5,-429.5],[-9.65,52.5,-403.4],[-14.55,52.5,-403.4]]
	await walk_route(upper_approach)
	await set_door("wet_market_lift",true)
	var upper_lift: Array = [[-14.55,52.5,-408.3],[-12.5,52.5,-408.3],[-12.5,52.5,-412.4]]
	await walk_route(upper_lift)
	await walk_route(upper_lift,true)
	await walk_to(Vector3(-14.55,52.5,-403.4))
	await set_door("wet_market_lift",false)
	await walk_route(upper_approach,true)
	await walk_to(Vector3(-14.55,52.5,-429.5))
	await set_door("wet_market_stair",true)
	await walk_to(Vector3(-14.55,52.5,-426.7))
	await set_door("wet_market_stair",false)
	await walk_route(stair,true)
	await walk_to(Vector3(-20,46.2,-447.8))
	await walk_route(data.accessible_ramp.route_xyz,true)
	await walk_route(data.public_interfaces.D08_route_xyz,true)
	var ceremonial: Array = [[-9.4,44,-432],[-11,44,-432],[-16.2,46.2,-432],[-20,46.2,-432]]
	await walk_route(ceremonial)
	await walk_route(ceremonial,true)
	await walk_to(Vector3(-5.4,44,-432))
	print("GRAND POOL ACCESS PASS: ",floor_rays," compiler floor samples across261 owners; ",guard_rays," source guard/glass contacts; ",interface_rays," wall/interface contacts; ",fixture_exits," budgeted fixture exits; ",pinned_section_fixtures," pinned section lights and ",wet_receiver_anchors," supported receivers; actual public-core/ramp/wet-circuit/closed-market-loop/stair/local-lift-approach round trip in ",walked_frames," walking frames. Loaded cart, lift interlocks, swimming and in-ship visual acceptance remain separate.")
	main.queue_free()
	await process_frame
	quit(0)
