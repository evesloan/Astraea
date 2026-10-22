extends "res://scripts/ship.gd"
# Explicit additive runtime successor. The predecessor builders and their gates remain intact.
const INDEX := "res://data/architecture/startup_residency_20261020/index.json"
signal construction_finished
signal runtime_ready
var startup_deferred_builders: Array[Callable] = []
var startup_previous_pause := false
var startup_steps := 0
var exact_contact_residency: Node
var streamed_models: Dictionary = {}
var exact_texture_intern: RefCounted
var d04_detail_residency: Node
var private_detail_residency: Node
func _ready() -> void:
	assert(FileAccess.get_sha256("res://scripts/startup_residency_20261020/ship.gd")=="22478e0ae0f6de5ef6dc331b775b0908890527f8705a2880ccd53d265cf8b8fe")
	exact_texture_intern = load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
	get_tree().node_added.connect(exact_texture_intern.observe)
	startup_previous_pause = get_tree().paused
	get_tree().paused = true
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX))
	assert(FileAccess.get_sha256("res://scripts/ship.gd") == str(data.predecessor_ship_sha256))
	streamed_models = data.models
	_verify_successor_routes()
	exact_contact_residency = load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new()
	exact_contact_residency.name = "ExactContactResidency"
	$ShipSystems.add_child(exact_contact_residency)
	exact_contact_residency.setup(self)
	private_detail_residency=load("res://scripts/night_garden_residency_20261022/manager.gd").new()
	private_detail_residency.name="PrivateDetailResidency"
	$ShipSystems.add_child(private_detail_residency)
	private_detail_residency.setup(self)
	d04_detail_residency=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new()
	d04_detail_residency.name="D04PrivateDetailResidency"
	$ShipSystems.add_child(d04_detail_residency)
	d04_detail_residency.setup(self)
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
	# Static world-oriented exterior, with zero sky contribution to indoor ambient.
	var space_material := ShaderMaterial.new()
	space_material.shader = load("res://shaders/astraea_space.gdshader")
	# Cached display was black on GL Compatibility; use the identical direct field.
	space_material.set_shader_parameter("use_radiance_cache",false)
	var space_sky := Sky.new()
	space_sky.sky_material = space_material
	space_sky.process_mode = Sky.PROCESS_MODE_QUALITY
	space_sky.radiance_size = Sky.RADIANCE_SIZE_256
	environment.sky = space_sky
	environment.background_mode = Environment.BG_SKY
	environment.background_energy_multiplier = 1.0
	environment.sky_rotation = Vector3.ZERO
	environment.sky_custom_fov = 0.0
	# GLES3 needs sky ambient enabled to generate the display cubemap.
	# A zero mix retains the exact existing color/energy above.
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	environment.ambient_light_sky_contribution = 0.0
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	environment.glow_enabled = true
	environment.glow_intensity = 0.18
	environment.glow_hdr_threshold = 0.95
	environment.ssao_enabled = true
	environment.ssao_radius = 0.65
	environment.ssao_intensity = 0.45
	# Construct the unchanged original actor before yielding: the original engineering
	# bank binds its camera once via call_deferred. Physics stays paused until ready.
	var player := CharacterBody3D.new()
	var player_successor:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/PLAYER_SUCCESSOR_20261019.json"))
	assert(FileAccess.get_sha256("res://scripts/player.gd")==str(player_successor.predecessor_player_sha256))
	assert(FileAccess.get_sha256("res://scripts/group6_completion/player_water_seat_20261019.gd")==str(player_successor.player_sha256))
	player.set_script(load("res://scripts/group6_swimming_20261019/player.gd"))
	$ShipSpace/PersistentActors.add_child(player)
	player.spawn_position = Vector3(63.0,d09_y+0.1,-20.5)
	player.position = player.spawn_position
	player.set_controls_enabled(false)
	build_structural_datums()
	var lower_hull:=model($ShipSpace/Districts,"AST-HUL-001.glb","LowerHullBody_WIP",Vector3.ZERO)
	lower_hull.set_meta("persistent_id","lower_hull_body_001")
	var upper_skin:=model($ShipSpace/Districts,"AST-HUL-002.glb","TheaterWestUpperHull_Skin_WIP",Vector3.ZERO)
	upper_skin.set_meta("persistent_id","theater_west_upper_hull_skin_002")
	load("res://scripts/structural_floor_builder.gd").build($ShipSpace,stone,ivory,{"staff_floor":surface("staff_floor",Color.WHITE)})
	await _construction_step("structural_floor_builder.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/structural_floor_builder.gd).build($ShipSpace,stone,ivory,{staff_floor:surface(staff_floor,Color.WHITE)})")
	if not load("res://scripts/botanical_pair_receiving.gd").validate_inputs():
		push_error("Botanical receiving successor inputs are not finalized")
		return
	model($ShipSpace,"AST-ATR-001_botanical_nursery_open001.glb","BotanicalCourtReceivingClosedInterim",Vector3.ZERO)
	model($ShipSpace,"AST-ARC-001.glb","D06_SweptGalleryBay_Draft",Vector3(-28.623,deck_y[5],0),PI/2)
	model($ShipSpace,"AST-ATR-001.glb","AuthoredAtriumGuards_All16Levels",Vector3.ZERO)
	build_retail_terrace()
	load("res://scripts/aquatic_section.gd").build($ShipSpace/Districts,self)
	await _construction_step("aquatic_section.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aquatic_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aquatic_annex_receiving.gd").build($ShipSpace/Districts,self)
	await _construction_step("aquatic_annex_receiving.gd")
	load("res://scripts/group6_completion/completion.gd").build($ShipSpace/Districts/AquaticRiverSlideAnnex_WIP,self)
	await _construction_step("group6_completion/completion.gd")
	load("res://scripts/group6_float_20261019/package.gd").build($ShipSpace/Districts/AquaticRiverSlideAnnex_WIP)
	await _construction_step("group6_float_20261019/package.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aquatic_annex_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/staff_section.gd").build($ShipSpace/Districts,self)
	await _construction_step("staff_section.gd")
	load("res://scripts/group1_synthesis_floor_receiving.gd").build(self)
	await _construction_step("group1_synthesis_floor_receiving.gd")
	load("res://scripts/group8/synthesis_plant.gd").build(self,true)
	await _construction_step("group8/synthesis_plant.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/staff_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/lower_staff_network.gd").build($ShipSpace/Districts,self)
	await _construction_step("lower_staff_network.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/lower_staff_network.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/atrium_lighting.gd").build($ShipSpace/Districts,self)
	await _construction_step("atrium_lighting.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/atrium_lighting.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/atrium_garden.gd").build($ShipSpace/Districts,self)
	await _construction_step("atrium_garden.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/atrium_garden.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/garden_overlook.gd").build($ShipSpace/Districts,self)
	await _construction_step("garden_overlook.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/garden_overlook.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/canopy_terrace.gd").build($ShipSpace/Districts,self)
	await _construction_step("canopy_terrace.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/canopy_terrace.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/central_house_connections.gd").build(self)
	await _construction_step("central_house_connections.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_house_connections.gd).build(self)")
	load("res://scripts/residential_suite.gd").build($ShipSpace/Districts,self)
	await _construction_step("residential_suite.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/residential_suite.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/residential_wayfinding.gd").build($ShipSpace/Districts,self)
	await _construction_step("residential_wayfinding.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/residential_wayfinding.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/night_garden.gd").build($ShipSpace/Districts,self)
	await _construction_step("night_garden.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/night_garden.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/vertical_commons.gd").build($ShipSpace/Districts,self)
	await _construction_step("vertical_commons.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/vertical_commons.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/retail_curios.gd").build($ShipSpace/Districts,self)
	await _construction_step("retail_curios.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/retail_curios.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/thread_shell.gd").build($ShipSpace/Districts,self)
	await _construction_step("thread_shell.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/thread_shell.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/orchard_exchange.gd").build($ShipSpace/Districts,self)
	await _construction_step("orchard_exchange.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/orchard_exchange.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/orchard_foodhall.gd").build($ShipSpace/Districts,self)
	await _construction_step("orchard_foodhall.gd")
	load("res://scripts/group8/orchard_service.gd").build(self)
	await _construction_step("group8/orchard_service.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/orchard_foodhall.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self)
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_CROWN_LINK.json")
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_CROWN_LINK.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/FORWARD_PUBLIC_CORE.json")
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/FORWARD_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json")
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json")
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_PUBLIC_CORE.json")
	await _construction_step("primary_atrium_core.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_PUBLIC_CORE.json)")
	load("res://scripts/central_command_crown.gd").build($ShipSpace/Districts,self)
	await _construction_step("central_command_crown.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_command_crown.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aft_command_crown.gd").build($ShipSpace/Districts,self)
	await _construction_step("aft_command_crown.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aft_command_crown.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/bridge_platform.gd").build($ShipSpace/Districts,self)
	await _construction_step("bridge_platform.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/bridge_platform.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/bridge_enclosure.gd").build($ShipSpace/Districts,self)
	await _construction_step("bridge_enclosure.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/bridge_enclosure.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aft_crown_platform.gd").build($ShipSpace/Districts,self)
	await _construction_step("aft_crown_platform.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aft_crown_platform.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/upper_horizon_enclosure.gd").build($ShipSpace/Districts,self)
	await _construction_step("upper_horizon_enclosure.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/upper_horizon_enclosure.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/arrivals_fusion.gd").build($ShipSpace/Districts,self)
	await _construction_step("arrivals_fusion.gd")
	load("res://scripts/group8/arrivals_service.gd").build(self)
	await _construction_step("group8/arrivals_service.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/arrivals_fusion.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/star_atlas.gd").build($ShipSpace/Districts,self)
	# Keep the original queued cabin-contact retirement and its fitted audit atomic.
	load("res://scripts/group2_vip_dry_club/package.gd").build_on_current_receiver($ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/star_atlas.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/star_atlas_fitted_receiving.gd").build($ShipSpace/Districts/D12_D14_StarAtlas_WIP,self)
	await _construction_step("star_atlas_fitted_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/star_atlas_fitted_receiving.gd).build($ShipSpace/Districts/D12_D14_StarAtlas_WIP,self)")
	load("res://scripts/d17_connected_house.gd").build($ShipSpace/Districts,self)
	await _construction_step("d17_connected_house.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/d17_connected_house.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_section.gd").build($ShipSpace/Districts,self)
	await _construction_step("grand_pool_section.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_first_pass.gd").build($ShipSpace/Districts,self)
	await _construction_step("grand_pool_first_pass.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_first_pass.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_finish.gd").build($ShipSpace/Districts,self)
	await _construction_step("grand_pool_finish.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_finish.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_architecture.gd").build($ShipSpace/Districts,self)
	await _construction_step("grand_pool_architecture.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_architecture.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/secondary_engineering_section.gd").build($ShipSpace/Districts,self)
	await _construction_step("secondary_engineering_section.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/secondary_engineering_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_lantern_theater_section.gd").build($ShipSpace/Districts,self)
	await _construction_step("grand_lantern_theater_section.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_lantern_theater_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/court_a_increment004.gd").build($ShipSpace/Districts,self)
	await _construction_step("court_a_increment004.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/court_a_increment004.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/theater_stair_walking_contacts.gd").build($ShipSpace/Districts)
	await _construction_step("theater_stair_walking_contacts.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/theater_stair_walking_contacts.gd).build($ShipSpace/Districts)")
	load("res://scripts/medical_welcome.gd").build($ShipSpace/Districts,self)
	await _construction_step("medical_welcome.gd")
	load("res://scripts/group8/medical_privacy.gd").build(self)
	await _construction_step("group8/medical_privacy.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/medical_welcome.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/d04_port_forward_receiving.gd").build(self)
	await _construction_step("d04_port_forward_receiving.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_forward_homes_first.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_forward_homes_first.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_forward_homes_second.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_forward_homes_second.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_forward_homes_third.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_forward_homes_third.gd")
	load("res://scripts/d04_port_forward_northern_receiving.gd").build(self)
	await _construction_step("d04_port_forward_northern_receiving.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_forward_homes_fourth.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_forward_homes_fourth.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_forward_homes_fifth.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_forward_homes_fifth.gd")
	load("res://scripts/d04_port_forward_commons_service.gd").build(self)
	await _construction_step("d04_port_forward_commons_service.gd")
	load("res://scripts/d04_port_forward_horticultural_service.gd").build(self)
	await _construction_step("d04_port_forward_horticultural_service.gd")
	load("res://scripts/d04_social_dayroom.gd").build(self)
	await _construction_step("d04_social_dayroom.gd")
	load("res://scripts/d04_commons_outlook_service.gd").build(self)
	await _construction_step("d04_commons_outlook_service.gd")
	load("res://scripts/d04_commons_cart_docking.gd").build(self)
	await _construction_step("d04_commons_cart_docking.gd")
	load("res://scripts/d04_commons_transport_routing.gd").build(self)
	await _construction_step("d04_commons_transport_routing.gd")
	load("res://scripts/d04_starboard_forward_north_receiving.gd").build(self)
	await _construction_step("d04_starboard_forward_north_receiving.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_starboard_forward_north_homes.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_starboard_forward_north_homes.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_starboard_forward_south_package.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_starboard_forward_south_package.gd")
	load("res://scripts/d04_starboard_full_commons.gd").build(self)
	await _construction_step("d04_starboard_full_commons.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_aft_neighborhood.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_aft_neighborhood.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_starboard_aft_neighborhood.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_starboard_aft_neighborhood.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_port_central_neighborhood.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_port_central_neighborhood.gd")
	load("res://scripts/startup_residency_20261020/d04/d04_starboard_central_neighborhood.gd").build(self)
	await _construction_step("startup_residency_20261020/d04/d04_starboard_central_neighborhood.gd")
	load("res://scripts/d04_port_aft_core_threshold.gd").build(self)
	await _construction_step("d04_port_aft_core_threshold.gd")
	load("res://scripts/d04_port_central_staff_riser.gd").build(self)
	await _construction_step("d04_port_central_staff_riser.gd")
	var cleaning_cart:RigidBody3D=(load("res://scripts/cleaning_cart.gd")as GDScript).new()
	cleaning_cart.name="CustodialCart"
	cleaning_cart.position=Vector3(85.2,84.04,-37.3)
	$ShipSpace/PersistentActors.add_child(cleaning_cart)

	load("res://scripts/d04_port_central_court_work_links.gd").build(self)
	await _construction_step("d04_port_central_court_work_links.gd")
	load("res://scripts/d04_port_central_west_staff_circuit.gd").build(self)
	await _construction_step("d04_port_central_west_staff_circuit.gd")
	load("res://scripts/d04_commons_transition_fore_staff.gd").fore_build(self)
	await _construction_step("d04_commons_transition_fore_staff.gd")
	load("res://scripts/d04_starboard_forward_work_branches.gd").build(self)
	await _construction_step("d04_starboard_forward_work_branches.gd")
	load("res://scripts/d04_starboard_forward_remaining_courts.gd").build(self)
	await _construction_step("d04_starboard_forward_remaining_courts.gd")
	load("res://scripts/d04_port_central_commons_recomposition.gd").build(self)
	await _construction_step("d04_port_central_commons_recomposition.gd")
	load("res://scripts/d04_starboard_central_court_routes.gd").build(self)
	await _construction_step("d04_starboard_central_court_routes.gd")
	load("res://scripts/d04_starboard_aft_court_routes.gd").build(self)
	await _construction_step("d04_starboard_aft_court_routes.gd")
	load("res://scripts/d04_commons_ceiling_junctions.gd").build(self)
	await _construction_step("d04_commons_ceiling_junctions.gd")
	load("res://scripts/d04_port_aft_court_routes.gd").build(self)
	await _construction_step("d04_port_aft_court_routes.gd")
	load("res://scripts/lower_shared_aft_staff_route.gd").build(self)
	await _construction_step("lower_shared_aft_staff_route.gd")
	load("res://scripts/d04_starboard_aft_commons_enclosure.gd").build(self)
	await _construction_step("d04_starboard_aft_commons_enclosure.gd")
	load("res://scripts/aft_crown_sitting_bays.gd").build(self)
	await _construction_step("aft_crown_sitting_bays.gd")
	load("res://scripts/aft_crown_sitting_lighting.gd").build(self)
	await _construction_step("aft_crown_sitting_lighting.gd")
	load("res://scripts/aft_crown_foyer_waiting_edges.gd").build(self)
	await _construction_step("aft_crown_foyer_waiting_edges.gd")
	load("res://scripts/group8/crown_interiors.gd").build(self,false)
	await _construction_step("group8/crown_interiors.gd")
	load("res://scripts/group4_boarding_safety.gd").build_terminals($ShipSpace/Districts)
	var lighting_budget := Node.new()
	lighting_budget.name = "LocalShadowSourceBudget"
	lighting_budget.set_script(load("res://scripts/lighting_budget.gd"))
	$ShipSystems.add_child(lighting_budget)
	preload("res://scripts/team_lounge_receiving.gd").build(self)
	load("res://scripts/movement_studio_receiving.gd").build($ShipSpace/Districts,self)
	load("res://scripts/startup_residency_20261020/immutable_source_contacts.gd").adopt($ShipSpace/Districts/D07_MovementStudio_Receiving_WIP/WholeRetainedMovementStudio.get_child(0),"res://assets/models/WP11_movement_studio_runtime_names001.glb",self)
	await _construction_step("movement_studio_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/movement_studio_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/moss_sanctuary_receiving.gd").build(self)
	load("res://scripts/startup_residency_20261020/immutable_source_contacts.gd").adopt($ShipSpace/D06_MossSanctuary_Receiving_WIP,"res://assets/models/WP10_moss_receiving_inert001.glb",self)
	await _construction_step("moss_sanctuary_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/moss_sanctuary_receiving.gd).build(self)")
	load("res://scripts/sports_care_receiving.gd").build($ShipSpace/Districts,self)
	await _construction_step("sports_care_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/sports_care_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/night_table_receiving.gd").build(self)
	await _construction_step("night_table_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/night_table_receiving.gd).build(self)")
	load("res://scripts/laundry_receiving.gd").build(self)
	await _construction_step("laundry_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/laundry_receiving.gd).build(self)")
	load("res://scripts/crew_batch_receiving.gd").build(self)
	await _construction_step("crew_batch_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/crew_batch_receiving.gd).build(self)")
	load("res://scripts/d12_pair_receiving.gd").build(self)
	await _construction_step("d12_pair_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/d12_pair_receiving.gd).build(self)")
	load("res://scripts/botanical_pair_receiving.gd").build(self)
	await _construction_step("botanical_pair_receiving.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/botanical_pair_receiving.gd).build(self)")
	load("res://scripts/tidal_garden_adoption.gd").build(self)
	await _construction_step("tidal_garden_adoption.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/tidal_garden_adoption.gd).build(self)")
	load("res://scripts/quiet_grove_adoption.gd").build(self)
	await _construction_step("quiet_grove_adoption.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/quiet_grove_adoption.gd).build(self)")
	load("res://scripts/family_terrace_adoption.gd").build(self)
	await _construction_step("family_terrace_adoption.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/family_terrace_adoption.gd).build(self)")
	load("res://scripts/sunset_adoption.gd").build(self)
	await _construction_step("sunset_adoption.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/sunset_adoption.gd).build(self)")
	await load("res://scripts/night_garden_integration_20261022/central_homes_adoption.gd").build(self)
	await _construction_step("central_homes_adoption.gd")
	load("res://scripts/star_atlas_d17_standard823.gd").build(self)
	await _construction_step("star_atlas_d17_standard823.gd")
	load("res://scripts/star_atlas_d17_standard_batch.gd").build(self)
	await _construction_step("star_atlas_d17_standard_batch.gd")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_homes_adoption.gd).build(self)")
	load("res://scripts/atrium_gallery_receiving.gd").build(self)
	await _construction_step("atrium_gallery_receiving.gd")
	# Sole-owner Group7 boundary: selected JSON and exact runtime files must be admitted first.
	# Complete retained physical envelope;new garden doors and unsafe transit stay held.
	_verify_group7_routes()
	load("res://scripts/startup_residency_20261020/group7_package.gd").build(self)
	await _construction_step("consolidated_all_eight_20261013/package.gd")
	# Approved six-house receiving frames and exact retained floors; engineering and room admission remain held.
	load("res://scripts/approved_receivers_20261014/package.gd").build(self)
	await _construction_step("approved_receivers_20261014/package.gd")
	load("res://scripts/private_pit_receivers_20261015/package.gd").build(self)
	await _construction_step("private_pit_receivers_20261015/package.gd")
	load("res://scripts/received_homes_20261015/package.gd").build(self)
	await _construction_step("received_homes_20261015/package.gd")
	load("res://scripts/group4_integrated_receiving.gd").before_budget(self)
	await _construction_step("group4_integrated_receiving.gd")
	lighting_budget.configure(self,player)
	load("res://scripts/group4_integrated_receiving.gd").after_budget(self)
	await _construction_step("group4_integrated_receiving.gd")
	# Exact missing-only Group3 precinct;source identities/capacity remain unassigned.
	load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(self)
	await _construction_step("group3_completion_20261011/d03_precinct.gd")
	# Exact supported labelled bank;unassigned rest surfaces,unknown private entry refused.
	load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(self)
	await _construction_step("group3_completion_20261011/labelled_bank.gd")
	# Exact supported five-service physical receivers;production door identity map remains unassigned.
	load("res://scripts/group3_d03_services_20261011/physical_package.gd").build(self)
	await _construction_step("group3_d03_services_20261011/physical_package.gd")
	# Exact current-supported theater exterior approaches;upper main doors stay inactive.
	var theater_upper_receiving:Node3D=load("res://scripts/group4_theater_upper_approaches.gd").build(get_node("ShipSpace/Districts"))
	var theater_receiver_lights:Array[Light3D]=[]
	for light:Light3D in theater_upper_receiving.find_children("*","SpotLight3D",true,false):theater_receiver_lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(theater_receiver_lights,self)
	load("res://scripts/theater_secondary_receiving_20261015/package.gd").build(self)
	await _construction_step("theater_secondary_receiving_20261015/package.gd")
	# Exact supported aft-riser physical lobbies;operating lift identities remain unassigned.
	load("res://scripts/group3_remaining_risers_20261011/aft_pair.gd").build(self)
	await _construction_step("group3_remaining_risers_20261011/aft_pair.gd")
	# Exact supported port2 clinical physical receiving;operating identities remain unassigned.
	load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(self)
	await _construction_step("group3_port2_clinical_20261011/physical_package.gd")
	# Exact current-source D03 port2 wall/floor connection;operating gate identities remain unassigned.
	load("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(self,{},true)
	await _construction_step("group3_d03_port2_20261011/physical_package.gd")
	# Exact supported fore-starboard physical receiving;operating identities remain unassigned.
	load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(self)
	await _construction_step("group3_fore_starboard_clinical_20261011/physical_package.gd")
	load("res://scripts/quiet_d15_receiving_20261016/package.gd").build(self)
	await _construction_step("quiet_d15_receiving_20261016/package.gd")
	# D14 composes the retained D15 shared-wall successor.
	load("res://scripts/quiet_d14_receiving_20261016/package.gd").build(self)
	await _construction_step("quiet_d14_receiving_20261016/package.gd")
	# D13 adds its separate bounded native lobby opening.
	load("res://scripts/quiet_d13_receiving_20261016/package.gd").build(self)
	await _construction_step("quiet_d13_receiving_20261016/package.gd")
	# D16 adds its separate bounded native lobby opening.
	load("res://scripts/quiet_d16_receiving_20261016/package.gd").build(self)
	await _construction_step("quiet_d16_receiving_20261016/package.gd")
	# Family D13 joins the existing aft staff lobby opening.
	load("res://scripts/family_d13_receiving_20261016/package.gd").build(self)
	await _construction_step("family_d13_receiving_20261016/package.gd")
	# Family D14 joins the existing aft staff lobby opening.
	load("res://scripts/family_d14_receiving_20261016/package.gd").build(self)
	await _construction_step("family_d14_receiving_20261016/package.gd")
	# Family D15 joins the existing aft staff lobby opening.
	load("res://scripts/family_d15_receiving_20261016/package.gd").build(self)
	await _construction_step("family_d15_receiving_20261016/package.gd")
	# Family D16 joins the existing aft staff lobby opening.
	load("res://scripts/family_d16_receiving_20261016/package.gd").build(self)
	await _construction_step("family_d16_receiving_20261016/package.gd")
	# Exact missing-only street successor; unsupported gate identities remain inactive.
	load("res://scripts/group3_d03_streets_20261011/physical_package.gd").build(self,{},true)
	await _construction_step("group3_d03_streets_20261011/physical_package.gd")
	# Six exact wall receivers with missing-only thresholds; source leaves stay closed and unassigned.
	load("res://scripts/group3_commons_crossings_20261012/physical_package.gd").build(self)
	await _construction_step("group3_commons_crossings_20261012/physical_package.gd")
	# Exact existing Family/Quiet floor receivers;agricultural services and programme admission stay held.
	load("res://scripts/group2_garden_quiet/package.gd").build_on_current_receivers(self)
	# Exact retained tabletop child fitout;food/staff services and dining designation stay held.
	load("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(self)
	# Physical child fitout only;closed authored entry,guardian/admission/services remain held.
	load("res://scripts/group2_family_childcare/package.gd").build_on_current_receiver(self)
	# Full clinical physical successor replacesonlyboundedport2 visual;sourcegates/clinicaloperationstayheld.
	load("res://scripts/group3_clinical_full_20261011/physical_package.gd").build(self)
	await _construction_step("group3_clinical_full_20261011/physical_package.gd")
	# Starboard3 exact physicallandings;privategates/lift/consent operationremainheld.
	load("res://scripts/group3_starboard3_private_20261011/physical_package.gd").build(self)
	await _construction_step("group3_starboard3_private_20261011/physical_package.gd")
	# One supported sourceadjunct/care receiver via westerncirculation;all structuralcapacity/service/consent holds remain.
	load("res://scripts/group2_central_receiving_20261013/package.gd").build(self)
	await _construction_step("group2_central_receiving_20261013/package.gd")
	# Approved retained D17 starboard reservations, physical receiving only.
	load("res://scripts/d17_starboard_standard_20261019/package.gd").build(self)
	await _construction_step("d17_starboard_standard_20261019/package.gd")
	# Two forward sourceadjunct/care pairs;slab/pier joins andguardwindows,operation/capacity holds remain.
	load("res://scripts/group2_forward_receiving_20261013/package.gd").build(self)
	await _construction_step("group2_forward_receiving_20261013/package.gd")
	# Port-central sourceadjunct/care pair;lower-stub bearing andwestvestibule fit,operational/engineering holds remain.
	load("res://scripts/group2_portcentral_receiving_20261013/package.gd").build(self)
	await _construction_step("group2_portcentral_receiving_20261013/package.gd")
	load("res://scripts/aft_adjunct_care_20261015/package.gd").build(self)
	await _construction_step("aft_adjunct_care_20261015/package.gd")
	load("res://scripts/fitted_wet_pavilions_20261015/package.gd").build(self)
	await _construction_step("fitted_wet_pavilions_20261015/package.gd")
	load("res://scripts/dining_public_core_20261015/package.gd").build(self)
	await _construction_step("dining_public_core_20261015/package.gd")
	load("res://scripts/theater_backstage_receiving_20261015/package.gd").build(self)
	await _construction_step("theater_backstage_receiving_20261015/package.gd")
	load("res://scripts/fitted_upper_horizon_20261015/package.gd").build(self)
	await _construction_step("fitted_upper_horizon_20261015/package.gd")
	load("res://scripts/dining_service_receiving_20261015/package.gd").build(self)
	await _construction_step("dining_service_receiving_20261015/package.gd")
	load("res://scripts/orchard_external_receiving_20261015/package.gd").build(self)
	await _construction_step("orchard_external_receiving_20261015/package.gd")
	load("res://scripts/synthesis_external_receiving_20261015/package.gd").build(self)
	await _construction_step("synthesis_external_receiving_20261015/package.gd")
	startup_deferred_builders.append(Callable(load("res://scripts/d09_retail_service_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/aquatic_external_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/arrivals_staff_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/arrivals_upper_staff_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/port_fore404_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/vesper_service_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/starboard_fore404_receiving_20261015/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/observation_cafe_service_20261016/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/tide_service_20261016/package.gd"),"build").bind(self))
	startup_deferred_builders.append(Callable(load("res://scripts/mineral_service_20261016/package.gd"),"build").bind(self))
	# Retained anonymous crew source: physical receiving, zero new berth or room identities.
	startup_deferred_builders.append(Callable(load("res://scripts/group3_remaining_crew_20261019/package.gd"),"build").bind(self))
	# Exact retained cascade cabinet hardware; onward network and controls remain inactive.
	startup_deferred_builders.append(Callable(load("res://scripts/group6_cascade_receiving_20261019/package.gd"),"build").bind(self))

	set_meta("construction_finished",true)
	construction_finished.emit()

func model(parent: Node3D, file: String, label: String, location: Vector3, yaw: float = 0.0) -> Node3D:
	if not streamed_models.has(file): return super.model(parent,file,label,location,yaw)
	var record: Dictionary = streamed_models[file]
	assert(FileAccess.get_sha256("res://assets/models/"+file) == str(record.source_sha256))
	assert(FileAccess.get_sha256(str(record.manifest_path)) == str(record.manifest_sha256))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(record.manifest_path)))
	assert(FileAccess.get_sha256(str(manifest.visual_path)) == str(manifest.visual_sha256))
	var wrapper := Node3D.new()
	wrapper.name = label
	wrapper.set_meta("catalogue_file",file)
	wrapper.set_meta("exact_batched_source_sha256",record.source_sha256)
	parent.add_child(wrapper)
	wrapper.position = location
	wrapper.rotation.y = yaw
	var visual: Node3D = load("res://scripts/startup_residency_20261020/original_visual_contacts.gd").instantiate_visual(file,manifest)
	wrapper.add_child(visual)
	exact_contact_residency.register_model(wrapper,manifest)
	return wrapper
func register_private_interior(parent:Node3D,file:String)->Node3D:
	return private_detail_residency.register_room(parent,file)

func arrive_at(arrival: Vector3, facing_y: float) -> bool:
	if private_detail_residency!=null:private_detail_residency.prepare_position(arrival)
	if d04_detail_residency!=null:d04_detail_residency.prepare_position(arrival)
	var rooms := get_node_or_null("ShipSystems/ReceivedRoomResidency")
	if rooms != null: rooms.prepare_position(arrival)
	if exact_contact_residency != null: exact_contact_residency.prepare_position(arrival)
	return super.arrive_at(arrival,facing_y)

func stream_private_visual(parent: Node3D, file: String, policy: Dictionary) -> Node3D:
	assert(streamed_models.has(file), "Missing exact private room bake: " + file)
	var record: Dictionary = streamed_models[file]
	assert(FileAccess.get_sha256(str(record.manifest_path)) == str(record.manifest_sha256))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(record.manifest_path)))
	assert(manifest.source_collision_policy == policy, "Private room collision/material policy changed")
	assert(d04_detail_residency.accepts(file))
	return d04_detail_residency.register_room(parent,file)

