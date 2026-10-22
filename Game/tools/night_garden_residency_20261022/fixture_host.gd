extends Node3D
var private_detail_residency:Node
func register_private_interior(home:Node3D,file:String)->Node3D:
 return private_detail_residency.register_room(home,file)
