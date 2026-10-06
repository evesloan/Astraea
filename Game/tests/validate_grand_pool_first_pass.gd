extends SceneTree
# Scratch candidate: must run against parent-integrated actual main scene.
# Exact source-mesh static contacts, supported approaches and preserved routes.
const CONTRACT := "res://data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json"
var data: Dictionary
var ship: Node3D
var built: Node3D
var original: Node3D
var floors: Node3D
var actor: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var walk_frames := 0
var start_msec := 0
var support_count := 0
var seat_count := 0
var reach_count := 0

func _initialize() -> void:
	start_msec = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec() - start_msec > 230000:
		push_error("Grand Pool first-pass focused check exceeded 230-second watchdog")
		quit(1)
	return false

func xyz(p: Array) -> Vector3:
	return Vector3(p[0],p[1],p[2])

func ray(a: Vector3, b: Vector3, exclude: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a,b,1)
	query.hit_back_faces = true
	query.exclude = exclude
	return space.intersect_ray(query)

func exclusions(item: Node3D) -> Array[RID]:
	var out: Array[RID] = [actor.get_rid()]
	for body in item.find_children("*", "CollisionObject3D", true, false): out.append(body.get_rid())
	return out

func model_for(name: String) -> Node3D:
	var item := built.get_node_or_null(NodePath(name)) as Node3D
	assert(item != null, "Missing furnishing: " + name)
	return item

func check_pins() -> void:
	for path in data.preserved_file_sha256:
		assert(FileAccess.get_sha256("res://" + str(path)) == data.preserved_file_sha256[path], "Unrelated section/floor/light data changed: " + str(path))
	for key in data.models:
		var model: Dictionary = data.models[key]
		var path := "res://assets/models/" + str(model.file)
		assert(FileAccess.get_sha256(path) == model.sha256)
		var config := ConfigFile.new()
		assert(config.load(path + ".import") == OK)
		var imported: String = config.get_value("remap", "path", "")
		assert(not imported.is_empty() and FileAccess.file_exists(imported))
		var cache := ConfigFile.new()
		assert(cache.load(imported.get_basename() + ".md5") == OK)
		assert(cache.get_value("", "source_md5", "") == FileAccess.get_md5(path), "Stale retained import: " + str(model.file))

func check_models_and_contacts() -> void:
	assert(built.get_child_count() == 51 and floors.get_child_count() == int(data.compiler_owner_count))
	assert(built.find_children("*", "Light3D", true, false).is_empty())
	for entry in data.placements:
		var item := model_for(str(entry.name))
		assert(str(item.get_meta("catalogue_file")) == str(entry.model_file))
		assert(item.global_position.distance_to(xyz(entry.position_xyz)) < .0001)
		assert(absf(item.rotation.y-float(entry.yaw_radians)) < .00001 and item.scale == Vector3.ONE)
		var lo := Vector3(INF,INF,INF)
		var hi := Vector3(-INF,-INF,-INF)
		var contact_count := 0
		for mesh in item.find_children("*", "MeshInstance3D", true, false):
			assert(mesh.mesh != null and mesh.material_override == null, "Preserve the source material/texture graph")
			var box: AABB = mesh.get_aabb()
			for index in range(8):
				var p: Vector3 = mesh.global_transform * box.get_endpoint(index)
				lo = lo.min(p)
				hi = hi.max(p)
			var contact := mesh.get_node_or_null("StaticContact")
			if str(entry.asset) in ["understory", "rosette"]:
				assert(contact == null, "Foliage remains noncolliding under the existing policy")
			else:
				assert(contact != null, "Missing physical furnishing contact: " + str(entry.name))
				for shape in contact.find_children("*", "CollisionShape3D", true, false):
					assert(shape.shape is ConcavePolygonShape3D, "Use retained exact per-mesh contacts, never a whole-object convex hull")
					assert(shape.shape.get_faces().size() > 0 and not shape.disabled)
					contact_count += 1
		assert(lo.distance_to(xyz(entry.envelope_min_xyz)) < .003 and hi.distance_to(xyz(entry.envelope_max_xyz)) < .003, "Runtime envelope differs from verified source: " + str(entry.name))
		if not str(entry.asset) in ["understory", "rosette"]: assert(contact_count > 0)
	# New static contacts must not become a new floor owner or close the void.
	assert(ray(Vector3(-31,52.6,-432),Vector3(-31,52.4,-432),[actor.get_rid()]).is_empty())

