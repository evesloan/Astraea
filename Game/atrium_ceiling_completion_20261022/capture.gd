extends SceneTree
const P := "res://night_garden_atrium_interiors_20261022/"
const FINISH := "res://night_garden_court_completion_20261022/"
const Q := "res://night_garden_receiving_courts_20261022/"
const V := "res://night_garden_view_galleries_20261022/"
func _initialize() -> void: call_deferred("run")
func raw(file: String) -> Node3D:
	var doc := GLTFDocument.new(); var state := GLTFState.new()
	if doc.append_from_file("res://assets/models/"+file,state)!=OK:
		push_error("Missing retained context: "+file);quit(1);return null
	return doc.generate_scene(state)
func run() -> void:
	root.size = Vector2i(1400,900)
	var host: Node3D = load("res://night_garden_atrium_interiors_20261022/capture_host.gd").new(); root.add_child(host)
	var space := Node3D.new(); space.name="ShipSpace";host.add_child(space)
	var districts := Node3D.new();districts.name="Districts";space.add_child(districts)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(49.5,102,-58)
	var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
	var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
	var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
	var commons := raw("AST-COM-003.glb");wrapper.add_child(commons)
	for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
	load("res://night_garden_warm_interiors_20261022/adapter.gd").finish(host)
	load(P+"adapter.gd").finish(host)
	assert(not district.has_node("OuterViewGalleries20261022"))
	for entry in manager.entries:
		if str(entry.record.model_file)=="NightGardenD15Specialty_416_r002.glb":manager._load_entry(entry)
	var sources := {}
	for file in ["G7_Completion_R003_Body_1_03.glb","G7_Completion_R005B_Body_1_04.glb","G7_Completion_R003_Body_1_05.glb","G7_Completion_R008_Body_-1_03.glb","G7_Completion_R003_Body_-1_04.glb","G7_Completion_R003_Body_-1_05.glb","G7_Completion_R003_G7C3_D12_Court_0.glb","G7_Completion_R003_G7C3_D12_Court_1.glb","G7_Completion_R003_G7C3_D12_Court_2.glb","G7_Completion_R003_G7C3_D16_Court_0.glb","G7_Completion_R003_G7C3_D16_Court_1.glb","G7_Completion_R003_G7C3_D16_Court_2.glb","G7_Completion_R006B_G7C6_D12_ComposedEdge.glb","G7_Completion_R006B_G7C6_D16_ComposedEdge.glb","G7_Completion_R007B_G7C7_D12_ForeGardenCourt.glb","G7_Completion_R007B_G7C7_D16_ForeGardenCourt.glb"]:
		districts.add_child(raw(file));sources[file]=FileAccess.get_sha256("res://assets/models/"+file)
	host.model(districts,"AST-HUL-001.glb","RetainedLowerHull",Vector3.ZERO)
	host.model(districts,"AST-HUL-002.glb","RetainedUpperHull",Vector3.ZERO)
	var structural:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var nearby_regions:Array=[]
	for region in structural.regions:
		if (float(region.floor_y)>=78 and float(region.floor_y)<=106.5) or str(region.id).ends_with("_atrium_circulation"):nearby_regions.append(region)
	load("res://scripts/structural_floor_builder.gd").build_regions(space,host.surface("warm_stone",Color.WHITE),host.surface("ivory_enamel",Color.WHITE),nearby_regions)
	host.model(space,"AST-ATR-001.glb","RetainedAtriumGuards",Vector3.ZERO)
	load("res://scripts/atrium_garden.gd").build(districts,host)
	load("res://scripts/atrium_lighting.gd").build(districts,host)

	# Existing installed neighbors and streets were absent from the previous bounded view.
	var units:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/NIGHT_GARDEN_UNITS.json"))
	var prototypes:Dictionary={}
	for prototype in units.prototypes:prototypes[str(prototype.key)]=prototype
	var neighbors:=0
	for unit in units.units:
		if float(unit.allocation_x[0])>70 or absf(float(unit.allocation_z[0]))>95:continue
		var prototype:Dictionary=prototypes[str(unit.source_recipe_key)]
		assert(FileAccess.get_sha256("res://assets/models/"+str(prototype.model_file))==str(prototype.sha256))
		var neighbor:=raw(str(prototype.model_file));districts.add_child(neighbor)
		neighbor.position=Vector3(unit.source_origin_world_xyz[0],unit.source_origin_world_xyz[1],unit.source_origin_world_xyz[2]);neighbor.rotation.y=float(unit.source_yaw_godot);neighbors+=1
	host.stone=host.surface("warm_stone",Color.WHITE);host.ivory=host.surface("ivory_enamel",Color.WHITE);host.metal=host.surface("champagne_metal",Color.WHITE)
	load("res://scripts/central_house_connections.gd").build(host)
	load(Q+"adapter.gd").build(host)
	load(FINISH+"adapter.gd").finish(host)
	load("res://atrium_ceiling_completion_20261022/adapter.gd").finish(host)
	load("res://scripts/primary_atrium_core.gd").build(districts,host)
	load("res://scripts/atrium_gallery_receiving.gd").build(host)
	assert(neighbors==36)
	var environment:=Environment.new()
	var material:=ShaderMaterial.new();material.shader=load("res://shaders/astraea_space.gdshader");material.set_shader_parameter("use_radiance_cache",false)
	var sky:=Sky.new();sky.sky_material=material;sky.process_mode=Sky.PROCESS_MODE_QUALITY;sky.radiance_size=Sky.RADIANCE_SIZE_256
	environment.sky=sky;environment.background_mode=Environment.BG_SKY
	environment.ambient_light_source=Environment.AMBIENT_SOURCE_SKY;environment.ambient_light_sky_contribution=0
	environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2
	environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
	var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
	var budget:Node=load(FINISH+"lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);await physics_frame;await physics_frame;budget.configure(host,actor)
	var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(49.5,103.65,-58);camera.look_at(Vector3(-16,96,22));camera.fov=90;camera.far=1600;camera.current=true
	var layer:=CanvasLayer.new();root.add_child(layer)
	var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_color",Color.WHITE);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2)
	label.text="CENTRAL ATRIUM / D17 GALLERY TO FULL CAP\nActual district source assembly — UNFINISHED / FINAL ACCEPTANCE PENDING"
	for frame in range(8): await process_frame
	await RenderingServer.frame_post_draw
	var path:="res://atrium_ceiling_completion_20261022/evidence/DISTRICT_ATRIUM_CEILING_UNFINISHED.png"
	assert(not FileAccess.file_exists(path))
	assert(root.get_texture().get_image().save_png(path)==OK)
	var receipt={"created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"camera_godot":[49.5,103.65,-58],"target_godot":[-16,96,22],"sources":sources,"window_source":P+"runtime/NG416_shell_r002.scn","scope":"Actual bounded Godot source assembly, new paired receiving courts with native canopy and fixture sources,36 previously omitted installed neighbors plus existing street floors/guards,retained commons,14 inner shells,16 preserved warm outer shells,416 coordinated private details,six retained hull models,ten retained upper/lower court packages,original atrium guard/garden/lighting builders,actual compiled floor regions Y78–106.5 and two original hull models,original space shader and source-light budget","new_ceiling_scene_sha256":FileAccess.get_sha256("res://atrium_ceiling_completion_20261022/runtime/AtriumLanternCeiling_r001.scn"),"additional_retained_context":["all16 atrium circulation levels","primary atrium vertical core","registered gallery fittings"],"existing_neighbors_restored_to_fixture":neighbors,"new_courts_scene_sha256":FileAccess.get_sha256(FINISH+"runtime/ResortCourts_r003.scn"),"active_sources":budget.previously_active.map(func(light):return str(light.get_path())),"source_limit":budget.shadow_source_budget,"compiler_finish_geometry_unchanged":true,"rejected_gallery_present":false,"main_integrated":false,"visual_accepted":false,"reference_pixels_locally_inspected":false}
	var out:=FileAccess.open("res://atrium_ceiling_completion_20261022/evidence/CAPTURE.json",FileAccess.WRITE);out.store_string(JSON.stringify(receipt,"\t")+"\n");out.close()
	print("FRONTAGE_CONTEXT_CAPTURED ",path)
	quit()
