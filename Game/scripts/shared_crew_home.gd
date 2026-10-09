extends RefCounted
static func _asset(parent:Node3D,path:String,label:String,pos:Vector3=Vector3.ZERO,yaw:float=0)->Node3D:
	var node:Node3D=(load("res://assets/models/crew_home/"+path) as PackedScene).instantiate()
	node.name=label
	node.position=pos
	node.rotation.y=yaw
	parent.add_child(node)
	load("res://scripts/static_contact_cache.gd").attach_group(node,node.find_children("*","MeshInstance3D",true,false))
	return node
static func build(ship:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHARED_CREW_HOME.json"))
	for file in d.model_sha256:assert(FileAccess.get_sha256("res://assets/models/crew_home/"+file)==d.model_sha256[file])
	var root:=Node3D.new()
	root.name="SharedCrewHome_WIP"
	root.set_meta("retained_programme","D03_employee_cabin0/player_home")
	root.set_meta("physical_rest_places",2)
	root.set_meta("population_migration_applied",false)
	root.set_meta("registered_berths_added",0)
	ship.get_node("ShipSpace/Districts").add_child(root)
	var enclosure:Node3D=_asset(root,"SharedCrewHome.glb","AuthoredEnclosure")
	var faces:=PackedVector3Array()
	for mesh:MeshInstance3D in enclosure.find_children("*","MeshInstance3D",true,false):
		if not (mesh.name.begins_with("HOME_Wall") or mesh.name.begins_with("HOME_Ceiling") or mesh.name.begins_with("HOME_Annex_Lintel")):continue
		for vertex in mesh.mesh.get_faces():faces.append(mesh.global_transform*vertex)
	load("res://scripts/architectural_occlusion.gd").from_faces(ship.get_node("ShipSpace"),faces,"SharedHomeOpaqueSurfaces")
	var lights:Array[Light3D]=[]
	for bed in d.beds:
		var place:=Node3D.new()
		place.name="PersonalPlace"+str(bed.key)
		place.position=Vector3(bed.position[0],bed.position[1],bed.position[2])
		place.rotation.y=bed.yaw
		root.add_child(place)
		_asset(place,"AST-CRW-001.glb","RestFrame")
		_asset(place,"AST-CRW-002.glb","PrivacyCurtain")
		var shelf:Node3D=_asset(place,"AST-CRW-004.glb","ReadingShelf",Vector3(-.26,.88,-2.14))
		var reading:=SpotLight3D.new()
		reading.name="SourceReadingLight"
		reading.position=Vector3(0,.15,.11)
		reading.rotation_degrees.x=-102.7
		reading.spot_range=1.8
		reading.spot_angle=48
		reading.light_color=Color(1,.87,.72)
		reading.light_energy=.65
		reading.visible=false
		reading.shadow_enabled=false
		shelf.add_child(reading)
		lights.append(reading)
		var anchor:=Marker3D.new()
		anchor.name="UnassignedPhysicalRestPlace"
		anchor.position=Vector3(0,.565,-.9)
		anchor.set_meta("registered_occupant",false)
		place.add_child(anchor)
	_asset(root,"AST-CRW-003.glb","PersonalStorageA",Vector3(-42.35,12,-431.8),PI/2)
	_asset(root,"AST-CRW-003.glb","PersonalStorageB",Vector3(-35.65,12,-431.8),-PI/2)
	for i in d.fixtures.size():
		var p:Array=d.fixtures[i]
		var light:=OmniLight3D.new()
		light.name="SourceCeilingLight"+str(i)
		light.position=Vector3(p[0],p[1],p[2])
		light.light_color=Color(.80,.88,1)
		light.light_energy=1.2
		light.omni_range=5.0
		light.visible=false
		light.shadow_enabled=false
		root.add_child(light)
		lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	return root
