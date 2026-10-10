extends RefCounted
# Retained structural contacts stay independent of cached/culled room interiors.
# Source skins remain visually owned by the lower rooms; new frame members render.
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasSpecialtyStructuralReceiving"):return districts.get_node("StarAtlasSpecialtyStructuralReceiving")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_STRUCTURAL_RECEIVING.json"))
	var path:String="res://assets/models/"+str(p.model_file);assert(FileAccess.get_sha256(path)==p.model_sha256)
	var root:=Node3D.new();root.name="StarAtlasSpecialtyStructuralReceiving";districts.add_child(root)
	var visual:Node3D=load(path).instantiate();root.add_child(visual)
	var contacts:Array[Node]=[]
	var retained:=0
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		assert(bool(extra.runtime_collision));contacts.append(mesh)
		if bool(extra.get("persistent_structural_contact_only",false)):
			mesh.visible=false;retained+=1
			assert(not str(extra.retained_owner).is_empty())
	load("res://scripts/static_contact_cache.gd").attach_group(visual,contacts)
	root.set_meta("always_present_structural_contacts",true);root.set_meta("retained_source_objects",retained);root.set_meta("interior_culling_unchanged",true);root.set_meta("structural_capacity_accepted",false)
	return root
