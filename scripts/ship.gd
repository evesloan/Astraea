extends Node3D
var deck_y: Array[float] = []
var d09_y := 0.0
var stone: StandardMaterial3D
var ivory: StandardMaterial3D
var metal: StandardMaterial3D
var glass: StandardMaterial3D

func _ready() -> void:
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for datum in contract.deck_datums: deck_y.append(float(datum.floor_elevation_m))
	d09_y = deck_y[8]
	stone = surface("warm_stone", Color.WHITE)
	ivory = surface("ivory_enamel", Color.WHITE)
	metal = surface("champagne_metal", Color(0.65,0.68,0.68))
	glass = StandardMaterial3D.new()
	glass.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass.albedo_color = Color(0.24,0.49,0.51,0.22)
	glass.roughness = 0.2
	glass.cull_mode = BaseMaterial3D.CULL_DISABLED
	var environment: Environment = $WorldEnvironment.environment
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.75,0.81,0.86)
	environment.ambient_light_energy = 0.2
	environment.glow_enabled = true
	environment.glow_intensity = 0.18
	environment.glow_hdr_threshold = 0.95
	environment.ssao_enabled = true
	environment.ssao_radius = 0.65
	environment.ssao_intensity = 0.45
	build_structural_datums()
	load("res://scripts/structural_floor_builder.gd").build($ShipSpace,stone,ivory)
	model($ShipSpace,"AST-ARC-001.glb","D06_SweptGalleryBay_Draft",Vector3(-48,deck_y[5],0),PI/2)
	build_retail_terrace()
	var player := CharacterBody3D.new()
	player.set_script(load("res://scripts/player.gd"))
	$ShipSpace/PersistentActors.add_child(player)
	player.spawn_position = Vector3(63.0,d09_y+0.1,-20.5)
	player.position = player.spawn_position

func surface(role: String, color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	var path := "res://assets/textures/" + role + ".png"
	if ResourceLoader.exists(path): material.albedo_texture = load(path)
	material.roughness = 0.83
	material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return material

func floor_mesh(parent: Node3D, label: String, points: PackedVector2Array, y: float, material: Material, collision: bool = true) -> MeshInstance3D:
	var triangles := Geometry2D.triangulate_polygon(points)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for n in range(0,triangles.size(),3):
		var a := Vector3(points[triangles[n]].x,y,points[triangles[n]].y)
		var b := Vector3(points[triangles[n+1]].x,y,points[triangles[n+1]].y)
		var c := Vector3(points[triangles[n+2]].x,y,points[triangles[n+2]].y)
		if (b-a).cross(c-a).y < 0.0:
			var swap := b; b = c; c = swap
		# Godot front faces use clockwise winding.
		for vertex in [a,c,b]:
			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(vertex.x,vertex.z)*0.3)
			st.add_vertex(vertex)
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.name = label
	instance.mesh = st.commit()
	parent.add_child(instance)
	if collision: instance.create_trimesh_collision()
	return instance

func beam(parent: Node3D, label: String, a: Vector3, b: Vector3, radius: float, material: Material) -> void:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = a.distance_to(b)
	mesh.radial_segments = 8
	mesh.rings = 1
	var instance := MeshInstance3D.new()
	instance.name = label
	instance.mesh = mesh
	instance.material_override = material
	parent.add_child(instance)
	instance.position = (a+b)*0.5
	var direction := (b-a).normalized()
	var right := direction.cross(Vector3.FORWARD)
	if right.length_squared() < 0.01: right = direction.cross(Vector3.RIGHT)
	right = right.normalized()
	instance.basis = Basis(right,direction,right.cross(direction)).orthonormalized()

func model(parent: Node3D, file: String, label: String, location: Vector3, yaw: float = 0.0) -> Node3D:
	var wrapper := Node3D.new()
	wrapper.name = label
	parent.add_child(wrapper)
	wrapper.position = location
	wrapper.rotation.y = yaw
	var visual := (load("res://assets/models/"+file) as PackedScene).instantiate()
	wrapper.add_child(visual)
	if not file.begins_with("AST-BOT"):
		_static_contacts(visual)
	return wrapper

func build_structural_datums() -> void:
	var structure := Node3D.new()
	structure.name = "All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE"
	$ShipSpace.add_child(structure)
	# Reversible hull-station study fitted to the overview, not finished hull or room allocation.
	var stations := [Vector2(-541,2),Vector2(-480,48),Vector2(-360,105),Vector2(-280,120),Vector2(0,120),Vector2(280,110),Vector2(450,82),Vector2(541,64)]
	for d in range(18):
		var deck := Node3D.new()
		deck.name = "D%02d_Datum" % (d+1)
		structure.add_child(deck)
		for side in [-1.0,1.0]:
			for i in range(stations.size()-1):
				var a: Vector2 = stations[i]; var b: Vector2 = stations[i+1]
				beam(deck,"HullDatum_%d_%d"%[int(side),i],Vector3(a.y*side,deck_y[d],a.x),Vector3(b.y*side,deck_y[d],b.x),0.14,metal)

