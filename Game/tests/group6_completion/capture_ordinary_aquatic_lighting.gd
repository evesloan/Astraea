extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP")
	var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,ship)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for light:Light3D in addition.find_children("*","Light3D",true,false):budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	actor.set_physics_process(false);actor.set_controls_enabled(false)
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var output:="res://docs/group6_completion/lighting_review002/";DirAccess.make_dir_recursive_absolute(output)
	var records:Array=[]
	for spec in [["annex_wide",Vector3(60.6,44.03,240),Vector3(78,46.0,224)],["west_rest",Vector3(64.8,45.48,220),Vector3(64.2,46.0,218)],["thermal_court",Vector3(76.2,45.48,217),Vector3(81.5,46.0,211.5)],["water_care",Vector3(96.8,45.48,210.6),Vector3(98.4,46.6,210.65)],["launch_and_river",Vector3(72,49.38,194.4),Vector3(79,46.0,215)]]:
		actor.global_position=spec[1];actor.velocity=Vector3.ZERO;residency.prepare_position(actor.global_position)
		var d:Vector3=spec[2]-actor.camera.global_position;actor.rotation.y=atan2(-d.x,-d.z);actor.camera.rotation.x=atan2(d.y,Vector2(d.x,d.z).length());actor.camera.fov=72
		for mode in ["default_retro","clear_setting"]:
			main.set_world_resolution(0 if mode=="default_retro" else 2);main.effects=mode=="default_retro";main.post_pass.material.set_shader_parameter("effects_enabled",main.effects);ship.set_display_effects(main.effects)
			budget.refresh()
			for i in range(18):await process_frame
			await RenderingServer.frame_post_draw
			var viewport:SubViewport=main.post_view if mode=="default_retro" else main.world_view
			var picture:Image=viewport.get_texture().get_image();assert(not picture.is_empty())
			var file:String=str(spec[0])+"_"+mode+".png";assert(picture.save_png(output+file)==OK)
			var active:Array=[]
			for light:Light3D in budget.sources:
				if light.visible and budget.requested_shadow.get(light.get_instance_id(),false):active.append(str(light.name))
			records.append({"file":file,"camera_eye_xyz":[actor.camera.global_position.x,actor.camera.global_position.y,actor.camera.global_position.z],"look_xyz":[spec[2].x,spec[2].y,spec[2].z],"world_resolution":[main.world_view.size.x,main.world_view.size.y],"retro_effects":main.effects,"active_requested_sources":active,"ambient_energy":ship.get_node("WorldEnvironment").environment.ambient_light_energy,"adapter":RenderingServer.get_video_adapter_name(),"source":"AquaticCompletion_r018.glb","scope":"Actual main scene/current annex source and original environment, materials, geometry and existing light budget. Stationary independent optical samples, not player routes. Native default retro and existing high-resolution/effects-off comfort setting. Software-adapter review is not target-hardware or final-art acceptance."})
	FileAccess.open(output+"CAPTURE_RECEIPT.json",FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
	print("GROUP6 ORDINARY CAPTURE PASS ",records.size());quit()
