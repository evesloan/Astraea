extends RefCounted
# Additive court/verge receiving structure. Whole-base hold is deliberately retained.
static func build(house:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FAMILY_RECEIVING_FRAME.json"))
	var path:String="res://assets/models/"+str(d.model_file)
	assert(FileAccess.get_sha256(path)==d.model_sha256)
	var frame:=Node3D.new()
	frame.name="FamilyCourtReceivingFrame"
	house.add_child(frame)
	var visual:Node3D=load(path).instantiate()
	frame.add_child(visual)
	var meshes:=visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(d.part_count))
	for mesh:MeshInstance3D in meshes:
		var extra:Dictionary=mesh.get_meta("extras",{})
		assert(extra.source_plan_sha256==d.plan_sha256)
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	frame.set_meta("source_part_count",d.part_count)
	frame.set_meta("source_reaction_feet",d.reaction_count)
	frame.set_meta("full_base_hold_closed",false)
	house.set_meta("court_receiving_frame_installed",true)
	house.set_meta("remaining_receiving_work","Inner garden and residential street over Celestial; one inner task receiver; full hull/structural acceptance")
	return frame
