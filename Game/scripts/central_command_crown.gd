extends RefCounted
# Six connected command shells. Operational equipment and remaining crown are unfinished.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_CROWN_RUNTIME.json"))
	var root:=Node3D.new()
	root.name="CentralCommandCrown_WIP"
	root.set_meta("persistent_id","D18_central_crown_001")
	parent.add_child(root)
	var shell:Node3D=ship.model(root,"AST-CMD-001.glb","CentralCrownArchitecture",Vector3.ZERO)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(mesh.name).to_lower():mesh.material_override=glass
	for entry in data.doors:
		var door:Node3D=load("res://scripts/service_door.gd").new()
		door.name="CrownDoor_"+str(entry.name)
		door.persistent_id=StringName("crown_"+str(entry.name))
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
		sign.name="CrownSign_"+str(programme.programme_key)
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
		var light:=OmniLight3D.new()
		root.add_child(light)
		light.name="CrownSource_"+str(item.name)
		light.global_position=marker.global_position
		light.light_color=Color(.82,.90,1.0) if str(item.get("profile","warm"))=="cool" else Color(1,.95,.87)
		light.light_energy=1.1
		light.omni_range=9.0
		light.omni_attenuation=.7
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
