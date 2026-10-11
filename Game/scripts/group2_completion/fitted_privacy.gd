extends "res://scripts/guest_privacy_door.gd"
# Retain the delivered hinge, actual hardware and inherited obstruction checks.
var source_visual: Node3D
var fitting: Dictionary
var closed_hinge_pose: Transform3D

func _ready() -> void:
	assert(source_visual != null and not persistent_id.is_empty())
	open_fraction = 0.0
	desired_open = false
	var hinge_name := ""
	for name in fitting.part_names:
		if str(name).ends_with("HINGE_LEFT"):
			hinge_name = str(name)
	var hinge := source_visual.find_child(hinge_name, true, false) as Node3D
	assert(hinge != null)
	var body := AnimatableBody3D.new()
	body.name = "MovingPrivacyLeaf"
	body.sync_to_physics = false
	add_child(body)
	body.global_transform = hinge.global_transform
	closed_hinge_pose = body.transform
	hinge.reparent(body, true)
	for mesh: MeshInstance3D in hinge.find_children("*", "MeshInstance3D", true, false):
		var contact := CollisionShape3D.new()
		contact.shape = mesh.mesh.create_convex_shape()
		contact.shape.margin = .001
		contact.transform = body.global_transform.affine_inverse() * mesh.global_transform
		body.add_child(contact)
	for name in fitting.part_names:
		if "POINT_handle" in str(name):
			var control := source_visual.find_child(str(name), true, false) as Node3D
			if control != null:
				control.reparent(self, true)
			else:
				# Some exact source handle markers belong to the moving hinge.
				assert(find_child(str(name), true, false) != null)
	leaves.append(body)
	_apply_pose()
	body.sync_to_physics = true
	set_meta("source_catalogue_id", "AST-DOR-001")

func _apply_pose() -> void:
	if not leaves.is_empty():
		leaves[0].transform = closed_hinge_pose * Transform3D(Basis(Vector3.UP, open_fraction * PI / 2), Vector3.ZERO)
