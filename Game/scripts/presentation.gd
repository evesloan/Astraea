extends Node
var world_view: SubViewport
var display: TextureRect
var post_view: SubViewport
var post_pass: TextureRect
var effects := true
var directory: PanelContainer
var directory_open := false
var reticle: Node2D
var interaction_hint: Label
var resolution_index := 0
var capture_records: Array = []
const RESOLUTIONS := [Vector2i(640,360),Vector2i(960,540),Vector2i(1920,1080)]

func _ready() -> void:
	Engine.max_fps = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	world_view = SubViewport.new()
	world_view.name = "World360"
	world_view.process_mode = Node.PROCESS_MODE_PAUSABLE
	world_view.size = Vector2i(640, 360)
	world_view.own_world_3d = true
	world_view.use_occlusion_culling = true
	world_view.positional_shadow_atlas_16_bits = false
	world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(world_view)
	world_view.add_child(load("res://scenes/ship.tscn").instantiate())
	post_view = SubViewport.new()
	post_view.name = "WorldDisplayEffects360"
	post_view.size = world_view.size
	post_view.disable_3d = true
	post_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(post_view)
	post_pass = TextureRect.new()
	post_pass.name = "SingleRetroPass"
	post_pass.size = Vector2(world_view.size)
	post_pass.texture = world_view.get_texture()
	post_pass.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	post_pass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	post_view.add_child(post_pass)
	reticle = Node2D.new()
	reticle.set_script(load("res://scripts/focus_reticle.gd"))
	post_view.add_child(reticle)
	reticle.hide()
	display = TextureRect.new()
	display.name = "NearestWorldPresentation"
	display.texture = post_view.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	display.stretch_mode = TextureRect.STRETCH_SCALE
	display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/retro.gdshader")
	post_pass.material = mat
	add_child(display)
	get_viewport().size_changed.connect(_resize)
	_resize()
	var hud := Label.new()
	hud.name = "NativeResolutionStatus"
	hud.text = "ASTRAEA / D09 TERRACE — PRODUCTION WIP\nWASD · Mouse · RMB focus · Esc release · M express directory · F4 effects\nInitial authored components; full ship and gameplay incomplete"
	hud.position = Vector2(18, 18)
	hud.add_theme_font_size_override("font_size", 16)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hud)
	interaction_hint = Label.new()
	interaction_hint.position = Vector2(18,110)
	interaction_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	interaction_hint.add_theme_font_size_override("font_size",16)
	add_child(interaction_hint)
	_build_directory()
	if "--capture-validation" in OS.get_cmdline_user_args():
		await get_tree().create_timer(2.0).timeout
		await _capture()
		var salon_actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
		salon_actor.spawn_position = Vector3(62,52.6,-9)
		salon_actor.position = salon_actor.spawn_position
		salon_actor.rotation.y = -PI/2
		salon_actor.pitch = -0.05
		salon_actor.camera.rotation.x = salon_actor.pitch
		await get_tree().create_timer(0.5).timeout
		await _capture("salon_conversation_")
		salon_actor.spawn_position = Vector3(48,52.6,0)
		salon_actor.position = salon_actor.spawn_position
		salon_actor.rotation.y = -PI/2
		salon_actor.pitch = 0
		salon_actor.camera.rotation.x = 0
		await get_tree().create_timer(0.5).timeout
		await _capture("salon_entry_")
		salon_actor.spawn_position = Vector3(55.5,52.6,-22.5)
		salon_actor.position = salon_actor.spawn_position
		salon_actor.rotation.y = PI/2
		await get_tree().create_timer(0.5).timeout
		await _capture("salon_window_")
		salon_actor.spawn_position = Vector3(64,52.6,-18.5)
		salon_actor.position = salon_actor.spawn_position
		salon_actor.rotation.y = -PI/4
		salon_actor.pitch = -0.18
		salon_actor.camera.rotation.x = salon_actor.pitch
		await get_tree().create_timer(0.5).timeout
		await _capture("salon_study_")
		var study_switch = world_view.get_node("Astraea").find_child("SharedStudyLightSwitch",true,false)
		var study_actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
		world_view.get_node("Astraea").arrive_at(Vector3(65.5,52.6,-21.5),0)
		await get_tree().create_timer(.3).timeout
		study_actor.look_at(Vector3(study_switch.global_position.x,study_actor.global_position.y,study_switch.global_position.z),Vector3.UP)
		var switch_delta: Vector3 = study_switch.global_position-study_actor.camera.global_position
		study_actor.pitch = atan2(switch_delta.y,Vector2(switch_delta.x,switch_delta.z).length())
		study_actor.camera.rotation.x = study_actor.pitch
		var study_focus := InputEventMouseButton.new()
		study_focus.button_index = MOUSE_BUTTON_RIGHT
		study_focus.pressed = true
		Input.parse_input_event(study_focus)
		await get_tree().create_timer(.4).timeout
		await _capture("study_focus_on_")
		var study_press := InputEventKey.new()
		study_press.keycode = KEY_E
		study_press.physical_keycode = KEY_E
		study_press.pressed = true
		Input.parse_input_event(study_press)
		await get_tree().create_timer(.3).timeout
		await _capture("study_focus_off_")
		study_press.pressed = false
		Input.parse_input_event(study_press)
		study_focus.pressed = false
		Input.parse_input_event(study_focus)
		study_switch.powered = true
		study_switch.apply_power()
		if "--capture-d06" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(-31.623,27.1,4)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = 0.0
			actor.pitch = -0.22
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D06 CURVED GALLERY — unfinished architecture"
			await _capture("d06_")
			actor.spawn_position = Vector3(-34,27.1,-19)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = .6435
			actor.pitch = .05
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(.6).timeout
			await _capture("garden_overlook_")
			for view in [{"p":Vector3(-42,27.1,3),"yaw":1.34,"label":"canopy_portico_"},{"p":Vector3(-53,27.1,0),"yaw":PI/2,"label":"canopy_arrival_"},{"p":Vector3(-72,27.1,0),"yaw":-PI/2,"label":"canopy_return_"}]:
				actor.spawn_position = view.p
				actor.position = view.p
				actor.velocity = Vector3.ZERO
				actor.rotation.y = view.yaw
				actor.pitch = .05
				actor.camera.rotation.x = actor.pitch
				await get_tree().create_timer(.6).timeout
				await _capture(view.label)

			for view in [{"p":Vector3(-48,78.1,0),"yaw":PI/2,"label":"star_atlas_approach_","pitch":.04},{"p":Vector3(-60,78.1,2.6),"yaw":2.245,"label":"star_atlas_reference_counter_","pitch":-.12},{"p":Vector3(-59,78.1,17.25),"yaw":-PI/2,"label":"star_atlas_atrium_reading_","pitch":-.06},{"p":Vector3(-68.2,84.1,-4.5),"yaw":-PI/2,"label":"star_atlas_window_study_","pitch":-.05},{"p":Vector3(-88.5,88.6,11),"yaw":0.0,"label":"star_atlas_conversation_","pitch":-.1},{"p":Vector3(-88,78.1,-18),"yaw":-.35,"label":"star_atlas_collection_","pitch":.07},{"p":Vector3(-54,78.1,0),"yaw":PI/2,"label":"star_atlas_entry_","pitch":.15},{"p":Vector3(-84,78.1,18),"yaw":0.0,"label":"star_atlas_lower_court_","pitch":.25},{"p":Vector3(-72.2,84.1,0),"yaw":PI/2,"label":"star_atlas_middle_","pitch":-.1},{"p":Vector3(-83,88.6,12.5),"yaw":0.0,"label":"star_atlas_upper_","pitch":-.25},{"p":Vector3(18,61.1,211),"yaw":-PI/2,"label":"vesper_watercourse_","pitch":-.12},{"p":Vector3(17.5,44.1,218),"yaw":-1.1,"label":"aquatic_cascade_","pitch":.48},{"p":Vector3(43,61.1,238),"yaw":PI/2,"label":"vesper_aft_dining_","pitch":-.12},{"p":Vector3(46.8,61.1,210.5),"yaw":-1.1,"label":"vesper_east_dining_","pitch":-.15},{"p":Vector3(-34,6.1,-442),"yaw":-.94,"label":"arrivals_gallery_pause_","pitch":-.12},{"p":Vector3(-11,.1,-432),"yaw":PI/2,"label":"arrivals_entry_","pitch":.17},{"p":Vector3(-25,.1,-432),"yaw":PI/2,"label":"arrivals_court_","pitch":.23},{"p":Vector3(-26,.1,-450.5),"yaw":.6,"label":"arrivals_reception_","pitch":-.08},{"p":Vector3(-22,.1,-432),"yaw":PI/2,"label":"arrivals_overhead_","pitch":.55},{"p":Vector3(-30,6.1,-443),"yaw":PI,"label":"arrivals_upper_exhibit_","pitch":.10},{"p":Vector3(82,52.6,236),"yaw":PI/2,"label":"R070_entry_","pitch":.12},{"p":Vector3(74,52.6,236),"yaw":PI/2,"label":"R070_interior_","pitch":.16},{"p":Vector3(94.1,84.1,0),"yaw":PI/2,"label":"commons_lift_cabin_","pitch":.03},{"p":Vector3(61,84.1,0),"yaw":-PI/2,"label":"commons_lower_arrival_","pitch":.12},{"p":Vector3(70,88.6,-11),"yaw":-2.5,"label":"commons_upper_landing_","pitch":-.10},{"p":Vector3(89,84.1,8),"yaw":.8,"label":"commons_lower_return_","pitch":.13},{"p":Vector3(85.2,84.1,-34.9),"yaw":0.0,"label":"custodial_cart_","pitch":-.30},{"p":Vector3(55,78.1,0),"yaw":-PI/2,"label":"night_garden_arrival_","pitch":.08},{"p":Vector3(90,78.1,0),"yaw":PI/2,"label":"night_garden_return_","pitch":.08},{"p":Vector3(76.3,84.1,-49.4),"yaw":PI/2,"label":"suite_13041_salon_","pitch":.05},{"p":Vector3(69.7,84.1,-48.75),"yaw":-PI/2,"label":"suite_13041_retreat_","pitch":.05},{"p":Vector3(84.8,84.1,-45.3),"yaw":2.70,"label":"suite_13017_arrival_","pitch":.10},{"p":Vector3(79.4,84.1,-40.0),"yaw":-PI/2,"label":"suite_13017_bath_","pitch":-.25},{"p":Vector3(80.9,84.1,-42),"yaw":PI/2,"label":"suite_13017_entry_"},{"p":Vector3(70,84.1,-42),"yaw":-PI/2,"label":"suite_13017_return_"},{"p":Vector3(64,84.1,-42),"yaw":-PI/2,"label":"suite_13017_window_"}]:
				actor.spawn_position = view.p
				actor.position = view.p
				actor.velocity = Vector3.ZERO
				actor.rotation.y = view.yaw
				actor.pitch = view.get("pitch",.03)
				actor.camera.rotation.x = actor.pitch
				get_node("NativeResolutionStatus").text = "ASTRAEA / CONNECTED INTERIORS — work in progress"
				await get_tree().create_timer(.6).timeout
				await _capture(view.label)
				if view.label in ["star_atlas_reference_counter_","arrivals_gallery_pause_","arrivals_court_"]:
					set_world_resolution(2)
					effects=false
					post_pass.material.set_shader_parameter("enabled",false)
					world_view.get_node("Astraea").set_display_effects(false)
					await get_tree().create_timer(.5).timeout
					await _capture(str(view.label).trim_suffix("_")+"_clear_")
					set_world_resolution(0)
					effects=true
					post_pass.material.set_shader_parameter("enabled",true)
					world_view.get_node("Astraea").set_display_effects(true)
				if view.label=="custodial_cart_":
					var cart=world_view.get_node("Astraea").find_child("CustodialCart",true,false)
					var delta:Vector3=cart.global_transform*cart.grip_local-actor.camera.global_position
					actor.rotation.y=atan2(-delta.x,-delta.z)
					actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length())
					actor.camera.rotation.x=actor.pitch
					var focus:=InputEventMouseButton.new()
					focus.button_index=MOUSE_BUTTON_RIGHT
					focus.pressed=true
					Input.parse_input_event(focus.duplicate())
					var action:=InputEventKey.new()
					action.keycode=KEY_E
					action.physical_keycode=KEY_E
					action.pressed=true
					Input.parse_input_event(action.duplicate())
					Input.flush_buffered_events()
					await get_tree().create_timer(1.3).timeout
					if cart.driver!=actor:
						push_error("Graphical RMB/E cart grab failed")
						get_tree().quit(1)
						return
					await _capture("custodial_cart_focus_")
					action.pressed=false
					Input.parse_input_event(action.duplicate())
					Input.flush_buffered_events()
					for tick in range(3):await get_tree().physics_frame
					focus.pressed=true
					Input.parse_input_event(focus.duplicate())
					action.pressed=true
					Input.parse_input_event(action.duplicate())
					Input.flush_buffered_events()
					for tick in range(5):await get_tree().physics_frame
					if cart.driver!=null:
						push_error("Graphical cart release failed")
						get_tree().quit(1)
						return
					action.pressed=false
					Input.parse_input_event(action.duplicate())
					Input.flush_buffered_events()
					focus.pressed=false
					Input.parse_input_event(focus.duplicate())
					_toggle_directory()
					await _capture("directory_")
					assert(directory.get_global_rect().end.y<=get_viewport().get_visible_rect().size.y,"Directory remains inside native viewport")
					_toggle_directory()

			# Inspect the actual entry from the residential street at ordinary eye height.
			actor.spawn_position = Vector3(84.1,84.1,-42)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = PI/2
			actor.pitch = -.05
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(.3).timeout
			var entry = world_view.get_node("Astraea").find_child("Suite13017EntryDoor",true,false)
			entry.interact(actor)
			await get_tree().create_timer(1.5).timeout
			await _capture("suite_13017_entry_closed_")
			entry.interact(actor)
			await get_tree().create_timer(1.5).timeout
			await _capture("suite_13017_entry_open_")
			actor.spawn_position = Vector3(5,52.6,-59)
			actor.position = actor.spawn_position
			actor.rotation.y = PI
			actor.pitch = 0.08
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / GRAND ATRIUM — restored floor contours, finish incomplete"
			await _capture("atrium_")
			actor.spawn_position = Vector3(5,52.6,-42.5)
			actor.position = actor.spawn_position
			actor.pitch = -0.50
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(0.5).timeout
			await _capture("atrium_overlook_")
			actor.spawn_position = Vector3(0,6.1,-51)
			actor.position = actor.spawn_position
			actor.rotation.y = PI
			actor.pitch = 0.12
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D02 BOTANICAL COURT — first architectural composition"
			await _capture("garden_")
			actor.spawn_position = Vector3(-9,6.1,-35)
			actor.position = actor.spawn_position
			actor.pitch = 0.20
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(0.5).timeout
			await _capture("garden_near_")
			set_world_resolution(2)
			effects = false
			post_pass.material.set_shader_parameter("enabled",effects)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(0.5).timeout
			await _capture("garden_clear_")
			set_world_resolution(0)
			effects = true
			post_pass.material.set_shader_parameter("enabled",effects)
			world_view.get_node("Astraea").set_display_effects(true)
		if "--capture-aquatic" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(13,44.1,218)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = -PI/2
			actor.pitch = 0.18
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D08–D10 AQUATIC SECTION — unfinished architecture"
			await _capture("aquatic_")
			actor.spawn_position=Vector3(15,44.1,216)
			actor.position=actor.spawn_position
			actor.velocity=Vector3.ZERO
			actor.rotation.y=.46
			actor.pitch=.06
			actor.camera.rotation.x=actor.pitch
			await get_tree().create_timer(.6).timeout
			await _capture("aquatic_arrival_recess_")
			set_world_resolution(2)
			effects=false
			post_pass.material.set_shader_parameter("enabled",false)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(.6).timeout
			await _capture("aquatic_arrival_recess_clear_")
			set_world_resolution(0)
			effects=true
			post_pass.material.set_shader_parameter("enabled",true)
			world_view.get_node("Astraea").set_display_effects(true)


			actor.spawn_position = Vector3(47,44.1,216)
			actor.position = actor.spawn_position
			actor.rotation.y = -PI/2
			actor.pitch = 0.0
			actor.camera.rotation.x = 0.0
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D08 WET RETREAT — component integration"
			await _capture("wet_retreat_")
			actor.spawn_position=Vector3(14,61.1,218)
			actor.position=actor.spawn_position
			actor.velocity=Vector3.ZERO
			actor.rotation.y=-PI/2
			actor.pitch=.15
			actor.camera.rotation.x=actor.pitch
			await get_tree().create_timer(.6).timeout
			await _capture("aquatic_upper_ceiling_")
			set_world_resolution(2)
			effects=false
			post_pass.material.set_shader_parameter("enabled",false)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(.6).timeout
			await _capture("aquatic_upper_ceiling_clear_")
			set_world_resolution(0)
			effects=true
			post_pass.material.set_shader_parameter("enabled",true)
			world_view.get_node("Astraea").set_display_effects(true)

			actor.spawn_position=Vector3(44.5,52.6,236)
			actor.position=actor.spawn_position
			actor.velocity=Vector3.ZERO
			actor.rotation.y=-PI/2
			actor.pitch=.02
			actor.camera.rotation.x=actor.pitch
			await get_tree().create_timer(.6).timeout
			await _capture("living_gifts_frontage_")
			actor.spawn_position=Vector3(50.8,52.6,235.7)
			actor.position=actor.spawn_position
			actor.rotation.y=.65
			actor.pitch=.04
			actor.camera.rotation.x=actor.pitch
			await get_tree().create_timer(.6).timeout
			await _capture("living_gifts_nursery_")
			set_world_resolution(2)
			effects=false
			post_pass.material.set_shader_parameter("enabled",false)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(.6).timeout
			await _capture("living_gifts_nursery_clear_")
			set_world_resolution(0)
			effects=true
			post_pass.material.set_shader_parameter("enabled",true)
			world_view.get_node("Astraea").set_display_effects(true)

			for level in [44.0,52.5,61.0]:
				actor.spawn_position=Vector3(9.2,level+.1,235)
				actor.position=actor.spawn_position
				actor.velocity=Vector3.ZERO
				actor.rotation.y=-PI/2
				actor.pitch=.05
				actor.camera.rotation.x=actor.pitch
				await get_tree().create_timer(.6).timeout
				await _capture("aquatic_lift_"+str(level)+"_")

		if "--capture-staff" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(-59,0.1,0)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = PI/2
			actor.pitch = 0.0
			actor.camera.rotation.x = 0.0
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D01 SYNTHESIS SERVICE BAY — partial installation"
			await _capture("staff_")
			var door = world_view.get_node("Astraea").find_child("SynthesisServiceDoor",true,false)
			await get_tree().physics_frame
			door.interact(actor)
			await get_tree().create_timer(1.4).timeout
			var focus := InputEventMouseButton.new()
			focus.button_index = MOUSE_BUTTON_RIGHT
			focus.pressed = true
			Input.parse_input_event(focus)
			await get_tree().create_timer(0.5).timeout
			await _capture("staff_focus_")
			focus.pressed = false
			Input.parse_input_event(focus)
			await get_tree().physics_frame
			door.interact(actor)
			await get_tree().create_timer(1.4).timeout
			set_world_resolution(2)
			effects = false
			post_pass.material.set_shader_parameter("effects_enabled",false)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(0.25).timeout
			await _capture("staff_clear_")
		if FileAccess.file_exists("res://artifacts/profile_architecture.request"):
			await _profile_architecture()
		get_tree().quit()

