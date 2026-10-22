extends Node3D
func model(parent:Node3D,file:String,label:String,at:Vector3,yaw:float=0)->Node3D:
 var wrapper:=Node3D.new();wrapper.name=label;wrapper.position=at;wrapper.rotation.y=yaw;parent.add_child(wrapper)
 var n:Node3D=load("res://royalty790_integration_20261022/package.gd").raw("res://assets/models/"+file);wrapper.add_child(n)
 for m:MeshInstance3D in n.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(m)
 return wrapper
