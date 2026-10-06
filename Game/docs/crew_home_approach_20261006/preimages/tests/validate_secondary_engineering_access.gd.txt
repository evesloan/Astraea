extends SceneTree
# Actual capsule movement, production cart straight smoke and conservative
# loaded-envelope queries. Diagnostic staff starts are NOT external connections.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"
var ship: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var built: Node3D
var floors: Node3D
var shell: Node3D
var space: PhysicsDirectSpaceState3D
var data: Dictionary
var started := 0
var walked_frames := 0
var cart_frames := 0
var support_rays := 0
var loaded_poses := 0

func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec() - started > 180000:
		push_error("Secondary engineering access exceeded180-second watchdog")
		quit(1)
	return false

func ray(a: Vector3, b: Vector3, excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a, b, 1)
	query.exclude = excluded
	query.hit_back_faces = true
	return space.intersect_ray(query)

func xyz(value: Array) -> Vector3:
	return Vector3(value[0], value[1], value[2])

func pin_imports() -> void:
	for filename in data.model_pins:
		var path := "res://assets/models/" + str(filename)
		assert(FileAccess.get_sha256(path) == str(data.model_pins[filename]), "Source export changed: " + str(filename))
		var config := ConfigFile.new()
		assert(config.load(path + ".import") == OK)
		var imported: String = config.get_value("remap", "path", "")
		assert(not imported.is_empty() and FileAccess.file_exists(imported))
		var cache := ConfigFile.new()
		assert(cache.load(imported.get_basename() + ".md5") == OK)
		assert(cache.get_value("", "source_md5", "") == FileAccess.get_md5(path), "Stale engineering import: " + str(filename))
	var capture_audit_path := "res://docs/SECONDARY_ENGINEERING_CAPTURE_ADOPTION.json"
	assert(FileAccess.get_sha256(capture_audit_path) == "083f3e11dc814279e8729153c7361255829072e1d5344a855ebb62ee9712618b")
	var capture_audit: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(capture_audit_path))
	for path in data.preserved_runtime_pins:
		if str(path) == "scripts/presentation.gd":
			# Explicit parent-approved second integration exception, never a
			# silent dropped byte pin. Retain and check the original pin too.
			assert(str(data.preserved_runtime_pins[path]) == str(capture_audit.original_sha256))
			load("res://tests/secondary_engineering_additive_guard.gd").validate_pinned_input(str(path),str(capture_audit.integrated_sha256))
		else:
			assert(FileAccess.get_sha256("res://" + str(path)) == str(data.preserved_runtime_pins[path]), "Existing runtime bytes changed: " + str(path))

func floor_support(p: Vector3, expected_owner: String = "", barrier_bearing_probe: bool = false) -> void:
	var excluded: Array[RID] = [actor.get_rid(), cart.get_rid()]
	var hit := ray(p + Vector3.UP * .12, p - Vector3.UP * .12, excluded)
	# At the barrier bearing line, its retained mesh underside coincides with
	# the compiler top. Exclude that intervening barrier from this support ray
	# only; retain every source collision for actual capsule/cart attempts.
	if barrier_bearing_probe:
		for crossing in range(8):
			if hit.is_empty() or floors.is_ancestor_of(hit.collider): break
			assert("UnbuiltServiceSafetyClosure_" in str(hit.collider.get_path()), "Unexpected bearing obstruction")
			excluded.append(hit.collider.get_rid())
			hit = ray(p + Vector3.UP * .12, p - Vector3.UP * .12, excluded)
	assert(not hit.is_empty() and absf(hit.position.y - p.y) < .015 and hit.normal.y > .99, "Missing same-level support: " + str(p))
	assert(floors.is_ancestor_of(hit.collider), "Support must be compiler-owned, not duplicate source slab")
	if not expected_owner.is_empty():
		assert(str(hit.collider.get_parent().name) == expected_owner, "Wrong compiler owner at " + str(p))
	support_rays += 1

