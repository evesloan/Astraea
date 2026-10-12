extends "res://scripts/group6_completion/valve_control.gd"
# Same mechanical control/input contract; console wheels turn about their Z axis.
func _apply_pose()->void:
	if body==null:return
	body.transform=Transform3D(Basis(Vector3.BACK,open_fraction*float(fitting.travel_radians)),local_pivot)
