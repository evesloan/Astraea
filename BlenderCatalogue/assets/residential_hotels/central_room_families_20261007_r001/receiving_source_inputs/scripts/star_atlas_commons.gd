extends RefCounted
# Different small activities in the existing commons, inside reviewed reservations.
static func build(district:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="StarAtlasCommonsActivities_WIP"
	district.add_child(root)
	var center:=Vector3(-64.7,84,-4.8)
	var orientation:=Basis(Vector3.UP,-PI/2)
	ship.model(root,"AST-LIB-STUDY-02.glb","D13WindowStudy",center,-PI/2)
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","D13WindowStudyChair",center+orientation*Vector3(.105,0,.99),PI/2)
	for shelf in [.42,.83]:
		var stock:Node3D=ship.model(root,"AST-LIB-006.glb","D13StudyStock_"+str(int(shelf*100)),center+orientation*Vector3(-.711,shelf,-.075))
		stock.set_meta("supported_book_group",true)
		# Static visual stock, matching the lower collection. No pickup/save claim.
		for contact in stock.find_children("StaticContact","StaticBody3D",true,false):contact.free()
	var fixture:Node3D=ship.model(root,"AST-LIB-008.glb","D13WindowStudyFixture",center+orientation*Vector3(-.433,.756,-.286),-PI/2)
	var lens:=fixture.find_child("POINT_diffuser_face",true,false)as Node3D
	assert(lens!=null)
	var light:=SpotLight3D.new()
	light.name="D13WindowStudyOpticalSource"
	root.add_child(light)
	light.global_position=lens.global_position+Vector3.DOWN*.01
	light.rotation.x=-PI/2
	light.spot_angle=75
	light.spot_range=2
	light.light_energy=.35
	light.light_color=Color(1,.93,.83)
	light.shadow_enabled=true
	var control:=Node3D.new()
	control.name="D13WindowStudyLightSwitch"
	control.set_script(load("res://scripts/fixture_switch.gd"))
	root.add_child(control)
	control.configure(fixture,light,&"D13_directory_04_window_study_light")
	var conversation:=Vector3(-88.5,88.5,9)
	ship.model(root,"AST-FUR-003_day_table.glb","D14ConversationTable",conversation)
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","D14ConversationChairWest",conversation+Vector3(-1.2,0,0),PI/2)
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","D14ConversationChairEast",conversation+Vector3(1.2,0,0),-PI/2)
