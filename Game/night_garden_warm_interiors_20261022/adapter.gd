extends RefCounted
const P := "res://night_garden_warm_interiors_20261022/"
const PREVIOUS := "res://night_garden_panoramic_suites_20261022/"
static func prepare(manager: Node, file: String) -> void:
	load(PREVIOUS+"adapter.gd").prepare(manager,file)
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX.json"))
	if not records.has(file):return
	assert(manager.entries.filter(func(entry):return str(entry.record.model_file)==file).is_empty())
	assert(manager.index[file].sha256==records[file].sha256)
	manager.index[file]=records[file]
static func glazing(shell: Node3D) -> void:
	load(PREVIOUS+"adapter.gd").glazing(shell)
static func finish(ship: Node3D) -> void:
	load(PREVIOUS+"adapter.gd").finish(ship)
	var district:Node3D=ship.get_node("ShipSpace/Districts/NightGardenD15SpecialtyReceiving20261020")
	assert(not district.get_meta("warm_interiors_applied",false))
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD.json"))
	for row in build.rooms:
		var home:Node3D=district.get_node(str(row.room_id))
		assert(not home.has_node("WarmCoveSource"))
		var existing:Array[Node]=home.find_children("*","SpotLight3D",false,false)
		assert(existing.size()==2,"Original fixture ownership changed")
		for light:SpotLight3D in existing:
			light.light_color=Color(1.0,.84,.65)
			light.light_energy=1.8
			light.shadow_enabled=true
		var view:SpotLight3D=home.get_node(str(row.view_light_name))
		view.position=Vector3(row.view_light_position[0],row.view_light_position[1],row.view_light_position[2])
		view.light_energy=2.6
		view.spot_angle=78
		var cove:=SpotLight3D.new()
		cove.name="WarmCoveSource"
		cove.position=Vector3(row.cove_light_position[0],row.cove_light_position[1],row.cove_light_position[2])
		cove.rotation.x=-PI/2
		cove.light_color=Color(1.0,.78,.51)
		cove.light_energy=1.5
		cove.spot_range=6.0
		cove.spot_angle=82
		cove.shadow_enabled=true
		cove.set_meta("native_fixture","NGW_"+str(int(row.index))+"_WindowHeadLight")
		home.add_child(cove)
		home.set_meta("warm_interior_applied",true)
		home.set_meta("warm_interior_native_sha256",row.native_sha256)
		home.set_meta("residential_visual_accepted",false)
	district.set_meta("warm_interiors_applied",true)
