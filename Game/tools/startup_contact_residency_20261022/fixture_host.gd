extends "res://scripts/ship.gd"
func _ready() -> void:
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for datum in contract.deck_datums: deck_y.append(float(datum.floor_elevation_m))
	d09_y = deck_y[8]
	stone = surface("warm_stone", Color.WHITE)
	ivory = surface("ivory_enamel", Color.WHITE)
	metal = surface("champagne_metal", Color(.65,.68,.68))