func build_retail_terrace() -> void:
	var district := Node3D.new()
	district.name = "D09_StarboardTerrace_AuthoredFootprint_WIP"
	$ShipSpace/Districts.add_child(district)
	var outline := PackedVector2Array([Vector2(48,-34),Vector2(66,-34),Vector2(72,-30),Vector2(76,-22),Vector2(76,-10),Vector2(70,-3),Vector2(60,4),Vector2(48,4)])
	# Floor is supplied by the compiled layout, with this authored footprint taking priority.
	# Quiet bay remains one assembled source family with its actual mating offset.
	var bay := Node3D.new()
	bay.name = "QuietReturn"
	district.add_child(bay)
	bay.position = Vector3(63.5,d09_y,-27)
	model(bay,"AST-SAL-003.glb","BookSeatBay",Vector3.ZERO)
	model(bay,"AST-SAL-002.glb","MatedOverhead",Vector3(-3.1,0,0))
	model(district,"AST-SAL-001.glb","PublicPortal_NoDoorYet",Vector3(52,d09_y,0),PI/2)
	model(district,"AST-FUR-001_day_window_bench.glb","CourtBench",Vector3(52.5,d09_y,-29),-PI/2)
	model(district,"AST-FUR-002_day_reading_chair.glb","ReadingChair",Vector3(56.2,d09_y,-34),-PI/2)
	model(district,"AST-FUR-003_day_table.glb","LowReadingTable",Vector3(54.8,d09_y,-33))
	model(district,"AST-GST-001.glb","ReadingLamp",Vector3(57,d09_y,-32))
	model(district,"AST-BOT-001.glb","SmallCanopy",Vector3(52.5,d09_y,-21))
	model(district,"AST-BOT-002.glb","Understory",Vector3(53.8,d09_y,-21))
	model(district,"AST-BOT-006.glb","PlantedSeatTerminal",Vector3(55,d09_y,-23))
	# Actual lights colocated with fixtures, not an unexplained directional sun.
	var light := OmniLight3D.new()
	light.name = "ReadingLampActualLight"
	district.add_child(light)
	light.position = Vector3(57,d09_y+1.3,-32)
	light.light_color = Color(1.0,0.83,0.65)
	light.light_energy = 1.4
	light.omni_range = 7.5
	light.shadow_enabled = true
	for side in [-1.6,1.6]:
		# Bind to the source's real lens surface, not an arbitrary room-light location.
		var marker: Node3D = bay.find_child("DATUM_fixture_lens_" + str(side).replace(".","_"),true,false)
		assert(marker != null, "Missing source fixture datum")
		var fixture := SpotLight3D.new()
		fixture.name = "QuietBayTaskLight_" + str(side)
		district.add_child(fixture)
		fixture.global_position = marker.global_position + Vector3.DOWN * 0.02
		fixture.rotation.x = -PI/2
		fixture.spot_angle = 62.0
		apply_light_profile(fixture, "guest_reading")
		var luminous := StandardMaterial3D.new()
		luminous.albedo_color = Color(0.9,0.85,0.72)
		luminous.emission_enabled = true
		luminous.emission = Color(1.0,0.88,0.68)
		luminous.emission_energy_multiplier = 1.35
		var lens := MeshInstance3D.new()
		lens.name = "SourceLensEmission_" + str(side)
		var face := QuadMesh.new()
		face.size = Vector2(0.245,0.145)
		lens.mesh = face
		lens.material_override = luminous
		district.add_child(lens)
		lens.global_position = marker.global_position + Vector3.DOWN*0.002
		lens.rotation.x = PI/2
	# Boundary protection for the currently playable floor; final authored guards pending.
	for i in range(outline.size()):
		var a := Vector3(outline[i].x,d09_y,outline[i].y)
		var b := Vector3(outline[(i+1)%outline.size()].x,d09_y,outline[(i+1)%outline.size()].y)
		# The six-metre ring continues through both ends of this terrace.
		# Keep its shared surface open rather than fencing the allocation shut.
		if i == 0: a.x = 54.0
		if i == 6: b.x = 54.0
		beam(district,"EdgeRail_%d"%i,a+Vector3.UP*1.05,b+Vector3.UP*1.05,0.045,metal)
		beam(district,"EdgePost_%d"%i,a,a+Vector3.UP*1.05,0.045,metal)
		var body := StaticBody3D.new()
		body.name = "TemporaryBoundary_%d"%i
		district.add_child(body)
		body.position = (a+b)*0.5+Vector3.UP*0.6
		body.rotation.y = -atan2(b.z-a.z,b.x-a.x)
		var collider := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = Vector3(a.distance_to(b),1.2,0.09)
		collider.shape = shape
		body.add_child(collider)

func apply_light_profile(light: Light3D, profile_name: String) -> void:
	var profiles: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/lighting_profiles.json"))
	var profile: Dictionary = profiles[profile_name]
	light.light_color = Color(profile.color[0],profile.color[1],profile.color[2])
	light.light_energy = profile.energy
	if light is OmniLight3D: light.omni_range = profile.range_m
	elif light is SpotLight3D: light.spot_range = profile.range_m
	light.shadow_enabled = profile.shadows

func set_display_effects(enabled: bool) -> void:
	var environment: Environment = $WorldEnvironment.environment
	environment.glow_enabled = enabled
	environment.ssao_enabled = enabled

func _static_contacts(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		node.create_trimesh_collision()
	for child in node.get_children():
		if not child is StaticBody3D: _static_contacts(child)

func express_arrive(deck_index: int) -> bool:
	if deck_index < 0 or deck_index >= deck_y.size(): return false
	var player: CharacterBody3D = $ShipSpace/PersistentActors/Player
	var arrival := Vector3(5.5,deck_y[deck_index]+0.1,-72)
	var query := PhysicsRayQueryParameters3D.create(arrival+Vector3.UP,arrival-Vector3.UP*2)
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty(): return false
	player.position = arrival
	player.spawn_position = arrival
	player.velocity = Vector3.ZERO
	return true
