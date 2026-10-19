extends "res://tests/group6_completion/validate_occupied_float_20261019.gd"
func run()->void:
 output_name="MAIN";exercise_circuit=false
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(20):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP")
 var floats:Node3D=annex.get_node("OccupiedSourceFloats")
 record("two_source_boarding_bindings",floats.get_child_count()==2)
 record("original_annex_architecture_and_completion_retained",annex.has_node("ExactAquaticArchitecture") and annex.has_node("Group6Completion"))
 await exercise(ship,floats,actor)
