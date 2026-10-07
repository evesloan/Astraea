extends RefCounted
# A library-specific arrival followed by browsing and an actual atrium-view bay.
static func build(district:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="StarAtlasLibraryArrival_WIP"
	district.add_child(root)
	var counter:Node3D=ship.model(root,"AST-LIB-012.glb","LibraryReferenceCounter",Vector3(-63,78,5),PI)
	for side in ["west","east"]:
		var surface:=counter.find_child("DATUM_"+side+"_work_surface",true,false)as Node3D
		assert(surface!=null)
		ship.model(root,"AST-LIB-007.glb","CounterReferenceFolio_"+side,surface.global_position,PI+(-.515 if side=="west" else .515))
		var receiver:=counter.find_child("DATUM_"+side+"_fixture_receiver",true,false)as Node3D
		assert(receiver!=null)
		var fixture:Node3D=ship.model(root,"AST-LIB-008.glb","CounterTaskFixture_"+side,receiver.global_position,PI+(-.515 if side=="west" else .515))
		var lens:=fixture.find_child("POINT_diffuser_face",true,false)as Node3D
		assert(lens!=null)
		var task_light:=SpotLight3D.new()
		task_light.name="CounterTaskSource_"+side
		root.add_child(task_light)
		task_light.global_position=lens.global_position+Vector3.DOWN*.01
		task_light.rotation.x=-PI/2
		task_light.spot_angle=75
		task_light.spot_range=2
		task_light.light_energy=.35
		task_light.light_color=Color(1,.94,.86)
		task_light.shadow_enabled=true
		var control:=Node3D.new()
		control.name="CounterStudyLightSwitch_"+side
		control.set_script(load("res://scripts/fixture_switch.gd"))
		root.add_child(control)
		control.configure(fixture,task_light,StringName("D12_stargazing4_reference_light_"+side))
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