func check_supports_seats_and_reach() -> void:
	for probe in data.support_probes:
		var item := model_for(str(probe.item))
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.018,p-Vector3.UP*.018,exclusions(item))
		assert(not hit.is_empty() and absf(hit.position.y-p.y) < .003, "Missing supported actual bottom vertex: " + str(probe))
		var owner: String = probe.support
		if owner.begins_with("D0"):
			var floor := floors.get_node_or_null(NodePath(owner))
			assert(floor != null and floor.is_ancestor_of(hit.collider), "Wrong compiler owner below " + str(probe.item))
		elif built.has_node(NodePath(owner)):
			assert(model_for(owner).is_ancestor_of(hit.collider), "Wrong parent furnishing under child stock/plant")
		else:
			assert(original.get_node("GrandPoolConnectedArchitecture").is_ancestor_of(hit.collider), "Soil support must belong to original connected architecture")
		support_count += 1
	for probe in data.seat_contact_probes:
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.03,p-Vector3.UP*.03,[actor.get_rid()])
		assert(not hit.is_empty() and model_for(str(probe.item)).is_ancestor_of(hit.collider), "Missing actual seat/recline contact")
		assert(absf(hit.position.y-p.y) < .004, "Seat surface disagrees with retained evaluated source")
		seat_count += 1
	for probe in data.reach_segments:
		assert(ray(xyz(probe.from_xyz),xyz(probe.to_xyz),[actor.get_rid()]).is_empty(), "Towel mouth reach is blocked: " + str(probe.role))
		reach_count += 1
	# Preserve the source-defined rear extraction/staging volume, without moving
	# the static scenic container or claiming a laundry/controller implementation.
	for reserve in data.return_reserves:
		var lo := xyz(reserve.min_xyz)
		var hi := xyz(reserve.max_xyz)
		var query := PhysicsShapeQueryParameters3D.new()
		var box := BoxShape3D.new()
		box.size = hi-lo
		query.shape = box
		query.transform.origin = (lo+hi)*.5
		query.collision_mask = 1
		query.exclude = exclusions(model_for("used_towel_return"))
		assert(space.intersect_shape(query).is_empty(), "Other physical object blocks towel extraction/staging reserve")

func settle_at(p: Vector3) -> void:
	assert(ship.arrive_at(p+Vector3.UP*.1,0), "Normal supported arrival rejected at " + str(p))
	for frame in range(24):
		actor.velocity = Vector3(0,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,0)
		actor.move_and_slide()
		await physics_frame
	assert(absf(actor.position.y-p.y) < .08)

func walk_to(target: Vector3) -> void:
	var start := actor.position
	var reached := false
	var frame_budget := ceili(Vector2(target.x-start.x,target.z-start.z).length()/3.1*60)+240
	for frame in range(frame_budget):
		var delta := Vector3(target.x-actor.position.x,0,target.z-actor.position.z)
		if delta.length() < .075:
			reached = true
			break
		var movement := delta.normalized()*3.1
		actor.velocity = Vector3(movement.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,movement.z)
		actor.move_and_slide()
		await physics_frame
		walk_frames += 1
		assert(walk_frames < 30000)
		assert(absf(actor.position.y-target.y) < .18, "Approach left its real supported floor")
	assert(reached, "Furnishing approach stalled at %s toward %s" % [actor.position,target])

func walk_path(points: Array, reverse: bool = false) -> void:
	var sequence := points.duplicate()
	if reverse: sequence.reverse()
	for p in sequence: await walk_to(xyz(p))

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	check_pins()
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	space = ship.get_world_3d().direct_space_state
	built = ship.find_child("GrandPoolFirstPassEssentials_WIP",true,false)
	original = ship.find_child("GrandPoolOrchardSection_WIP",true,false)
	floors = ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	assert(built != null and original != null)
	check_models_and_contacts()
	check_supports_seats_and_reach()
	for path in data.approach_paths:
		await settle_at(xyz(path.points[0]))
		await walk_path(path.points)
		await walk_path(path.points,true)
	# Exact retained wet-route centreline, never moved to accommodate furniture.
	var wet: Array = [[-45.9,46.2,-458],[-45.9,46.2,-405]]
	await settle_at(xyz(wet[0]))
	await walk_path(wet)
	await walk_path(wet,true)
	# Original dry market circuit must still operate with all pool/service doors closed.
	var section: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json"))
	var market: Array = []
	for p in section.market.adopted_dry_loop_centreline_xz: market.append([p[0],52.5,p[1]])
	for door in original.find_children("GrandPoolDoor_*","Node3D",true,false): assert(door.open_fraction < .001 and not door.desired_open)
	await settle_at(xyz(market[0]))
	await walk_path(market)
	await walk_path(market,true)
	for door in original.find_children("GrandPoolDoor_*","Node3D",true,false): assert(door.open_fraction < .001 and not door.desired_open)
	check_pins()
	print("GRAND POOL FIRST PASS FURNISHING PASS: 51 pinned instances; ",support_count," supported bottom probes; ",seat_count," physical seat contacts; ",reach_count," open towel reach segments; 17 supported approach branches and unchanged wet/closed-market routes in ",walk_frames," walking frames. Loaded cart/lift/full regression and visual first-pass completion remain separate.")
	main.queue_free()
	await process_frame
	quit(0)
