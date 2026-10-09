extends RefCounted
const DATA="res://data/architecture/TIDAL_AQUATIC_SINGLES.json"
static func patch_frontage(visual:Node3D)->void:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var file:String="res://assets/models/"+str(d.frontage_model)
	assert(FileAccess.get_sha256(file)==d.frontage.export_sha256)
	var patch:Node3D=load(file).instantiate()
	for item in d.frontage.changed_batches:
		var target:MeshInstance3D=visual.find_child(str(item.batch),true,false)
		var replacement:MeshInstance3D=patch.find_child(str(item.batch),true,false)
		assert(target!=null and replacement!=null and target.get_meta("extras",{}).category in ["guard","public_glass"])
		target.mesh=replacement.mesh
		target.set_meta("tidal_aquatic_cumulative_guard_openings",15)
	patch.free()
static func build(ship:Node3D)->void:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var parent:Node3D=ship.get_node("ShipSpace/Districts/SpecialtyHomeCandidates")
	var street_path:String="res://assets/models/"+str(d.street_model)
	assert(FileAccess.get_sha256(street_path)==d.street_extension.model_sha256)
	var street:Node3D=load(street_path).instantiate();street.name="TidalD14SouthStreetExtension"
	ship.get_node("ShipSpace/Districts").add_child(street)
	load("res://scripts/tidal_specialty.gd")._contacts(street)
	assert(parent.get_child_count()==10)
	for unit in d.units:
		assert(parent.get_node_or_null(str(unit.allocation.proposed_runtime_id))==null)
		load("res://scripts/tidal_specialty.gd").build_unit(parent,unit)
	assert(parent.get_child_count()==15)
	parent.set_meta("retained_d14_aquatic_reservations_instantiated",5)
	parent.set_meta("species_assignments_accepted",false)
