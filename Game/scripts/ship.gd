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
	build_structural_datums()
	var lower_hull:=model($ShipSpace/Districts,"AST-HUL-001.glb","LowerHullBody_WIP",Vector3.ZERO)
	lower_hull.set_meta("persistent_id","lower_hull_body_001")
	var upper_skin:=model($ShipSpace/Districts,"AST-HUL-002.glb","TheaterWestUpperHull_Skin_WIP",Vector3.ZERO)
	upper_skin.set_meta("persistent_id","theater_west_upper_hull_skin_002")
	load("res://scripts/structural_floor_builder.gd").build($ShipSpace,stone,ivory,{"staff_floor":surface("staff_floor",Color.WHITE)})
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/structural_floor_builder.gd).build($ShipSpace,stone,ivory,{staff_floor:surface(staff_floor,Color.WHITE)})")
	if not load("res://scripts/botanical_pair_receiving.gd").validate_inputs():
		push_error("Botanical receiving successor inputs are not finalized")
		return
	model($ShipSpace,"AST-ATR-001_botanical_nursery_open001.glb","BotanicalCourtReceivingClosedInterim",Vector3.ZERO)
	model($ShipSpace,"AST-ARC-001.glb","D06_SweptGalleryBay_Draft",Vector3(-28.623,deck_y[5],0),PI/2)
	model($ShipSpace,"AST-ATR-001.glb","AuthoredAtriumGuards_All16Levels",Vector3.ZERO)
	build_retail_terrace()
	load("res://scripts/aquatic_section.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aquatic_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aquatic_annex_receiving.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group6_completion/completion.gd").build($ShipSpace/Districts/AquaticRiverSlideAnnex_WIP,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aquatic_annex_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/staff_section.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group1_synthesis_floor_receiving.gd").build(self)
	load("res://scripts/group8/synthesis_plant.gd").build(self,true)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/staff_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/lower_staff_network.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/lower_staff_network.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/atrium_lighting.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/atrium_lighting.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/atrium_garden.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/atrium_garden.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/garden_overlook.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/garden_overlook.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/canopy_terrace.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/canopy_terrace.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/central_house_connections.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_house_connections.gd).build(self)")
	load("res://scripts/residential_suite.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/residential_suite.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/residential_wayfinding.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/residential_wayfinding.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/night_garden.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/night_garden.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/vertical_commons.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/vertical_commons.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/retail_curios.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/retail_curios.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/thread_shell.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/thread_shell.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/orchard_exchange.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/orchard_exchange.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/orchard_foodhall.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group8/orchard_service.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/orchard_foodhall.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_CROWN_LINK.json")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_CROWN_LINK.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/FORWARD_PUBLIC_CORE.json")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/FORWARD_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json)")
	load("res://scripts/primary_atrium_core.gd").build($ShipSpace/Districts,self,"res://data/architecture/AFT_PUBLIC_CORE.json")
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/primary_atrium_core.gd).build($ShipSpace/Districts,self,res://data/architecture/AFT_PUBLIC_CORE.json)")
	load("res://scripts/central_command_crown.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_command_crown.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aft_command_crown.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aft_command_crown.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/bridge_platform.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/bridge_platform.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/bridge_enclosure.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/bridge_enclosure.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/aft_crown_platform.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/aft_crown_platform.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/upper_horizon_enclosure.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/upper_horizon_enclosure.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/arrivals_fusion.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group8/arrivals_service.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/arrivals_fusion.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/star_atlas.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group2_vip_dry_club/package.gd").build_on_current_receiver($ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/star_atlas.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/star_atlas_fitted_receiving.gd").build($ShipSpace/Districts/D12_D14_StarAtlas_WIP,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/star_atlas_fitted_receiving.gd).build($ShipSpace/Districts/D12_D14_StarAtlas_WIP,self)")
	load("res://scripts/d17_connected_house.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/d17_connected_house.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_section.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_first_pass.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_first_pass.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_finish.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_finish.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_pool_architecture.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_pool_architecture.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/secondary_engineering_section.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/secondary_engineering_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/grand_lantern_theater_section.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/grand_lantern_theater_section.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/court_a_increment004.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/court_a_increment004.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/theater_stair_walking_contacts.gd").build($ShipSpace/Districts)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/theater_stair_walking_contacts.gd).build($ShipSpace/Districts)")
	load("res://scripts/medical_welcome.gd").build($ShipSpace/Districts,self)
	load("res://scripts/group8/medical_privacy.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/medical_welcome.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/d04_port_forward_receiving.gd").build(self)
	load("res://scripts/d04_port_forward_homes_first.gd").build(self)
	load("res://scripts/d04_port_forward_homes_second.gd").build(self)
	load("res://scripts/d04_port_forward_homes_third.gd").build(self)
	load("res://scripts/d04_port_forward_northern_receiving.gd").build(self)
	load("res://scripts/d04_port_forward_homes_fourth.gd").build(self)
	load("res://scripts/d04_port_forward_homes_fifth.gd").build(self)
	load("res://scripts/d04_port_forward_commons_service.gd").build(self)
	load("res://scripts/d04_port_forward_horticultural_service.gd").build(self)
	load("res://scripts/d04_social_dayroom.gd").build(self)
	load("res://scripts/d04_commons_outlook_service.gd").build(self)
	load("res://scripts/d04_commons_cart_docking.gd").build(self)
	load("res://scripts/d04_commons_transport_routing.gd").build(self)
	load("res://scripts/d04_starboard_forward_north_receiving.gd").build(self)
	load("res://scripts/d04_starboard_forward_north_homes.gd").build(self)
	load("res://scripts/d04_starboard_forward_south_package.gd").build(self)
	load("res://scripts/d04_starboard_full_commons.gd").build(self)
	load("res://scripts/d04_port_aft_neighborhood.gd").build(self)
	load("res://scripts/d04_starboard_aft_neighborhood.gd").build(self)
	load("res://scripts/d04_port_central_neighborhood.gd").build(self)
	load("res://scripts/d04_starboard_central_neighborhood.gd").build(self)
	load("res://scripts/d04_port_aft_core_threshold.gd").build(self)
	load("res://scripts/d04_port_central_staff_riser.gd").build(self)
	var cleaning_cart:RigidBody3D=(load("res://scripts/cleaning_cart.gd")as GDScript).new()
	cleaning_cart.name="CustodialCart"
	cleaning_cart.position=Vector3(85.2,84.04,-37.3)
	$ShipSpace/PersistentActors.add_child(cleaning_cart)
	var player := CharacterBody3D.new()
	player.set_script(load("res://scripts/player.gd"))
	$ShipSpace/PersistentActors.add_child(player)
	player.spawn_position = Vector3(63.0,d09_y+0.1,-20.5)
	player.position = player.spawn_position
	load("res://scripts/d04_port_central_court_work_links.gd").build(self)
	load("res://scripts/d04_port_central_west_staff_circuit.gd").build(self)
	load("res://scripts/d04_commons_transition_fore_staff.gd").fore_build(self)
	load("res://scripts/d04_starboard_forward_work_branches.gd").build(self)
	load("res://scripts/d04_starboard_forward_remaining_courts.gd").build(self)
	load("res://scripts/d04_port_central_commons_recomposition.gd").build(self)
	load("res://scripts/d04_starboard_central_court_routes.gd").build(self)
	load("res://scripts/d04_starboard_aft_court_routes.gd").build(self)
	load("res://scripts/d04_commons_ceiling_junctions.gd").build(self)
	load("res://scripts/d04_port_aft_court_routes.gd").build(self)
	load("res://scripts/lower_shared_aft_staff_route.gd").build(self)
	load("res://scripts/d04_starboard_aft_commons_enclosure.gd").build(self)
	load("res://scripts/aft_crown_sitting_bays.gd").build(self)
	load("res://scripts/aft_crown_sitting_lighting.gd").build(self)
	load("res://scripts/aft_crown_foyer_waiting_edges.gd").build(self)
	load("res://scripts/group8/crown_interiors.gd").build(self,false)
	load("res://scripts/group4_boarding_safety.gd").build_terminals($ShipSpace/Districts)
	var lighting_budget := Node.new()
	lighting_budget.name = "LocalShadowSourceBudget"
	lighting_budget.set_script(load("res://scripts/lighting_budget.gd"))
	$ShipSystems.add_child(lighting_budget)
	preload("res://scripts/team_lounge_receiving.gd").build(self)
	load("res://scripts/movement_studio_receiving.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/movement_studio_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/moss_sanctuary_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/moss_sanctuary_receiving.gd).build(self)")
	load("res://scripts/sports_care_receiving.gd").build($ShipSpace/Districts,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/sports_care_receiving.gd).build($ShipSpace/Districts,self)")
	load("res://scripts/night_table_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/night_table_receiving.gd).build(self)")
	load("res://scripts/laundry_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/laundry_receiving.gd).build(self)")
	load("res://scripts/crew_batch_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/crew_batch_receiving.gd).build(self)")
	load("res://scripts/d12_pair_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/d12_pair_receiving.gd).build(self)")
	load("res://scripts/botanical_pair_receiving.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/botanical_pair_receiving.gd).build(self)")
	load("res://scripts/tidal_garden_adoption.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/tidal_garden_adoption.gd).build(self)")
	load("res://scripts/quiet_grove_adoption.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/quiet_grove_adoption.gd).build(self)")
	load("res://scripts/family_terrace_adoption.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/family_terrace_adoption.gd).build(self)")
	load("res://scripts/sunset_adoption.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/sunset_adoption.gd).build(self)")
	load("res://scripts/central_homes_adoption.gd").build(self)
	load("res://scripts/star_atlas_d17_standard823.gd").build(self)
	load("res://scripts/star_atlas_d17_standard_batch.gd").build(self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/central_homes_adoption.gd).build(self)")
	load("res://scripts/atrium_gallery_receiving.gd").build(self)
	# Sole-owner Group7 boundary: selected JSON and exact runtime files must be admitted first.
	# Complete retained physical envelope;new garden doors and unsafe transit stay held.
	load("res://scripts/consolidated_all_eight_20261013/package.gd").build(self)
	# Approved six-house receiving frames and exact retained floors; engineering and room admission remain held.
	load("res://scripts/approved_receivers_20261014/package.gd").build(self)
	load("res://scripts/private_pit_receivers_20261015/package.gd").build(self)
	load("res://scripts/received_homes_20261015/package.gd").build(self)
	load("res://scripts/group4_integrated_receiving.gd").before_budget(self)
	lighting_budget.configure(self,player)
	load("res://scripts/group4_integrated_receiving.gd").after_budget(self)
	# Exact missing-only Group3 precinct;source identities/capacity remain unassigned.
	load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(self)
	# Exact supported labelled bank;unassigned rest surfaces,unknown private entry refused.
	load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(self)
	# Exact supported five-service physical receivers;production door identity map remains unassigned.
	load("res://scripts/group3_d03_services_20261011/physical_package.gd").build(self)
	# Exact current-supported theater exterior approaches;upper main doors stay inactive.
	var theater_upper_receiving:Node3D=load("res://scripts/group4_theater_upper_approaches.gd").build(get_node("ShipSpace/Districts"))
	var theater_receiver_lights:Array[Light3D]=[]
	for light:Light3D in theater_upper_receiving.find_children("*","SpotLight3D",true,false):theater_receiver_lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(theater_receiver_lights,self)
	load("res://scripts/theater_secondary_receiving_20261015/package.gd").build(self)
	# Exact supported aft-riser physical lobbies;operating lift identities remain unassigned.
	load("res://scripts/group3_remaining_risers_20261011/aft_pair.gd").build(self)
	# Exact supported port2 clinical physical receiving;operating identities remain unassigned.
	load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(self)
	# Exact current-source D03 port2 wall/floor connection;operating gate identities remain unassigned.
	load("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(self,{},true)
	# Exact supported fore-starboard physical receiving;operating identities remain unassigned.
	load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(self)
	# Exact missing-only street successor; unsupported gate identities remain inactive.
	load("res://scripts/group3_d03_streets_20261011/physical_package.gd").build(self,{},true)
	# Six exact wall receivers with missing-only thresholds; source leaves stay closed and unassigned.
	load("res://scripts/group3_commons_crossings_20261012/physical_package.gd").build(self)
	# Exact existing Family/Quiet floor receivers;agricultural services and programme admission stay held.
	load("res://scripts/group2_garden_quiet/package.gd").build_on_current_receivers(self)
	# Exact retained tabletop child fitout;food/staff services and dining designation stay held.
	load("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(self)
	# Physical child fitout only;closed authored entry,guardian/admission/services remain held.
	load("res://scripts/group2_family_childcare/package.gd").build_on_current_receiver(self)
	# Full clinical physical successor replacesonlyboundedport2 visual;sourcegates/clinicaloperationstayheld.
	load("res://scripts/group3_clinical_full_20261011/physical_package.gd").build(self)
	# Starboard3 exact physicallandings;privategates/lift/consent operationremainheld.
	load("res://scripts/group3_starboard3_private_20261011/physical_package.gd").build(self)
	# One supported sourceadjunct/care receiver via westerncirculation;all structuralcapacity/service/consent holds remain.
	load("res://scripts/group2_central_receiving_20261013/package.gd").build(self)
	# Two forward sourceadjunct/care pairs;slab/pier joins andguardwindows,operation/capacity holds remain.
	load("res://scripts/group2_forward_receiving_20261013/package.gd").build(self)
	# Port-central sourceadjunct/care pair;lower-stub bearing andwestvestibule fit,operational/engineering holds remain.
	load("res://scripts/group2_portcentral_receiving_20261013/package.gd").build(self)
	load("res://scripts/aft_adjunct_care_20261015/package.gd").build(self)
	load("res://scripts/fitted_wet_pavilions_20261015/package.gd").build(self)
	load("res://scripts/dining_public_core_20261015/package.gd").build(self)
	load("res://scripts/theater_backstage_receiving_20261015/package.gd").build(self)
	load("res://scripts/fitted_upper_horizon_20261015/package.gd").build(self)
	load("res://scripts/dining_service_receiving_20261015/package.gd").build(self)
	load("res://scripts/orchard_external_receiving_20261015/package.gd").build(self)
	load("res://scripts/synthesis_external_receiving_20261015/package.gd").build(self)
	load("res://scripts/d09_retail_service_receiving_20261015/package.gd").build.call_deferred(self)
	load("res://scripts/aquatic_external_receiving_20261015/package.gd").build.call_deferred(self)
	load("res://scripts/arrivals_staff_receiving_20261015/package.gd").build.call_deferred(self)
	load("res://scripts/arrivals_upper_staff_receiving_20261015/package.gd").build.call_deferred(self)
	load("res://scripts/port_fore404_receiving_20261015/package.gd").build.call_deferred(self)
	load("res://scripts/vesper_service_receiving_20261015/package.gd").build.call_deferred(self)

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
	wrapper.set_meta("catalogue_file",file)
	parent.add_child(wrapper)
	wrapper.position = location
	wrapper.rotation.y = yaw
	var visual := (load("res://assets/models/"+file) as PackedScene).instantiate()
	wrapper.add_child(visual)
	if file == "AST-ATR-001.glb":
		# D02 now has a level garden floor; its former drop-edge guard is superseded.
		for part in visual.find_children("D02_*","MeshInstance3D",true,false):
			part.visible = false
	if file == "AST-ARC-001.glb":
		# The continuous fitted network owns this edge; keep the source floor/soffit.
		for part in visual.find_children("*","MeshInstance3D",true,false):
			if part.name.begins_with("ARC_Guard") or part.name.begins_with("ARC_Handrail") or part.name.begins_with("ARC_Continuous") or part.name.begins_with("ARC_Glass") or part.name.begins_with("ARC_Post") or part.name in ["ARC_ProfiledFascia","ARC_LowerShadowReveal"]:
				part.visible = false
	if not file.begins_with("AST-BOT"):
		_static_contacts(visual)
	return wrapper

func build_structural_datums() -> void:
	var structure := Node3D.new()
	structure.name = "All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE"
	$ShipSpace.add_child(structure)
	var hull: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/hull_envelope.json"))
	var outline: Array = hull.plan_xz_m
	for d in range(18):
		var deck := Node3D.new()
		deck.name = "D%02d_Datum" % (d+1)
		structure.add_child(deck)
		for i in range(outline.size()):
			var a: Array = outline[i]
			var b: Array = outline[(i+1)%outline.size()]
			beam(deck,"HullDatum_%d"%i,Vector3(a[0],deck_y[d],a[1]),Vector3(b[0],deck_y[d],b[1]),0.14,metal)

func build_retail_terrace() -> void:
	var district := Node3D.new()
	district.name = "D09_StarboardTerrace_AuthoredFootprint_WIP"
	district.set_meta("allocation_room_id","D09_salon5")
	$ShipSpace/Districts.add_child(district)
	var outline := PackedVector2Array([Vector2(48,-34),Vector2(66,-34),Vector2(72,-30),Vector2(76,-22),Vector2(76,-10),Vector2(70,-3),Vector2(60,4),Vector2(48,4)])
	var shell := model(district,"AST-SAL-007.glb","AuthoredSalonShell",Vector3(64,d09_y,-15))
	load("res://scripts/architectural_occlusion.gd").salon_shell(shell)
	var pane := ShaderMaterial.new()
	pane.shader = load("res://shaders/hospitality_glass.gdshader")
	for part in shell.find_children("SAL_Glass_*","MeshInstance3D",true,false): part.material_override = pane
	for i in range(6):
		var datum := shell.find_child("DATUM_ceiling_light_"+str(i),true,false) as Node3D
		assert(datum != null)
		var fixture := SpotLight3D.new()
		fixture.name = "SalonCeilingSource_"+str(i)
		district.add_child(fixture)
		fixture.global_position = datum.global_position
		fixture.rotation.x = -PI/2
		fixture.spot_angle = 65
		fixture.spot_range = 9
		fixture.light_color = Color(1,.92,.81)
		fixture.light_energy = 1.5
		fixture.shadow_enabled = true
	var conversation := model(district,"AST-SAL-008.glb","CrescentConversationAlcove",Vector3(68,d09_y,-12))
	for part in conversation.find_children("ALC_VisualFloor*","MeshInstance3D",true,false): part.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for i in range(3):
		var datum := conversation.find_child("DATUM_light_"+str(i),true,false) as Node3D
		assert(datum != null)
		var fixture := SpotLight3D.new()
		fixture.name = "ConversationSource_"+str(i)
		district.add_child(fixture)
		fixture.global_position = datum.global_position
		fixture.rotation.x = -PI/2
		fixture.spot_angle = 58
		fixture.spot_range = 5
		fixture.light_color = Color(1,.91,.78)
		fixture.light_energy = 1.1
		fixture.shadow_enabled = true
	for z in [-13.4,-10.6]: model(district,"AST-FUR-003_day_table.glb","ConversationTable_"+("North" if z < -12 else "South"),Vector3(69.5,d09_y,z))
	# Floor is supplied by the compiled layout, with this authored footprint taking priority.
	# Quiet bay remains one assembled source family with its actual mating offset.
	var bay := Node3D.new()
	bay.name = "QuietReturn"
	district.add_child(bay)
	bay.position = Vector3(63.5,d09_y,-27)
	model(bay,"AST-SAL-003.glb","BookSeatBay",Vector3.ZERO)
	model(bay,"AST-SAL-002.glb","MatedOverhead",Vector3(-3.1,0,0))
	model(district,"AST-SAL-001.glb","PublicPortal_NoDoorYet",Vector3(52,d09_y,0),PI/2)
	model(district,"AST-FUR-001_day_window_bench.glb","CourtBench",Vector3(53.7,d09_y,-25.2),-PI/2)
	model(district,"AST-FUR-002_day_reading_chair.glb","ReadingChair",Vector3(56.2,d09_y,-31.4),-PI/2)
	model(district,"AST-FUR-003_day_table.glb","LowReadingTable",Vector3(54.8,d09_y,-30.7))
	model(district,"AST-GST-001.glb","ReadingLamp",Vector3(57,d09_y,-32))
	model(district,"AST-BOT-001.glb","SmallCanopy",Vector3(54,d09_y,-21))
	model(district,"AST-BOT-002.glb","Understory",Vector3(54.9,d09_y,-20.6))
	load("res://scripts/salon_contents.gd").build(district,self)
	if OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/salon_contents.gd).build(district,self)")
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
		if i == 7: continue # Continuous connection into the restored inner terrace
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
	if node is MeshInstance3D and node.mesh != null and node.visible and not node.name.begins_with("ALC_VisualFloor"):
		load("res://scripts/static_contact_cache.gd").attach(node)
	for child in node.get_children():
		if not child is StaticBody3D: _static_contacts(child)

func express_arrive(deck_index: int) -> bool:
	if deck_index < 0 or deck_index >= deck_y.size(): return false
	if deck_index==17:return arrive_at(Vector3(0,deck_y[deck_index]+0.1,-77),0.0)
	return arrive_at(Vector3(5.5,deck_y[deck_index]+0.1,-72),0.0)

func arrive_at(arrival: Vector3, facing_y: float) -> bool:
	var residency:=get_node_or_null("ShipSystems/ReceivedRoomResidency")
	if residency!=null:residency.prepare_position(arrival)
	var remaining:=get_node_or_null("ShipSystems/RemainingBatchStreaming")
	if remaining!=null:remaining.prepare_position(arrival)
	var player: CharacterBody3D = $ShipSpace/PersistentActors/Player
	var state := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(arrival+Vector3.UP,arrival-Vector3.UP*2)
	query.exclude = [player.get_rid()]
	var hit := state.intersect_ray(query)
	if hit.is_empty() or hit.normal.y < 0.7: return false
	if absf(hit.position.y-(arrival.y-0.1)) > 0.15: return false
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	var clearance := PhysicsShapeQueryParameters3D.new()
	clearance.shape = capsule
	clearance.transform.origin = arrival+Vector3.UP*0.9
	clearance.exclude = [player.get_rid()]
	if not state.intersect_shape(clearance).is_empty(): return false
	player.position = arrival
	player.spawn_position = arrival
	player.velocity = Vector3.ZERO
	player.rotation.y = facing_y
	return true
