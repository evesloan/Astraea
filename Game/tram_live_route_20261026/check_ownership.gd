extends SceneTree
# Explicit opt-in root-owned selected-world check. No default scene fallback,
# second ship in an existing world, actor movement or production admission.
const P := "res://tram_section_successor_20261024/"
var checks := 0
var failures := 0
var ship: Node3D
var presentation:Node
var frame_times:Array[float]=[]
var window_frame_times:Array[float]=[]
var route_motor:Node
var route_actor:Node3D
var previous_tick:int=0
var recording:bool=false
var input_down:bool=false
var next_sample:int=0

func _initialize() -> void:
	call_deferred("run")

func require(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error("TRAM_INSTALLED_R003_FAIL: " + message)

func argument(key: String) -> String:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with(key + "="):
			return arg.substr(key.length() + 1)
	return ""

func run() -> void:
	if "--negative-control" in OS.get_cmdline_user_args():
		require(false, "intentional fail-latch control; no ship constructed")
		finish({})
		return
	var scene_path := argument("--ship-scene")
	var scene_sha := argument("--ship-sha256")
	var script_sha := argument("--script-sha256")
	require(scene_path.begins_with("res://") and scene_sha.length() == 64 and script_sha.length() == 64, "explicit candidate scene, scene digest and main-script digest required")
	if failures > 0:
		finish({})
		return
	require(FileAccess.get_sha256(scene_path) == scene_sha, "exact root-owned candidate scene bytes")
	if failures > 0:
		finish({})
		return
	var packed: PackedScene = load(scene_path)
	require(packed != null, "candidate scene resolves")
	if packed == null:
		finish({})
		return
	presentation=load("res://aquatic_tram_interior_20261026/integration/main.tscn").instantiate()
	root.add_child(presentation)
	presentation.set_world_resolution(2)
	ship=presentation.world_view.get_node("Astraea")
	require(ship != null and ship.has_signal("runtime_ready") and ship.has_signal("construction_finished"), "complete inherited constructor interface")
	if ship == null:
		finish({})
		return
	var script: Script = ship.get_script()
	require(script != null and FileAccess.get_sha256(script.resource_path) == script_sha, "exact root-owned most-derived constructor bytes")
	if failures > 0:
		finish({})
		return
	var verify_ok: bool = load("res://aquatic_tram_interior_20261026/integration/adapter.gd").verify(ship)
	require(verify_ok, "retained assembly, predecessor and integration contracts before construction")
	if failures > 0:
		finish({})
		return
	# No scene is ever loaded implicitly. The supplied experimental scene retains
	# every actual district hook and ReceivedSectionInstallation/deferred phase.
	# Presentation owns the sole ship and actual player camera.
	var started := Time.get_ticks_msec()
	var limit := 300.0
	if not argument("--startup-limit").is_empty():
		limit = clampf(float(argument("--startup-limit")), 30.0, 900.0)
	while not bool(ship.get_meta("runtime_ready", false)):
		if ship.has_meta("tram_section_adapter_error"):
			require(false, str(ship.get_meta("tram_section_adapter_error")))
			finish({"stage":str(ship.get_meta("startup_stage", ""))})
			return
		if Time.get_ticks_msec() - started > int(limit * 1000.0):
			require(false, "bounded startup limit; no readiness inferred")
			finish({"stage":str(ship.get_meta("startup_stage", "")), "startup_limit_seconds":limit})
			return
		await process_frame
	require(not ship.has_meta("tram_section_adapter_error"), "no failed adapter hidden by readiness")
	var installation: Node = ship.get_node_or_null("ReceivedSectionInstallation")
	require(installation != null and bool(installation.get_meta("installation_ready", false)), "actual received-section installation completed")
	require(ship.startup_deferred_builders.is_empty(), "all actual deferred receiving hooks completed")
	if failures > 0:
		finish({})
		return
	# Allow actual physics to establish stationary docking. The synchronous
	# read-only sweep changes no actor physics, world pause or body transform.
	for i in range(20):
		await physics_frame
	var assembly: Node3D = ship.get_node_or_null("ShipSpace/Districts/Group4Completion")
	require(assembly != null, "canonical single Group4 owner")
	if assembly == null:
		finish({})
		return
	require(not ship.has_node("ShipSpace/Districts/Group4SectionSuccessor20261024"), "no second temporary-named owner survived")
	require(assembly.get_meta("tram_section_source_revision", "") == "20261024/r003", "named normal-constructor successor is installed")
	require(bool(assembly.get_meta("tram_section_before_complete", false)) and bool(assembly.get_meta("tram_section_after_complete", false)), "both integration phases completed")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var cart: RigidBody3D = ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	var body: AnimatableBody3D = assembly.get_node("Group4OwnedTram_Source024")
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var restraint: Node3D = assembly.get_node("Group4OriginalCartRestraint")
	var motor: Node3D = assembly.get_node("Group4LoadedSourceTravelActuator")
	var controls: Node3D = assembly.get_node("Group4SourceOperatingControls")
	var information: Node3D = assembly.get_node("Group4SourceStationInformation")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var identity: Dictionary = assembly.get_meta("tram_section_original_identity")
	var products: Array[int] = []
	for product: RigidBody3D in cart.products:
		products.append(product.get_instance_id())
	require(actor.get_instance_id() == identity.actor and cart.get_instance_id() == identity.cart and products == identity.products, "original player/cart/four stock identities preserved")
	require(cart.interaction_owner.get_instance_id() == identity.handle and controls.original_handle_script == identity.handle_script, "same original handle and restoration script")
	require(restraint.cart == cart and motor.restraint == restraint and controls.restraint == restraint and controls.player == actor, "actual motor/restraint/controls bind original actors")
	require(controls.motor == motor and controls.vehicle == body and safety.vehicle == body and motor.vehicle == body, "one exact vehicle owner throughout")
	require(controls.light_budget == budget and budget.sources.count(controls.light) == 1, "existing light budget owns exactly one retained car light")
	require(information.safety == safety and information.gates.size() == 5 and controls.controls.size() == 13, "all five station cases/calls and eight car controls retained")
	require(not assembly.get_meta("tram_operations_admitted") and not safety.get_meta("integration_boarding_admitted") and not restraint.get_meta("integration_joint_admitted") and not motor.get_meta("integration_motion_admitted"), "all production admission remains false")
	require(not motor.moving and not motor.motion_fault and not restraint.motion_fault and restraint.phase == "unlocked", "unloaded startup retains no new motion/restraint fault")
	require(motor.bogies.size() == 2 and motor.wheel_pivots.size() == 4 and body.get_meta("exact_original_portal_contact_components", 0) == 18, "actual articulated source bogies/wheels and exact portal components installed")
	require(safety.stationary_frames >= 15 and safety._physical_dock_matches("CENTRAL") and safety.door_side("CENTRAL") == "PORT", "actual stationary curved CENTRAL docking and explicit PORT identity")
	require(not safety.request_boarding("CENTRAL") and not motor.request_stop("AFT") and not restraint.request_lock(), "normal requests cannot bypass admission holds")
	if failures > 0:
		finish({"startup_seconds":float(Time.get_ticks_msec() - started) / 1000.0})
		return
	print("TRAM_OPERATION_STAGE installed_contact_sweep")
	var result: Dictionary = current_sweep(assembly)
	require(result.status == "PASS_CURRENT_CENTRAL_INTERVAL", "actual installed-world contact sweep: " + str(result.status))
	result.startup_seconds = float(Time.get_ticks_msec() - started) / 1000.0
	result.scene = scene_path
	result.scene_sha256 = scene_sha
	result.main_script_sha256 = script_sha
	if failures==0:result.operation=await operate(assembly)
	finish(result)

func finish(sweep: Dictionary) -> void:
	var result := {"status":"PASS_INSTALLED_SOURCE_CONNECTION" if failures == 0 else "FAIL_INSTALLED_SOURCE_CONNECTION", "checks":checks, "failures":failures, "production_admission":false, "contact_sweep":sweep, "not_accepted":["moving passenger/scenic experience", "original loaded cart/caster/joint", "structural capacity", "full visual geometry coverage", "whole-ship gameplay/performance"]}
	print("TRAM_INSTALLED_R003_RESULT " + JSON.stringify(result))
	var report_path := argument("--report")
	if not report_path.is_empty():
		var output := FileAccess.open(report_path, FileAccess.WRITE)
		if output != null:
			output.store_string(JSON.stringify(result, "  ") + "\n")
	release_input()
	if is_instance_valid(presentation):
		presentation.queue_free();await process_frame;await process_frame
	quit(1 if failures > 0 else 0)

func release_input()->void:
	if input_down:
		var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=false;Input.parse_input_event(event);input_down=false
func _process(_delta:float)->bool:
	var now:=Time.get_ticks_usec()
	if recording and previous_tick>0:
		frame_times.append((now-previous_tick)/1000.0)
		window_frame_times.append((now-previous_tick)/1000.0)
	previous_tick=now
	if recording and now>=next_sample:
		next_sample=now+5000000
		var row:Dictionary={"seconds":now/1000000.0,"static_bytes":Performance.get_monitor(Performance.MEMORY_STATIC),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"process_seconds":Performance.get_monitor(Performance.TIME_PROCESS),"physics_seconds":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)}
		if ship.private_detail_residency!=null:row.private=ship.private_detail_residency.statistics()
		var rooms:Node=ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")
		if rooms!=null:
			row.received=rooms.statistics()
			print("RECEIVED_OWNER_SAMPLE ",JSON.stringify({"seconds":now/1000000.0,"rooms":rooms.ownership_snapshot()}))
		if route_motor!=null:row.tram={"cursor":route_motor.cursor,"distance_m":route_motor.distance_travelled,"moving":route_motor.moving}
		if route_actor!=null:row.actor_position=str(route_actor.global_position)
		if not window_frame_times.is_empty():
			window_frame_times.sort()
			row.frame_window={"count":window_frame_times.size(),"median_ms":window_frame_times[window_frame_times.size()/2],"p95_ms":window_frame_times[int((window_frame_times.size()-1)*.95)]}
			window_frame_times.clear()
		var remaining:Node=ship.get_node_or_null("ShipSystems/RemainingBatchStreaming")
		if remaining!=null:row.remaining=remaining.visibility_activation_statistics()
		print("TRAM_ROUTE_SAMPLE ",JSON.stringify(row))
	return false
