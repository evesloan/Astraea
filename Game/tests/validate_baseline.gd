extends SceneTree

func _initialize() -> void:
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	assert(contract.binding_scale.decks == 18)
	assert(contract.binding_scale.guest_units == 1000)
	assert(contract.binding_scale.passenger_admission_hard_cap == 2000)
	assert(contract.binding_scale.crew_total_including_player == 400)
	assert(contract.deck_datums.size() == 18)
	var expected := [0.0, 6.0, 12.0, 16.5, 21.0, 27.0, 35.5, 44.0, 52.5, 61.0, 69.5, 78.0, 84.0, 88.5, 93.0, 97.5, 102.0, 106.5]
	for i in range(18):
		assert(is_equal_approx(float(contract.deck_datums[i].floor_elevation_m), expected[i]))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://docs/INITIAL_ASSET_PROVENANCE.json"))
	var count := 0
	for item in manifest.runtime_inputs:
		var path: String = "res://assets/models/" + str(item.import_file).get_file()
		var packed := load(path) as PackedScene
		assert(packed != null, path)
		var instance := packed.instantiate()
		assert(instance is Node3D, path)
		instance.free()
		count += 1
	assert(count == 8)
	var main := load("res://scenes/ship.tscn") as PackedScene
	assert(main != null)
	print("BASELINE PASS: 18 canonical deck datums; owner capacity invariants; 8 production GLBs instantiated; main scene parsed. No visual or gameplay acceptance claimed.")
	quit(0)
