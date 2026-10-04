extends RefCounted
# Quiet resting edge on the existing D13 connector, derived from actual local routes.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D13_ResidentialWayfindingBay_WIP"
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-RES-001.glb","ResidentialWayfindingArchitecture",Vector3(71.8,84,-26))
	for finish in architecture.find_children("RES_VisualFloor*","MeshInstance3D",true,false):
		var contact:=finish.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	for i in range(2):
		var base:Node3D=architecture.find_child("DATUM_plant_"+str(i),true,false)
		var pot:Node3D=ship.model(root,"AST-BOT-012_low.glb","ResidentialRestingPot_"+str(i),base.global_position)
		var soil:Node3D=pot.find_child("DATUM_soil_surface",true,false)
		ship.model(root,"AST-BOT-003.glb","ResidentialRestingFlower_"+str(i),soil.global_position)
		var marker:Node3D=architecture.find_child("DATUM_light_"+str(i),true,false)
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="ResidentialWayfindingLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_range=4.2
		light.spot_angle=70
		light.light_energy=.85
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true
	var marker:Node3D=architecture.find_child("DATUM_map_center",true,false)
	var map:=MeshInstance3D.new()
	root.add_child(map)
	map.name="CurrentD13LocalRouteMap"
	var quad:=QuadMesh.new()
	quad.size=Vector2(2.92,1.25)
	map.mesh=quad
	map.global_position=marker.global_position
	map.rotation.y=PI
	map.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var material:=StandardMaterial3D.new()
	material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_texture=load("res://assets/textures/D13_residential_local_map.png")
	material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST
	map.material_override=material
