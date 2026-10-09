extends RefCounted
# Narrow retained-roof composite receiver; no interior piers or source replacement.
static func build(house:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FAMILY_CELESTIAL_RECEIVER.json"))
	var path:String="res://assets/models/"+str(d.model_file)
	assert(FileAccess.get_sha256(path)==d.model_sha256)
	var receiver:=Node3D.new()
	receiver.name="FamilyCelestialRoofReceiver"
	house.add_child(receiver)
	var model:Node3D=load(path).instantiate()
	receiver.add_child(model)
	var meshes:=model.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(d.part_count))
	for mesh:MeshInstance3D in meshes:
		assert(mesh.get_meta("extras",{}).source_plan_sha256==d.plan_sha256)
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	receiver.set_meta("source_part_count",d.part_count)
	receiver.set_meta("plane_matched_roof_contacts",25)
	house.set_meta("celestial_roof_receiver_installed",true)
	house.set_meta("receiving_structure_accepted",false)
	house.set_meta("open_construction_hold","FT_RECEIVING_REVIEW_HOLD")
	house.set_meta("superseded_missing_geometry_hold","FT_BASE_RECEIVING_HOLD")
	house.set_meta("remaining_receiving_work","Final receiving/visual review and full ship hull acceptance; no structural capacity certification")
	return receiver
