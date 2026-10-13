extends RefCounted
static func build_source_fixture(parent: Node3D)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"),"Group1 commons, Group8 dining ledger and admission coordination remain held")
	return _build_contents(parent)

static func build_on_current_receiver(receiver: Node3D)->Node3D:
	assert(receiver.name=="D15_D17_StarAtlasUpper_WIP")
	assert(receiver.transform.is_equal_approx(Transform3D.IDENTITY),"Retained models use zero-origin world coordinates")
	assert("D17_directory_03" in receiver.get_meta("programme_keys",[]))
	assert(int(receiver.get_meta("source_part_count",-1))==514)
	assert(receiver.get_node_or_null("VIPDryClub_Source")==null,"One retained fitout, no duplicates")
	assert(FileAccess.get_sha256("res://assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb")=="f6fe84992dfb8cb22beee696959f77b8f8b4f91261e46d77c9cf36719303c888")
	assert(FileAccess.get_sha256("res://assets/group2_vip_dry_club/VIP_DRY_CLUB_r002.glb")=="95cc7e8279e993a2b919a2229b4001d215b8146807be9d8d1b306865b50d0800")
	assert(FileAccess.get_sha256("res://data/group2_vip_dry_club/COMPONENT_r002.json")=="cb5902beb0a8cb39f4ac125b7b1bb0a9354ea5e83aa3751372929791bd806c4a")
	var section:=_build_contents(receiver)
	section.set_meta("construction_installed",true)
	section.set_meta("existing_parent_programme","D17_directory_03")
	section.set_meta("food_service_membership_booking_and_capacity_accepted",false)
	return section

static func _build_contents(parent: Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_vip_dry_club/COMPONENT_r002.json"))
	var section:=Node3D.new();section.name="VIPDryClub_Source";parent.add_child(section)
	var visual:Node3D=(load("res://assets/group2_vip_dry_club/VIP_DRY_CLUB_r002.glb")as PackedScene).instantiate();section.add_child(visual)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
	var door:Node3D=load("res://scripts/group2_vip_dry_club/entry.gd").new();door.name="DiningEntry";door.persistent_id=StringName(data.door.persistent_id)
	door.position=Vector3(data.door.world_xyz[0],data.door.world_xyz[1],data.door.world_xyz[2]);door.rotation.y=data.door.yaw;section.add_child(door)
	for row in data.lights:
		assert(visual.find_child(row.source_mesh,true,false)!=null)
		var light:=OmniLight3D.new();light.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);light.omni_range=row.range;light.light_energy=row.energy
		light.light_color=Color(1,.86,.68);light.shadow_enabled=true;light.visible=false;section.add_child(light)
	section.set_meta("production_adoption",false);return section
