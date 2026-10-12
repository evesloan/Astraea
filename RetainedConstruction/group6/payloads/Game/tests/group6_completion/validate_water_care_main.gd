extends "res://tests/group6_completion/validate_water_care.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var actor_id:=actor.get_instance_id()
	var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP");var floor:Node3D=annex.get_node("AquaticAnnexOwnedSlabs");var floor_id:=floor.get_instance_id();var old_lights:Array=annex.find_children("*","OmniLight3D",true,false)
	var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,ship)
	record("candidate_build_succeeded",addition!=null)
	if addition!=null:
		record("four_original_floor_owners",floor.get_instance_id()==floor_id and floor.get_child_count()==4)
		record("same_programme",annex.get_meta("programme_key")=="D08_directory_08")
		for light in old_lights:record("old_light_retained_"+str(light.name),is_instance_valid(light))
		var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
		for light:Light3D in addition.find_children("*","Light3D",true,false):
			budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
		actor.global_position=Vector3(93.7,45.48,210.6);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
		for i in range(20):await physics_frame
		await care_checks(ship,addition,actor)
		record("same_original_persistent_player",actor.get_instance_id()==actor_id)
	record("all_traversal_cases_exercised",legs.size()==18)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":care_motion,"supported_fixture_starts":1,"traversal_position_or_velocity_writes":0,"scope":"Focused actual-main water-care construction/door/mechanical isolator and retained stock/refreshment access. Original player and controls. No outside X100 route, cascade, pumping/filter/flow/pressure/temperature, permission/save, species/chair or final-art acceptance."}
	FileAccess.open("res://docs/group6_completion/WATER_CARE_MAIN002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 WATER CARE MAIN ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
