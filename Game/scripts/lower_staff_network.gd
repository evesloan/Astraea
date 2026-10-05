extends RefCounted
# Three lower service stops and bounded destination approaches, not finished rooms.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_STAFF_NETWORK.json"))
	var root:=Node3D.new()
	root.name="LowerStaffNetwork_WIP"
	root.set_meta("persistent_id","port_forward_staff_network_001")
	parent.add_child(root)
	var enclosure:Node3D=ship.model(root,"AST-STF-009.glb","LowerStaffEnclosure",Vector3.ZERO)
	for marker in enclosure.find_children("DATUM_light_*","Node3D",true,false):
		var light:=OmniLight3D.new()
		root.add_child(light)
		light.name="StaffRouteLight_"+str(marker.name)
		light.global_position=marker.global_position
		light.light_color=Color(.82,.90,1.0)
		light.light_energy=1.0
		light.omni_range=8.0
		light.omni_attenuation=.7
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="ForwardStaffLift"
	lift.position=Vector3(-25,0,-490)
	lift.rotation.y=PI
	lift.floor_heights.assign([0.0,6.0,12.0])
	lift.deck_numbers.assign([1,2,3])
	lift.stop_ids.assign(["D01","D02","D03"])
	lift.stop_names.assign(["Synthesis service","Fusion maintenance","Crew and depot thresholds"])
	lift.stop_codes.assign(["01","02","03"])
	lift.gate_origin_xz=Vector2(-1.8,0)
	lift.identity_prefix="forward_staff"
	lift.district_label="Forward staff"
	lift.cabin_file=str(data.lift.cabin_file)
	lift.persistent_id=&"forward_staff_lift_001"
	root.add_child(lift)
	for light in lift.find_children("*","Light3D",true,false):light.light_color=Color(.82,.90,1.0)
	for i in range(3):
		var sign:=Label3D.new()
		sign.name="StaffDeckSign_%02d"%(i+1)
		sign.text="D%02d  |  SERVICE"%(i+1)
		sign.font_size=48;sign.pixel_size=.005
		sign.position=Vector3(-18.94,float(data.deck_stops_y[i])+1.75,-486)
		sign.rotation.y=-PI/2
		root.add_child(sign)
