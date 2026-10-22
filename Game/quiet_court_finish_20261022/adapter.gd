extends RefCounted
const P:="res://quiet_court_finish_20261022/"
static func build(ship:Node3D)->Node3D:
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R003.json"))
	assert(FileAccess.get_sha256("res://assets/models/"+str(plan.installed_glb))==plan.installed_sha256)
	var house:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
	assert(not house.has_meta("court_finish_20261022"))
	var materials:={}
	for role in plan.materials:
		var c:Array=plan.materials[role];var m:=StandardMaterial3D.new();m.resource_name="QuietCourtFinish_"+str(role);m.albedo_color=Color(c[0],c[1],c[2],c[3]);m.roughness=.34 if role=="champagne_metal" else .62;m.metallic=.55 if role=="champagne_metal" else 0.0;materials[role]=m
	var changed:=0;var original_meshes:=0
	for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
		var e:Dictionary=mesh.get_meta("extras",{})
		if str(e.get("source_plan_sha256",""))!=str(plan.source_plan_sha256):continue
		original_meshes+=1
		var role:String=str(e.get("role",""))
		if materials.has(role):mesh.material_override=materials[role];changed+=1
	assert(original_meshes==580,"Preserve later nineteen guard-batch replacements")
	var receiving:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_RECEIVING.json"))
	var lights:=0
	for row in receiving.lights:
		var xyz:=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2])
		var matches:Array=house.get_children().filter(func(n):return n is OmniLight3D and n.position.distance_to(xyz)<.001)
		assert(matches.size()==1,"Exact retained fixture position required");var light:OmniLight3D=matches[0]
		light.light_color=Color(1,.9,.76);light.light_energy=plan.fixture_energy;light.omni_range=plan.fixture_range;lights+=1
	assert(lights==79)
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RUNTIME_BOUNDS.json"))
	assert(FileAccess.get_sha256(P+"runtime/QuietGroveCourtPlanting_r003.scn")==receipt.scene_sha256)
	var planting:Node3D=load(P+"runtime/QuietGroveCourtPlanting_r003.scn").instantiate();planting.name="QuietCourtPlantedBeds20261022";house.add_child(planting)
	assert(planting.find_children("*","CollisionObject3D",true,false).is_empty())
	planting.set_meta("placements",149);planting.set_meta("receiving_beds",33);planting.set_meta("original_house_meshes",original_meshes);planting.set_meta("material_meshes",changed);planting.set_meta("existing_fixtures_retuned",lights);planting.set_meta("visual_accepted",false)
	house.set_meta("court_finish_20261022",true)
	return planting