func phase_wait(safety:Node3D,wanted:String,seconds:float)->bool:
	var start:=Time.get_ticks_msec()
	while safety.phase!=wanted:
		if Time.get_ticks_msec()-start>seconds*1000:return false
		await physics_frame
	return true
func walk(actor:CharacterBody3D,target:Vector3,seconds:float)->bool:
	var start:=Time.get_ticks_msec()
	actor.gameplay_input_enabled=true
	while Vector2(actor.global_position.x-target.x,actor.global_position.z-target.z).length()>.16:
		if Time.get_ticks_msec()-start>seconds*1000 or actor.global_position.y<55.9:release_input();return false
		var delta:=target-actor.global_position
		actor.rotation.y=atan2(-delta.x,-delta.z)
		if not input_down:
			var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=true;Input.parse_input_event(event);input_down=true
		await physics_frame
	release_input();actor.set_controls_enabled(false)
	return true
func operate(assembly:Node3D)->Dictionary:
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
	motor.set_meta("integration_motion_admitted",true)
	var original_cursor:float=motor.cursor;var initial_local:Vector3=body.to_local(actor.global_position)
	var max_local:=0.0
	route_motor=motor;route_actor=actor
	recording=true;previous_tick=0
	for target:float in [original_cursor+10.,original_cursor]:
		require(motor.request_distance(target),"guarded physical route request")
		if failures>0:break
		var started:=Time.get_ticks_msec()
		while motor.moving:
			await process_frame
			max_local=maxf(max_local,body.to_local(actor.global_position).distance_to(initial_local))
			if motor.motion_fault or max_local>.15 or Time.get_ticks_msec()-started>90000:
				require(false,"bounded carried-player route safety");break
		if failures>0:break
	recording=false
	data.max_passenger_local_error_m=max_local;data.distance_m=motor.distance_travelled;data.frames=frame_times.size()
	if not frame_times.is_empty():
		frame_times.sort();data.frame_median_ms=frame_times[frame_times.size()/2];data.frame_p95_ms=frame_times[int((frame_times.size()-1)*.95)]
	data.draw_calls=Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME);data.primitives=Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME);data.resources=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT);data.static_bytes=Performance.get_monitor(Performance.MEMORY_STATIC)
	if not motor.moving:
		for i in range(20):await physics_frame
		require(safety._physical_dock_matches("CENTRAL"),"actual returned central dock")
	motor.set_meta("integration_motion_admitted",false);safety.set_meta("integration_boarding_admitted",false)
	data.stage="complete" if failures==0 else "held"
	return data

func current_sweep(assembly:Node3D)->Dictionary:
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var motor:Node3D=assembly.get_node("Group4LoadedSourceTravelActuator")
	var excludes:Array[RID]=[body.get_rid()]
	for node:CollisionObject3D in body.find_children("*","CollisionObject3D",true,false):excludes.append(node.get_rid())
	for rolling:Node3D in assembly.find_children("RollingGuidewayContacts","Node3D",true,false):
		for node:CollisionObject3D in rolling.find_children("*","CollisionObject3D",true,false):excludes.append(node.get_rid())
	var interval:Array=[motor.cursor-.1,motor.cursor+10.1]
	var r:Dictionary=load("res://orchard_tram_interior_20261025/integration/component_sweep.gd").audit(ship,assembly,motor.poses,interval,excludes)
	r.interval=interval;r.status="PASS_CURRENT_CENTRAL_INTERVAL" if r.hits.is_empty() and r.queries>0 else "FAIL_CURRENT_CENTRAL_INTERVAL"
	return r
