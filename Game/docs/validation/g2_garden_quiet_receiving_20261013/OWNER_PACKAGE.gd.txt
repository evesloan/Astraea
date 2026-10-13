extends RefCounted
static func build_source_fixture(parent:Node3D,kind:String)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"))
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_garden_quiet/COMPONENTS_r002.json"))
	var section:=Node3D.new();section.name=kind;parent.add_child(section)
	var visual:Node3D=(load("res://assets/group2_garden_quiet/"+kind+"_r002.glb")as PackedScene).instantiate();section.add_child(visual)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
	for row in data.lights:
		if row.kind!=kind:continue
		assert(visual.find_child(str(row.source_mesh),true,false)!=null)
		var light:=OmniLight3D.new();light.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);light.omni_range=row.range;light.light_energy=row.energy;light.light_color=Color(1,.86,.68);light.shadow_enabled=true;light.visible=false;section.add_child(light)
	section.set_meta("production_adoption",false);return section
