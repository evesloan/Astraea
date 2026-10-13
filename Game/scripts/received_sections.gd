extends RefCounted

# Additive received sections use the existing production model/contact builders.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/received_sections.json"))
	var districts: Node3D = ship.get_node("ShipSpace/Districts")
	assert(districts.get_node_or_null("ReceivedSections") == null)
	var root := Node3D.new()
	root.name = "ReceivedSections"
	districts.add_child(root)
	for section in definition.sections:
		var file: String = str(section.model_file)
		assert(FileAccess.get_sha256("res://assets/models/" + file) == str(section.source_sha256), "Received export pin mismatch")
		var p: Array = section.translation_xyz
		var room: Node3D = ship.model(root, file, str(section.programme_key), Vector3(p[0],p[1],p[2]), float(section.rotation_y))
		room.set_meta("programme_key", str(section.programme_key))
		room.set_meta("persistent_id", str(section.programme_key))
		room.set_meta("source_archive_sha256", str(section.source_archive_sha256))
		room.set_meta("operational_acceptance", false)
		if ["D10_directory_06","D10_directory_10"].has(str(section.programme_key)):
			load("res://scripts/group8/dining_fixture_adaptation.gd").build(ship,room)
	return root

