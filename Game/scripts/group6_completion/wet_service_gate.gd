extends "res://scripts/service_door.gd"
# Registered staff-threshold geometry and original movement state, scoped label
# and fail-closed obstruction saturation. No permission, save or water logic.
func get_interaction_label()->String:
	if obstructed:return "Clear water-care gate swing"
	return "E · Close water-care gate" if desired_open else "E · Open water-care gate"
func _sweep_occupied()->bool:
	var query:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new()
	shape.size=Vector3(2.5,2.65,1.55);query.shape=shape
	query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.325,-.65))
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,128)
	if hits.size()==128:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
