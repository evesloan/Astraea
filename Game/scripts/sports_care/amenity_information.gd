extends Node3D
## Package-local receiving candidate. Uses the existing player and focus hint.
## This reads authored information; it does not implement cleaning or inventory.
var candidate_id := ""
var prompt := ""
var information := ""
var expanded := false

func configure(visual: MeshInstance3D, spec: Dictionary) -> bool:
	if spec.get("action", "") != "read_information" or not is_instance_valid(visual):
		return false
	var focus: Array = spec.get("focus_world_m", [])
	var dimensions: Array = spec.get("target_size_m", [])
	if focus.size() != 3 or dimensions.size() != 3:
		return false
	for value in focus + dimensions:
		if not (value is float or value is int) or not is_finite(float(value)):
			return false
	var size := Vector3(float(dimensions[0]), float(dimensions[1]), float(dimensions[2]))
	if size.x <= 0 or size.y <= 0 or size.z <= 0 or size.length() > 1.2:
		return false
	var proposed_information := str(spec.get("information", ""))
	var proposed_prompt := str(spec.get("label", ""))
	var proposed_id := str(spec.get("id", ""))
	if proposed_id.is_empty() or proposed_prompt.is_empty() or proposed_information.is_empty() or proposed_information.length() > 160:
		return false
	var point := Vector3(float(focus[0]), float(focus[1]), float(focus[2]))
	if not visual.get_aabb().grow(0.06).has_point(visual.to_local(point)):
		return false
	var visible_world_bounds: AABB = visual.global_transform * visual.get_aabb()
	for x in [-1, 1]:
		for y in [-1, 1]:
			for z in [-1, 1]:
				var corner := point + Vector3(x, y, z) * size * 0.5
				if not visible_world_bounds.grow(0.06).has_point(corner):
					return false
	candidate_id = proposed_id
	prompt = proposed_prompt
	information = proposed_information
	global_position = point
	var target := Area3D.new()
	target.name = "AuthoredInformationTarget"
	target.collision_layer = 2
	target.collision_mask = 0
	target.monitoring = false
	target.monitorable = false
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	target.add_child(collider)
	add_child(target)
	return true

func get_interaction_label() -> String:
	if not expanded:
		return "E · " + prompt
	# The existing 16px focus hint has no width constraint. Keep authored text
	# within ordinary viewport width without modifying the shared presentation.
	var lines: Array[String] = []
	var current := ""
	for word in information.split(" ", false):
		if not current.is_empty() and current.length() + word.length() + 1 > 72:
			lines.append(current)
			current = word
		else:
			current += (" " if not current.is_empty() else "") + word
	if not current.is_empty(): lines.append(current)
	return "\n".join(lines) + "\nE · Close"

func interact(_actor: CharacterBody3D) -> void:
	expanded = not expanded

