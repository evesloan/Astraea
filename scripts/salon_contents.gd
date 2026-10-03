extends RefCounted
# Purposeful activity groupings in the existing room; furniture is currently static.
static func build(room: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "SalonActivityFurnishings_WIP"
	room.add_child(root)
	var y: float = ship.d09_y
	var center := Vector3(67,y,-21.5)
	ship.model(root,"AST-LIB-STUDY-01.glb","SharedReadingTable",center)
	for column in range(2):
		var x: float = [-0.55,0.55][column]
		for row in range(2):
			var z: float = [-1.035,1.035][row]
			ship.model(root,"AST-FUR-002_day_reading_chair.glb","StudyChair_%d_%d"%[column,row],center+Vector3(x,0,z),PI if z>0 else 0.0)
	for point_index in range(2):
		var point: Vector2 = [Vector2(-0.55,0.27),Vector2(0.55,-0.27)][point_index]
		ship.model(root,"AST-LIB-007.glb","OpenReadingFolio_"+str(point_index),center+Vector3(point.x,.75,point.y),0.0 if point.y>0 else PI)
	var task_fixture := ship.model(root,"AST-LIB-008.glb","SharedStudyTaskFixture",center+Vector3(0,.754,0)) as Node3D
	var lens := task_fixture.find_child("POINT_diffuser_face",true,false) as Node3D
	assert(lens != null)
	var task_light := SpotLight3D.new()
	task_light.name = "StudyTableOpticalSource"
	root.add_child(task_light)
	task_light.global_position = lens.global_position+Vector3.DOWN*.01
	task_light.rotation.x = -PI/2
	task_light.spot_angle = 75
	task_light.spot_range = 2
	task_light.light_energy = .35
	task_light.light_color = Color(1,.93,.83)
	task_light.shadow_enabled = true
	# The rear-of-reading route now serves a real fitted counter, not leftover empty space.
	ship.model(root,"AST-HSP-001.glb","GuestRefreshmentCounter",Vector3(59,y,-33.35))
	ship.model(root,"AST-HSP-003.glb","TwinSpoutStation_StaticOnly",Vector3(60.2,y+.90,-33.35))
	# A paired window conversation setting is distinct from the larger crescent gathering.
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","WindowCompanionChair_A",Vector3(54,y,-8),PI)
	ship.model(root,"AST-FUR-002_day_reading_chair.glb","WindowCompanionChair_B",Vector3(54,y,-10.5),0)
	ship.model(root,"AST-FUR-003_day_table.glb","WindowCompanionTable",Vector3(54,y,-9.25))
