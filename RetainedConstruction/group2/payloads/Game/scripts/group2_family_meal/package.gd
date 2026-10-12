extends RefCounted
static func build_source_fixture(parent:Node3D)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"))
	var kit:Node3D=(load("res://assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb")as PackedScene).instantiate();parent.add_child(kit)
	load("res://scripts/static_contact_cache.gd").attach_group(kit,kit.find_children("*","MeshInstance3D",true,false));kit.set_meta("production_adoption",false);return kit
