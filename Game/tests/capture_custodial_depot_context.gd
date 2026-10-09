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
	func surface(role: String,color: Color) -> StandardMaterial3D:
		var material:=finish(role)
		material.albedo_color=color
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
	actor.position=Vector3(10,0,460)
	space.add_child(actor)
	var budget:=Node.new()
	budget.name="LocalShadowSourceBudget"
	budget.set_script(load("res://scripts/lighting_budget.gd"))
	systems.add_child(budget)
	budget.configure(ship,actor)
	load("res://scripts/custodial_depot_candidate.gd").build(ship)
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
		["01_arrival",Vector3(10,1.65,460),Vector3(32,1.8,460)],
		["02_cart_spine",Vector3(26.5,1.65,453),Vector3(26.5,2,422)],
		["03_work_bay",Vector3(19.4,1.65,439),Vector3(12.5,1.5,436)],
		["04_ready_stock",Vector3(39,1.65,449),Vector3(41,1.8,434)],
		["05_used_carriers",Vector3(19.5,1.65,405),Vector3(14,1.1,408.5)]
	]
	DirAccess.make_dir_recursive_absolute("res://artifacts/custodial_depot_context_visual")
	var receipt: Array=[]
	for view in views:
		camera.position=view[1]
		actor.position=camera.position-Vector3.UP*1.65
		camera.look_at(view[2])
		for frame in range(12):await physics_frame
		budget.refresh()
		for frame in range(4):await process_frame
		await RenderingServer.frame_post_draw
		assert(world.get_texture().get_image().save_png("res://artifacts/custodial_depot_context_visual/"+str(view[0])+".png")==OK)
		var active:=0
		for light in budget.sources:
			if light.visible:active+=1
		assert(active<=8)
		receipt.append({"view":view[0],"active_normalized_sources":active})
		print("CUSTODIAL_DEPOT_CONTEXT_CAPTURE ",view[0]," active=",active)
	FileAccess.open("res://artifacts/custodial_depot_context_visual/CAPTURE.json",FileAccess.WRITE).store_string(JSON.stringify(receipt,"  "))
	quit(0)
