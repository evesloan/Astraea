extends "res://scripts/service_door.gd"
# Sliding fitting of the existing door state machine. Pockets remain hollow.
var leaf_origins: Array[Vector3] = []
var visual_file:="AST-DOR-002.glb"
var leaf_width:=.78
var leaf_travel:=.84
var enclosure_width:=3.48
var door_description:="suite door"
func _ready() -> void:
	assert(not persistent_id.is_empty())
	var fittings:Dictionary={"AST-DOR-002.glb":[.78,.84,3.48],"AST-DOR-002_wide.glb":[1.18,1.24,5.16]}
	assert(fittings.has(visual_file),"Door needs an authored matching source profile")
	var expected:Array=fittings[visual_file]
	assert(is_equal_approx(leaf_width,expected[0]) and is_equal_approx(leaf_travel,expected[1]) and is_equal_approx(enclosure_width,expected[2]),"Door collision and travel must match its export")
	set_meta("catalogue_file",visual_file)
	var visual := (load("res://assets/models/"+visual_file) as PackedScene).instantiate()
	add_child(visual)
	for side in ["LEFT","RIGHT"]:
		var source := visual.find_child("LEAF_"+side,true,false) as Node3D
		assert(source!=null)
		var body := AnimatableBody3D.new()
		body.name="SlidingLeaf_"+side
		body.sync_to_physics=false
		body.transform=global_transform.affine_inverse()*source.global_transform
		add_child(body)
		source.reparent(body,true)
		source.transform=Transform3D.IDENTITY
		var contact:=CollisionShape3D.new()
		contact.name="LeafContact"
		var shape:=BoxShape3D.new()
		shape.size=Vector3(leaf_width,2.45,.060)
		shape.margin=.001
		contact.shape=shape
		contact.position=Vector3(0,1.26,0)
		body.add_child(contact)
		if side=="LEFT":
			var seal_contact:=CollisionShape3D.new()
			seal_contact.name="MeetingSealContact"
			var seal:=BoxShape3D.new()
			seal.size=Vector3(.04,2.45,.015)
			seal.margin=.001
			seal_contact.shape=seal
			seal_contact.position=Vector3(leaf_width*.5+.012,1.26,.0375)
			body.add_child(seal_contact)
		leaves.append(body)
		leaf_origins.append(body.position)
	for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	_apply_pose()
	for leaf in leaves:leaf.sync_to_physics=true
func get_interaction_label() -> String:
	if obstructed:return "Clear door travel"
	return "E · Close "+door_description if desired_open else "E · Open "+door_description
func _apply_pose() -> void:
	for i in range(leaves.size()):
		var fraction:=clampf(open_fraction/.85,0,1) if i==0 else clampf((open_fraction-.15)/.85,0,1)
		leaves[i].position=leaf_origins[i]+Vector3((-1 if i==0 else 1)*leaf_travel*fraction,0,0)
func _sweep_occupied() -> bool:
	var query:=PhysicsShapeQueryParameters3D.new()
	var shape:=BoxShape3D.new()
	shape.size=Vector3(enclosure_width+.04,2.66,.32)
	query.shape=shape
	query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.33,0))
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
