extends "res://scripts/guest_privacy_door.gd"
# Unchanged retained source mechanism; construction changing privacy only.
func _ready() -> void:
	open_fraction = 0.0
	desired_open = false
	super._ready()
func get_interaction_label() -> String:
	if obstructed: return "Clear door swing"
	return "E · Close changing door" if desired_open else "E · Open changing door"
