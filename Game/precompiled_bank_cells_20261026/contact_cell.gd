extends StaticBody3D
@export var records:Array=[]
func _ready()->void:
 for row:Array in records:
  var id:=create_shape_owner(self)
  shape_owner_set_transform(id,row[0]);shape_owner_add_shape(id,row[1])
func _exit_tree()->void:
 for id:int in get_shape_owners():remove_shape_owner(id)
