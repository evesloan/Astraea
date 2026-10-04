extends RefCounted
# Partial fit in the original florist allocation; no second business registry.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="LivingGiftsInterior_WIP"
	root.set_meta("programme_key","D09_directory_08")
	root.set_meta("historical_room_id","D09_florist7")
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-RTL-006.glb","LivingGiftsAuthoredInterior",Vector3(46,52.5,230.4))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in part.name:part.material_override=glass
		if part.name.begins_with("RTL_finish_"):
			var contact:=part.get_node_or_null("StaticContact")
			if contact!=null:contact.free()
		if "lens" in part.name:part.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var marker:=architecture.find_child("DATUM_display_bay",true,false)as Node3D
	ship.model(root,"AST-RTL-001.glb","LivingGiftsRecessedDisplay",marker.global_position,-PI/2)
	marker=architecture.find_child("DATUM_wrapping_workbench",true,false)as Node3D
	ship.model(root,"AST-RTL-003.glb","LivingGiftsWrappingWorkbench",marker.global_position)
	for i in range(4):
		marker=architecture.find_child("DATUM_flora_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var file:="AST-BOT-001.glb" if i==0 else "AST-BOT-003.glb" if i==3 else "AST-BOT-009.glb"
		ship.model(root,file,"LivingGiftsSpecimen_"+str(i),marker.global_position,float(i)*.42)
	for i in range(4):
		marker=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=OmniLight3D.new()
		root.add_child(light)
		light.name="LivingGiftsSource_"+str(i)
		light.global_position=marker.global_position+Vector3.DOWN*.035
		light.omni_range=5.5
		light.omni_attenuation=.6
		light.light_energy=[.65,.6,.55,.65][i]
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.shadow_normal_bias=1.5
		light.shadow_bias=.08
