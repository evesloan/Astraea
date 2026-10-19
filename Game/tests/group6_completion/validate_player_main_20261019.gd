extends "res://tests/group6_completion/validate_player_20261019.gd"
func run()->void:
	output_name="MAIN"
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	active_residency=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var rooms:Array=[]
	for entry in active_residency.entries:
		if str(entry.room.name) in ["D08_directory_02","D08_directory_03"]:rooms.append(entry.room)
	record("two_installed_thermal_rooms",rooms.size()==2)
	await exercise(ship,rooms,actor)
