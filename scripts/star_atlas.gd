extends RefCounted
static func build(parent:Node3D,ship:Node3D) -> void:
	var district:=Node3D.new()
	district.name="D12_D14_StarAtlas_WIP"
	district.set_meta("programme_keys",["D12_directory_05","D13_directory_04","D14_directory_03"])
	district.set_meta("historical_library_id","D12_stargazing4")
	parent.add_child(district)
	var architecture:Node3D=ship.model(district,"AST-LIB-011.glb","StarAtlasAuthoredArchitecture",Vector3(-80,78,0))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in part.name:part.material_override=glass
		if part.name.begins_with("LIB_steps") or part.name.begins_with("LIB_finish"):
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
	# Closed source-authored stair wedges provide the single smooth walking contact.
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="StarAtlasPassengerLift"
	lift.floor_heights.assign([78.0,84.0,88.5])
	lift.deck_numbers.assign([12,13,14])
	lift.gate_origin_xz=Vector2(-68.2,-10.2)
	lift.identity_prefix="star_atlas"
	lift.district_label="Star Atlas"
	lift.cabin_file="AST-CIR-003_three_stop.glb"
	lift.persistent_id=&"star_atlas_lift_001"
	district.add_child(lift)
	for i in range(10):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=SpotLight3D.new()
		district.add_child(light)
		light.name="StarAtlasSource_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_angle=67
		light.spot_range=22 if i==5 else 10
		light.light_energy=2.1 if i==5 else 1.3
		light.light_color=Color(1,.95,.87)
		light.shadow_enabled=true

	load("res://scripts/star_atlas_collections.gd").build(district,ship)
