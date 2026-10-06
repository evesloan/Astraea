extends Node3D
# Precise source-marked control using the existing player RMB/E first-hit dispatcher.
var gate: Node3D
var source_marker: StringName
func configure(controller: Node3D, marker: Node3D) -> void:
	assert(controller != null and marker != null and is_inside_tree())
	gate = controller
	source_marker = StringName(marker.name)
	global_transform = marker.global_transform
	var area := Area3D.new()
	area.name = "SourceCellGateTarget"
	area.collision_layer = 2
	area.collision_mask = 0
	area.monitoring = false
	area.monitorable = false
	var contact := CollisionShape3D.new()
	var shape := SphereShape3D.new()
	shape.radius = .026
	contact.shape = shape
	area.add_child(contact)
	add_child(area)
func get_interaction_label() -> String:
	return gate.get_interaction_label()
func interact(actor: CharacterBody3D) -> void:
	gate.interact(actor)
