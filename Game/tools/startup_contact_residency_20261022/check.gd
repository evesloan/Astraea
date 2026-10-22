extends SceneTree
var receipt: Dictionary = {"scope":"bounded original Tidal package; not full startup acceptance", "checks":[]}
var host: Node3D
func _initialize() -> void: call_deferred("run")
func check(value: bool, label: String) -> void:
	receipt.checks.append({"pass":value,"label":label})
	assert(value, label)
func signature(root_node: Node) -> Dictionary:
	var result := {}
	for mesh: MeshInstance3D in root_node.find_children("*", "MeshInstance3D", true, false):
		result[str(mesh.get_instance_id())] = [mesh.mesh.get_instance_id() if mesh.mesh else 0, mesh.global_transform, mesh.visible, mesh.material_override]
	return result
func run() -> void:
	paused = true
	host = load("res://tools/startup_contact_residency_20261022/fixture_host.gd").new()
	host.name = "Ship"
	var space := Node3D.new(); space.name = "ShipSpace"; host.add_child(space)
	var districts := Node3D.new(); districts.name = "Districts"; space.add_child(districts)
	var actors := Node3D.new(); actors.name = "PersistentActors"; space.add_child(actors)
	var player: CharacterBody3D = load("res://scripts/player.gd").new()
	player.name = "Player"; player.position = Vector3(63,52.6,-20.5); actors.add_child(player)
	var systems := Node.new(); systems.name = "ShipSystems"; host.add_child(systems)
	var budget: Node = load("res://scripts/lighting_budget.gd").new()
	budget.name = "LocalShadowSourceBudget"; systems.add_child(budget)
	root.add_child(host)
	load("res://scripts/lower_staff_network.gd").build(districts,host)
	var before := OS.get_static_memory_usage()
	var house: Node3D = load("res://scripts/tidal_garden_adoption.gd").build(host)
	receipt.tidal_static_increment_bytes = OS.get_static_memory_usage() - before
	check(house.get_meta("installed_guest_units") == 131, "Original 131-unit adoption completed")
	check(host.find_child("ForwardStaffUpperInterfaces",true,false).get_meta("upper_operation_enabled"), "Original service reconciliation completed")
	await process_frame # Original builders defer cleanup of their temporary source holders.
	var meshes := signature(host)
	var nodes_before := get_node_count()
	var manager: Node = load("res://scripts/startup_contact_residency_20261022/manager.gd").new()
	systems.add_child(manager); manager.setup(host); manager.set_physics_process(false)
	manager.adopt(house)
	manager.adopt(districts.get_node("SpecialtyHomeCandidates"))
	check(manager.entries.size() > 0, "Eligible immutable exact contacts found")
	receipt.before_release_static_bytes = OS.get_static_memory_usage()
	manager.refresh()
	await process_frame
	receipt.after_release_static_bytes = OS.get_static_memory_usage()
	receipt.released_static_bytes = receipt.before_release_static_bytes - receipt.after_release_static_bytes
	receipt.distant = manager.statistics()
	check(signature(host) == meshes, "Every mesh instance, resource, transform, visibility and override retained")
	check(get_node_count() == nodes_before + 1, "All original nodes retained")
	var sampled := 0
	for entry in manager.entries:
		var collider: CollisionShape3D = entry.collider.get_ref()
		if collider.shape != null: continue
		manager.prepare_position(entry.bounds.get_center())
		check(collider.shape != null and manager._digest(collider.shape.get_faces()) == entry.sha256, "Arrival restores exact triangles " + str(sampled))
		sampled += 1
		if sampled == 3: break
	check(sampled == 3, "Three separated arrival witnesses exercised")
	var sample: Dictionary = manager.entries[0]
	var rigid := RigidBody3D.new(); rigid.freeze = true; actors.add_child(rigid); rigid.global_position = sample.bounds.get_center()
	manager.refresh()
	check(sample.collider.get_ref().shape != null, "Persistent rigid actor retains nearby contacts")
	rigid.free()
	manager.refresh()
	check(signature(host) == meshes, "Residency transitions preserve all visual architecture")
	player.global_position = Vector3(-44,93.03,-490)
	manager.prepare_position(player.global_position)
	manager.refresh()
	player.process_mode = Node.PROCESS_MODE_ALWAYS
	manager.process_mode = Node.PROCESS_MODE_ALWAYS
	manager.set_physics_process(true)
	for frame in range(12): await physics_frame
	check(player.is_on_floor() and absf(player.global_position.y-93)<.08, "D15 original controller arrives on retained source floor")
	var key := InputEventKey.new(); key.physical_keycode = KEY_W; key.pressed = true; Input.parse_input_event(key)
	var start := player.global_position
	for frame in range(80): await physics_frame
	key = InputEventKey.new(); key.physical_keycode = KEY_W; key.pressed = false; Input.parse_input_event(key)
	for frame in range(12): await physics_frame
	check(player.global_position.z < start.z-3.0 and player.is_on_floor() and absf(player.global_position.y-93)<.08, "Continuous D15 service-floor walk with original controller")
	receipt.controller_route = {"start":str(start),"end":str(player.global_position),"floor_y":93}
	receipt.final = manager.statistics()
	receipt.full_startup_accepted = false
	var out := FileAccess.open("res://docs/validation/startup_contact_residency_20261022/CHECK_attempt003.json",FileAccess.WRITE)
	out.store_string(JSON.stringify(receipt,"\t")); out.close()
	print("TIDAL_CONTACT_RESULT ", JSON.stringify({"checks":receipt.checks.size(),"released_static_bytes":receipt.released_static_bytes,"stats":receipt.final}))
	var passed := true
	for result in receipt.checks: passed = passed and result.pass
	quit(0 if passed else 1)
