extends "res://scripts/group5_retail_slider.gd"
# Saved-node successor: inherit original interaction/obstruction/physics behavior,
# but bind already-authored panels instead of generating duplicate geometry.
# Configuration and physical IDs are saved metadata on this authored door.
func _ready() -> void:
	persistent_id=StringName(str(get_meta("persistent_id")))
	width=float(get_meta("authored_width"))
	height=float(get_meta("authored_height"))
	assert(not persistent_id.is_empty())
	panels.clear()
	displacement.clear()
	for side in ["L","R"]:
		for index in range(2):
			var body:AnimatableBody3D=get_node("MovingPanel_"+side+str(index))
			panels.append(body)
			displacement.append((-1.0 if side=="L" else 1.0)*((width/4.0+.05) if index==0 else (width/2.0+.05)))
	set_meta("save_acceptance",false)
