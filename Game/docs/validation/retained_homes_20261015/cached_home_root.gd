extends Node3D
func _notification(what:int)->void:
 if what==NOTIFICATION_PREDELETE and has_meta("resident_visual"):
  var source:Node3D=get_meta("resident_visual")
  if is_instance_valid(source)and source.get_parent()==null:source.free()
