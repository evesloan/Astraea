extends "res://scripts/lift_button.gd"
# Same existing physical button and interaction lifecycle; scoped dispatch action.
var supervisor:Node3D
var flow_axis:String
func interact(_actor:CharacterBody3D)->void:
 supervisor.request_axis("closed"if supervisor.selected_axis==flow_axis else flow_axis)
func get_interaction_label()->String:
 if not supervisor.blocked_reason.is_empty():return supervisor.blocked_reason
 return "E · Close fore transfer gates"if supervisor.selected_axis==flow_axis else "E · Request "+("clean supply passage"if flow_axis=="clean"else"sealed return passage")