func _resize() -> void:
	var screen := Vector2(get_viewport().size)
	var logical := Vector2(world_view.size)
	var scale_factor := minf(screen.x / logical.x, screen.y / logical.y)
	if scale_factor >= 1.0:
		scale_factor = maxf(1.0, floorf(scale_factor))
	display.size = logical * scale_factor
	display.position = (screen - display.size) * 0.5

func _unhandled_input(event: InputEvent) -> void:
	if directory_open and event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		_toggle_directory()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M:
		_toggle_directory()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F3:
		set_world_resolution((resolution_index+1)%RESOLUTIONS.size())
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		get_window().mode = Window.MODE_WINDOWED if get_window().mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN
	if event is InputEventKey and event.pressed and event.keycode == KEY_F12:
		_capture()
	if event is InputEventKey and event.pressed and event.keycode == KEY_F4:
		effects = not effects
		post_pass.material.set_shader_parameter("effects_enabled", effects)
		world_view.get_node("Astraea").set_display_effects(effects)

func _input(event: InputEvent) -> void:
	if is_instance_valid(world_view) and not directory_open: world_view.push_input(event)

func _capture(prefix: String = "") -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://artifacts")
	world_view.get_texture().get_image().save_png("res://artifacts/"+prefix+"world_capture.png")
	post_view.get_texture().get_image().save_png("res://artifacts/"+prefix+"processed_world_capture.png")
	get_viewport().get_texture().get_image().save_png("res://artifacts/"+prefix+"presentation_capture.png")
	var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
	capture_records.append({"prefix":prefix,"world_resolution":[world_view.size.x,world_view.size.y],"effects_enabled":effects,"camera_position":[actor.camera.global_position.x,actor.camera.global_position.y,actor.camera.global_position.z],"camera_rotation":[actor.camera.global_rotation.x,actor.camera.global_rotation.y,actor.camera.global_rotation.z],"fov":actor.camera.fov,"adapter":RenderingServer.get_video_adapter_name(),"rendered_objects":Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),"rendered_primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"static_memory_bytes":Performance.get_monitor(Performance.MEMORY_STATIC),"process_seconds":Performance.get_monitor(Performance.TIME_PROCESS),"physics_seconds":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),"active_physics_objects":Performance.get_monitor(Performance.PHYSICS_3D_ACTIVE_OBJECTS),"scope":"Single-capture engine observations on reported adapter; not a benchmark or target-platform performance acceptance"})
	var record := FileAccess.open("res://artifacts/capture_settings.json",FileAccess.WRITE)
	record.store_string(JSON.stringify(capture_records,"  "))
	record.close()

func _build_directory() -> void:
	directory = PanelContainer.new()
	directory.name = "ExpressDirectory"
	directory.position = Vector2(80,90)
	directory.custom_minimum_size = Vector2(920,530)
	add_child(directory)
	var column := VBoxContainer.new()
	directory.add_child(column)
	var title := Label.new()
	title.text = "EXPRESS DECK DIRECTORY — structural destinations, interiors unfinished"
	column.add_child(title)
	var scroll:=ScrollContainer.new()
	scroll.name="DestinationScroll"
	scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus=true
	column.add_child(scroll)
	var lists:=VBoxContainer.new()
	lists.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	scroll.add_child(lists)
	var grid := GridContainer.new()
	grid.columns = 2
	lists.add_child(grid)
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for index in range(contract.deck_datums.size()):
		var button := Button.new()
		var datum: Dictionary = contract.deck_datums[index]
		button.text = datum.deck_id + "  " + datum.historical_program_label
		button.custom_minimum_size = Vector2(450,46)
		grid.add_child(button)
		button.pressed.connect(_travel.bind(index))
	var places := GridContainer.new()
	places.columns = 2
	lists.add_child(places)
	for target in [{"name":"D06 Canopy terrace — partial", "position":Vector3(-53,27.1,0),"facing":PI/2}, {"name":"D12 Night garden — partial", "position":Vector3(55,78.1,0),"facing":-PI/2}, {"name":"D13 Suite 13017 — partial", "position":Vector3(80.9,84.1,-42),"facing":PI/2}, {"name":"D13 Twin retreat 13041 — partial", "position":Vector3(80.9,84.1,-49.4),"facing":PI/2}, {"name":"D13 Cart starting bay", "position":Vector3(85.2,84.1,-34.9),"facing":0}, {"name":"D02 Botanical garden — unfinished", "position":Vector3(0,6.1,-51),"facing":PI}, {"name":"D09 Grand Atrium — unfinished", "position":Vector3(5,52.6,-59),"facing":PI}, {"name":"D01 Synthesis service bay — partial", "position":Vector3(-59,0.1,0)}, {"name":"D08 Gentle Waters — unfinished", "position":Vector3(13,44.1,218)}, {"name":"D09 Living Gifts — unfinished", "position":Vector3(13,52.6,218)}, {"name":"D10 Vesper — unfinished", "position":Vector3(13,61.1,218)}, {"name":"D09 Conversation salon — partial", "position":Vector3(63,52.6,-20.5)}]:
		var button := Button.new()
		button.text = target.name
		button.custom_minimum_size = Vector2(450,36)
		places.add_child(button)
		button.pressed.connect(_visit.bind(target.name,target.position,target.get("facing",PI/2 if target.position.x < 0 else -PI/2)))
	var close := Button.new()
	close.text = "Close directory"
	close.pressed.connect(_toggle_directory)
	column.add_child(close)
	directory.hide()

func _toggle_directory() -> void:
	directory_open = not directory_open
	directory.visible = directory_open
	get_tree().paused = directory_open
	world_view.get_node("Astraea/ShipSpace/PersistentActors/Player").set_controls_enabled(not directory_open)

func _travel(index: int) -> void:
	var world = world_view.get_node("Astraea")
	if world.express_arrive(index):
		get_node("NativeResolutionStatus").text = "ASTRAEA / D%02d / +%.1f m — STRUCTURE ONLY\nWASD · Mouse · RMB focus · M directory · F4 effects\nInteriors, transport, population and final architecture unfinished" % [index+1,world.deck_y[index]]
		_toggle_directory()

func _visit(label: String, arrival: Vector3, facing: float) -> void:
	var world = world_view.get_node("Astraea")
	if world.arrive_at(arrival,facing):
		get_node("NativeResolutionStatus").text = "ASTRAEA / "+label+"\nWASD · Mouse · RMB focus · M directory · F4 effects\nProduction architecture in progress"
		_toggle_directory()

func _process(_delta: float) -> void:
	if not is_instance_valid(reticle): return
	reticle.visible = Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and not directory_open
	var actor = world_view.get_node_or_null("Astraea/ShipSpace/PersistentActors/Player")
	if actor != null and reticle.visible and is_instance_valid(actor.interaction_target):
		interaction_hint.text = actor.interaction_target.get_interaction_label()
	else: interaction_hint.text = ""

func set_world_resolution(index: int) -> void:
	assert(index >= 0 and index < RESOLUTIONS.size())
	resolution_index = index
	world_view.size = RESOLUTIONS[index]
	post_view.size = world_view.size
	post_pass.size = Vector2(world_view.size)
	reticle.queue_redraw()
	_resize()

func _profile_architecture() -> void:
	set_world_resolution(0)
	effects = true
	post_pass.material.set_shader_parameter("enabled",true)
	world_view.get_node("Astraea").set_display_effects(true)
	var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
	var routes := [{"name":"reading","position":Vector3(63,52.6,-20.5),"yaw":0.0,"pitch":0.0},{"name":"conversation","position":Vector3(62,52.6,-9),"yaw":-PI/2,"pitch":-0.05},{"name":"window","position":Vector3(55.5,52.6,-22.5),"yaw":PI/2,"pitch":0.0},{"name":"garden","position":Vector3(-9,6.1,-35),"yaw":PI,"pitch":0.20}]
	var records: Array = []
	for route in routes:
		actor.spawn_position = route.position
		actor.position = route.position
		actor.velocity = Vector3.ZERO
		actor.rotation.y = route.yaw
		actor.pitch = route.pitch
		actor.camera.rotation.x = route.pitch
		for enabled in [false,true]:
			world_view.use_occlusion_culling = enabled
			await get_tree().create_timer(2.0).timeout
			var samples: Array = []
			for i in range(12):
				await RenderingServer.frame_post_draw
				samples.append({"visible_draws":world_view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"shadow_draws":world_view.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"visible_primitives":world_view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME),"shadow_primitives":world_view.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)})
			var tag: String = "occlusion_"+route.name+("_on" if enabled else "_off")
			world_view.get_texture().get_image().save_png("res://artifacts/"+tag+".png")
			records.append({"view":route.name,"occlusion":enabled,"samples":samples})
	world_view.use_occlusion_culling = true
	var file := FileAccess.open("res://artifacts/occlusion_profile.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"adapter":RenderingServer.get_video_adapter_name(),"world_resolution":[640,360],"scope":"Paired stationary-view render counters after warmup; twelve frame samples; not target-PC FPS or a full moving-route benchmark","records":records},"  "))
	DirAccess.remove_absolute(ProjectSettings.globalize_path("res://artifacts/profile_architecture.request"))
