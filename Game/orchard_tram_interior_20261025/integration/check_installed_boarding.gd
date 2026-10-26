extends SceneTree
const P:="res://orchard_tram_interior_20261025/integration/"
var report:={"scope":"Actual installed stationary Orchard: original lift, player, boarding controller and bridge. No cart relocation, tram travel or FPS claim.","selected":false,"checks":[],"failures":[]}
var presentation:Node
var ship:Node3D
var actor:CharacterBody3D
var safety:Node3D
func _initialize()->void:call_deferred("run")
func argument(key:String)->String:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with(key+"="):return arg.substr(key.length()+1)
	return ""
func require(ok:bool,label:String)->bool:
	report.checks.append(label)
	if not ok:report.failures.append(label)
	return ok
func key(down:bool)->void:
	var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=down;Input.parse_input_event(event)
func walk(target:Vector3)->bool:
	var start:=Time.get_ticks_msec();actor.gameplay_input_enabled=true;key(true)
	while Vector2(actor.global_position.x-target.x,actor.global_position.z-target.z).length()>.16:
		if Time.get_ticks_msec()-start>12000 or actor.global_position.y<55.9:
			key(false);actor.set_controls_enabled(false);report.walk_stop=str(actor.global_position);return false
		var delta:=target-actor.global_position;actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
	key(false);actor.set_controls_enabled(false);return true
func gates_open()->bool:
	var start:=Time.get_ticks_msec()
	while safety.phase!="boarding" or safety.station_gates["FORE_MIDSHIP"].open_fraction<.999 or safety.car_gates["PORT"].open_fraction<.999:
		if Time.get_ticks_msec()-start>20000:return false
		await physics_frame
	return true
func capture(label:String,yaw:float)->void:
	actor.rotation.y=yaw;actor.camera.current=true
	for i in range(8):await process_frame
	await RenderingServer.frame_post_draw
	var path:=argument("--result").get_base_dir()+"/"+label+".png"
	report[label]={"error":presentation.world_view.get_texture().get_image().save_png(path),"position":str(actor.global_position),"camera":str(actor.camera.global_position),"yaw":yaw}
func run()->void:
	presentation=load(P+"main.tscn").instantiate();root.add_child(presentation);presentation.set_world_resolution(2)
	ship=presentation.world_view.get_node("Astraea");var start:=Time.get_ticks_msec()
	while not ship.get_meta("runtime_ready",false):
		if Time.get_ticks_msec()-start>180000:require(false,"Startup deadline");finish();return
		await process_frame
	report.ready_seconds=(Time.get_ticks_msec()-start)/1000.;actor=ship.get_node("ShipSpace/PersistentActors/Player")
	if not require(ship.arrive_at(Vector3(13.5,56.2,-236.1),PI/2),"Original verified station arrival"):finish();return
	actor.set_controls_enabled(false)
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var lift:Node3D=assembly.get_node("Group4Lift_FORE_MIDSHIP");safety=assembly.get_node("Group4BoardingSafety")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var pose:=body.global_transform;var original_actor:=actor.get_instance_id();var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart");var cart_id:=cart.get_instance_id()
	for i in range(3):await physics_frame
	require(not safety.request_boarding("FORE_MIDSHIP"),"Production boarding hold retained")
	if not require(lift.request_floor(1),"Original lift accepts upper station request"):finish();return
	start=Time.get_ticks_msec()
	while lift.current_floor!=1 or lift.phase=="moving" or lift.phase=="closing":
		if Time.get_ticks_msec()-start>20000:require(false,"Lift upper arrival deadline");finish();return
		await physics_frame
	require(absf(lift.cabin.global_position.y-56.1)<.001,"Original cabin at boarding datum")
	await capture("occupied_arrival",PI/2)
	# Permission applies only to this diagnostic instance after installed sweep029.
	# Source/default operation and motor admission stay held.
	safety.set_meta("integration_boarding_admitted",true)
	if not require(safety.request_boarding("FORE_MIDSHIP"),"Original stationary boarding request"):finish();return
	if not require(await gates_open(),"Original bridge and station/car gates fully open"):finish();return
	if not require(await walk(body.to_global(Vector3(0,.02,0))),"Original player physically crosses bridge into car"):finish();return
	await capture("rider_orchard_interior",0.)
	if not require(safety.request_secure(),"Original secure request accepted"):finish();return
	start=Time.get_ticks_msec()
	while safety.phase!="secured":
		if Time.get_ticks_msec()-start>20000:require(false,"Secure deadline");finish();return
		await physics_frame
	require(safety.unloaded_clear_to_depart(),"Original portals and bridge secured; no motion")
	if not require(safety.request_boarding("FORE_MIDSHIP"),"Original reboard request"):finish();return
	if not require(await gates_open(),"Original portals reopen for alighting"):finish();return
	if not require(await walk(Vector3(13.5,56.12,-236.1)),"Original player returns physically to station"):finish();return
	require(actor.get_instance_id()==original_actor and cart.get_instance_id()==cart_id,"Persistent original player/cart retained")
	require(body.global_transform.is_equal_approx(pose),"Tram remained stationary throughout")
	report.remaining=["Loaded cart boarding and travel","Ordinary approach beyond diagnostic spawn","Grand-space architectural review","Resource stability and actual moving route performance","Aquatic integration and matching Windows"]
	finish()
func finish()->void:
	key(false)
	if is_instance_valid(actor):actor.set_controls_enabled(false)
	if is_instance_valid(safety):safety.set_meta("integration_boarding_admitted",false)
	var output:=argument("--result");assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close();print(JSON.stringify(report));quit(0 if report.failures.is_empty() else 2)
