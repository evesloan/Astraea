extends "res://tests/group6_completion/validate_thermal_targets.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var actor_id:=actor.get_instance_id()
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var floor_root:Node=ship.get_node("ShipSpace/ReceivedSectionStructuralFloors")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"))
	for spec in plan.rooms:
		residency.prepare_position(vec(spec.entries[0].dry_xyz))
		var room:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/"+str(spec.programme_key));var room_id:=room.get_instance_id()
		var floor_ids:Array=[]
		for suffix in ["_authored_floor","_spine_connection"]:floor_ids.append(floor_root.get_node(str(spec.programme_key)+suffix).get_instance_id())
		var addition:Node3D=load("res://scripts/group6_completion/thermal_entries.gd").build(room);record(str(spec.programme_key)+"_build_succeeded",addition!=null)
		if addition!=null:await thermal_checks(room,actor,spec)
		record(str(spec.programme_key)+"_same_original_room_and_id",room.get_instance_id()==room_id and room.get_meta("persistent_id")==str(spec.programme_key))
		for j in range(2):record(str(spec.programme_key)+"_same_compiler_floor_"+str(j),floor_root.get_node(str(spec.programme_key)+["_authored_floor","_spine_connection"][j]).get_instance_id()==floor_ids[j])
		if not errors.is_empty():break
	record("same_original_persistent_player",actor.get_instance_id()==actor_id)
	record("all_four_thermal_entries_exercised",legs.size()==8)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"motion":thermal_motion,"supported_independent_fixtures":4,"traversal_position_or_velocity_writes":0,"scope":"Focused actual-main four retained thermal entry paths, water visual contact correction, same received rooms/four floor owners and original persistent player. Four supported fixture starts. No swimming, temperature/gravity, operational hoist/chair/species, broad connectivity or final-art acceptance."}
	FileAccess.open("res://docs/group6_completion/THERMAL_TARGET_MAIN001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 THERMAL TARGET MAIN ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
