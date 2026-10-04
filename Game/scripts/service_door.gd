extends Node3D
@export var persistent_id: StringName
var leaves: Array[AnimatableBody3D] = []
var open_fraction := 1.0
var desired_open := true
var obstructed := false
var pose_initialized := false

func _ready() -> void:
	assert(not persistent_id.is_empty(),"Door requires a stable authored identity")
	set_meta("catalogue_file","AST-STF-008.glb")
	var visual := (load("res://assets/models/AST-STF-008.glb") as PackedScene).instantiate()
	add_child(visual)
	for side in ["LEFT","RIGHT"]:
		var hinge := visual.find_child("HINGE_"+side,true,false) as Node3D
		assert(hinge != null)
		var transform_before := hinge.global_transform
		var body := AnimatableBody3D.new()
		body.name = "MovingLeaf_"+side
		body.sync_to_physics = false
		body.transform = global_transform.affine_inverse()*transform_before
		body.rotation.y = PI/2 if side == "LEFT" else -PI/2
		add_child(body)
		hinge.reparent(body,true)
		hinge.transform = Transform3D.IDENTITY
		var collision := CollisionShape3D.new()
		collision.name = "LeafContact"
		var box := BoxShape3D.new()
		box.size = Vector3(1.13,2.535,0.07)
		box.margin = 0.001
		collision.shape = box
		collision.position = Vector3(0.575 if side == "LEFT" else -0.575,1.2925,0)
		body.add_child(collision)
		var push_contact := CollisionShape3D.new()
		push_contact.name = "PushContact"
		var push := BoxShape3D.new()
		push.size = Vector3(0.13,0.42,0.024)
		push.margin = 0.001
		push_contact.shape = push
		push_contact.position = Vector3(0.98 if side == "LEFT" else -0.98,1.19,0.054)
		body.add_child(push_contact)
		if side == "LEFT":
			var seal_contact := CollisionShape3D.new()
			seal_contact.name = "MeetingSealContact"
			var seal := BoxShape3D.new()
			seal.size = Vector3(0.04,2.53,0.03)
			seal.margin = 0.001
			seal_contact.shape = seal
			seal_contact.position = Vector3(1.15,1.2925,0.05)
			body.add_child(seal_contact)
		leaves.append(body)
	for mesh in visual.find_children("*","MeshInstance3D",true,false): load("res://scripts/static_contact_cache.gd").attach(mesh)
	_apply_pose()
	for leaf in leaves: leaf.sync_to_physics = true

func get_interaction_label() -> String:
	if obstructed: return "Clear door swing"
	return "E · Close service doors" if desired_open else "E · Open service doors"

func interact(_actor: CharacterBody3D) -> void:
	if _sweep_occupied():
		obstructed = true
		return
	obstructed = false
	desired_open = not desired_open

func _physics_process(delta: float) -> void:
	if not pose_initialized:
		_apply_pose()
		pose_initialized = true
	if obstructed and not _sweep_occupied(): obstructed = false
	var target := 1.0 if desired_open else 0.0
	if not is_equal_approx(open_fraction,target):
		if _sweep_occupied():
			obstructed = true
			return
		obstructed = false
		open_fraction = move_toward(open_fraction,target,delta*0.85)
		_apply_pose()

func _apply_pose() -> void:
	for index in range(leaves.size()):
		# Meeting seal opens first and closes last, like a coordinated real pair.
		var fraction := clampf(open_fraction/0.85,0.0,1.0) if index == 0 else clampf((open_fraction-0.15)/0.85,0.0,1.0)
		leaves[index].rotation.y = fraction*PI/2*(1.0 if index == 0 else -1.0)

func _sweep_occupied() -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(2.5,2.65,1.55)
	query.shape = box
	query.transform = global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.325,-0.65))
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D: return true
	return false
