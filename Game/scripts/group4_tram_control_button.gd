extends Node3D
var controller:Node3D
var action:String
var station:String
func get_interaction_label()->String:return controller.control_label(action,station)
func interact(actor:CharacterBody3D)->void:controller.request_control(action,station,actor)
