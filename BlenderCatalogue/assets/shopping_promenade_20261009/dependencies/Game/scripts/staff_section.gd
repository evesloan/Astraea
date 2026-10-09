extends RefCounted
# One service bay inside the food-synthesis allocation; not an entire food plant.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "D01_SynthesisServiceBay_WIP"
	parent.add_child(root)
	for index in range(6):
		ship.model(root,"AST-STF-001.glb","NorthWashableBay",Vector3(-68.4+index*1.2,0,-3.6))
		ship.model(root,"AST-STF-001.glb","SouthWashableBay",Vector3(-61.2-index*1.2,0,3.6),PI)
		ship.model(root,"AST-STF-001.glb","WestWashableBay",Vector3(-68.4,0,3.6-index*1.2),PI/2)
	for index in range(2):
		ship.model(root,"AST-STF-001.glb","EastNorthReturn",Vector3(-61.2,0,-3.6+index*1.2),-PI/2)
		ship.model(root,"AST-STF-001.glb","EastSouthReturn",Vector3(-61.2,0,1.2+index*1.2),-PI/2)
	for index in range(2):
		ship.model(root,"AST-STF-001.glb","OuterNorthReturn",Vector3(-61.08,0,-1.2-index*1.2),PI/2)
		ship.model(root,"AST-STF-001.glb","OuterSouthReturn",Vector3(-61.08,0,3.6-index*1.2),PI/2)
	var doorway := (load("res://scripts/service_door.gd") as GDScript).new() as Node3D
	doorway.name = "SynthesisServiceDoor"
	doorway.persistent_id = &"D01_food_synthesis_service_door_A"
	doorway.position = Vector3(-61.14,0,0)
	doorway.rotation.y = PI/2
	root.add_child(doorway)
	var ceiling_material := ship.surface("staff_white_paint",Color.WHITE) as StandardMaterial3D
	ceiling_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	ship.floor_mesh(root,"ServiceCeiling",PackedVector2Array([Vector2(-68.4,-3.6),Vector2(-61.2,-3.6),Vector2(-61.2,3.6),Vector2(-68.4,3.6)]),3.4,ceiling_material,false)
	for z in [-2.4,2.4]:
		for index in range(6):
			ship.model(root,"AST-STF-004.glb","OverheadServiceRun",Vector3(-68.4+index*1.2,3.4,z))
		for x in [-67.2,-63.6]:
			var fixture := ship.model(root,"AST-STF-006.glb","GuardedUtilityFixture",Vector3(x,3.4,z*0.5)) as Node3D
			var light := SpotLight3D.new()
			root.add_child(light)
			var lens := fixture.find_child("*staff_opal",true,false) as MeshInstance3D
			assert(lens != null)
			var bounds := lens.get_aabb()
			light.global_position = lens.to_global(bounds.position+bounds.size*Vector3(0.5,0,0.5))+Vector3.DOWN*0.008
			var luminous := lens.get_active_material(0).duplicate() as StandardMaterial3D
			luminous.emission_enabled = true
			luminous.emission = Color(0.82,0.9,1.0)
			luminous.emission_energy_multiplier = 1.1
			lens.material_override = luminous
			light.rotation.x = -PI/2
			light.spot_angle = 68
			ship.apply_light_profile(light,"staff_work")
	ship.model(root,"AST-STF-007.glb","SupplyAndWorkCabinet",Vector3(-64.2,0,-3.45))
	ship.model(root,"AST-ENG-001.glb","TransferPump",Vector3(-65.5,0,1.7))
	ship.model(root,"AST-ENG-002.glb","FilterVessel",Vector3(-67.2,0,2.0))
	ship.model(root,"AST-ENG-003.glb","WaterRecoveryConsole",Vector3(-62.7,1.35,-3.48))