func floor_and_cap() -> void:
	var compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	load("res://tests/secondary_engineering_additive_guard.gd").validate(compiled)
	assert(data.old_region_records.size() == 258)
	validate_loaded_theater_roster(compiled)
	var current: Dictionary = {}
	for region in compiled.regions: current[str(region.id)] = region
	for old in data.old_region_records:
		assert(current.has(str(old.id)) and current[str(old.id)] == old, "Every old258 record must remain EXACTLY equal: " + str(old.id))
	for entry in data.floor_regions:
		assert(current.has(str(entry.id)))
		var actual: Dictionary = current[str(entry.id)]
		assert(absf(float(actual.floor_y) - float(entry.floor_y)) < .00001 and absf(float(actual.thickness) - .24) < .00001)
		var owner := floors.get_node(NodePath(str(entry.id)))
		assert(owner.find_children("*", "StaticBody3D", true, false).size() == 1)
	floor_support(Vector3(7.9, 6, -432), "D02_secondary_engineering_visitor_gap")
	floor_support(Vector3(12, 6, -432), "D02_secondary_engineering_floor")
	floor_support(Vector3(51, 6, -432), "D02_secondary_engineering_floor")
	var cap := ray(Vector3(34, 11.74, -432), Vector3(34, 11.80, -432))
	assert(not cap.is_empty() and floors.is_ancestor_of(cap.collider) and absf(cap.position.y - 11.76) < .003, "Opaque Y12 cap underside missing")
	assert(str(cap.collider.get_parent().name) == "D03_secondary_engineering_cap")

func source_and_lights() -> void:
	assert(built.get_meta("first_pass_quality_accepted") == false)
	assert(built.get_meta("guest_observation_connected") == true)
	assert(data.door_fittings.is_empty(), "Original open-aperture shell contract installs no dynamic doors; separate cell gate has its own contract")
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		assert(mesh.get_node_or_null("StaticContact") != null, "Source contact removed: " + str(mesh.name))
		assert(mesh.material_override == null, "Frozen pressure glass/material may not be replaced")
		assert(not "PREVIEW" in str(mesh.name))
	var sources := built.find_children("SecondaryEngineeringSource_*", "SpotLight3D", true, false)
	assert(sources.size() == 9)
	for item in data.fixtures:
		var marker := shell.find_child(str(item.name), true, false) as Node3D
		if marker == null: marker = shell.find_child(str(item.name).validate_node_name(), true, false) as Node3D
		assert(marker != null and marker.global_position.distance_to(xyz(item.position_xyz)) < .0001)
		var light := built.find_child(("SecondaryEngineeringSource_" + str(item.name)).validate_node_name(), true, false) as SpotLight3D
		assert(light != null and light.global_position.distance_to(marker.global_position - Vector3.UP * .08) < .0001)
		assert(ray(light.global_position, light.global_position - Vector3.UP * .04).is_empty(), "Fixture lens exit blocked")
	var budget := ship.find_child("LocalShadowSourceBudget", true, false)
	assert(budget != null and budget.shadow_source_budget == 8)
	for light in sources: assert(budget.sources.has(light), "Shared budget must own every source")
	budget.refresh()
	var active := 0
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active += 1
	assert(active <= 8)
	# Diagnostic evidence only: never assert stacked-pane visual acceptance.
	for suffix in ["DATUM_plant_inspection_n", "DATUM_plant_inspection_s"]:
		var light := built.find_child("SecondaryEngineeringSource_" + suffix, true, false) as SpotLight3D
		var blocker := ray(light.global_position, actor.global_position + Vector3.UP*1.65, [actor.get_rid()])
		var blocker_path := "none" if blocker.is_empty() else str(blocker.collider.get_path())
		print("SECONDARY VISITOR INSPECTION LIGHT DIAGNOSTIC:", suffix, " visible=", light.visible, " shadow=", light.shadow_enabled, " budget_visible_sample=", budget.call("_has_visible_sample",light), " first_retained_collision=",blocker_path," source=", light.global_position)
	print("SECONDARY VISITOR GLASS/LIGHTING: actual normal-eye visual review remains UNACCEPTED; cap remains8")
	light_selection_diagnostics()

