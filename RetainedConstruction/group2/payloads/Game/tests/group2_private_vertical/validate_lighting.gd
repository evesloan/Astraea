extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var world := Node3D.new();root.add_child(world)
	var rows: Array = []
	for key in ["787","792","794","795","797"]:
		var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(world,key)
		var lift: Node3D = load("res://scripts/group2_private_vertical/package.gd").build_for_section(section,key)
		var actor := CharacterBody3D.new();world.add_child(actor)
		actor.global_position = lift.cabin.to_global(Vector3(.7,0,-1.8))
		var lights: Array[Node] = lift.find_children("*","Light3D",true,false)
		assert(lights.size() == 2)
		for light in lights:
			assert(not light.visible and light.shadow_enabled and light.spot_range == 4.0)
		var visual: Node3D = lift.cabin.get_child(0)
		for side in [-1,1]:
			var marker: Node3D = visual.find_child("DATUM_light_"+str(side),true,false)
			assert(marker != null)
			var matched := false
			for light in lights:
				if light.global_position.distance_to(marker.global_position) < .002: matched = true
			assert(matched,"Original native cabin light exit is exact")
		for frame in range(3): await physics_frame
		var manager: Node = load("res://scripts/lighting_budget.gd").new();section.add_child(manager);manager.configure(section,actor)
		var admitted := 0;var cabin_admitted := 0
		for light in manager.sources:
			if light.visible:
				admitted += 1
				if light in lights:
					cabin_admitted += 1;assert(manager._has_visible_sample(light))
		assert(admitted <= 8 and cabin_admitted > 0)
		rows.append({"source_index":int(key),"native_exits":2,"cabin_admitted":cabin_admitted,"total_admitted":admitted,"real_visibility_rays":true})
		actor.free();section.free();await physics_frame
	var file := FileAccess.open("res://artifacts/group2_private_lighting.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"suites":rows,"budget_unchanged":8,"new_native_source_lights":10,"game_photometry_accepted":false},"\t")+"\n")
	print("GROUP2 PRIVATE LIGHTING PASS ten exact native exits; initial invisibility and original eight-source admission")
	quit()
