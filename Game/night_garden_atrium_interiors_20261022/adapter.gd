extends RefCounted
const P := "res://night_garden_atrium_interiors_20261022/"
static func prepare(manager:Node,file:String)->void:
	if not file.begins_with("NightGardenD15Specialty_"):return
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX_R002.json"))
	if not records.has(file):return
	assert(manager.entries.filter(func(entry):return str(entry.record.model_file)==file).is_empty())
	assert(manager.index[file].sha256==records[file].sha256)
	manager.index[file]=records[file]
static func glazing(shell:Node3D)->void:
	for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
		if not str(mesh.name).ends_with("OvalAtriumGlass"):continue
		var material:=ShaderMaterial.new()
		material.shader=load("res://night_garden_view_galleries_20261022/private_view.gdshader")
		material.set_shader_parameter("plane_x",69.16)
		material.set_shader_parameter("interior_sign",1.0)
		mesh.material_override=material
static func finish(ship:Node3D)->void:
	var district:Node3D=ship.get_node("ShipSpace/Districts/NightGardenD15SpecialtyReceiving20261020")
	assert(district.get_meta("warm_interiors_applied",false))
	assert(not district.get_meta("atrium_interiors_applied",false))
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R002.json"))
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
	for row in build.rooms:
		var home:Node3D=district.get_node(str(row.room_id))
		assert(home.get_meta("rest_slot_ids")==row.rest_slot_ids)
		var original:Dictionary={}
		for item in package.rooms:
			if item.model_file==row.model_file:original=item;break
		assert(not original.is_empty())
		for d in original.doors:
			if not str(d.name).begins_with("CocoonPrivacyDoor_"):continue
			var door:Node3D=home.get_node(str(d.name))
			assert(door.persistent_id==d.persistent_id)
			assert(door.position.is_equal_approx(Vector3(d.position[0],d.position[1],d.position[2])))
			var slot:int=int(str(d.name).get_slice("_",1))-1
			door.position.x+=float(row.rest_moves[slot].delta[0])
		var actual_rests:Array=[]
		for j in range(original.rest_adjustments.size()):
			var before:Array=original.rest_adjustments[j].target_position;var delta:Array=row.rest_moves[j].delta
			actual_rests.append({"slot_id":row.rest_moves[j].slot_id,"position":[before[0]+delta[0],before[1]+delta[1],before[2]+delta[2]]})
		home.set_meta("atrium_rest_positions",actual_rests)
		assert(home.find_children("*","SpotLight3D",false,false).size()==2)
		for light:SpotLight3D in home.find_children("*","SpotLight3D",false,false):
			light.light_color=Color(1,.84,.65);light.light_energy=1.8;light.shadow_enabled=true
		var view:SpotLight3D=home.get_node(str(row.view_light_name))
		view.position=Vector3(row.view_light_position[0],row.view_light_position[1],row.view_light_position[2]);view.light_energy=2.6;view.spot_angle=78
		assert(not home.has_node("AtriumCoveSource"))
		var cove:=SpotLight3D.new();cove.name="AtriumCoveSource"
		cove.position=Vector3(row.cove_light_position[0],row.cove_light_position[1],row.cove_light_position[2]);cove.rotation.x=-PI/2
		cove.light_color=Color(1,.78,.51);cove.light_energy=1.5;cove.spot_range=6;cove.spot_angle=82;cove.shadow_enabled=true
		cove.set_meta("native_fixture","NGA_"+str(int(row.index))+"_OvalHeadLight");home.add_child(cove)
		home.set_meta("atrium_interior_applied",true);home.set_meta("atrium_native_sha256",row.native_sha256);home.set_meta("residential_visual_accepted",false)
	district.set_meta("atrium_interiors_applied",true)
