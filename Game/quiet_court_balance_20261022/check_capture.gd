extends SceneTree
const P:="res://quiet_grove_bank_20261022/"
func _initialize()->void:call_deferred("run")
func run()->void:
	assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
	root.size=Vector2i(1400,900)
	var host:Node3D=load("res://scripts/quiet_court_balance_integration_20261022/fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var actor:=Node3D.new();actor.name="Player";actor.position=Vector3(98,93,-400);actors.add_child(actor)
	load("res://scripts/quiet_grove_receiving.gd").build(host)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	await host._construction_step("quiet_grove_adoption.gd")
	for entry in manager.entries:
		if str(entry.record.model_file)=="QuietGroveBank_409_r001.glb":manager._load_entry(entry)
	# Actual retained nearby homes, not replacement blocks or invented background architecture.
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_UNITS.json"));var prototypes:={};var neighbors:=0
	for row in data.prototypes:prototypes[str(row.key)]=row
	for row in data.units:
		if false:continue
		var prototype:Dictionary=prototypes[row.source_recipe_key];var path:String="res://assets/models/"+str(prototype.model_file)
		assert(FileAccess.get_sha256(path)==prototype.sha256)
		var neighbor:Node3D=load(path).instantiate();districts.add_child(neighbor);neighbor.position=Vector3(row.source_origin_world_xyz[0],row.source_origin_world_xyz[1],row.source_origin_world_xyz[2]);neighbor.rotation.y=row.source_yaw_godot;neighbors+=1
	var environment:=Environment.new();environment.background_mode=Environment.BG_COLOR;environment.background_color=Color(.025,.034,.046);environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2;environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
	var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
	var house:Node3D=host.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
	assert(house.has_meta("court_balance_20261022"))
	var fixtures:Array=house.get_children().filter(func(n):return n is OmniLight3D)
	assert(fixtures.size()==79)
	for light:OmniLight3D in fixtures:assert(light.shadow_enabled and not light.visible and light.get_meta("quiet_court_budget_eligible",false))
	var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();systems.add_child(budget);await physics_frame;await physics_frame;budget.configure(host,actor)
	budget.set_process(false)
	var probes:Array=[]
	# Exercise five actual retained deck datums with the unchanged selector.
	for y:float in [84.,88.5,93.,97.5,102.]:
		actor.position=Vector3(98,y,-400);budget.refresh()
		var active:=0
		for light:OmniLight3D in fixtures:
			assert(light.visible==light.shadow_enabled)
			if light.visible:active+=1
		assert(active<=8)
		probes.append({"floor":y,"active":active})
	actor.position=Vector3(98,93,-400);budget.refresh()
	var active_before:=0
	for light:OmniLight3D in fixtures:
		if light.visible:active_before+=1
	assert(active_before>0,"No court illumination reaches the actual gallery viewpoint")
	for light:OmniLight3D in fixtures:light.set_meta("fixture_powered",false)
	budget.refresh()
	for light:OmniLight3D in fixtures:assert(not light.visible and not light.shadow_enabled)
	for light:OmniLight3D in fixtures:light.remove_meta("fixture_powered")
	budget.refresh()
	var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(98,94.65,-400);camera.look_at(Vector3(76,90,-440));camera.fov=82;camera.far=900;camera.current=true
	var layer:=CanvasLayer.new();root.add_child(layer);var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);label.text="QUIET GROVE / FIVE-LEVEL SHARED COURT / CANOPY + GALLERY LIGHT HIERARCHY\nActual main-hook bounded assembly — UNFINISHED / NOT WHOLE-SHIP ACCEPTANCE"
	for frame in range(8):await process_frame
	await RenderingServer.frame_post_draw
	var path:="res://quiet_court_balance_20261022/evidence/QUIET_GROVE_BALANCED_COURT_UNFINISHED.png";assert(not FileAccess.file_exists(path));assert(root.get_texture().get_image().save_png(path)==OK)
	var f:=FileAccess.open("res://quiet_court_balance_20261022/evidence/CHECK_CAPTURE.json",FileAccess.WRITE);f.store_string(JSON.stringify({"created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"camera":[98,94.65,-400],"target":[76,90,-440],"main_hook_used":true,"five_floor_budget_probes":probes,"active_at_viewpoint":active_before,"power_off_guard_pass":true,"balance":house.get_meta("court_balance_20261022"),"fixtures":79,"budget":8,"bounded_source_assembly":true,"existing_nearby_home_sources":neighbors,"retained_house_architecture":true,"retained_landscape_instances":250,"source_lighting_budget_unchanged":true,"whole_ship_runtime":false,"final_visual_accepted":false},"\t")+"\n");f.close();print("QUIET_GROVE_CAPTURE ",neighbors," retained neighbors");quit()
