extends Node3D
# One authored control using the shared camera-ray interaction contract.
# Identity and current state are exposed; disk persistence is not implemented.
var persistent_id: StringName
var powered := true
var source: Light3D
var diffuser_materials: Array[StandardMaterial3D] = []

func configure(fixture: Node3D, light: Light3D, identity: StringName, toggle_datum_name:String="POINT_toggle", diffuser_mesh_prefix:String="") -> void:
	assert(not identity.is_empty())
	persistent_id = identity
	source = light
	var datum := fixture.find_child(toggle_datum_name,true,false) as Node3D
	assert(datum != null)
	global_transform = datum.global_transform
	var target := Area3D.new()
	target.name = "PhysicalToggleTarget"
	target.collision_layer = 2
	target.collision_mask = 0
	target.monitoring = false
	target.monitorable = false
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = .018
	shape.shape = sphere
	target.add_child(shape)
	add_child(target)
	for mesh in fixture.find_children("*","MeshInstance3D",true,false):
		if not diffuser_mesh_prefix.is_empty() and not str(mesh.name).begins_with(diffuser_mesh_prefix):continue
		for index in range(mesh.mesh.get_surface_count()):
			var material: Material = mesh.get_active_material(index)
			if material is StandardMaterial3D and (not diffuser_mesh_prefix.is_empty() or "opal_diffuser" in material.resource_name):
				var local := material.duplicate() as StandardMaterial3D
				mesh.set_surface_override_material(index,local)
				if diffuser_mesh_prefix.is_empty():
					local.emission = Color(1,.93,.83)
					local.emission_energy_multiplier = .18
				# Explicit built-in lenses retain their authored emission/color balance.
				diffuser_materials.append(local)
	apply_power()

func get_interaction_label() -> String:
	return "E · Switch reading light off" if powered else "E · Switch reading light on"

func interact(_actor: CharacterBody3D) -> void:
	powered = not powered
	apply_power()

func apply_power() -> void:
	if not is_instance_valid(source): return
	source.set_meta("fixture_powered",powered)
	# The shadow budget owns visibility when on. Turning off is immediate.
	if not powered:
		source.visible = false
		source.shadow_enabled = false
	for material in diffuser_materials: material.emission_enabled = powered
