extends SceneTree

# Isolate selection policy from the existing physical glass/receiver ray tests.
class BudgetProbe:
	extends "res://scripts/lighting_budget.gd"
	var sampled: Array[Light3D] = []
	func _has_visible_sample(light: Light3D) -> bool:
		sampled.append(light)
		return light.get_meta("sample_visible", false)

func _initialize() -> void: call_deferred("run")

func assert_selection(budget: Node, expected: int) -> void:
	var count := 0
	for light in budget.sources:
		assert(light.visible == light.shadow_enabled, "Requested sources must not become unshadowed fillers")
		if light.visible:
			count += 1
			assert(light.get_meta("fixture_powered", true))
			assert(light.get_meta("sample_visible", false), "Hidden lights cannot fill spare slots")
			assert(light in budget.sampled, "Untested lights cannot fill spare slots")
	assert(count == expected, "Eligible fixture count differs: %d versus %d" % [count, expected])
	assert(count <= 8)
	assert(budget.sampled.size() <= 32, "Visibility work must remain independent of the source count")

func run() -> void:
	var room := Node3D.new()
	root.add_child(room)
	var player := Node3D.new()
	room.add_child(player)
	var probe := BudgetProbe.new()
	room.add_child(probe)
	probe.set_process(false)
	var fixtures: Array[SpotLight3D] = []
	for index in range(40):
		var light := SpotLight3D.new()
		room.add_child(light)
		light.position = Vector3(index + 1, 2, 0)
		light.spot_range = 1.0
		light.shadow_enabled = true
		light.set_meta("sample_visible", index in [1, 5, 7, 10, 14, 18, 21, 24])
		fixtures.append(light)
	probe.configure(room, player)
	assert_selection(probe, 8)
	assert(fixtures[24].visible, "The visible fixture just beyond the old 24-candidate window must remain eligible")
	assert(probe.sampled.size() == 25, "Sampling should stop as soon as eight visible sources are found")
	fixtures[24].set_meta("fixture_powered", false)
	probe.sampled.clear()
	probe.refresh()
	assert_selection(probe, 7)
	assert(not fixtures[24].visible and not fixtures[24].shadow_enabled)
	assert(fixtures[24] not in probe.sampled, "Powered-off fixtures must not consume visibility work")
	for light in fixtures: light.set_meta("sample_visible", false)
	# A visible source beyond the bounded window must not be admitted without a sample.
	fixtures[39].set_meta("sample_visible", true)
	probe.sampled.clear()
	probe.refresh()
	assert_selection(probe, 0)
	assert(probe.sampled.size() == 32)
	for light in fixtures: light.set_meta("sample_visible", true)
	probe.sampled.clear()
	probe.refresh()
	assert_selection(probe, 8)
	assert(probe.sampled.size() == 8)
	room.free()

	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var actor: Node3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	actor.set_physics_process(false)
	budget.set_process(false)
	var samples := [
		["commons", Vector3(89,84.1,8), "CommonsFixture_4"],
		["D17 portal", Vector3(80,102.1,18), "D17HouseSource_DATUM_light_Portal"],
		["D17 court", Vector3(88,102.1,25), "D17HouseSource_DATUM_light_Court"],
		["D17 lane", Vector3(92.4,102.1,30), "D17HouseSource_DATUM_light_Lane"],
		["D17 receiving", Vector3(101,102.1,33), "D17HouseSource_DATUM_light_Receiving"],
		["D17 view", Vector3(113,102.1,40), "D17HouseSource_DATUM_light_ViewAft"],
		["commons return", Vector3(89,84.1,8), "CommonsFixture_4"]
	]
	for sample in samples:
		actor.position = sample[1]
		for attempt in range(2):
			budget.refresh()
			var active: Array[String] = []
			for light in budget.sources:
				if not budget.requested_shadow[light.get_instance_id()]: continue
				assert(light.visible == light.shadow_enabled)
				if not light.visible: continue
				active.append(str(light.name))
				assert(light.get_meta("fixture_powered", true))
				assert(budget._has_visible_sample(light), "Every active source requires a clear sample at " + sample[0])
			assert(active.size() <= 8)
			assert(sample[2] in active, "Actual local source lost at %s: %s" % [sample[0], active])
			if sample[0].begins_with("commons"):
				assert(active.size() == 8, "Commons retains eight genuinely visible fixtures after D17 source additions")
				for name in active:
					assert(not name.begins_with("NightGardenLocalSource") and not name.begins_with("RoofDaylightSource"))
			print("LIGHT BUDGET SAMPLE: ", sample[0], " refresh ", attempt, " active ", active)
	print("LIGHT BUDGET PASS: bounded positive-visibility selection, no hidden/untested fillers, powered-off rejection, eight-source cap, recovered commons source and five D17 local fixtures across repeated refreshes and return. Existing physical glass/receiver checks and graphical review remain separate.")
	main.queue_free()
	await process_frame
	quit()
