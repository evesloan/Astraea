extends "res://visible_resource_budget_20261026/check_precompiled_bank_tram.gd"
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
	var owners:Array[Node]=ship.get_node("ShipSpace/Districts").get_children()
	for child:Node in ship.get_node("ShipSpace").get_children():
		if child.name not in ["Districts","PersistentActors"]:owners.append(child)
	var ranked:Array=[]
	var planes:Array[Plane]=actor.camera.get_frustum()
	for owner:Node in owners:
		var meshes:Array[MeshInstance3D]=[]
		var eligible:=0
		for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
			if mesh.mesh==null or not mesh.is_visible_in_tree() or (mesh.layers & actor.camera.cull_mask)==0:continue
			meshes.append(mesh)
			var box:AABB=mesh.global_transform*mesh.get_aabb()
			var intersects:=true
			for plane:Plane in planes:
				var outside:=true
				for corner in 8:
					if plane.distance_to(box.get_endpoint(corner))<=0:outside=false;break
				if outside:intersects=false;break
			if intersects:eligible+=mesh.mesh.get_surface_count()
		ranked.append({"owner":str(owner.get_path()),"frustum_surface_upper_bound":eligible,"meshes":meshes})
	ranked.sort_custom(func(a:Dictionary,b:Dictionary)->bool:return a.frustum_surface_upper_bound>b.frustum_surface_upper_bound)
	var census:Array=[]
	for row:Dictionary in ranked:census.append({"owner":row.owner,"meshes":row.meshes.size(),"frustum_surface_upper_bound":row.frustum_surface_upper_bound})
	data.census=census
	data.measurements=[]
	data.measurements.append(await stationary_sample("baseline"))
	for i in mini(6,ranked.size()):
		var row:Dictionary=ranked[i]
		var preimages:Array=[]
		for mesh:MeshInstance3D in row.meshes:
			preimages.append([weakref(mesh),mesh.layers]);mesh.layers=0
		var measurement:Dictionary=await stationary_sample("excluded_render_layers:"+row.owner)
		for preimage:Array in preimages:
			var mesh:MeshInstance3D=preimage[0].get_ref()
			if mesh!=null:mesh.layers=preimage[1]
		data.measurements.append(measurement)
		data.measurements.append(await stationary_sample("restored:"+row.owner))
	data.scope="Diagnostic marginal render-layer exclusion only; source/contacts/lights/occluders retained, each preimage restored. Frustum counts are upper bounds, not actual GPU submissions. Live streaming may vary; paired restored samples recorded. No route or production selection."
	safety.set_meta("integration_boarding_admitted",false)
	return data
func stationary_sample(stage:String)->Dictionary:
	for i in 4:await process_frame
	var times:Array=[];var draws:Array=[];var physics:Array=[];var process:Array=[]
	var previous:=Time.get_ticks_usec()
	for i in 16:
		await process_frame
		var now:=Time.get_ticks_usec();times.append((now-previous)/1000.0);previous=now
		draws.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
		physics.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000)
		process.append(Performance.get_monitor(Performance.TIME_PROCESS)*1000)
	times.sort();draws.sort();physics.sort();process.sort()
	var row:Dictionary={"stage":stage,"median_ms":times[8],"p95_ms":times[15],"draw_calls":draws[8],"physics_ms":physics[8],"process_ms":process[8],"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"static_bytes":Performance.get_monitor(Performance.MEMORY_STATIC)}
	print("STATIONARY_RENDER_OWNER ",JSON.stringify(row))
	return row
