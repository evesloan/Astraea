extends SceneTree
const P := "res://night_garden_panoramic_suites_20261022/"
const V := "res://night_garden_view_galleries_20261022/"
func _initialize() -> void: call_deferred("run")
func raw(file: String) -> Node3D:
	var doc := GLTFDocument.new(); var state := GLTFState.new()
	assert(doc.append_from_file("res://assets/models/"+file,state)==OK)
	return doc.generate_scene(state)
func run() -> void:
	root.size = Vector2i(1400,900)
	var host: Node3D = load("res://night_garden_panoramic_suites_20261022/fixture_host.gd").new(); root.add_child(host)
	var space := Node3D.new(); space.name="ShipSpace";host.add_child(space)
	var districts := Node3D.new();districts.name="Districts";space.add_child(districts)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(95.1,93,-47.7)
	var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
	var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
	var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
	var commons := raw("AST-COM-003.glb");wrapper.add_child(commons)
	for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
	load(P+"adapter.gd").finish(host)
	assert(not district.has_node("OuterViewGalleries20261022"))
	for entry in manager.entries:
		if str(entry.record.model_file)=="NightGardenD15Specialty_428_r002.glb":manager._load_entry(entry)
	var sources := {}
	for file in ["G7_Completion_R003_Body_1_03.glb","G7_Completion_R005B_Body_1_04.glb","G7_Completion_R003_Body_1_05.glb"]:
		districts.add_child(raw(file));sources[file]=FileAccess.get_sha256("res://assets/models/"+file)
	var environment:=Environment.new()
	var material:=ShaderMaterial.new();material.shader=load("res://shaders/astraea_space.gdshader");material.set_shader_parameter("use_radiance_cache",false)
	var sky:=Sky.new();sky.sky_material=material;sky.process_mode=Sky.PROCESS_MODE_QUALITY;sky.radiance_size=Sky.RADIANCE_SIZE_256
	environment.sky=sky;environment.background_mode=Environment.BG_SKY
	environment.ambient_light_source=Environment.AMBIENT_SOURCE_SKY;environment.ambient_light_sky_contribution=0
	environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2
	environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
	var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.configure(host,actor)
	var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(95.1,94.65,-47.7);camera.look_at(Vector3(111,95,-50.5));camera.fov=75;camera.far=1600;camera.current=true
	var layer:=CanvasLayer.new();root.add_child(layer)
	var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_color",Color.WHITE);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2)
	label.text="NIGHT GARDEN 428 • PANORAMIC SUITE SUCCESSOR\nActual construction candidate • wide opening + relocated rest • FINAL ACCEPTANCE PENDING"
	for frame in range(8): await process_frame
	await RenderingServer.frame_post_draw
	var path:=P+"evidence/RESIDENT_428_PANORAMIC_SUITE_UNFINISHED.png"
	assert(not FileAccess.file_exists(path))
	assert(root.get_texture().get_image().save_png(path)==OK)
	var receipt={"created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"camera_godot":[95.1,94.65,-47.7],"target_godot":[111,95,-50.5],"sources":sources,"window_source":P+"runtime/NG428_shell_r001.scn","scope":"Actual bounded Godot source assembly, retained commons,14 original inner shells,16 panoramic outer shells,428 coordinated private details,three reviewed hull models,original space shader and source-light budget","rejected_gallery_present":false,"main_integrated":false,"visual_accepted":false,"reference_pixels_locally_inspected":false}
	var out:=FileAccess.open(P+"evidence/CAPTURE.json",FileAccess.WRITE);out.store_string(JSON.stringify(receipt,"\t")+"\n");out.close()
	print("FRONTAGE_CONTEXT_CAPTURED ",path)
	quit()
