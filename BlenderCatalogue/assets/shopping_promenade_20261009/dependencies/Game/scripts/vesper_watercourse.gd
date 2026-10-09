extends RefCounted
# Architectural recirculation feature with animated surface appearance, not fluid simulation.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:Node3D=ship.model(parent,"AST-AQU-015.glb","VesperWatercourse_WIP",Vector3(21.5,61,207))
	root.set_meta("persistent_id","D10_banquet7_watercourse")
	root.set_meta("programme_key","D10_directory_08")
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in root.find_children("*","MeshInstance3D",true,false):
		if "Glass" in part.name:part.material_override=glass
		if str(part.name).begins_with("WAT_visual"):
			var water:=ShaderMaterial.new()
			water.shader=load("res://shaders/flowing_water.gdshader")
			water.set_shader_parameter("flow_speed",2.4 if "fall" in part.name else .7)
			part.material_override=water
			part.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
		if "FixtureLens" in part.name:part.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for i in range(3):
		var marker:=root.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var source:=SpotLight3D.new()
		root.add_child(source)
		source.name="WatercourseSource_"+str(i)
		source.global_position=marker.global_position
		source.rotation.x=-PI/2 if i<2 else PI/2
		source.spot_angle=68
		source.spot_range=3 if i<2 else 14
		source.light_energy=.45 if i<2 else 1.4
		source.light_color=Color(1,.95,.87)
		source.shadow_enabled=true
