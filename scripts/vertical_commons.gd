extends RefCounted
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D13_D14_StarboardCommons_WIP"
	root.set_meta("programme_keys",["D13_directory_05","D14_directory_04"])
	parent.add_child(root)
	var visual:Node3D=(load("res://assets/models/AST-COM-001.glb")as PackedScene).instantiate()
	visual.set_meta("catalogue_file","AST-COM-001.glb")
	root.add_child(visual)
	visual.position=Vector3(63,84,0)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh in visual.find_children("*","MeshInstance3D",true,false):
		if "glass" in mesh.name:mesh.material_override=glass
		if not mesh.name.begins_with("SC_step_"):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for i in range(8):
		var marker:=visual.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="CommonsFixture_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.light_color=Color(1,.95,.86)
		light.light_energy=1.7
		light.spot_angle=70
		light.spot_range=11
		light.shadow_enabled=true
	# Matched walking planes; lower maintenance volume is deliberately closed.
	const stairs=preload("res://scripts/aquatic_section.gd")
	stairs._contact(root,[Vector3(64.2,84,-9.6),Vector3(66.2,84,-9.6),Vector3(66.2,86.25,-4.8),Vector3(64.2,86.25,-4.8)])
	stairs._contact(root,[Vector3(67.2,88.5,-9.6),Vector3(69.2,88.5,-9.6),Vector3(69.2,86.25,-4.8),Vector3(67.2,86.25,-4.8)])
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="CommonsPassengerLift"
	root.add_child(lift)
