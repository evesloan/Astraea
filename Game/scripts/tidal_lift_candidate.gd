extends RefCounted
# Explicit test-only successor; not installed by the default scene.
static func build(ship: Node3D) -> Node3D:
	var house: Node3D = load("res://scripts/tidal_garden_receiving.gd").build(ship,"res://data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json")
	var lift: Node3D = load("res://scripts/commons_lift.gd").new()
	lift.name = "TidalGardenPassengerLiftCandidate"
	lift.position = Vector3(-74.5,0,-377.90)
	lift.rotation.y = PI/2
	lift.gate_origin_xz = Vector2.ZERO
	lift.floor_heights.assign([84.0,88.5,93.0,97.5,102.0])
	lift.deck_numbers.assign([13,14,15,16,17])
	lift.identity_prefix = "tidal_garden"
	lift.persistent_id = &"tidal_garden_lift_001"
	lift.district_label = "Tidal Garden"
	lift.cabin_file = "AST-CIR-003_five_stop.glb"
	house.add_child(lift)
	return lift
