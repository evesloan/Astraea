extends RefCounted
# Permanent connected section; no completed waterpark or swimming claim.
static func build(parent: Node3D, ship: Node3D) -> void:
	var root := Node3D.new()
	root.name = "GentleWaters_LivingGifts_Vesper_Section_WIP"
	parent.add_child(root)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/aquatic_section.json"))
	var enclosure:Node3D=ship.model(root,"AST-CIR-004.glb","AquaticLiftEnclosure",Vector3(12,44,235))
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="AquaticPassengerLift"
	lift.floor_heights.assign([44.0,52.5,61.0])
	lift.deck_numbers.assign([8,9,10])
	lift.gate_origin_xz=Vector2(12,235)
	lift.identity_prefix="aquatic"
	lift.district_label="Aquatic"
	lift.cabin_file="AST-CIR-003_three_stop.glb"
	lift.persistent_id=&"aquatic_lift_001"
	root.add_child(lift)
	var ceiling:Node3D=ship.model(root,"AST-AQU-012.glb","AquaticAuthoredCeiling",Vector3(8,61,182))
	for i in range(4):
		var marker:=ceiling.find_child("DATUM_ceiling_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=OmniLight3D.new()
		root.add_child(light)
		light.name="AquaticCoveSource_"+str(i)
		light.global_position=marker.global_position
		light.omni_range=12
		light.light_energy=1.0
		light.light_color=Color(1,.95,.87)
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
	var edges:Node3D=ship.model(root,"AST-AQU-013.glb","AquaticAuthoredBalconyEdges",Vector3(8,44,182))
	var guard_glass:=ShaderMaterial.new()
	guard_glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in edges.find_children("*","MeshInstance3D",true,false):
		if "glass" in part.name:part.material_override=guard_glass
	for deck in ["D09","D10"]:
		for i in range(4):
			var marker:=edges.find_child("DATUM_"+deck+"_light_"+str(i),true,false)as Node3D
			var receiver:=edges.find_child("DATUM_"+deck+"_receiver_"+str(i),true,false)as Node3D
			assert(marker!=null and receiver!=null)
			var light:=OmniLight3D.new()
			root.add_child(light)
			light.name="AquaticBalconySource_"+deck+"_"+str(i)
			light.global_position=marker.global_position
			light.look_at(receiver.global_position,Vector3.RIGHT if absf(receiver.global_position.x-marker.global_position.x)<.01 else Vector3.UP)
			light.omni_range=marker.global_position.distance_to(receiver.global_position)+2
			light.omni_attenuation=.7
			light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
			light.light_energy=2.2
			light.light_color=Color(1,.95,.88)
			light.shadow_enabled=true
			light.set_meta("illumination_anchor",receiver.global_position)
	var arrival:Node3D=ship.model(root,"AST-AQU-014.glb","GentleWatersArrival",Vector3(8,44,210))
	arrival.set_meta("programme_key","D08_directory_08")
	for part in arrival.find_children("ARR_finish_*","MeshInstance3D",true,false):
		var contact:=part.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	for lens in arrival.find_children("ARR_static_lens","MeshInstance3D",true,false):
		lens.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for i in range(2):
		var marker:=arrival.find_child("DATUM_arrival_light_"+str(i),true,false)as Node3D
		assert(marker!=null)
		var light:=OmniLight3D.new()
		root.add_child(light)
		light.name="GentleWatersArrivalSource_"+str(i)
		light.global_position=marker.global_position+Vector3.DOWN*.055
		light.omni_range=5.5
		light.omni_attenuation=.6
		light.light_energy=1.4
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true
		light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.shadow_normal_bias=1.5
		light.shadow_bias=.08
	load("res://scripts/living_gifts.gd").build(root,ship)
	load("res://scripts/vesper_dining.gd").build(root,ship)
	var basin: Dictionary = data.basin
	var boundary: Array = basin.boundary
	var vertices: Array[Vector3] = []
	for index in range(boundary.size()):
		var a: Array = boundary[index]
		var b: Array = boundary[(index+1)%boundary.size()]
		vertices.append_array([Vector3(a[0],basin.lip_y,a[1]),Vector3(b[0],basin.lip_y,b[1]),Vector3(b[0],basin.bottom_y,b[1]),Vector3(a[0],basin.lip_y,a[1]),Vector3(b[0],basin.bottom_y,b[1]),Vector3(a[0],basin.bottom_y,a[1])])
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for v in vertices:
		st.set_uv(Vector2(v.x,v.z)*0.5)
		st.add_vertex(v)
	st.generate_normals()
	st.set_material(ship.stone)
	var wall := MeshInstance3D.new()
	wall.name = "BasinRetainingWall"
	wall.mesh = st.commit()
	root.add_child(wall)
	wall.create_trimesh_collision()
	var water_material := ShaderMaterial.new()
	water_material.shader = load("res://shaders/shallow_water.gdshader")
	var water_outline := PackedVector2Array()
	for point in boundary: water_outline.append(Vector2(point[0],point[1]))
	water_material.set_shader_parameter("boundary",water_outline)
	var water_visual := ship.floor_mesh(root,"ShallowWaterVisual_NoSwimmingYet",water_outline,basin.water_y,water_material,false) as MeshInstance3D
	water_visual.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var retreat := ship.model(root,"AST-AQU-011.glb","ShelteredWetRetreat",Vector3(51,44,216),-PI/2) as Node3D
	for key in ["LOUNGER_LEFT","LOUNGER_RIGHT","TRAY"]:
		var datum := retreat.find_child("DATUM_"+key,true,false) as Node3D
		assert(datum != null)
		ship.model(root,"AST-AQU-002.glb" if key == "TRAY" else "AST-AQU-001.glb",key,datum.global_position,-PI/2)
	for index in range(2):
		var datum := retreat.find_child("DATUM_light_"+str(index),true,false) as Node3D
		var light := SpotLight3D.new()
		root.add_child(light)
		light.global_position = datum.global_position
		light.rotation.x = -PI/2
		ship.apply_light_profile(light,"guest_reading")
		light.light_energy = 0.7
		light.spot_range = 6
		light.spot_angle = 62
	for base_y in [44.0,52.5,61.0]:
		for location in [Vector2(20,186),Vector2(50,244),Vector2(12,243)]:
			var column := ship.model(root,"AST-STR-001-H810.glb" if base_y==61.0 else "AST-STR-001.glb","BearingColumn",Vector3(location.x,base_y,location.y)) as Node3D
			for index in range(4):
				var marker := column.find_child("DATUM_light_"+str(index),true,false) as Node3D
				assert(marker != null)
				var light := SpotLight3D.new()
				light.name = "ColumnDownlight"
				column.add_child(light)
				light.global_position = marker.global_position
				light.rotation.x = -PI/2
				light.spot_angle = 62
				light.spot_range = 12
				light.light_color = Color(1.0,0.91,0.78)
				light.light_energy = 0.45
				light.shadow_enabled = index == 0
	for base_y in [44.0,52.5]:
		var stairs := (load("res://assets/models/AST-CIR-001.glb") as PackedScene).instantiate()
		stairs.name = "Switchback_"+str(base_y)
		stairs.set_meta("catalogue_file","AST-CIR-001.glb")
		root.add_child(stairs)
		stairs.position = Vector3(10,base_y,200.5)
		for part in stairs.find_children("CIR_Guard*","MeshInstance3D",true,false):
			part.create_trimesh_collision()
		# Smooth contact beneath authored treads. No solid box fills the stairwell.
		_contact(root,[Vector3(10,base_y,200.5),Vector3(12.5,base_y,200.5),Vector3(12.5,base_y+4.25,193),Vector3(10,base_y+4.25,193)])
		_contact(root,[Vector3(10,base_y+4.25,193),Vector3(16,base_y+4.25,193),Vector3(16,base_y+4.25,190),Vector3(10,base_y+4.25,190)])
		_contact(root,[Vector3(13.5,base_y+8.5,200.5),Vector3(16,base_y+8.5,200.5),Vector3(16,base_y+4.25,193),Vector3(13.5,base_y+4.25,193)])

static func _contact(parent: Node3D, quad: Array[Vector3]) -> void:
	var body := StaticBody3D.new()
	body.name = "StairSmoothContact"
	var shape := ConcavePolygonShape3D.new()
	shape.backface_collision = true
	shape.set_faces(PackedVector3Array([quad[0],quad[2],quad[1],quad[0],quad[3],quad[2]]))
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	parent.add_child(body)
