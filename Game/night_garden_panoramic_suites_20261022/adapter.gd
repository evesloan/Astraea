extends RefCounted
const P := "res://night_garden_panoramic_suites_20261022/"
static func prepare(manager: Node, file: String) -> void:
	if not file.begins_with("NightGardenD15Specialty_"):return
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX.json"))
	if not records.has(file):return
	assert(manager.entries.filter(func(entry):return str(entry.record.model_file)==file).is_empty())
	assert(manager.index[file].sha256==records[file].sha256)
	manager.index[file]=records[file]
static func glazing(shell: Node3D) -> void:
	for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
		if not str(mesh.name).begins_with("NGP_") or not str(mesh.name).ends_with("PrivateViewPane"):continue
		var material:=ShaderMaterial.new();material.shader=load("res://night_garden_view_galleries_20261022/private_view.gdshader")
		material.set_shader_parameter("plane_x",98.86);material.set_shader_parameter("interior_sign",-1.0)
		mesh.material_override=material
static func finish(ship: Node3D) -> void:
	var district:Node3D=ship.get_node("ShipSpace/Districts/NightGardenD15SpecialtyReceiving20261020")
	assert(not district.get_meta("panoramic_frontage_applied",false))
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD.json"))
	var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
	for row in build.rooms:
		var home:Node3D=district.get_node(str(row.room_id))
		assert(home.get_meta("rest_slot_ids")==row.rest_slot_ids)
		var source:Dictionary={}
		for candidate in original.rooms:
			if str(candidate.model_file)==str(row.model_file):source=candidate;break
		assert(not source.is_empty())
		for door_record in source.doors:
			if not str(door_record.name).begins_with("CocoonPrivacyDoor_"):continue
			var door:Node3D=home.get_node(str(door_record.name))
			assert(str(door.persistent_id)==str(door_record.persistent_id))
			assert(door.position.is_equal_approx(Vector3(door_record.position[0],door_record.position[1],door_record.position[2])))
			door.position.x-=2.78
		var actual_rests:Array=[]
		for i in range(source.rest_adjustments.size()):
			var before:Array=source.rest_adjustments[i].target_position;var delta:Array=row.rest_moves[i].delta
			actual_rests.append({"slot_id":row.rest_moves[i].slot_id,"position":[before[0]+delta[0],before[1]+delta[1],before[2]+delta[2]]})
		home.set_meta("panoramic_rest_positions",actual_rests)
		home.set_meta("panoramic_native_sha256",row.native_sha256)
		home.set_meta("residential_visual_accepted",false)
	assert(not district.has_node("OuterViewGalleries20261022"))
	district.set_meta("panoramic_frontage_applied",true)
	district.set_meta("panoramic_outer_suites",16)
	district.set_meta("inner_atrium_suites_preserved",14)
