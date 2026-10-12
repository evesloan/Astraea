extends Node3D
var fitting:Dictionary
var source_mesh:MeshInstance3D
var body:AnimatableBody3D
var local_pivot:Vector3
var desired_open:=false
var open_fraction:=0.0
func _ready()->void:
	assert(source_mesh!=null and not str(fitting.id).is_empty())
	set_meta("persistent_id",str(fitting.id));set_meta("water_operation_implemented",false)
	local_pivot=global_transform.affine_inverse()*Vector3(fitting.pivot_xyz[0],fitting.pivot_xyz[1],fitting.pivot_xyz[2])
	body=AnimatableBody3D.new();body.name="SourceWheelMotion";body.sync_to_physics=false
	body.position=local_pivot;add_child(body)
	source_mesh.reparent(body,true)
	load("res://scripts/static_contact_cache.gd").attach(source_mesh)
	_apply_pose()
	body.sync_to_physics=true
func get_interaction_label()->String:
	return "E · Return "+str(fitting.circuit)+" isolator" if desired_open else "E · Turn "+str(fitting.circuit)+" isolator"
func interact(_actor:CharacterBody3D)->void:
	desired_open=not desired_open
func _physics_process(delta:float)->void:
	open_fraction=move_toward(open_fraction,1.0 if desired_open else 0.0,delta*1.4)
	_apply_pose()
func _apply_pose()->void:
	body.transform=Transform3D(Basis(Vector3.RIGHT,open_fraction*float(fitting.travel_radians)),local_pivot)
