extends RefCounted
static func build_source_fixture(parent: Node3D)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"),"Group1/8 receiving and child admission coordination remains held")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_childcare/COMPONENT_r001.json"))
	var section:=Node3D.new();section.name="FamilyChildcare_Source";parent.add_child(section)
	var visual:Node3D=(load("res://assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb")as PackedScene).instantiate();section.add_child(visual)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
	var door:Node3D=load("res://scripts/group2_family_childcare/entry.gd").new();door.name="CareEntry";door.persistent_id=StringName(data.door.persistent_id)
	door.position=Vector3(data.door.world_xyz[0],data.door.world_xyz[1],data.door.world_xyz[2]);section.add_child(door)
	for row in data.lights:
		assert(visual.find_child(row.source_mesh,true,false)!=null)
		var light:=OmniLight3D.new();light.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);light.omni_range=row.range;light.light_energy=row.energy
		light.light_color=Color(1,.86,.68);light.shadow_enabled=true;light.visible=false;section.add_child(light)
	section.set_meta("production_adoption",false);return section
