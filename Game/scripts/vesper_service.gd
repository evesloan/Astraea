extends RefCounted
# Local finishing and return support within Vesper; no full kitchen throughput claim.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D10_VesperFinishingService_WIP"
	root.set_meta("programme_key","D10_directory_08")
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-DIN-003.glb","VesperServiceArchitecture",Vector3(48.6,61,233))
	for part in architecture.find_children("DIN_VisualFloor*","MeshInstance3D",true,false):
		var contact:=part.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	for i in range(2):
		var marker:=architecture.find_child("DATUM_counter_"+str(i),true,false)as Node3D
		ship.model(root,"AST-HSP-001.glb","VesperFinishingCounter_"+str(i),marker.global_position,PI/2)
	var credenza:=architecture.find_child("DATUM_credenza",true,false)as Node3D
	ship.model(root,"AST-HSP-005.glb","VesperPlateTrayStock",credenza.global_position,PI/2)
	var dirty_return:=architecture.find_child("DATUM_dish_return",true,false)as Node3D
	ship.model(root,"AST-HSP-004.glb","VesperDirtyReturn",dirty_return.global_position,-PI/2)
	var door:Node3D=load("res://scripts/service_door.gd").new()
	door.name="VesperServiceDoor"
	door.persistent_id=&"D10_banquet7_service_door"
	door.position=Vector3(48.6,61,237)
	door.rotation.y=-PI/2
	root.add_child(door)
	for i in range(2):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="VesperFinishingTaskLight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_range=5
		light.spot_angle=70
		light.light_energy=1.0
		light.light_color=Color(.87,.93,1)
		light.shadow_enabled=true