func _verify_successor_routes() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/d04_route_guards.json"))
	for row in data.routes:
		assert(FileAccess.get_sha256(str(row.original)) == str(row.original_sha256))
		assert(FileAccess.get_sha256(str(row.successor)) == str(row.successor_sha256))
		assert(FileAccess.get_sha256(str(row.contract)) == str(row.contract_sha256))

func _construction_step(label: String) -> void:
	var demoted:Dictionary=load("res://scripts/startup_residency_20261020/deferred_scene_references.gd").release_unused_scene_owners(self)
	if int(demoted.demoted_room_scene_owners)>0:print("DEFERRED_SCENE_OWNERS_RELEASED ",JSON.stringify(demoted))
	exact_texture_intern.flush()
	startup_steps += 1
	set_meta("startup_stage",label)
	set_meta("startup_steps",startup_steps)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP") == "1":
		print("STAGED_MEMORY ",JSON.stringify({"stage":label,"step":startup_steps,"static_bytes":OS.get_static_memory_usage(),"nodes":get_tree().get_node_count(),"textures":exact_texture_intern.statistics()}))
	await get_tree().process_frame

func finish_runtime_startup() -> void:
	for build in startup_deferred_builders:
		build.call()
		await _construction_step("Final receiving details")
	startup_deferred_builders.clear()
	get_tree().process_frame.connect(exact_texture_intern.flush)
	var maintenance:=Timer.new()
	maintenance.name="ImmutableResidencyCacheMaintenance"
	maintenance.wait_time=5.0
	maintenance.timeout.connect(exact_texture_intern.prune_expired_references)
	maintenance.timeout.connect(private_detail_residency.prune_expired_contacts)
	$ShipSystems.add_child(maintenance)
	maintenance.start()
	var actor := get_node("ShipSpace/PersistentActors/Player")
	actor.set_controls_enabled(true)
	set_meta("runtime_ready",true)
	get_tree().paused = startup_previous_pause
	runtime_ready.emit()

func _verify_group7_routes()->void:
	var routes:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/group7_routes.json"))
	for route in routes:
		assert(FileAccess.get_sha256(str(route.predecessor))==str(route.predecessor_sha256))
		assert(FileAccess.get_sha256(str(route.successor))==str(route.successor_sha256))
