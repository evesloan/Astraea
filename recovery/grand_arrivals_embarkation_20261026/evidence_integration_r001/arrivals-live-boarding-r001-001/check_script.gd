extends SceneTree
const P:="res://grand_arrivals_tram_20261026/integration_r001/"
var report:Dictionary={"scope":"Actual retained player controller/capsule, original powered portals and bridge, source lower platform, short flat rider carry. Scripted velocity demand, no OS input, teleport, reparent or collision exclusion. Not installed full ship, graded rider carry or visual/FPS acceptance."}
var checks:=0
var failures:Array=[]
func require(ok:bool,label:String)->bool:
	checks+=1
	if not ok:failures.append(label)
	return ok
func _initialize()->void:call_deferred("run")
func run()->void:
	var ship:=Node3D.new();root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var districts:=Node3D.new();space.add_child(districts)
	var factory=load(P+"assembly.gd")
	var assembly:Node3D=factory.create(districts,"FORWARD")
	var receiving:Node3D=factory.raw_model("res://grand_arrivals_tram_20261026/r007/LowerDeparture.glb");districts.add_child(receiving)
	for mesh:MeshInstance3D in receiving.find_children("*","MeshInstance3D",true,false):mesh.create_trimesh_collision()
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var cart:RigidBody3D=load("res://scripts/cleaning_cart.gd").new();cart.name="CustodialCart";cart.position=Vector3(-20,.39,-452);actors.add_child(cart)
	var motor:Node3D=factory.attach_original_cart(assembly,cart)
	var safety:Node3D=motor.safety
	var player:CharacterBody3D=load("res://aquatic_tram_interior_20261026/integration/player.gd").new()
	player.spawn_position=Vector3(-15.6,.415,-449);player.position=player.spawn_position;actors.add_child(player)
	player.set_controls_enabled(false)
	for i in 90:await physics_frame
	if not require(player.is_on_floor() and absf(player.global_position.y-.365)<.03,"Actual player grounded on lower source platform"):report.player_position=str(player.global_position);ship.free();finish();return
	safety.set_meta("integration_boarding_admitted",true)
	if not require(safety.request_boarding("FORWARD"),"Original stationary docking guard permits lower boarding"):ship.free();finish();return
	for i in 240:await physics_frame
	if not require(safety.phase=="boarding" and safety.bridges.FORWARD.fraction>.999,"Original bridge physically deployed and boarding phase reached"):ship.free();finish();return
	var steps:=0
	while player.global_position.x< -12.7 and steps<300:
		# Original controller decelerates 16m/s2 toward no physical-key demand;
		# supply a bounded pre-step demand; its unchanged move_and_slide handles
		# all collisions, gravity and moving-platform velocity.
		player.velocity.x=1.0+16.0/Engine.physics_ticks_per_second
		await physics_frame;steps+=1
	player.velocity.x=0
	for i in 20:await physics_frame
	report.walk_frames=steps;report.boarded_position=str(player.global_position)
	if not require(player.global_position.x> -13.0 and player.is_on_floor(),"Actual player crosses original bridge and portal onto vehicle without position writes"):ship.free();finish();return
	if not require(safety.request_secure(),"Original closing request accepted after actual boarding"):ship.free();finish();return
	for i in 300:await physics_frame
	if not require(safety.unloaded_clear_to_depart(),"Actual thresholds clear, original portals closed and bridge stowed"):report.phase=safety.phase;ship.free();finish();return
	var local_start:Vector3=body.to_local(player.global_position)
	motor.set_meta("integration_motion_admitted",true)
	if not require(motor.request_distance(6.5),"Original unloaded-cart and portal guards admit short rider departure"):ship.free();finish();return
	var frames:=0;var maximum_drift:=0.0
	while motor.moving and frames<300:
		await physics_frame;frames+=1
		maximum_drift=maxf(maximum_drift,body.to_local(player.global_position).distance_to(local_start))
	report.carry_frames=frames;report.maximum_rider_local_drift_m=maximum_drift;report.cursor=motor.cursor
	require(not motor.moving and not motor.motion_fault and absf(motor.cursor-6.5)<.00001,"Short original-controller rider journey reaches exact destination")
	require(maximum_drift<.025 and player.is_on_floor(),"Original moving-platform carry retains rider within25mm without snapping")
	ship.free();finish()
func finish()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	report.checks=checks;report.failures=failures
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print(JSON.stringify(report));quit(0 if failures.is_empty() else 1)
