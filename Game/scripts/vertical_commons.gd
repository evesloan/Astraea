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
	# A planted social island sits beneath the real opening; the lower canopy
	# frames existing conversation seating while upper tables support quieter use.
	var gathering:Node3D=ship.model(root,"AST-COM-002.glb","CommonsShelteredGathering",Vector3(79,84,4))
	for mesh in gathering.find_children("GATHER_floor_*","MeshInstance3D",true,false):
		var contact:=mesh.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	for i in range(2):
		var marker:=gathering.find_child("DATUM_canopy_plant_"+str(i),true,false)as Node3D
		ship.model(root,"AST-BOT-001.glb" if i==0 else "AST-BOT-007.glb","CommonsCanopyPlant_"+str(i),marker.global_position,i*.65)
	for i in range(12):
		var marker:=gathering.find_child("DATUM_underplant_"+str(i),true,false)as Node3D
		ship.model(root,"AST-BOT-002.glb","CommonsIslandUnderplant_"+str(i),marker.global_position,i*.6)
	for i in range(3):
		var marker:=gathering.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="CommonsGatheringLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_angle=65
		light.spot_range=12 if i==2 else 6
		light.light_energy=1.65 if i==2 else 1.25
		light.light_color=Color(1,.94,.84)
		light.shadow_enabled=true
	for center in [Vector3(79,84,10),Vector3(82,88.5,-10)]:
		ship.model(root,"AST-FUR-003_day_table.glb","CommonsConversationTable",center)
	ship.model(root,"AST-LIB-STUDY-01.glb","CommonsSharedReadingTable",Vector3(88,88.5,-9))
	for side in [-1,1]:
		ship.model(root,"AST-FUR-002_day_reading_chair.glb","CommonsSharedReadingChair",Vector3(88,88.5,-9+side*1.4),PI if side>0 else 0)
	# Paired practical wall lights give the enclosure readable vertical surfaces.
	for level in [84.0,88.5]:
		for side in [-1,1]:
			var lantern:Node3D=ship.model(root,"AST-LGT-001.glb","CommonsWallLantern",Vector3(79,level+1.70,side*13.105),PI if side>0 else 0)
			var marker:=lantern.find_child("DATUM_light_exit",true,false)as Node3D
			var light:=OmniLight3D.new()
			root.add_child(light)
			light.name="CommonsWallSource_%s_%s"%[level,side]
			light.global_position=marker.global_position
			light.omni_range=7.0
			light.light_color=Color(1,.95,.87)
			light.light_energy=1.1
			light.shadow_enabled=true
	# Matched walking planes; lower maintenance volume is deliberately closed.
	const stairs=preload("res://scripts/aquatic_section.gd")
	stairs._contact(root,[Vector3(64.2,84,-9.6),Vector3(66.2,84,-9.6),Vector3(66.2,86.25,-4.8),Vector3(64.2,86.25,-4.8)])
	stairs._contact(root,[Vector3(67.2,88.5,-9.6),Vector3(69.2,88.5,-9.6),Vector3(69.2,86.25,-4.8),Vector3(67.2,86.25,-4.8)])
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="CommonsPassengerLift"
	root.add_child(lift)
