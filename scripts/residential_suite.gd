extends RefCounted
# A fitted subset of the existing census, not a replacement room registry.
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D13_13017_profile.json"))
	var root := Node3D.new()
	root.name = "D13_13017_TwinSuite_WIP"
	root.set_meta("historical_address","13017")
	root.set_meta("rebuild_identity",data.rebuild_identity)
	parent.add_child(root)
	var shell := ship.model(root,"AST-SUI-001.glb","AuthoredTwinSuite",Vector3(81.95,84,-42),PI/2) as Node3D
	var pane := ShaderMaterial.new()
	pane.shader = load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("SUI_Runtime_glass*","MeshInstance3D",true,false): mesh.material_override = pane
	for i in range(2):
		var marker := shell.find_child("DATUM_bed_"+str(i),true,false) as Node3D
		assert(marker != null)
		ship.model(root,"AST-SLP-001.glb","HistoricalBedAnchor_"+str(i),marker.global_position,PI/2)
	for i in range(3):
		var marker := shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		var light := SpotLight3D.new()
		root.add_child(light)
		light.name = "SuiteSource_"+str(i)
		light.global_position = marker.global_position
		light.rotation.x = -PI/2
		light.spot_range = 5.5
		light.spot_angle = 70
		light.light_energy = 1.15
		light.light_color = Color(1,.96,.89)
		light.shadow_enabled = true
	var marker := shell.find_child("DATUM_living_bench",true,false) as Node3D
	ship.model(root,"AST-FUR-001_day_window_bench.glb","LivingWindowBench",marker.global_position,PI)
	marker = shell.find_child("DATUM_living_table",true,false) as Node3D
	ship.model(root,"AST-FUR-003_day_table.glb","LivingTable",marker.global_position,PI/2)
	for i in range(2):
		var bedside := shell.find_child("DATUM_bed_table_"+str(i),true,false) as Node3D
		ship.model(root,"AST-FUR-003_day_table.glb","BedsideTable_"+str(i),bedside.global_position,PI/2)
		var source := shell.find_child("DATUM_bed_light_"+str(i),true,false) as Node3D
		var light := OmniLight3D.new()
		root.add_child(light)
		light.name = "SuiteBedsideSource_"+str(i)
		light.global_position = source.global_position
		light.omni_range = 2.6
		light.light_energy = .85
		light.light_color = Color(1,.94,.84)
		light.shadow_enabled = true
	# Guard exposed slab edges while adjoining census units remain unbuilt.
	# Entry portals and the connection to the original atrium stay open.
	var edges := [[Vector2(54,-36),Vector2(54,-30)],[Vector2(54,-36),Vector2(63,-36)],[Vector2(63,-36),Vector2(69.05,-38.4)],[Vector2(54,-48),Vector2(63,-48)],[Vector2(63,-48),Vector2(69.05,-45.6)],[Vector2(50,-26),Vector2(86.05,-26)],[Vector2(54,-30),Vector2(81.95,-30)],[Vector2(81.95,-51),Vector2(86.05,-51)],[Vector2(86.05,-51),Vector2(86.05,-26)],[Vector2(81.95,-51),Vector2(81.95,-45.6)],[Vector2(81.95,-38.4),Vector2(81.95,-30)]]
	for i in range(edges.size()):
		var a := Vector3(edges[i][0].x,84,edges[i][0].y)
		var b := Vector3(edges[i][1].x,84,edges[i][1].y)
		ship.beam(root,"GalleryGuardRail_"+str(i),a+Vector3.UP*1.1,b+Vector3.UP*1.1,.04,ship.metal)
		for t in [0.0,.25,.5,.75,1.0]:
			var point := a.lerp(b,t)
			ship.beam(root,"GalleryGuardPost",point,point+Vector3.UP*1.1,.035,ship.metal)
		var body := StaticBody3D.new()
		root.add_child(body)
		body.position=(a+b)*.5+Vector3.UP*.55
		body.rotation.y=-atan2(b.z-a.z,b.x-a.x)
		var collider := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size=Vector3(a.distance_to(b),1.1,.08)
		collider.shape=shape
		body.add_child(collider)
	# Visible bearing composition beneath the new view terrace, keeping the
	# D12 cross-street centre clear. This is not structural-load certification.
	for z in [-47.2,-36.8]:
		ship.model(root,"AST-STR-001-H576.glb","WindowTerraceBearing",Vector3(54,78,z),0)
		ship.beam(root,"WindowTerraceCantilever",Vector3(54,83.55,z),Vector3(68.8,83.55,z),.19,ship.metal)
		ship._static_contacts(root.get_child(root.get_child_count()-1))
		ship.beam(root,"WindowTerraceDiagonal",Vector3(54,80.3,z),Vector3(68.8,83.55,z),.16,ship.metal)
		ship._static_contacts(root.get_child(root.get_child_count()-1))
