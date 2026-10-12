extends Node3D
# Four source-backed surface panels keep the narrow rear corner clear.
# Uses the existing player's RMB/E interaction dispatch; no new input/controller.
var persistent_id:StringName
var width:=2.2
var height:=3.0
var model_path:="res://assets/models/group5/retail_service_slider_r001.glb"
var panels:Array[AnimatableBody3D]=[]
var displacement:Array[float]=[]
var fraction:=0.0
var desired_open:=false
var obstructed:=false
var controls:Array=[]
func _ready()->void:
	assert(not persistent_id.is_empty())
	var visual:Node3D=(load(model_path) as PackedScene).instantiate()
	add_child(visual)
	for side in ["L","R"]:
		for index in range(2):
			var source:Node3D=visual.find_child("Panel_"+side+str(index),true,false)
			assert(source!=null)
			var body:=AnimatableBody3D.new()
			body.name="MovingPanel_"+side+str(index)
			body.sync_to_physics=false
			add_child(body)
			source.reparent(body,true)
			var shape:=BoxShape3D.new()
			shape.size=Vector3(width/4.0,height-.05,.044)
			shape.margin=.001
			var collision:=CollisionShape3D.new()
			collision.shape=shape
			var center:float=(-3.0 if index==0 else -1.0)*width/8.0*(1.0 if side=="L" else -1.0)
			collision.position=Vector3(center,height/2.0,-.06*index)
			body.add_child(collision)
			panels.append(body)
			displacement.append((-1.0 if side=="L" else 1.0)*((width/4.0+.05) if index==0 else (width/2.0+.05)))
			# The controller supplies poses inside physics_process, rather than an
			# AnimationPlayer. Keep this direct physics update in the same tick.
			body.sync_to_physics=false
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		# Only the original fixed track receives immutable contact.
		if str(mesh.name).begins_with("track_"):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for spec in controls:
		var pod:Node3D=(load("res://assets/models/group5/retail_door_control_r001.glb") as PackedScene).instantiate()
		pod.name=str(spec.id)
		pod.position=Vector3(spec.local_xyz[0],spec.local_xyz[1],spec.local_xyz[2])
		pod.rotation.y=float(spec.rotation_y)
		add_child(pod)
		for mesh:MeshInstance3D in pod.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	set_meta("persistent_id",persistent_id)
	set_meta("save_acceptance",false)
func get_interaction_label()->String:
	if obstructed:return "Clear doorway"
	return "E · Close retail doors" if desired_open else "E · Open retail doors"
func interact(_actor:CharacterBody3D)->void:
	if _occupied():
		obstructed=true
		return
	obstructed=false
	desired_open=not desired_open
func _physics_process(delta:float)->void:
	var target:float=1.0 if desired_open else 0.0
	if is_equal_approx(fraction,target):
		if fraction!=target:
			fraction=target
			_apply_pose()
		return
	if _occupied():
		obstructed=true
		return
	obstructed=false
	fraction=move_toward(fraction,target,delta*.8)
	_apply_pose()
func _apply_pose()->void:
	for index in range(panels.size()):panels[index].position.x=displacement[index]*fraction
func _occupied()->bool:
	if not is_inside_tree():return false
	var box:=BoxShape3D.new()
	box.size=Vector3(width*1.5+.2,height+.10,.40)
	var query:=PhysicsShapeQueryParameters3D.new()
	query.shape=box
	query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,height/2.0,-.04))
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,64)
	if hits.size()>=64:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
