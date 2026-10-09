extends RefCounted
# Supported public bypass and bridge platform; the separate enclosure owns its doors.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/BRIDGE_PLATFORM_RUNTIME.json"))
	assert(data.get("doors",[]).is_empty(),"Platform kit does not own the enclosure doors")
	var root:=Node3D.new()
	root.name="BridgePlatform_WIP"
	root.set_meta("persistent_id","D18_bridge_platform_stage1")
	root.set_meta("scope","Supported platform and public bypass; operational systems unfinished")
	parent.add_child(root)
	var shell:Node3D=ship.model(root,"AST-CMD-003.glb","BridgePlatformArchitecture",Vector3.ZERO)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(mesh.name).to_lower():mesh.material_override=glass
	for item in data.light_markers:
		var marker:=shell.find_child(str(item.name),true,false)as Node3D
		assert(marker!=null,"Every bypass source light requires an actual exported fixture marker")
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="BridgePlatformSource_"+str(item.name)
		light.global_position=marker.global_position
		var color:Array=item.get("suggested_color",[1.0,.78,.5])
		light.light_color=Color(color[0],color[1],color[2])
		light.light_energy=1.1
		light.spot_range=float(item.get("suggested_range",9.5))
		light.spot_angle=float(item.get("suggested_spot_angle_degrees",76.0))
		light.rotation.x=-PI/2
		light.shadow_enabled=true
