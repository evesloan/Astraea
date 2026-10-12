extends RefCounted
# Additive fittings on immutable care counters, never a shared root loader.
static func build(section: Node3D,key: String,supported_source_receiver: bool) -> Node3D:
	assert(supported_source_receiver and key!="790")
	assert(section.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_care_programmes/FITTINGS_r001.json"))
	var row: Dictionary={}
	for candidate in data.rows:
		if candidate.key==key:row=candidate
	assert(not row.is_empty())
	assert(section.get_node("RetainedSource").find_child("CareStoneSurface",true,false)!=null)
	var kit: Node3D=(load("res://assets/group2_care_programmes/CARE_"+key+"_r001.glb")as PackedScene).instantiate()
	section.add_child(kit)
	load("res://scripts/static_contact_cache.gd").attach_group(kit,kit.find_children("*","MeshInstance3D",true,false))
	kit.set_meta("fluid_food_hygiene_simulation_accepted",false)
	return kit
