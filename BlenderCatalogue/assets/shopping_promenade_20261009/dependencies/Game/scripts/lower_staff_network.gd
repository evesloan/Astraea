extends RefCounted
# Same persistent lower service network, extended only to the two sourced upper stops.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_STAFF_NETWORK.json"))
	var extension:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json"))
	var upper:Dictionary=extension.staff
	assert(upper.preserved_lower_stops_y==data.deck_stops_y and upper.existing_persistent_lift_id=="forward_staff_lift_001")
	var root:=Node3D.new()
	root.name="LowerStaffNetwork_WIP"
	root.set_meta("persistent_id","port_forward_staff_network_001")
	parent.add_child(root)
	var enclosure:Node3D=ship.model(root,"AST-STF-009_secondary_engineering.glb","LowerStaffEnclosure",Vector3.ZERO)
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
	assert(upper.upper_light_markers.size()==20)
	for item in upper.upper_light_markers:
		var marker:Node3D=load("res://scripts/grand_pool_section.gd").source_marker(enclosure,str(item.name))
		assert(marker!=null,"Upper service source needs its authored fixture marker")
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="UpperStaffRouteLight_"+str(marker.name)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		ship.apply_light_profile(light,"staff_work")
		light.spot_range=float(item.suggested_range_m)
		light.spot_angle=75
		light.shadow_enabled=true
		light.set_meta("source_marker",str(item.name))
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="ForwardStaffLift"
	lift.position=Vector3(-25,0,-490)
	lift.rotation.y=PI
	lift.floor_heights.assign(upper.proposed_all_stops_y)
	lift.deck_numbers.assign(upper.proposed_deck_numbers)
	lift.stop_ids.assign(upper.proposed_stop_ids)
	lift.stop_names.assign(["Synthesis service","Fusion maintenance","Crew and depot thresholds","D08 wet service","D09 market service"])
	lift.stop_codes.assign(["01","02","03","08W","09"])
	lift.gate_origin_xz=Vector2(-1.8,0)
	lift.identity_prefix="forward_staff"
	lift.district_label="Forward staff"
	lift.cabin_file=str(upper.cabin_file)
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

	for i in range(upper.upper_route_y.size()):
		var sign:=Label3D.new()
		sign.name="StaffDeckSign_"+("D08_WET" if i==0 else "D09")
		sign.text="D08  |  WET SERVICE" if i==0 else "D09  |  MARKET SERVICE"
		sign.font_size=48;sign.pixel_size=.005
		sign.position=Vector3(-18.94,float(upper.upper_route_y[i])+1.75,-486)
		sign.rotation.y=-PI/2
		root.add_child(sign)
