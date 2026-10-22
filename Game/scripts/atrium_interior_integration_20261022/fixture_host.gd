extends "res://scripts/atrium_interior_integration_20261022/ship.gd"
# Exercise the actual integration methods without constructing unrelated ship packages.
func _ready()->void:
	exact_texture_intern=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
