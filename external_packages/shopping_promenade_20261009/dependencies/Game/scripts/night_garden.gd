extends RefCounted
# A fitted destination in the existing D12 Night garden allocation.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D12_NightGarden_WIP"
	root.set_meta("allocation_programme","Night garden")
	root.set_meta("programme_key","D12_directory_06")
	root.set_meta("historical_room_id","D12_quiet_garden5")
	parent.add_child(root)
	var shell:=ship.model(root,"AST-GAR-006.glb","NightGardenArchitecture",Vector3(52,78,0)) as Node3D
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("NG_glass*","MeshInstance3D",true,false):mesh.material_override=glass
	for court in range(4):
		for i in range(7):
			var marker:=shell.find_child("DATUM_plant_%d_%d"%[court,i],true,false) as Node3D
			var file:String=["AST-BOT-001.glb","AST-BOT-007.glb","AST-BOT-009.glb","AST-BOT-002.glb"][i%4]
			ship.model(root,file,"NightGardenPlant_%d_%d"%[court,i],marker.global_position,i*.75+court)
		for j in range(16):
			var marker:=shell.find_child("DATUM_underplant_%d_%d"%[court,j],true,false) as Node3D
			ship.model(root,"AST-BOT-002.glb","NightGardenUnderplant_%d_%d"%[court,j],marker.global_position,j*.7)
		for j in range(8):
			var marker:=shell.find_child("DATUM_flower_%d_%d"%[court,j],true,false) as Node3D
			ship.model(root,"AST-BOT-003.glb","NightGardenFlower_%d_%d"%[court,j],marker.global_position,j*.8)
	for i in range(6):
		var marker:=shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="NightGardenLocalSource_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_range=16
		light.spot_angle=74
		light.light_energy=2.2
		light.light_color=Color(1,.96,.88)
		light.shadow_enabled=true
	for i in range(2):
		var marker:=shell.find_child("DATUM_uplight_"+str(i),true,false) as Node3D
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="NightGardenPlanterUplight_"+str(i)
		light.global_position=marker.global_position
		light.rotation.x=PI/2
		light.spot_range=7.5
		light.spot_angle=60
		light.light_energy=1.0
		light.light_color=Color(1,.90,.76)
		light.shadow_enabled=true
	for i in range(3):
		var marker:=shell.find_child("DATUM_conversation_"+str(i),true,false) as Node3D
		var center:=marker.global_position
		ship.model(root,"AST-FUR-003_day_table.glb","NightGardenTable_"+str(i),center)
		for side in [-1,1]:
			ship.model(root,"AST-FUR-002_day_reading_chair.glb","NightGardenConversation_%d_%d"%[i,side],center+Vector3(0,0,side*1.25),PI if side>0 else 0)
