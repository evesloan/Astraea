extends "res://scripts/service_door.gd"
# Preserve native doors and inside egress. No external admission without owner permission.
var can_enter:Callable
var authorization_denied:=false
func interact(actor:CharacterBody3D)->void:
 if not desired_open and to_local(actor.global_position).z<=.25:
  if not can_enter.is_valid()or not can_enter.call(actor):
   authorization_denied=true;return
 authorization_denied=false;super.interact(actor)
func get_interaction_label()->String:
 if authorization_denied:return "Private entry authorization required"
 return super.get_interaction_label()
