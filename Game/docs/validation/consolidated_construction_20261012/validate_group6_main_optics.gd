extends "res://tests/group6_completion/validate_optical_profile.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(25):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP");var addition:Node3D=annex.get_node("Group6Completion");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	record("Four original annex floor owners",annex.get_node("AquaticAnnexOwnedSlabs").get_child_count()==4)
	record("Fourteen retained original Omni sources",annex.find_children("*","OmniLight3D",true,false).size()==14)
	record("Original eight-source budget",budget.shadow_source_budget==8)
	await optical_checks(ship,annex,addition,actor,budget)
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"evidence":optical_evidence,"scope":"r019 exact mounted fixture/receiver/body visibility in current combined main;seven independent stationary optical fixtures;no walking,luminance,CRT,hardware or final-art acceptance"}
	FileAccess.open("res://artifacts/group6_r019_main_optics001.json",FileAccess.WRITE).store_string(JSON.stringify(result," ")+"\n")
	print("GROUP6 MAIN OPTICS ",result.status," ",checks.size()," checks");quit(0 if errors.is_empty()else 1)
