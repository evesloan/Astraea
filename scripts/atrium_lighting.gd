extends RefCounted
# Actual source fixtures; no renderer switch or additional post-process stack.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "AtriumFixtureAndBearingComposition_WIP"
	parent.add_child(root)
	var stations := [Vector2(-44,-18),Vector2(-44,18),Vector2(44,-18),Vector2(44,18),Vector2(-18,-59),Vector2(18,-59),Vector2(-18,59),Vector2(18,59)]
	for definition in [[5,"H826"],[8,"H826"],[11,"H576"],[15,"H426"]]:
		var index := int(definition[0])
		var floor_y := float(ship.deck_y[index])
		var below_gap := floor_y-float(ship.deck_y[index-1])
		for station in stations:
			var column := ship.model(root,"AST-STR-001-"+definition[1]+".glb","D%02d_LanternBearing"%(index+1),Vector3(station.x,floor_y,station.y)) as Node3D
			for lens_index in [0,2]:
				var marker := column.find_child("DATUM_light_"+str(lens_index),true,false) as Node3D
				assert(marker != null)
				var light := SpotLight3D.new()
				light.name = "SourceLanternLight"
				root.add_child(light)
				light.global_position = marker.global_position
				light.rotation.x = -PI/2
				light.spot_angle = 62
				ship.apply_light_profile(light,"atrium_lantern")
				var height := marker.global_position.y-floor_y
				light.spot_range = minf(sqrt(height*height+64.0),height+below_gap-0.5)
				light.shadow_enabled = lens_index == 0
	for z in [-24.0,24.0]:
		var coffer := ship.model(root,"AST-ATR-002.glb","ArtificialDaylightCoffer",Vector3(0,106.26,z)) as Node3D
		var marker := coffer.find_child("DATUM_emitter",true,false) as Node3D
		assert(marker != null)
		var light := SpotLight3D.new()
		light.name = "RoofDaylightSource"
		root.add_child(light)
		light.global_position = marker.global_position
		light.rotation.x = -PI/2
		ship.apply_light_profile(light,"atrium_daylight")
		light.spot_angle = 60
		light.spot_attenuation = 0.35
