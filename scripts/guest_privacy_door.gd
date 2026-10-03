extends "res://scripts/service_door.gd"
# Asset-specific fitting; shared interaction, motion and obstruction state stay
# in the existing service-door implementation. No second interaction controller.
func _ready() -> void:
	assert(not persistent_id.is_empty())
	set_meta("catalogue_file","AST-DOR-001.glb")
	var visual := (load("res://assets/models/AST-DOR-001.glb") as PackedScene).instantiate()
	add_child(visual)
	var hinge := visual.find_child("HINGE_LEFT",true,false) as Node3D
	assert(hinge != null)
	var body := AnimatableBody3D.new()
	body.name = "MovingPrivacyLeaf"
	body.sync_to_physics = false
	body.transform = global_transform.affine_inverse()*hinge.global_transform
	body.rotation.y = PI/2
	add_child(body)
	hinge.reparent(body,true)
	hinge.transform = Transform3D.IDENTITY
	for spec in [{"name":"LeafContact","size":Vector3(1.026,2.125,.05),"center":Vector3(.525,1.0875,0)},{"name":"InnerHandleContact","size":Vector3(.17,.23,.035),"center":Vector3(.925,1.1,-.060)},{"name":"OuterHandleContact","size":Vector3(.17,.23,.035),"center":Vector3(.925,1.1,.060)}]:
		var collision := CollisionShape3D.new()
		collision.name = spec.name
		var shape := BoxShape3D.new()
		shape.size = spec.size
		shape.margin = .001
		collision.shape = shape
		collision.position = spec.center
		body.add_child(collision)
	leaves.append(body)
	for mesh in visual.find_children("*","MeshInstance3D",true,false): load("res://scripts/static_contact_cache.gd").attach(mesh)
	_apply_pose()
	body.sync_to_physics = true

func get_interaction_label() -> String:
	if obstructed: return "Clear door swing"
	return "E · Close bathroom door" if desired_open else "E · Open bathroom door"

func _sweep_occupied() -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.16,2.3,1.26)
	query.shape = shape
	query.transform = global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.15,-.55))
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D: return true
	return false
