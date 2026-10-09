extends SceneTree
# Bounded Godot receiving-source review, not full default ship or target performance.
class ContextShip extends Node3D:
	var stone: StandardMaterial3D
	var ivory: StandardMaterial3D
	func finish(role: String) -> StandardMaterial3D:
		var material:=StandardMaterial3D.new()
		material.albedo_texture=load("res://assets/textures/"+role+".png")
		material.roughness=.83
		material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
		return material
func _initialize() -> void:call_deferred("run")
func run() -> void:
	root.size=Vector2i(1280,720)
	var world:=SubViewport.new()
	world.size=Vector2i(640,360)
	world.own_world_3d=true
	world.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(world)
	var ship:=ContextShip.new()
	ship.stone=ship.finish("warm_stone")
	ship.ivory=ship.finish("ivory_enamel")
	world.add_child(ship)
	var space:=Node3D.new()
	space.name="ShipSpace"
	ship.add_child(space)
	var districts:=Node3D.new()
	districts.name="Districts"
	space.add_child(districts)
	var systems:=Node.new()
	systems.name="ShipSystems"
	ship.add_child(systems)
	var actor:=Node3D.new()
	actor.position=Vector3(13,69.5,280)
	space.add_child(actor)
	var budget:=Node.new()
	budget.name="LocalShadowSourceBudget"
	budget.set_script(load("res://scripts/lighting_budget.gd"))
	systems.add_child(budget)
	budget.configure(ship,actor)
	var baseline: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var retained: Array=[]
	for region in baseline.regions:
		if region.id=="D11_aquatic_cinema_interface":retained.append(region)
	assert(retained.size()==1)
	load("res://scripts/structural_floor_builder.gd").build_regions(space,ship.stone,ship.ivory,retained,{},"RetainedAquaticInterface")
	load("res://scripts/cinema5_candidate.gd").build(ship)
	var environment:=Environment.new()
	environment.background_mode=Environment.BG_COLOR
	environment.background_color=Color(.025,.034,.046)
	environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color=Color(.75,.81,.86)
	environment.ambient_light_energy=.2
	var setting:=WorldEnvironment.new()
	setting.environment=environment
	ship.add_child(setting)
	var display:=TextureRect.new()
	display.texture=world.get_texture()
	display.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	display.size=Vector2(1280,720)
	display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	root.add_child(display)
	var camera:=Camera3D.new()
	ship.add_child(camera)
	camera.fov=72
	camera.make_current()
	var views: Array=[
		["01_arrival",Vector3(13,71.15,280),Vector3(36,72,270)],
		["02_audience",Vector3(36,73.61,291),Vector3(36,73.1,246)],
		["03_level_transfer",Vector3(22,71.15,259.6),Vector3(35,72.1,280)],
		["04_projection",Vector3(36,71.15,302),Vector3(36,71.15,308)],
		["05_east_closure",Vector3(57.45,71.15,278),Vector3(60.55,70.8,280)]
	]
	DirAccess.make_dir_recursive_absolute("res://artifacts/cinema5_context_visual")
	var receipt: Array=[]
	for view in views:
		camera.position=view[1]
		actor.position=camera.position-Vector3.UP*1.65
		camera.look_at(view[2])
		for frame in range(12):await physics_frame
		budget.refresh()
		for frame in range(4):await process_frame
		await RenderingServer.frame_post_draw
		assert(world.get_texture().get_image().save_png("res://artifacts/cinema5_context_visual/"+str(view[0])+".png")==OK)
		var active:=0
		for light in budget.sources:
			if light.visible:active+=1
		assert(active<=8)
		receipt.append({"view":view[0],"active_normalized_sources":active})
		print("CINEMA5_CONTEXT_CAPTURE ",view[0]," active=",active)
	FileAccess.open("res://artifacts/cinema5_context_visual/CAPTURE.json",FileAccess.WRITE).store_string(JSON.stringify(receipt,"  "))
	quit(0)
