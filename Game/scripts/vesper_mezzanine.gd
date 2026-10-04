extends RefCounted
# Authored D10 upper dining; access and final-art acceptance recorded separately.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D10_VesperMezzanine_WIP"
	root.set_meta("programme_key","D10_directory_08")
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-DIN-004.glb","VesperMezzanineArchitecture",Vector3(21,61,182))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(part.name).to_lower():part.material_override=glass
		if str(part.name).begins_with("MEZ_Step_"):
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
	for i in range(8):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="VesperMezzanineTaskLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_range=5.0
		light.spot_angle=65
		light.light_energy=1.0
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true
	for level in [61.0,64.5]:
		for i in range(5):
			var file:="AST-DIN-005_lower.glb" if level==61.0 else "AST-DIN-005.glb"
			var wall:Node3D=ship.model(root,file,"VesperNorthDiningWall_%s_%d"%[level,i],Vector3(26.6+i*5.4,level,182))
			var marker:=wall.find_child("DATUM_wash_source",true,false)as Node3D
			var receiver:=wall.find_child("DATUM_wall_receiver",true,false)as Node3D
			assert(marker!=null and receiver!=null)
			var wash:=SpotLight3D.new()
			root.add_child(wash)
			wash.name="VesperNorthWallWash_%s_%d"%[level,i]
			wash.global_position=marker.global_position
			wash.look_at(receiver.global_position)
			wash.spot_range=3.5
			wash.spot_angle=65
			wash.light_energy=.8
			wash.light_color=Color(1,.95,.90)
			wash.shadow_enabled=true
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="VesperDiningLift"
	lift.floor_heights.assign([61.0,64.5])
	lift.deck_numbers.assign([10,10])
	lift.stop_ids.assign(["D10","D10M"])
	lift.stop_names.assign(["Dining","Upper dining"])
	lift.stop_codes.assign(["10","M"])
	lift.gate_origin_xz=Vector2(20.5,192)
	lift.identity_prefix="vesper"
	lift.district_label="Vesper"
	lift.persistent_id=&"vesper_local_lift_001"
	root.add_child(lift)
