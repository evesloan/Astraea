extends RefCounted
# A library-specific arrival followed by browsing and an actual atrium-view bay.
static func build(district:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="StarAtlasLibraryArrival_WIP"
	district.add_child(root)
	var counter:Node3D=ship.model(root,"AST-LIB-012.glb","LibraryReferenceCounter",Vector3(-59,78,7),PI)
	for side in ["west","east"]:
		var surface:=counter.find_child("DATUM_"+side+"_work_surface",true,false)as Node3D
		assert(surface!=null)
		ship.model(root,"AST-LIB-007.glb","CounterReferenceFolio_"+side,surface.global_position,PI+(-.515 if side=="west" else .515))
	# Static catalogue hardware; no search/catalogue service is claimed yet.
	ship.model(root,"AST-LIB-010.glb","LibraryCatalogue_StaticOnly",Vector3(-55.7,78,7.4),2.65)
	ship.model(root,"AST-LIB-009.glb","PeriodicalBrowseEdge",Vector3(-59,78,12),PI)
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","AtriumReadingChairNorth",Vector3(-55.2,78,16))
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","AtriumReadingChairSouth",Vector3(-55.2,78,18.5),PI)
	ship.model(root,"AST-FUR-003_day_table.glb","AtriumReadingTable",Vector3(-55.2,78,17.25))
	var lamp:Node3D=ship.model(root,"AST-GST-001.glb","AtriumReadingFloorLamp",Vector3(-56.1,78,16.1),PI/3)
	var diffuser:=lamp.find_child("FLOOR_DIFFUSER",true,false)as Node3D
	var aim:=lamp.find_child("FLOOR_READING_AIM",true,false)as Node3D
	assert(diffuser!=null and aim!=null)
	var light:=SpotLight3D.new()
	light.name="AtriumReadingLampSource"
	root.add_child(light)
	light.global_position=diffuser.global_position+Vector3.DOWN*.015
	light.look_at(aim.global_position,Vector3.UP)
	light.spot_angle=65
	light.spot_range=3
	light.light_energy=.65
	light.light_color=Color(1,.94,.86)
	light.shadow_enabled=true
