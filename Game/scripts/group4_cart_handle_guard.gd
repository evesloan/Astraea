extends "res://scripts/cart_handle.gd"
# One scoped adapter on the same original handle instance, preserving original behavior when unrestrained.
var restraint:Node3D
func get_interaction_label()->String:
 if is_instance_valid(restraint) and restraint.phase!="unlocked":return "Cart secured in tram · release at a station"
 return super.get_interaction_label()
func interact(actor:CharacterBody3D)->void:
 if is_instance_valid(restraint) and restraint.phase!="unlocked":return
 super.interact(actor)
