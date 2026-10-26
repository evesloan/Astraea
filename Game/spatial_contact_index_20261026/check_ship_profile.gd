extends "res://visible_resource_budget_20261026/check_precompiled_private_tram.gd"
func operate(assembly:Node3D)->Dictionary:
	require(bank_builder_replaced,"Original deferred bank builder replaced once before construction")
	if failures>0:return {"stage":"builder_not_bound"}
	var bank:Node3D=ship.find_child("Group3RemainingCrewBank",true,false)
	require(bank!=null and bank.has_meta("precompiled_crew_bank"),"Direct precompiled source loaded")
	if failures>0:return {"stage":"compiled_bank_missing"}
	var snapshot:Dictionary=load("res://spatial_instance_cells_20261026/ship_lighting.gd").lighting(ship)
	require(not snapshot.has("failed"),"Exact original light budget and all additional sources")
	if failures>0:return {"stage":"light_snapshot_failed"}
	var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(bank,snapshot.lights)
	selected.bank_nodes=bank.find_children("*","",true,false).size()+1
	print("PRECOMPILED_BANK_SELECTED ",JSON.stringify(selected))
	require(selected.saved_submissions>=7000 and selected.bank_nodes<=34000,"Meaningful direct representation reduction required")
	if failures>0:return {"stage":"precompiled_reduction_not_warranted","candidate":selected}
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var motor:Node3D=assembly.get_node("Group4LoadedSourceTravelActuator")
	var controls:Node3D=assembly.get_node("Group4SourceOperatingControls")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var data:Dictionary={"production_admission":false,"resolution":"1920x1080","renderer":"GL Compatibility","route":"CENTRAL +10m and return, conditional on real boarding","cart":"original cart left in its existing world location; no live relocation","stage":"arrival"}
	require(body.has_meta("initial_pose_before_tree"),"normal constructor used verified initial pose")
	if failures>0:return data
	if not ship.arrive_at(Vector3(-4.5,56.15,-75.3),0):require(false,"physical central platform arrival");return data
	actor.set_controls_enabled(false)
	for i in range(20):await physics_frame
	safety.set_meta("integration_boarding_admitted",true)
	data.stage="boarding";print("TRAM_OPERATION_STAGE boarding")
	require(controls.begin_boarding("CENTRAL"),"real central boarding requested")
	if failures>0:return data
	require(await phase_wait(safety,"boarding",20),"bridge deploys and original gates open")
	if failures>0:return data
	var opening_started:=Time.get_ticks_msec()
	while safety.station_gates["CENTRAL"].open_fraction<.999 or safety.car_gates[safety.door_side("CENTRAL")].open_fraction<.999:
		if Time.get_ticks_msec()-opening_started>20000:require(false,"actual gate leaves finish opening before threshold entry");return data
		await physics_frame
	data.station_gate_open=safety.station_gates["CENTRAL"].open_fraction;data.car_gate_open=safety.car_gates[safety.door_side("CENTRAL")].open_fraction
	require(await walk(actor,body.to_global(Vector3(0,.02,0)),20),"original player walks across actual boarding bridge")
	data.actor_after_crossing=str(actor.global_position)
	if failures>0:return data
	require(controls.actor_aboard(actor) and actor.is_on_floor(),"original player physically supported aboard")
	if failures>0:return data
	require(controls.request_control("SECURE","",actor),"actual console secures boarding")
	require(await phase_wait(safety,"secured",20),"portals close and bridge stows")
	if failures>0:return data
	data.stage="moving_route";print("TRAM_OPERATION_STAGE moving_route")
	actor.rotation.y=PI;actor.pitch=0;actor.camera.rotation.x=0
	await create_timer(3).timeout
	await RenderingServer.frame_post_draw
	var picture:=argument("--report").get_base_dir().path_join("central_aboard_actual.png")
	data.image_save_error=presentation.world_view.get_texture().get_image().save_png(picture)
	data.image=picture;data.camera_yaw=actor.rotation.y;data.camera_position=str(actor.camera.global_position)
	data.stage="stationary_render_attribution"
	data.precompiled_bank=selected
	data.stage="stationary_builtin_profile"
	var view:Viewport=presentation.world_view
	RenderingServer.viewport_set_measure_render_time(view.get_viewport_rid(),true)
	for i in 24:await process_frame
	data.samples=[]
	var previous:=Time.get_ticks_usec()
	for i in 96:
		await process_frame
		var now:=Time.get_ticks_usec()
		data.samples.append({"frame_ms":(now-previous)/1000.0,"render_cpu_ms":RenderingServer.viewport_get_measured_render_time_cpu(view.get_viewport_rid()),"render_gpu_ms":RenderingServer.viewport_get_measured_render_time_gpu(view.get_viewport_rid()),"render_setup_ms":RenderingServer.get_frame_setup_time_cpu(),"process_ms":Performance.get_monitor(Performance.TIME_PROCESS)*1000,"physics_ms":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000,"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"draw_calls":view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"primitives":view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)})
		previous=now
	data.stable_samples=[]
	var received:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var settle_started:int=Time.get_ticks_msec()
	var stable_since:int=settle_started
	var signature:Array=residency_signature(received)
	var settled:=false
	while Time.get_ticks_msec()-settle_started<20000:
		await process_frame
		var current:Array=residency_signature(received)
		if current!=signature or not received.pending_visible.is_empty() or not ship.private_detail_residency.pending_visible.is_empty():
			signature=current;stable_since=Time.get_ticks_msec()
		elif Time.get_ticks_msec()-stable_since>=1000:
			settled=true;break
	data.settle_elapsed_ms=Time.get_ticks_msec()-settle_started
	data.stable_signature=signature
	data.stable_window_eligible=settled
	if settled:
		previous=Time.get_ticks_usec()
		for i in 96:
			await process_frame
			var now:=Time.get_ticks_usec()
			data.stable_samples.append({"frame_ms":(now-previous)/1000.0,"render_cpu_ms":RenderingServer.viewport_get_measured_render_time_cpu(view.get_viewport_rid()),"render_gpu_ms":RenderingServer.viewport_get_measured_render_time_gpu(view.get_viewport_rid()),"render_setup_ms":RenderingServer.get_frame_setup_time_cpu(),"process_ms":Performance.get_monitor(Performance.TIME_PROCESS)*1000,"physics_ms":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000,"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"draw_calls":view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"primitives":view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)})
			previous=now
			if residency_signature(received)!=signature:data.stable_window_eligible=false
	data.contact_index=ship.tidal_contacts.statistics()
	RenderingServer.viewport_set_measure_render_time(view.get_viewport_rid(),false)
	data.scope="Fixed real boarded camera, current opt-in integration, built-in script profiler and viewport CPU/GPU timers. No owner scans or exclusions in sampling loop. Nested/in-flight categories are not additive; editor debug and profiler overhead remain. Not a release FPS claim."
	data.debug_build=OS.is_debug_build()
	data.fixture_registration=private_installed.get("fixture_registration",{})
	data.private_residency=ship.private_detail_residency.statistics()
	safety.set_meta("integration_boarding_admitted",false)
	return data

func residency_signature(received:Node)->Array:
	return [Performance.get_monitor(Performance.OBJECT_NODE_COUNT),Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),received.changes,ship.private_detail_residency.loads,ship.private_detail_residency.releases]
