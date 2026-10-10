extends "res://scripts/guest_privacy_door.gd"
# Reuse the registered privacy leaf and existing motion/obstruction controller.
func get_interaction_label() -> String:
	if obstructed:return "Clear cocoon door swing"
	return "E · Close cocoon door" if desired_open else "E · Open cocoon door"
