extends "res://scripts/physics_tether.gd"
@export var persistent_id:StringName
func _ready() -> void:
	set_meta("catalogue_file","AST-HSK-006.glb")
	add_child((load("res://assets/models/AST-HSK-006.glb")as PackedScene).instantiate())
	mass=.45
	center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
	center_of_mass=Vector3(0,.125,0)
	continuous_cd=true
	linear_damp=.25
	angular_damp=.3
	physics_material_override=PhysicsMaterial.new()
	physics_material_override.friction=.65
	physics_material_override.bounce=.08
	var collider:=CollisionShape3D.new()
	var shape:=CylinderShape3D.new()
	shape.radius=.057
	shape.height=.25
	collider.shape=shape
	collider.position.y=.125
	add_child(collider)
	grip_local=Vector3(0,.125,0)
	interaction_owner=self
	follow_camera=true
	hold_distance=1.35
	stiffness=45
	damping=4.5
	maximum_force=35
func get_interaction_label() -> String:
	return "E · Release cleaner bottle" if is_instance_valid(driver) else "E · Pick up cleaner bottle"
func interact(actor:CharacterBody3D) -> void:toggle_grab(actor)
