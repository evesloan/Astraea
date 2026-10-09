extends RefCounted
# Two aft command shells. Shared controllers are retained; operating systems remain unfinished.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_COMMAND_RUNTIME.json"))
	var root:=Node3D.new()
	root.name="AftCommandCrown_WIP"
	root.set_meta("persistent_id","D18_aft_command_001")
	parent.add_child(root)
	var shell:Node3D=ship.model(root,"AST-CMD-002.glb","AftCommandArchitecture",Vector3.ZERO)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(mesh.name).to_lower():mesh.material_override=glass
	for entry in data.doors:
		var door:Node3D=load("res://scripts/service_door.gd").new()
		door.name="AftCommandDoor_"+str(entry.name)
		door.persistent_id=StringName("aft_command_"+str(entry.name))
		door.position=Vector3(entry.position[0],entry.position[1],entry.position[2])
		door.rotation.y=float(entry.yaw)
		door.open_fraction=0.0;door.desired_open=false
		root.add_child(door)
	for programme in data.programmes:
		var anchor:=Node3D.new()
		anchor.name=str(programme.programme_key)
		anchor.set_meta("programme_key",str(programme.programme_key))
		anchor.set_meta("scope","Unfurnished programme shell; operational command systems unfinished")
		root.add_child(anchor)
		var sign:=Label3D.new()
		sign.name="AftCommandSign_"+str(programme.programme_key)
		sign.text=str(programme.name).to_upper()
		sign.font_size=48;sign.pixel_size=.0045
		var x:float=float(programme.entry_xz[0])
		sign.position=Vector3(x-signf(x)*.02,109.65,float(programme.entry_xz[1]))
		sign.rotation.y=float(programme.door_yaw)
		anchor.add_child(sign)
	# Exact fixture anchors and warm/cool profiles are installed from the verified source contract.
	for item in data.light_markers:
		var marker:=shell.find_child(str(item.name),true,false)as Node3D
		assert(marker!=null,"Crown fixture contract requires an actual exported marker")
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="AftCommandSource_"+str(item.name)
		light.global_position=marker.global_position
		var color:Array=item.get("suggested_color",[1.0,.95,.87])
		light.light_color=Color(color[0],color[1],color[2])
		light.light_energy=1.1
		light.spot_range=float(item.get("suggested_range",10.0))
		light.spot_angle=float(item.get("suggested_spot_angle_degrees",76.0))
		light.rotation.x=-PI/2
		light.shadow_enabled=true
