extends RefCounted
# Existing D06_directory_05: eastern garden-room subset, not a new room registry.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "D06_CanopyTerrace_Arrival_WIP"
	parent.add_child(root)
	var shell := ship.model(root,"AST-GAR-004.glb","CanopyTerraceAuthoredRoom",Vector3(-52,27,0)) as Node3D
	for pocket in range(2):
		for item in range(5):
			var marker := shell.find_child("DATUM_plant_%d_%d" % [pocket,item],true,false) as Node3D
			assert(marker != null)
			ship.model(root,"AST-BOT-001.glb" if item%2==0 else "AST-BOT-007.glb","GardenCanopy_%d_%d" % [pocket,item],marker.global_position,item*.9+pocket)
	for i in range(4):
		var marker := shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		var source := SpotLight3D.new()
		root.add_child(source)
		source.name = "CanopyPendant_"+str(i)
		source.global_position = marker.global_position
		source.rotation.x = -PI/2
		source.spot_range = 10
		source.spot_angle = 72
		source.light_energy = 2.3
		source.light_color = Color(1,.96,.88)
		source.shadow_enabled = true
	# Conversation groups sit against the planted edges, leaving the spine clear.
	for group in [{"center":Vector3(-67,27,-3.2),"axis":0.0},{"center":Vector3(-60.5,27,5),"axis":PI/2}]:
		var center: Vector3 = group.center
		ship.model(root,"AST-FUR-003_day_table.glb","CanopyConversationTable",center)
		for side in [-1,1]:
			var offset := Vector3(1.25*side,0,0).rotated(Vector3.UP,group.axis)
			var yaw := atan2(-offset.x,-offset.z)
			ship.model(root,"AST-FUR-002_day_reading_chair.glb","CanopyConversationChair",center+offset,yaw)
