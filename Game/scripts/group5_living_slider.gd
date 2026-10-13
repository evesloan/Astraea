extends "res://scripts/group5_retail_slider.gd"
# Source-specific plane pitch;the narrow service aperture stacks all leaves left.
var mode:="public"
func _ready()->void:
	super()
	var depths:Array=[0,-.12,0,-.12] if mode=="public" else [0,-.12,-.36,-.24]
	if mode=="service_left":displacement.assign([-.55,-1.05,-2.05,-1.55])
	for i in range(panels.size()):
		for child in panels[i].get_children():
			if child is CollisionShape3D:child.position.z=depths[i]
	_apply_pose()
func _occupied()->bool:
	if not is_inside_tree():return false
	var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new()
	if mode=="public":
		box.size=Vector3(width*1.5+.2,height+.1,.5)
		query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,height/2+.025,-.06))
	else:
		box.size=Vector3(2.75,height+.1,.6)
		query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(-.275,height/2+.025,-.18))
	query.shape=box
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,64)
	if hits.size()==64:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