func light_selection_diagnostics() -> void:
	var budget: Node = ship.find_child("LocalShadowSourceBudget", true, false)
	var saved := actor.global_position
	var records: Array = []
	for view in [{"label":"visitor", "foot":Vector3(12,6,-432)}, {"label":"maintenance_diagnostic", "foot":Vector3(46,6,-439)}, {"label":"workbay_diagnostic", "foot":Vector3(30,6,-405)}]:
		actor.global_position = view.foot
		budget.refresh()
		var record: Dictionary = {"view":view.label, "eye_xyz":[view.foot.x,view.foot.y+1.65,view.foot.z], "sources":[]}
		for suffix in ["DATUM_plant_inspection_n", "DATUM_plant_inspection_s"]:
			var light := built.find_child("SecondaryEngineeringSource_" + suffix, true, false) as SpotLight3D
			var excluded: Array[RID] = [actor.get_rid(), cart.get_rid()]
			var blockers: Array = []
			for layer in range(12):
				var hit := ray(light.global_position, actor.global_position + Vector3.UP*1.65, excluded)
				if hit.is_empty(): break
				blockers.append(str(hit.collider.get_path()))
				excluded.append(hit.collider.get_rid())
			var item: Dictionary = {"source":suffix, "source_xyz":[light.global_position.x,light.global_position.y,light.global_position.z], "selected":light.visible and light.shadow_enabled, "visible_sample":budget.call("_has_visible_sample",light), "retained_ray_blockers":blockers}
			record.sources.append(item)
			print("SECONDARY LIGHT SELECTION:", JSON.stringify({"view":view.label,"source":item}))
		records.append(record)
	actor.global_position = saved
	budget.refresh()
	var file := FileAccess.open("res://artifacts/secondary_engineering_light_diagnostic.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"Read-only source selection/ray diagnostic; no visual acceptance or material/budget change", "shadow_cap":8, "views":records}, "  "))

func walk_to(destination: Vector2) -> void:
	var reached := false
	for frame in range(1000):
		var delta := Vector3(destination.x - actor.global_position.x, 0, destination.y - actor.global_position.z)
		if delta.length() < .08:
			reached = true
			break
		var movement := delta.normalized() * 2.0
		actor.velocity.x = movement.x
		actor.velocity.z = movement.z
		actor.velocity.y = -.1 if actor.is_on_floor() else actor.velocity.y - 9.8 / 60.0
		actor.move_and_slide()
		walked_frames += 1
		assert(absf(actor.global_position.y - 6) < .15, "Capsule left supportedY6")
		await physics_frame
	assert(reached, "Capsule blocked at %s toward %s" % [actor.global_position, destination])
	floor_support(Vector3(actor.global_position.x, 6, actor.global_position.z))

func loaded_route(points: Array) -> void:
	var load := BoxShape3D.new()
	load.size = Vector3(1.2, 2.15, 1.8)
	var excluded: Array[RID] = [actor.get_rid(), cart.get_rid()]
	for product in cart.products: excluded.append(product.get_rid())
	for index in range(points.size() - 1):
		var a: Vector2 = points[index]
		var b: Vector2 = points[index + 1]
		var yaw := atan2(-(b.x-a.x), -(b.y-a.y))
		var steps := maxi(1, ceili(a.distance_to(b)/.20))
		for step in range(steps + 1):
			var p := a.lerp(b, float(step)/steps)
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = load
			query.margin = .001
			query.exclude = excluded
			query.transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(p.x, 7.095, p.y))
			var hits := space.intersect_shape(query, 128)
			assert(hits.size() < 128 and hits.is_empty(), "Conservative loaded cart blocked at " + str(p))
			floor_support(Vector3(p.x, 6, p.y))
			loaded_poses += 1

	# Actual collision queries also sweep rotation at every interior turn.
	for index in range(1, points.size() - 1):
		var p: Vector2 = points[index]
		var prior: Vector2 = points[index - 1]
		var next: Vector2 = points[index + 1]
		var from_yaw := atan2(-(p.x-prior.x), -(p.y-prior.y))
		var to_yaw := atan2(-(next.x-p.x), -(next.y-p.y))
		for step in range(25):
			var yaw := from_yaw + wrapf(to_yaw-from_yaw, -PI, PI)*float(step)/24.0
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = load
			query.margin = .001
			query.exclude = excluded
			query.transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(p.x, 7.095, p.y))
			assert(space.intersect_shape(query, 128).is_empty(), "Loaded-cart turning envelope blocked at " + str(p))
			loaded_poses += 1

