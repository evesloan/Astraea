extends SceneTree
# Isolated additive candidate test in the complete selected ship. No production selection.
var report := {"status":"STARTED","views":[],"clearance":[],"performance_acceptance":false}
var output := ""
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	call_deferred("run")
func finish(code:int)->void:
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("installed.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify(report,"\t"))
	print("ROOF_INSTALLED_RESULT ",JSON.stringify(report))
	quit(code)
func checkpoint(ship:Node3D,label:String)->void:
	var row:={"stage":label,"seconds":Time.get_ticks_msec()/1000.0,"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"static_bytes":Performance.get_monitor(Performance.MEMORY_STATIC)}
	for key:String in ["private_detail_residency","d04_detail_residency","exact_contact_residency"]:
		var manager=ship.get(key)
		if manager!=null:row[key]=manager.statistics()
	var received:Node=ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")
	if received!=null:row.received=received.statistics()
	print("ROOF_CHECK_STAGE ",JSON.stringify(row))
	var f:=FileAccess.open(output.path_join("last_stage.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify(row,"\t"));f.close()
func run()->void:
	if output.is_empty():quit(2);return
	var presentation:Node=load("res://scenes/main_clinical_transfer_junctions_integrated_20261024.tscn").instantiate()
	root.add_child(presentation)
	var ship:Node3D=presentation.world_view.get_node("Astraea")
	var started:=Time.get_ticks_msec()
	while not bool(ship.get_meta("runtime_ready",false)):
		if Time.get_ticks_msec()-started>420000:
			report.status="FAIL_STARTUP_TIMEOUT";finish(1);return
		await process_frame
	report.startup_seconds=(Time.get_ticks_msec()-started)/1000.0
	print("ROOF_CHECK_RUNTIME_READY ",report.startup_seconds)
	checkpoint(ship,"before_candidate")
	if not load("res://group7_aft_fixture_clearance_20261025/adapter.gd").build(ship):report.status="FAIL_FIXTURE";finish(1);return
	var candidate:Node3D=load("res://group7_terminal_roof_links_20261025/runtime_adapter.gd").build(ship)
	if candidate==null:report.status="FAIL_ADAPTER";finish(1);return
	checkpoint(ship,"after_candidate")
	presentation.set_world_resolution(2)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_controls_enabled(false)
	var views:Array=[{"name":"fore_neck","z":-514.0,"yaw":PI},{"name":"fore_body","z":-185.0,"yaw":0.0},{"name":"aft_body","z":202.0,"yaw":PI},{"name":"aft_neck","z":514.0,"yaw":0.0}]
	for view:Dictionary in views:
		checkpoint(ship,"before_arrival_"+str(view.name))
		if not ship.arrive_at(Vector3(0,106.55,float(view.z)),float(view.yaw)):
			report.status="FAIL_ARRIVAL";finish(1);return
		checkpoint(ship,"after_arrival_"+str(view.name))
		actor.set_controls_enabled(false)
		actor.pitch=0.08
		actor.camera.rotation.x=0.08
		await create_timer(4.0).timeout
	# Query real installed physics at sampled gallery points, excluding only the player.
	var shape:=BoxShape3D.new();shape.size=Vector3(7.98,4.0,0.12)
	for z:float in [-508.0,-490.0,-400.0,-300.0,-200.0,-181.1,194.1,200.0,300.0,400.0,490.0,508.0,193.7]:
		var query:=PhysicsShapeQueryParameters3D.new()
		query.shape=shape;query.margin=0.0;query.transform.origin=Vector3(0,108.505,z);query.exclude=[actor.get_rid()]
		var hits:Array[Dictionary]=ship.get_world_3d().direct_space_state.intersect_shape(query,32)
		var owners:Array[String]=[]
		for hit:Dictionary in hits:owners.append(str(hit.collider.get_path()))
		report.clearance.append({"z":z,"owners":owners,"scope":"sampled installed 7.98m wide by 4.0m high route air, bottom 5mm above floor"})
	report.status="PASS_SAMPLED_INSTALLED_CLEARANCE"
	for row:Dictionary in report.clearance:
		if not row.owners.is_empty():report.status="FAIL_INSTALLED_CLEARANCE"
	report.candidate_parts=candidate.get_meta("authored_parts")
	report.candidate_batches=candidate.get_meta("mesh_batches")
	finish(0)
