extends Node3D
# Programme-owned garden service sashes; no habitat atmosphere or stock simulation.
var leaves:Array[AnimatableBody3D]=[]
var specs:Array=[]
var desired_open:=false
var open_fraction:=0.0
var obstructed:=false
func get_interaction_label()->String:
	if obstructed:return "Clear garden service swing"
	return "E · Close garden service sashes" if desired_open else "E · Open garden service sashes"
func interact(_actor:CharacterBody3D)->void:
	if occupied():obstructed=true;return
	obstructed=false;desired_open=not desired_open
func occupied()->bool:
	var space:=get_world_3d().direct_space_state
	for s in specs:
		var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(1.25,3.05,2.7)
		q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(s.pivot[0],18.65,-358.6))
		for h in space.intersect_shape(q,64):
			if h.collider is CharacterBody3D or h.collider is RigidBody3D:return true
	return false
func _physics_process(delta:float)->void:
	var target:=1.0 if desired_open else 0.0
	if not is_equal_approx(open_fraction,target):
		if occupied():obstructed=true
		else:
			obstructed=false;open_fraction=move_toward(open_fraction,target,delta*.75)
	# Supply the complete authored hinge pose during physics synchronization.
	# Updating rotation alone can let a newly created animatable body's initial
	# server transform restore an identity origin on its first moving frame.
	for j in range(leaves.size()):
		var s:Dictionary=specs[j]
		leaves[j].transform=Transform3D(Basis(Vector3.RIGHT,deg_to_rad(60)*open_fraction),Vector3(s.pivot[0],s.pivot[1],s.pivot[2]))
