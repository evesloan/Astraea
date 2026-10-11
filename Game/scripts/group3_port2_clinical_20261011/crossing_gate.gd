extends "res://scripts/service_door.gd"
# Only routes existing interaction to the scoped crossing supervisor.
# Existing source fitting, leaf contacts, motion and obstruction guard are inherited.
var supervisor:Node
var flow_axis:String
func interact(_actor:CharacterBody3D)->void:
 supervisor.request_axis("closed"if supervisor.selected_axis==flow_axis else flow_axis)
func get_interaction_label()->String:
 if not supervisor.blocked_reason.is_empty():return supervisor.blocked_reason
 return "E · Close clinical crossing"if supervisor.selected_axis==flow_axis else "E · Request "+("clean passage"if flow_axis=="clean"else"sealed return passage")