func safety_closures() -> void:
	assert(built.find_children("UnbuiltServiceSafetyClosure_*", "Node3D", true, false).size() == 2)
	for z in [-432.0, -404.0]:
		for offset in [-1.1, -.6, 0.0, .6, 1.1]:
			for y in [6.3, 7.3, 8.3]:
				var hit := ray(Vector3(53.5, y, z + offset), Vector3(54.1, y, z + offset))
				assert(not hit.is_empty() and built.is_ancestor_of(hit.collider), "Visible barrier missing")
				assert(hit.collider.get_parent() is MeshInstance3D, "Safety closure must be retained visible model, not invisible wall")
		floor_support(Vector3(53.82, 6, z), "D02_secondary_engineering_floor", true)
		var load := BoxShape3D.new()
		load.size = Vector3(1.2, 2.15, 1.8)
		var sweep := PhysicsShapeQueryParameters3D.new()
		sweep.shape = load
		sweep.margin = .001
		sweep.exclude = [actor.get_rid(), cart.get_rid()]
		sweep.transform = Transform3D(Basis(Vector3.UP, -PI / 2), Vector3(52.7, 7.095, z))
		sweep.motion = Vector3(2, 0, 0)
		var fractions := space.cast_motion(sweep)
		assert(fractions.size() == 2 and fractions[0] > .01 and fractions[0] < .15, "Loaded-cart sweep must stop at visible barrier before unsupported edge")
		actor.global_position = Vector3(52.7, 6.04, z)
		actor.velocity = Vector3.ZERO
		for frame in range(75):
			actor.velocity = Vector3(2, -.1, 0)
			actor.move_and_slide()
			await physics_frame
		assert(actor.global_position.x < 53.60 and actor.global_position.x > 53.25 and absf(actor.global_position.y - 6) < .12, "Capsule must stop at visible unbuilt-route barrier")
	assert(built.find_children("UnbuiltRouteNotice", "Label3D", true, false).size() == 2)

