extends RefCounted
# Actual source fixtures; no renderer switch or additional post-process stack.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "AtriumFixtureAndBearingComposition_WIP"
	parent.add_child(root)
	var stations := [Vector2(-31,-18),Vector2(-31,18),Vector2(31,-18),Vector2(31,18),Vector2(-18,-46),Vector2(18,-46),Vector2(-18,46),Vector2(18,46)]
	for definition in [[5,"H826"],[8,"H826"],[11,"H576"],[15,"H426"]]:
		var index := int(definition[0])
		var floor_y := float(ship.deck_y[index])
		var below_gap := floor_y-float(ship.deck_y[index-1])
		for station_index in range(stations.size()):
			var station: Vector2 = stations[station_index]
			var yaw: float = (0.0 if station.x>0 else PI) if absf(station.x)>absf(station.y) else (PI/2 if station.y<0 else -PI/2)
			var column := ship.model(root,"AST-STR-001-"+definition[1]+".glb","D%02d_LanternBearing_%d"%[index+1,station_index],Vector3(station.x,floor_y,station.y),yaw) as Node3D
			var fan := ship.model(root,"AST-STR-002-"+definition[1]+".glb","D%02d_GalleryFan_%d"%[index+1,station_index],Vector3(station.x,floor_y,station.y),yaw) as Node3D
			fan.set_meta("upper_floor_y",float(ship.deck_y[index+1]))
			fan.set_meta("lower_floor_y",floor_y)
			for lens_index in [1,2]:
				var marker := column.find_child("DATUM_light_"+str(lens_index),true,false) as Node3D
				assert(marker != null)
				var light := SpotLight3D.new()
				light.name = "D%02d_LanternLight_%d_%d"%[index+1,station_index,lens_index]
				root.add_child(light)
				light.global_position = marker.global_position
				light.rotation.x = -PI/2
				light.spot_angle = 62
				ship.apply_light_profile(light,"atrium_lantern")
				var height := marker.global_position.y-floor_y
				light.spot_range = minf(sqrt(height*height+64.0),height+below_gap-0.5)
				light.shadow_enabled = lens_index == 1
	for z in [-24.0,24.0]:
		var coffer := ship.model(root,"AST-ATR-002.glb","ArtificialDaylightCoffer_"+("Fore" if z<0 else "Aft"),Vector3(0,106.26,z)) as Node3D
		var marker := coffer.find_child("DATUM_emitter",true,false) as Node3D
		assert(marker != null)
		var light := OmniLight3D.new()
		light.name = "RoofDaylightSource_"+("Fore" if z<0 else "Aft")
		root.add_child(light)
		light.global_position = marker.global_position
		ship.apply_light_profile(light,"atrium_daylight")
		light.omni_attenuation = 0.35
		light.omni_shadow_mode = OmniLight3D.SHADOW_CUBE
		light.light_specular = 0.15
		light.shadow_normal_bias = 1.5
		light.shadow_bias = 0.08
