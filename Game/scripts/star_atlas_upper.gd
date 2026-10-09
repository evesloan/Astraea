extends RefCounted
# Additive upper commons. Lower library, protected D15 cover and room identities stay intact.
static func build(parent:Node3D,ship:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_UPPER_COMMONS.json"))
	var path:String="res://assets/models/"+str(d.model_file)
	assert(FileAccess.get_sha256(path)==d.model_sha256)
	var root:=Node3D.new()
	root.name="D15_D17_StarAtlasUpper_WIP"
	root.set_meta("programme_keys",d.programme_keys)
	root.set_meta("new_guest_units",0)
	root.set_meta("D15_cover_reused",true)
	parent.add_child(root)
	var visual:Node3D=load(path).instantiate()
	root.add_child(visual)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	var meshes:=visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(d.part_count))
	for mesh:MeshInstance3D in meshes:
		var extra:Dictionary=mesh.get_meta("extras",{})
		assert(extra.source_plan_sha256==d.plan_sha256)
		if extra.role=="hospitality_glass":mesh.material_override=glass
		if bool(extra.runtime_collision):load("res://scripts/static_contact_cache.gd").attach(mesh)
	root.set_meta("source_part_count",meshes.size())
	for item in d.lights:
		var light:=SpotLight3D.new()
		light.name=str(item.name)
		light.position=Vector3(item.position[0],item.position[1],item.position[2])
		light.rotation.x=-PI/2
		light.light_color=Color(1,.93,.8)
		light.light_energy=float(item.energy)
		light.spot_range=float(item.range)
		light.spot_angle=70
		light.shadow_enabled=false
		root.add_child(light)
	for deck in [15,16,17]:
		var anchor:=Marker3D.new()
		anchor.name="D"+str(deck)+"_CommonsArrival"
		anchor.position=Vector3(-65.5,93.0+4.5*(deck-15),0)
		anchor.set_meta("programme_key","D"+str(deck)+"_directory_03")
		root.add_child(anchor)
	return root
