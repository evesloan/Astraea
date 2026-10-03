extends RefCounted
# A purposeful stopping place on the existing D06 terrace, not a new room allocation.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "D06_PortBotanicalOverlook_WIP"
	parent.add_child(root)
	var bay := ship.model(root,"AST-GAR-003.glb","AuthoredGardenOverlook",Vector3(-39,27,-27)) as Node3D
	for index in range(2):
		var plant := bay.find_child("DATUM_plant_"+str(index),true,false) as Node3D
		assert(plant != null)
		ship.model(root,"AST-BOT-002.glb" if index==0 else "AST-BOT-003.glb","ContainedPlanting_"+str(index),plant.global_position,float(index))
		var datum := bay.find_child("DATUM_light_"+str(index),true,false) as Node3D
		assert(datum != null)
		var light := SpotLight3D.new()
		light.name = "OverlookReadingSource_"+str(index)
		root.add_child(light)
		light.global_position = datum.global_position
		light.rotation.x = -PI/2
		light.spot_angle = 65
		light.spot_range = 7
		light.light_energy = .8
		light.light_color = Color(1,.94,.84)
		light.shadow_enabled = true
	# Contained rear planting makes the bay a sheltered gallery destination.
	for segment in range(7):
		for item in range(2):
			var marker := bay.find_child("DATUM_backplant_%d_%d" % [segment,item],true,false) as Node3D
			assert(marker != null)
			ship.model(root,("AST-BOT-007.glb" if item==0 else "AST-BOT-002.glb") if segment in [2,3,4] else ("AST-BOT-009.glb" if item==0 else "AST-BOT-003.glb"),"RearGarden_%d_%d" % [segment,item],marker.global_position,float(segment)*.65+item)
	for segment in [2,3,4]:
		var marker := bay.find_child("DATUM_plantlight_"+str(segment),true,false) as Node3D
		var source := SpotLight3D.new()
		root.add_child(source)
		source.name = "ContainedPlantLight_"+str(segment)
		source.global_position = marker.global_position
		source.rotation.x = PI/2
		source.spot_range = 4.8
		source.spot_angle = 66
		source.light_energy = 1.4
		source.light_color = Color(1,.95,.86)
		source.shadow_enabled = true
	ship.model(root,"AST-FUR-003_day_table.glb","OverlookSharedTable",Vector3(-39.7,27,-27.8))
