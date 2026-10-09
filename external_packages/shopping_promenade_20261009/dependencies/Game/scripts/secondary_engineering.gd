extends RefCounted
# Connected D02 plant architecture. Fictional equipment has no simulation behavior.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"))
	var section:=Node3D.new()
	section.name="SecondaryEngineering"
	section.set_meta("persistent_id","secondary_engineering_D02_001")
	section.set_meta("programme_key","D02_directory_02")
	parent.add_child(section)
	var core:=ship.find_child("ForwardPublicCore_WIP",true,false) as Node3D
	var core_sign:=core.find_child("PrimaryDeckSign_02",true,false) as Label3D
	assert(core_sign!=null)
	# The retained D02 wall sign now needs the intact jamb beside the new portal.
	core_sign.position.z=-435.7
	core_sign.font_size=36
	core_sign.pixel_size=.004
	core_sign.text="D02 / FORWARD CORE"
	var shell:Node3D=ship.model(section,str(data.model),"SecondaryEngineeringArchitecture",Vector3.ZERO)
	for item in data.fixtures:
		var marker:=shell.find_child(str(item.name),true,false) as Node3D
		assert(marker!=null,"Source-backed engineering fixture missing")
		var light:=SpotLight3D.new()
		light.name="EngineeringSource_"+str(item.name)
		section.add_child(light)
		light.global_position=marker.global_position-Vector3.UP*.08
		light.rotation.x=-PI/2
		ship.apply_light_profile(light,"staff_work")
		light.light_energy=1.8
		light.spot_range=10.0
		light.spot_angle=76.0
		light.shadow_enabled=true
		light.set_meta("source_marker",str(item.name))
	var staff:=ship.find_child("LowerStaffEnclosure",true,false) as Node3D
	assert(staff!=null)
	for item in data.staff_connection.fixtures:
		var marker:=staff.find_child(str(item.name),true,false) as Node3D
		assert(marker!=null)
		var light:=OmniLight3D.new()
		light.name="EngineeringStaffSource_"+str(item.name)
		section.add_child(light)
		light.global_position=marker.global_position
		light.light_color=Color(.82,.90,1)
		light.light_energy=1.0
		light.omni_range=8.0
		light.omni_attenuation=.7
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.set_meta("source_marker",str(item.name))
	var door:Node3D=load("res://scripts/guest_entry_door.gd").new()
	door.name="SecondaryEngineeringReceivingDoor"
	door.persistent_id=&"secondary_engineering_receiving_D02_001"
	door.visual_file=str(data.entry_door_model)
	door.leaf_width=1.18
	door.leaf_travel=1.24
	door.enclosure_width=5.16
	door.door_description="engineering visitor door"
	door.position=Vector3(8.8,6,-432)
	door.rotation.y=PI/2
	section.add_child(door)
	for item in [[Vector3(8.1,8.05,-435.6),-PI/2,"SECONDARY ENGINEERING\nVISITOR GALLERY"],[Vector3(53.65,8.0,-434.8),-PI/2,"ENGINEERING\nSERVICE ACCESS"],[Vector3(53.65,8.0,-407),-PI/2,"WORKSHOP / RETURNS"]]:
		var sign:=Label3D.new()
		sign.position=item[0];sign.rotation.y=item[1];sign.text=item[2]
		sign.font_size=38;sign.pixel_size=.004
		section.add_child(sign)
