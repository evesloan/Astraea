extends RefCounted
# Coordinated D15-D17 commons section. Existing D13/D14 identities stay intact.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D15_D17_StarboardHouseUpper_WIP"
	root.set_meta("programme_keys",["D15_directory_04","D16_directory_04","D17_directory_04"])
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-COM-003.glb","StarboardHouseUpperArchitecture",Vector3(63,84,0))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(part.name).to_lower():part.material_override=glass
		if str(part.name).begins_with("HC_Step_"):
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
	for level in range(3):
		for index in range(4):
			var marker:=architecture.find_child("DATUM_light_%s_%s"%[level,index],true,false)as Node3D
			assert(marker!=null,"Upper commons fixture datum missing")
			var light:=SpotLight3D.new()
			root.add_child(light)
			light.name="HouseUpperFixture_%s_%s"%[level,index]
			light.global_position=marker.global_position
			light.rotation.x=-PI/2
			light.light_color=Color(1,.95,.87)
			light.light_energy=1.15
			light.spot_angle=70
			light.spot_range=7
			light.shadow_enabled=true
	const stairs=preload("res://scripts/aquatic_section.gd")
	for base in [88.5,97.5]:
		stairs._contact(root,[Vector3(86.25,base,4.7),Vector3(88.25,base,4.7),Vector3(88.25,base+2.25,9.4),Vector3(86.25,base+2.25,9.4)])
		stairs._contact(root,[Vector3(88.65,base+4.5,5.013333),Vector3(90.65,base+4.5,5.013333),Vector3(90.65,base+2.25,9.4),Vector3(88.65,base+2.25,9.4)])
		stairs._contact(root,[Vector3(88.65,base+4.5,4.64),Vector3(90.65,base+4.5,4.64),Vector3(90.65,base+4.5,5.013333),Vector3(88.65,base+4.5,5.013333)])
	stairs._contact(root,[Vector3(64.2,93,-9.6),Vector3(66.2,93,-9.6),Vector3(66.2,95.25,-4.8),Vector3(64.2,95.25,-4.8)])
	stairs._contact(root,[Vector3(67.2,97.5,-9.28),Vector3(69.2,97.5,-9.28),Vector3(69.2,95.25,-4.8),Vector3(67.2,95.25,-4.8)])
	stairs._contact(root,[Vector3(67.2,97.5,-9.66),Vector3(69.2,97.5,-9.66),Vector3(69.2,97.5,-9.28),Vector3(67.2,97.5,-9.28)])
	# Sheltered writing edge faces the shared court, outside the south cart route.
	var reading:Node3D=ship.model(root,"AST-RES-002.glb","D15ResidentialReadingEdge",Vector3(83,93,-13),PI)
	for i in range(2):
		var anchor:=reading.find_child("DATUM_chair_"+str(i),true,false)as Node3D
		ship.model(root,"AST-FUR-002_day_reading_chair.glb","D15ReadingChair_"+str(i),anchor.global_position,PI)
		var marker:=reading.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="D15ReadingTaskLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_angle=62
		light.spot_range=3.3
		light.light_energy=.85
		light.light_color=Color(1,.95,.87)
		light.shadow_enabled=true
		var control:=Node3D.new()
		control.name="D15ReadingLightSwitch_"+str(i)
		control.set_script(load("res://scripts/fixture_switch.gd"))
		root.add_child(control)
		control.configure(reading,light,StringName("D15_directory_04_reading_light_"+str(i)),"DATUM_toggle_"+str(i),"READ_TaskLens_"+str(i))
	for i in range(5):
		var marker:=reading.find_child("DATUM_shelf_"+str(i),true,false)as Node3D
		var stock:Node3D=ship.model(root,"AST-LIB-006.glb","D15ReadingStock_"+str(i),marker.global_position)
		stock.set_meta("supported_book_group",true)
		for contact in stock.find_children("StaticContact","StaticBody3D",true,false):contact.free()
	var conversation:Node3D=ship.model(root,"AST-RES-003.glb","D16CourtConversationEdge",Vector3(67.1,97.5,9.1),PI/2)
	for part in conversation.find_children("TALK_VisualFloor*","MeshInstance3D",true,false):
		var contact:=part.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	var table_anchor:=conversation.find_child("DATUM_table",true,false)as Node3D
	ship.model(root,"AST-FUR-003_day_table.glb","D16ConversationTable",table_anchor.global_position)
	for i in range(2):
		var anchor:=conversation.find_child("DATUM_chair_"+str(i),true,false)as Node3D
		var facing:Vector3=table_anchor.global_position-anchor.global_position
		ship.model(root,"AST-FUR-002_day_reading_chair.glb","D16ConversationChair_"+str(i),anchor.global_position,atan2(facing.x,facing.z))
		var plant:=conversation.find_child("DATUM_plant_"+str(i),true,false)as Node3D
		ship.model(root,"AST-BOT-002.glb","D16ConversationPlant_"+str(i),plant.global_position,i*.6)
		var source:=conversation.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="D16ConversationLight_"+str(i)
		light.global_position=source.global_position
		light.rotation.x=-PI/2
		light.light_color=Color(1,.95,.87)
		light.light_energy=.85
		light.spot_angle=75
		light.spot_range=4
		light.shadow_enabled=true
