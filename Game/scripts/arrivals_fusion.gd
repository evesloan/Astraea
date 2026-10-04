extends RefCounted
static func build(parent:Node3D,ship:Node3D) -> void:
	var district:=Node3D.new()
	district.name="D01_D02_ArrivalsFusion_Integrated_WIP"
	district.set_meta("programme_keys",["D01_directory_01","D02_directory_01"])
	parent.add_child(district)
	var architecture:Node3D=ship.model(district,"AST-ARR-002.glb","ArrivalsAuthoredArchitecture",Vector3(-31,0,-432))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "Glass" in part.name:part.material_override=glass
		if part.name.begins_with("ARR_Step"):
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
	const stair_contact=preload("res://scripts/aquatic_section.gd")
	stair_contact._contact(district,[Vector3(-30,0,-435.45),Vector3(-36,3,-435),Vector3(-36,3,-429),Vector3(-30,0,-428.55)])
	stair_contact._contact(district,[Vector3(-45,3,-437),Vector3(-42,3,-437),Vector3(-42,6,-443),Vector3(-45,6,-443)])
	stair_contact._contact(district,[Vector3(-45,3,-427),Vector3(-42,3,-427),Vector3(-42,6,-421),Vector3(-45,6,-421)])
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="ArrivalsVisitorLift"
	lift.floor_heights.assign([0.0,6.0])
	lift.deck_numbers.assign([1,2])
	lift.gate_origin_xz=Vector2(-16.4,-424)
	lift.identity_prefix="arrivals"
	lift.district_label="Arrivals"
	lift.persistent_id=&"arrivals_fusion_lift_001"
	district.add_child(lift)
	for i in range(11):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		district.add_child(light)
		light.name="ArrivalsArchitecturalLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_angle=65
		light.spot_range=16
		light.light_energy=1.15
		light.light_color=Color(1,.95,.87)
		light.shadow_enabled=true
	for i in range(2):
		var marker:=architecture.find_child("DATUM_wallwash_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		district.add_child(light)
		light.name="ArrivalsReliefWallwash_"+str(i)
		light.global_position=marker.global_position
		light.look_at(Vector3(-47.15,7.5,-432),Vector3.UP)
		light.spot_angle=58
		light.spot_range=12
		light.light_energy=2.1
		light.light_color=Color(1,.94,.85)
		light.shadow_enabled=true
	for i in range(2):
		var mount:=architecture.find_child("DATUM_exhibit_center_"+str(i),true,false)as Node3D
		var exhibit:Node3D=ship.model(district,"AST-ENG-007.glb","ContainedFusionExhibit_"+str(i),mount.global_position)
		exhibit.set_meta("presentation","Curated sealed machinery; service catwalks remain behind opaque screens")
		for j in range(2):
			var marker:=exhibit.find_child("DATUM_transmitted_light_"+str(j),true,false)as Node3D
			var light:=SpotLight3D.new()
			district.add_child(light)
			light.name="FilteredExhibitLight_%d_%d"%[i,j]
			light.global_position=marker.global_position
			light.rotation.x=-PI/2
			light.spot_angle=68
			light.spot_range=10
			light.light_energy=.30
			light.light_color=Color(.55,.85,1)
			light.shadow_enabled=true
