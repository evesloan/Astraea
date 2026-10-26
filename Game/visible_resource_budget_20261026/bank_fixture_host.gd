extends Node3D
func _static_contacts(node:Node)->void:
 if node is MeshInstance3D and node.mesh!=null and node.visible and not node.name.begins_with("ALC_VisualFloor"):
  load("res://scripts/static_contact_cache.gd").attach(node)
 for child in node.get_children():
  if not child is StaticBody3D:_static_contacts(child)
