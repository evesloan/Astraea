extends "res://scripts/guest_entry_door.gd"
# Bind the exact delivered fitting to the retained door motion state machine.
# No duplicate visual and no alteration of source vertices, UVs or materials.
var source_visual: Node3D
var fitting: Dictionary
var visit: RefCounted
var private_threshold := true
var access_refused := false

func _ready() -> void:
	assert(source_visual != null and not persistent_id.is_empty())
	open_fraction = 0.0
	desired_open = false
	var prefix := str(fitting.part_names[0]).trim_suffix("LEAF_RIGHT")
	for side in ["LEFT", "RIGHT"]:
		var source := source_visual.find_child(prefix + "LEAF_" + side, true, false) as Node3D
		assert(source != null)
		var before := source.global_transform
		var body := AnimatableBody3D.new()
		body.name = "SlidingLeaf_" + side
		body.sync_to_physics = false
		add_child(body)
		body.global_transform = before
		source.reparent(body, true)
		for mesh: MeshInstance3D in source.find_children("*", "MeshInstance3D", true, false):
			var contact := CollisionShape3D.new()
			contact.shape = mesh.mesh.create_convex_shape()
			contact.shape.margin = .001
			contact.transform = body.global_transform.affine_inverse() * mesh.global_transform
			body.add_child(contact)
		leaves.append(body)
		leaf_origins.append(body.position)
	# Fixed controls must remain children of this interaction owner.
	for name in fitting.part_names:
		if "Call" in str(name) or "call_button" in str(name):
			var control := source_visual.find_child(str(name), true, false) as Node3D
			assert(control != null)
			control.reparent(self, true)
			if control is MeshInstance3D:
				load("res://scripts/static_contact_cache.gd").attach(control)
	_apply_pose()
	for leaf in leaves:
		leaf.sync_to_physics = true
	set_meta("production_private_consent_provider_available", false)
	set_meta("source_catalogue_id", "AST-DOR-002")

func interact(actor: CharacterBody3D) -> void:
	if private_threshold and not desired_open and (visit == null or not visit.allows(actor, persistent_id)):
		access_refused = true
		return
	access_refused = false
	super.interact(actor)

func get_interaction_label() -> String:
	if private_threshold and visit == null and not desired_open:
		return "Service visit required"
	return super.get_interaction_label()
