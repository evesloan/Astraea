extends Node3D
# Exact local room constructors use their normal model/contact path in this fixture.
func model(parent:Node3D,file:String,label:String,location:Vector3,yaw:float=0)->Node3D:
	var wrapper:=Node3D.new();wrapper.name=label;wrapper.position=location;wrapper.rotation.y=yaw
	wrapper.set_meta("catalogue_file",file);parent.add_child(wrapper)
	var visual:Node3D=(load("res://assets/models/"+file)as PackedScene).instantiate()
	wrapper.add_child(visual);_static_contacts(visual);return wrapper
func _static_contacts(node:Node)->void:
	if node is MeshInstance3D and node.mesh!=null and node.visible and not str(node.name).begins_with("ALC_VisualFloor"):
		load("res://scripts/static_contact_cache.gd").attach(node)
	for child:Node in node.get_children():
		if not child is CollisionObject3D:_static_contacts(child)
