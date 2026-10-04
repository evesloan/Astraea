extends RefCounted
# First collection shelter. Books remain local static stock, not persistent pickups.
static func build(district:Node3D,ship:Node3D) -> void:
	var bay:=Node3D.new()
	bay.name="NorthCollectionStudy_WIP"
	district.add_child(bay)
	var origin:=Vector3(-88,78,-26.5)
	ship.model(bay,"AST-LIB-STR-003_start.glb","CollectionStartCap",origin)
	var placements:Array=[{"id":"AST-LIB-STR-001","p":origin,"yaw":0.0},{"id":"AST-LIB-STR-001","p":origin+Vector3(2.4,0,0),"yaw":0.0},{"id":"AST-LIB-STR-002","p":origin+Vector3(4.8,0,0),"yaw":0.0}]
	ship.model(bay,"AST-LIB-STR-003.glb","CollectionTurnCap",origin+Vector3(6.6,0,-1.8),PI/2)
	var anchors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/library_stock_anchors.json"))
	var transforms:Array[Transform3D]=[]
	for index in range(placements.size()):
		var part:Dictionary=placements[index]
		ship.model(bay,part.id+".glb","CollectionProfile_"+str(index),part.p,part.yaw)
		for anchor in anchors[part.id]:
			var p:Array=anchor.position_m
			var local:=Vector3(p[0],p[2],-p[1])
			var orientation:=Basis(Vector3.UP,part.yaw+deg_to_rad(anchor.rotation_z_degrees))
			transforms.append(Transform3D(orientation,part.p+Basis(Vector3.UP,part.yaw)*local))
	var stock:Node3D=(load("res://assets/models/AST-LIB-006.glb")as PackedScene).instantiate()
	bay.add_child(stock)
	for part in stock.find_children("*","MeshInstance3D",true,false):
		var batch:=MultiMeshInstance3D.new()
		batch.name="LocalCollectionStock"
		var mm:=MultiMesh.new()
		mm.transform_format=MultiMesh.TRANSFORM_3D
		mm.mesh=part.mesh
		mm.instance_count=transforms.size()
		for i in range(transforms.size()):mm.set_instance_transform(i,transforms[i]*part.global_transform)
		batch.multimesh=mm
		batch.set_meta("stock_groups",transforms.size())
		bay.add_child(batch)
	stock.free()
	var center:=Vector3(-86,78,-21.5)
	ship.model(bay,"AST-LIB-STUDY-01.glb","CollectionSharedStudy",center)
	for x in [-.55,.55]:
		for z in [-1.035,1.035]:ship.model(bay,"AST-FUR-002_day_reading_chair.glb","CollectionStudyChair",center+Vector3(x,0,z),PI if z>0 else 0.0)
	ship.model(bay,"AST-LIB-007.glb","CollectionReadingFolio",center+Vector3(.55,.75,.27))
	var fixture:Node3D=ship.model(bay,"AST-LIB-008.glb","CollectionTaskFixture",center+Vector3(0,.754,0))
	var lens:=fixture.find_child("POINT_diffuser_face",true,false)as Node3D
	assert(lens!=null)
	var light:=SpotLight3D.new()
	bay.add_child(light)
	light.global_position=lens.global_position+Vector3.DOWN*.01
	light.rotation.x=-PI/2
	light.spot_angle=75
	light.spot_range=2
	light.light_energy=.35
	light.light_color=Color(1,.93,.83)
	light.shadow_enabled=true
	var control:=Node3D.new()
	control.name="CollectionStudyLightSwitch"
	control.set_script(load("res://scripts/fixture_switch.gd"))
	bay.add_child(control)
	control.configure(fixture,light,&"D12_stargazing4_collection_study_light")
