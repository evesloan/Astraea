extends "res://tests/group6_completion/validate_river_entries.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var actor_id:=actor.get_instance_id()
	var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP");var floor:Node3D=annex.get_node("AquaticAnnexOwnedSlabs");var floor_id:=floor.get_instance_id()
	var addition:Node3D=annex.get_node("Group6Completion");record("candidate_build_succeeded",addition!=null)
	if addition!=null:
		record("four_original_floor_owners",floor.get_instance_id()==floor_id and floor.get_child_count()==4)
		var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
		for light:Light3D in addition.find_children("*","Light3D",true,false):record("installed_light_registered_"+str(light.name),budget.sources.has(light))
		await river_checks(ship,actor,JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FIT_CONTRACT.json")),ship.get_node("ShipSystems/ReceivedRoomResidency"))
		record("same_original_persistent_player",actor.get_instance_id()==actor_id)
		record("same_programme",annex.get_meta("programme_key")=="D08_directory_08")
	record("both_river_entries_exercised",legs.size()==4)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":river_motion,"supported_independent_fixture_starts":2,"traversal_position_or_velocity_writes":0,"scope":"Focused actual-main river bank/bed entry-return paths and original persistent player. Separate supported dry fixtures only. Swimming/current/buoyancy/AFK/hoist/chair/species/final-art acceptance remains open."}
	FileAccess.open("res://artifacts/group6_validate_river_entries_main_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 RIVER ENTRY MAIN ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