func physical_cart_straight_smoke() -> void:
	# Single initial cart/products placement, then actual rigid-body forces only.
	# This bounded smoke is NOT full route/turn/handle gameplay acceptance.
	var locals: Array[Vector3] = []
	for product in cart.products: locals.append(cart.to_local(product.global_position))
	assert(locals.size() == 4)
	cart.global_position = Vector3(6, 6.04, -432)
	cart.rotation = Vector3(0, -PI / 2, 0)
	cart.linear_velocity = Vector3.ZERO
	cart.angular_velocity = Vector3.ZERO
	cart.sleeping = false
	for index in range(4):
		cart.products[index].global_position = cart.global_transform * locals[index]
		cart.products[index].linear_velocity = Vector3.ZERO
		cart.products[index].angular_velocity = Vector3.ZERO
		cart.products[index].sleeping = false
	actor.global_position = Vector3(4.1, 6.04, -432)
	actor.velocity = Vector3.ZERO
	for frame in range(30): await physics_frame
	var reached := false
	for frame in range(1500):
		var error := Vector3(12 - cart.global_position.x, 0, -432 - cart.global_position.z)
		if error.length() < .15:
			reached = true
			break
		var desired := error.normalized() * .7
		var horizontal := Vector3(cart.linear_velocity.x, 0, cart.linear_velocity.z)
		cart.apply_central_force((desired-horizontal)*cart.mass*4.0)
		var yaw_error := wrapf(-PI / 2 - cart.rotation.y, -PI, PI)
		cart.apply_torque(Vector3.UP * clampf(yaw_error*60-cart.angular_velocity.y*14, -55, 55))
		assert(absf(cart.global_position.y - 6) < .20 and absf(cart.global_position.z + 432) < .30, "Actual cart drift/fall in guest aperture")
		if frame % 12 == 0: floor_support(Vector3(cart.global_position.x, 6, cart.global_position.z))
		cart_frames += 1
		await physics_frame
	assert(reached, "Actual four-product cart did not traverse guest aperture")
	for product in cart.products:
		assert(absf(product.global_position.x-cart.global_position.x) < 1.0 and absf(product.global_position.z-cart.global_position.z) < 1.0 and product.global_position.y > 6.5, "Loose cart product escaped during straight smoke")

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	pin_imports()
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	cart = ship.find_child("CustodialCart", true, false)
	built = ship.find_child("SecondaryEngineeringSection_WIP", true, false)
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms", true, false)
	assert(built != null and floors != null and cart != null)
	shell = built.get_node("SecondaryEngineeringArchitecture")
	space = ship.get_world_3d().direct_space_state
	actor.set_physics_process(false)
	actor.global_position = Vector3(6, 6.04, -432)
	actor.velocity = Vector3.ZERO
	var core_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	assert(str(core_data.enclosure_file) == str(data.core_export) and core_data.deck_numbers.size() == 17 and core_data.floor_y.size() == 17)
	for z in [-433.19, -432.0, -430.81]:
		for y in [6.02, 7.65, 8.69]:
			assert(ray(Vector3(7.0,y,z),Vector3(9.1,y,z),[actor.get_rid(),cart.get_rid()]).is_empty(), "Near-full2.4x2.7 guest aperture blocked")
	floor_and_cap()
	await walk_to(Vector2(12, -432))
	source_and_lights()
	await walk_to(Vector2(6, -432))
	loaded_route([Vector2(6,-432), Vector2(12,-432)])
	# Explicit diagnostic interior start, never an invented visitor/staff doorway.
	actor.global_position = Vector3(30, 6.04, -459)
	actor.velocity = Vector3.ZERO
	var staff := [Vector2(30,-459),Vector2(30,-452.8),Vector2(38,-452.8),Vector2(38,-445),Vector2(45.5,-445),Vector2(45.5,-432),Vector2(51,-432),Vector2(51,-411.2),Vector2(30,-411.2),Vector2(30,-405)]
	for target in staff: await walk_to(target)
	loaded_route(staff)
	assert(not ray(Vector3(16.5,7.6,-432),Vector3(17.5,7.6,-432)).is_empty(), "Visitor glass separation must remain")
	assert(not ray(Vector3(20.5,7.6,-432),Vector3(21.5,7.6,-432)).is_empty(), "Hall west isolation must remain")
	await safety_closures()
	await physical_cart_straight_smoke()
	print("SECONDARY ENGINEERING ACCESS PASS: guest observation capsule arrival/return; actual four-product cart straight force-driven smoke;",loaded_poses," conservative load poses;",support_rays," support rays;",walked_frames," walked frames;",cart_frames," cart frames. All258 old records equal; Y6 floor/Y12 cap; nine fixtures under unchanged8-source budget; visible east safety closures. Internal staff tests used diagnostic starts, NOT an external staff connection. Essential materials/textures/lighting/furnishings/details, stacked-pane visitor view, dynamic doors, operations and full first-pass completion remain UNACCEPTED.")
	main.queue_free()
	await process_frame
	quit()

# The authenticated nine-record theater addition changes the global roster only.
# validate(compiled) above still proves every old258/current engineering4 record.
func validate_loaded_theater_roster(compiled: Dictionary) -> void:
	var guard = load("res://tests/secondary_engineering_additive_guard.gd")
	assert(FileAccess.get_sha256(guard.THEATER_PROPOSAL)==guard.THEATER_PROPOSAL_SHA)
	var proposal: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(guard.THEATER_PROPOSAL))
	var additions: Dictionary = proposal.new_compiled_records
	var approved_ids: Array = guard.ALLOWED_THEATER_COMPILED_IDS.duplicate()
	var added_ids: Array = additions.keys()
	approved_ids.sort()
	added_ids.sort()
	assert(added_ids==approved_ids and additions.size()==9,"Exactly the authenticated nine theater owners required")
	assert(compiled.regions.size()==271 and floors.get_child_count()==271,"Exact reviewed combined floor count required")
	var current: Dictionary = {}
	for row in compiled.regions:
		assert(not current.has(str(row.id)),"Duplicate compiled owner")
		current[str(row.id)] = row
	for id in approved_ids:
		assert(current.has(id) and current[id]==additions[id],"Whole theater record changed: "+str(id))
	var loaded_ids: Array = []
	for owner in floors.get_children():
		var id := str(owner.name)
		assert(current.has(id) and not loaded_ids.has(id),"Unknown or duplicate loaded floor owner: "+id)
		loaded_ids.append(id)
	var compiled_ids: Array = current.keys()
	compiled_ids.sort()
	loaded_ids.sort()
	assert(loaded_ids==compiled_ids,"Every exact compiled owner must exist in the loaded world")
