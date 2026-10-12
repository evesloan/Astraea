extends "res://scripts/service_door.gd"
# Asset fitting only: use unchanged shared focus/motion/stagger/occupied-state backend.
var native_architecture:Node3D
var binding:Dictionary
var hinge_nodes:Array[Node3D]=[]
var original_open_poses:Dictionary={}
var bound_meshes:Array[MeshInstance3D]=[]
func _ready()->void:
	assert(not persistent_id.is_empty()and native_architecture!=null)
	set_meta("source_geometry_role","exact retained clinical privacy leaves with new fitted motion")
	for side in ["left","right"]:
		var pivot:=Node3D.new();pivot.name="SourceHinge_"+side;add_child(pivot)
		pivot.position=Vector3(-1.87 if side=="left"else 1.87,0,-.261);pivot.rotation.y=PI/2 if side=="left"else -PI/2;hinge_nodes.append(pivot)
		for source_name in binding.members[side]:
			var mesh:MeshInstance3D=native_architecture.find_child(str(source_name),true,false);assert(mesh!=null and mesh.mesh!=null)
			var before:=mesh.global_transform;original_open_poses[str(source_name)]=before
			var old:StaticBody3D=mesh.get_node("StaticContact");var old_shape:CollisionShape3D=old.get_child(0)
			assert(old_shape.shape is ConcavePolygonShape3D and not old_shape.disabled and old.collision_layer==1)
			var shape:Shape3D=old_shape.shape;var old_body_pose:=old.transform;var shape_pose:=old_shape.transform
			old.free();mesh.reparent(pivot,true)
			var body:=AnimatableBody3D.new();body.name="StaticContact";body.sync_to_physics=false;mesh.add_child(body);body.transform=old_body_pose
			var contact:=CollisionShape3D.new();contact.name="NativeTriangleContact";contact.shape=shape;contact.transform=shape_pose;body.add_child(contact) # Code-driven parent motion: keep sync_to_physics=false.
			mesh.set_meta("source_open_static",false);mesh.set_meta("operation_enabled",true);mesh.set_meta("original_source_open_static",true);mesh.set_meta("group8_privacy_driver",persistent_id)
			assert(mesh.global_transform.is_equal_approx(before),"Initial exact native source-open pose must survive")
			bound_meshes.append(mesh)
	assert(bound_meshes.size()==10 and hinge_nodes.size()==2)
	open_fraction=1.0;desired_open=true;_apply_pose()
func _apply_pose()->void:
	for index in range(hinge_nodes.size()):
		var fraction:=clampf(open_fraction/0.85,0,1)if index==0 else clampf((open_fraction-0.15)/0.85,0,1)
		hinge_nodes[index].rotation.y=fraction*PI/2*(1 if index==0 else -1)
	# Publish exact current world poses after the hinge change; these contacts are driven
	# in the inherited physics callback, without an AnimationPlayer interpolation path.
	for mesh:MeshInstance3D in bound_meshes:
		var body:AnimatableBody3D=mesh.get_node("StaticContact")
		body.global_transform=mesh.global_transform
func _sweep_occupied()->bool:
	var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(3.90,2.70,2.16);query.shape=box
	query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.35,-1.19))
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
func get_interaction_label()->String:
	if obstructed:return "Clear door swing"
	return "E · Close privacy doors"if desired_open else "E · Open privacy doors"
