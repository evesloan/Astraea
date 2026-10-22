extends SceneTree
const P:="res://quiet_grove_bank_20261022/"
func _initialize()->void:call_deferred("run")
func run()->void:
	root.size=Vector2i(1400,900)
	var host:Node3D=load("res://scripts/quiet_grove_integration_20261022/fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var actor:=Node3D.new();actor.name="Player";actor.position=Vector3(56.1,93,-328);actors.add_child(actor)
	load("res://scripts/quiet_grove_receiving.gd").build(host)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	await host._construction_step("quiet_grove_adoption.gd")
	load(P+"adapter.gd").build(host)
	for entry in manager.entries:
		if str(entry.record.model_file)=="QuietGroveBank_409_r001.glb":manager._load_entry(entry)
	# Actual retained nearby homes, not replacement blocks or invented background architecture.
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_UNITS.json"));var prototypes:={};var neighbors:=0
	for row in data.prototypes:prototypes[str(row.key)]=row
	for row in data.units:
		if absf((float(row.allocation_z[0])+float(row.allocation_z[1]))*.5+328)>20:continue
		var prototype:Dictionary=prototypes[row.source_recipe_key];var path:String="res://assets/models/"+str(prototype.model_file)
		assert(FileAccess.get_sha256(path)==prototype.sha256)
		var neighbor:Node3D=load(path).instantiate();districts.add_child(neighbor);neighbor.position=Vector3(row.source_origin_world_xyz[0],row.source_origin_world_xyz[1],row.source_origin_world_xyz[2]);neighbor.rotation.y=row.source_yaw_godot;neighbors+=1
	var environment:=Environment.new();environment.background_mode=Environment.BG_COLOR;environment.background_color=Color(.025,.034,.046);environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2;environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
	var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
	var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();systems.add_child(budget);await physics_frame;await physics_frame;budget.configure(host,actor)
	var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(56.1,94.65,-328);camera.look_at(Vector3(85,95.5,-328));camera.fov=92;camera.far=900;camera.current=true
	var layer:=CanvasLayer.new();root.add_child(layer);var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);label.text="QUIET GROVE / NEW SPECIALTY BANK / NEW D15 ROOM409 / AUTHORED VIEW LOUNGE\nActual source candidate assembly — UNFINISHED / NOT WHOLE-SHIP ACCEPTANCE"
	for frame in range(8):await process_frame
	await RenderingServer.frame_post_draw
	var path:=P+"evidence/QUIET_GROVE_D15_409_VIEW_LOUNGE_UNFINISHED.png";assert(not FileAccess.file_exists(path));assert(root.get_texture().get_image().save_png(path)==OK)
	var f:=FileAccess.open(P+"evidence/CAPTURE_LOUNGE.json",FileAccess.WRITE);f.store_string(JSON.stringify({"created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"camera":[56.1,94.65,-328],"target":[85,95.5,-328],"main_hook_used":false,"bounded_source_assembly":true,"existing_nearby_home_sources":neighbors,"retained_house_architecture":true,"retained_landscape_instances":250,"source_lighting_budget_unchanged":true,"whole_ship_runtime":false,"final_visual_accepted":false},"\t")+"\n");f.close();print("QUIET_GROVE_CAPTURE ",neighbors," retained neighbors");quit()
