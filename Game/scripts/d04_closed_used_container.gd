extends "res://scripts/physics_tether.gd"
# Physical handled/closed fitting only; no invented contents, processing or save.
var authored_visual:Node3D
var authored_prefix:String
var persistent_id:StringName
func _ready()->void:
	assert(authored_visual!=null and not persistent_id.is_empty())
	mass=.8;continuous_cd=true;linear_damp=.25;angular_damp=.3;center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM;center_of_mass=Vector3(0,.35,0);contact_monitor=true;max_contacts_reported=16
	for mesh:MeshInstance3D in authored_visual.find_children(authored_prefix+"*","MeshInstance3D",true,false):
		for old in mesh.get_children():
			if old is StaticBody3D:old.free()
		var col:=CollisionShape3D.new();col.shape=mesh.mesh.create_convex_shape();col.shape.margin=.001;col.transform=global_transform.affine_inverse()*mesh.global_transform;add_child(col);mesh.reparent(self,true)
	grip_local=Vector3(0,.6,0);interaction_owner=self;follow_camera=true;hold_distance=1.35;stiffness=80;damping=10;maximum_force=80
func get_interaction_label()->String:return "E · Release closed used-item container" if is_instance_valid(driver) else "E · Carry closed used-item container"
func interact(actor:CharacterBody3D)->void:toggle_grab(actor)
