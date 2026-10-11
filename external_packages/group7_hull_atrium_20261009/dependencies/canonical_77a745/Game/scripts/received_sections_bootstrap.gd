extends Node
# Additive installation in the existing main ship. Keep its controller and all
# 303 predecessor floor records intact; reuse the same floor/contact builders.
func _ready() -> void:
	var ship := get_parent() as Node3D
	await ship.ready
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == str(definition.source_checks.baseline_structural_sha256))
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"), ship.stone, ship.ivory, definition.regions, {"staff_floor":ship.surface("staff_floor",Color.WHITE)}, "ReceivedSectionStructuralFloors")
	load("res://scripts/received_sections.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/received_sections.gd).build(ship)")
	load("res://scripts/listening_salon_candidate.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/listening_salon_candidate.gd).build(ship)")
	load("res://scripts/stillroom_candidate.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/stillroom_candidate.gd).build(ship)")
	load("res://scripts/cinema5_candidate.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/cinema5_candidate.gd).build(ship)")
	load("res://scripts/custodial_depot_candidate.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/custodial_depot_candidate.gd).build(ship)")
	load("res://scripts/equipment_depot_candidate.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/equipment_depot_candidate.gd).build(ship)")
	load("res://scripts/remaining_batch_receiving.gd").build(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/remaining_batch_receiving.gd).build(ship)")
	load("res://scripts/shopping_promenade_adoption.gd").build(ship)
	load("res://scripts/shared_crew_home.gd").build(ship)
	var occlusion: Dictionary = load("res://scripts/static_room_occlusion.gd").install(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP var occlusion: Dictionary = load(res://scripts/static_room_occlusion.gd).install(ship)")
	set_meta("static_room_occlusion",occlusion)
	var residency:Node=load("res://scripts/received_room_residency.gd").new()
	residency.name="ReceivedRoomResidency"
	ship.get_node("ShipSystems").add_child(residency)
	residency.setup(ship)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP residency.setup(ship)")
	set_meta("installation_ready", true)
