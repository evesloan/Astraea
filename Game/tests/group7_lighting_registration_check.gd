extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var ship := Node3D.new()
	root.add_child(ship)
	var systems := Node.new()
	systems.name = "ShipSystems"
	ship.add_child(systems)
	var budget := Node.new()
	budget.name = "LocalShadowSourceBudget"
	budget.set_script(load("res://scripts/lighting_budget.gd"))
	systems.add_child(budget)
	var actor := Node3D.new()
	ship.add_child(actor)
	var early := SpotLight3D.new()
	early.shadow_enabled = true
	ship.add_child(early)
	var module = load("res://scripts/group7_completion.gd")
	module.register_new_light(ship, early)
	assert(budget.sources.is_empty(), "Pre-configuration source must await the retained scan")
	await physics_frame
	budget.configure(ship, actor)
	assert(budget.sources.size() == 1 and budget.sources[0] == early)
	var late := SpotLight3D.new()
	late.shadow_enabled = true
	ship.add_child(late)
	module.register_new_light(ship, late)
	assert(budget.sources.size() == 2 and budget.sources[0] == early and budget.sources[1] == late)
	assert(budget.requested_shadow[late.get_instance_id()] == true)
	assert(budget.shadow_source_budget == 8)
	var report := {"status":"PASS", "early_scan_once":true, "late_append_only":true, "retained_budget":8}
	FileAccess.open("res://../external_packages/group7_completion_20261011/qa/LIGHT_REGISTRATION_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(report, "  ")+"\n")
	print(JSON.stringify(report))
	quit()
