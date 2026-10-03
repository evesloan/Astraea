extends RefCounted
# Authored lower botanical court within the pre-existing atrium base.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "D02_OffsetGardenCourt_WIP"
	parent.add_child(root)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/atrium_garden.json"))
	var garden := ship.model(root,"AST-GAR-001.glb","BasinAndSeatedIsland",Vector3(0,6,0)) as Node3D
	for name in ["CANOPY_A","CANOPY_B"]:
		var datum := garden.find_child("DATUM_"+name,true,false) as Node3D
		assert(datum != null)
		var tree := ship.model(root,"AST-BOT-011.glb",name,datum.global_position,0.0 if name=="CANOPY_A" else 1.8) as Node3D
		if name == "CANOPY_B": tree.scale = Vector3.ONE*0.82
		for part in tree.find_children("TREE_bark*","MeshInstance3D",true,false): part.create_trimesh_collision()
	# Deliberate lower/middle planting layers within the planted island, away from routes.
	var cluster_angles := [-2.7,-2.1,-1.2,-0.2,0.5,1.4,2.2]
	var cluster_index := 0
	for angle in cluster_angles:
		var center := Vector3(-3+4.8*cos(angle),6.46,-4+11.5*sin(angle))
		ship.model(root,"AST-BOT-007.glb","FanCrown_"+str(cluster_index),center,angle)
		for side in [-1,1]:
			var offset := Vector3(cos(angle+PI/2),0,sin(angle+PI/2))*float(side)*0.95
			ship.model(root,"AST-BOT-002.glb","BroadLeaf_"+str(cluster_index)+"_"+str(side),center+offset,angle+side*0.6)
			ship.model(root,"AST-BOT-009.glb","FlowerBank_"+str(cluster_index)+"_"+str(side),center+offset+Vector3(cos(angle),0,sin(angle))*0.8,angle)
		for side in [-1,0,1]:
			var offset := Vector3(cos(angle+PI/2),0,sin(angle+PI/2))*float(side)*0.65+Vector3(cos(angle),0,sin(angle))*1.25
			ship.model(root,"AST-BOT-003.glb","SpoonRosette_"+str(cluster_index)+"_"+str(side),center+offset,angle+side)
		cluster_index += 1
	for i in range(4):
		var datum := garden.find_child("DATUM_uplight_"+str(i),true,false) as Node3D
		assert(datum != null)
		var light := SpotLight3D.new()
		light.name = "PlantedIslandSourceUplight_"+str(i)
		root.add_child(light)
		light.global_position = datum.global_position
		light.rotation.x = PI/2
		light.spot_range = 22
		light.spot_angle = 48
		light.light_color = Color(1.0,0.93,0.78)
		light.light_energy = 5.0
		light.shadow_enabled = true
		light.shadow_normal_bias = 0.015
		light.shadow_bias = 0.02
	var lamp_sites: Array[Vector2] = []
	for route in data.approach_centerlines:
		var center := Vector2(route[1][0],route[1][1])
		var tangent := (Vector2(route[2][0],route[2][1])-Vector2(route[0][0],route[0][1])).normalized()
		lamp_sites.append(center+Vector2(tangent.y,-tangent.x)*2.0)
	lamp_sites.append_array([Vector2(-15,-45),Vector2(15,-45),Vector2(15,45),Vector2(-15,45),Vector2(-30,-25),Vector2(30,25)])
	for i in range(lamp_sites.size()):
		var site := lamp_sites[i]
		var lamp := ship.model(root,"AST-GAR-002.glb","PathLantern_"+str(i),Vector3(site.x,6,site.y)) as Node3D
		var datum := lamp.find_child("DATUM_light",true,false) as Node3D
		assert(datum != null)
		var light := SpotLight3D.new()
		light.name = "GardenPathSource_"+str(i)
		root.add_child(light)
		light.global_position = datum.global_position
		light.rotation.x = -PI/2
		light.spot_angle = 68
		light.spot_range = 11
		light.light_energy = 2.2
		light.light_color = Color(1,0.92,0.80)
		light.shadow_enabled = i < 4
	var water := ShaderMaterial.new()
	water.shader = load("res://shaders/garden_water.gdshader")
	for i in range(data.pools.size()):
		var boundary := PackedVector2Array()
		for p in data.pools[i]: boundary.append(Vector2(p[0],p[1]))
		var water_visual := ship.floor_mesh(root,"OrnamentalGardenPocket_"+str(i),boundary,float(data.water_y),water,false) as MeshInstance3D
		water_visual.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
