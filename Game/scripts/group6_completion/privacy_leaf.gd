extends "res://scripts/service_door.gd"
# Exact retained leaf on the existing interaction/motion state machine.
var source_meshes:Array[MeshInstance3D]=[]
var fitting:Dictionary
var fixed_controls:Array[Node]=[]
func _ready()->void:
	assert(source_meshes.size()==2 and not persistent_id.is_empty())
	for i in range(2):
		var spec:Dictionary=fitting.leaves[i];var source_mesh:MeshInstance3D=source_meshes[i]
		var body:=AnimatableBody3D.new();body.name="SourceDerivedPrivacyLeaf_"+str(i);body.sync_to_physics=false;add_child(body)
		body.global_position=Vector3(spec.pivot[0],spec.pivot[1],spec.pivot[2])
		var contact:=source_mesh.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
		source_mesh.reparent(body,true)
		var collision:=CollisionShape3D.new();var shape:=BoxShape3D.new()
		shape.size=Vector3(.12,2.34,1.1);shape.margin=.001;collision.shape=shape
		collision.position=Vector3(spec.contact_center[0],spec.contact_center[1],spec.contact_center[2]);body.add_child(collision);leaves.append(body)
	for control in fixed_controls:control.reparent(self,true)
	_apply_pose()
	for body in leaves:body.sync_to_physics=true
func _apply_pose()->void:
	if leaves.is_empty():return
	for i in range(leaves.size()):leaves[i].rotation.y=open_fraction*float(fitting.leaves[i].open_radians)
func _sweep_occupied()->bool:
	var query:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new()
	shape.size=Vector3(1.25,2.5,2.45);shape.margin=.001
	query.shape=shape
	query.transform=Transform3D(Basis.IDENTITY,Vector3(60.65,46.7,float(fitting.center_z)))
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,128)
	if hits.size()==128:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
func get_interaction_label()->String:
	if obstructed:return "Clear rinse door swing"
	return "E · Close rinse privacy door" if desired_open else "E · Open rinse privacy door"
