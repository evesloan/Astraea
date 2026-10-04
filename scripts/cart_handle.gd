extends Node3D
var cart:RigidBody3D
func _ready() -> void:add_to_group("cart_handles")
func get_interaction_label() -> String:
	return "E · Release cart handle" if is_instance_valid(cart.driver) else "E · Take cart handle"
func interact(actor:CharacterBody3D) -> void:cart.toggle_grab(actor)
