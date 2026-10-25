extends SceneTree
var host:Node
var ship:Node3D
var assembly:Node3D
var actor:CharacterBody3D
var cart:RigidBody3D
var body:AnimatableBody3D
var safety:Node3D
var motor:Node3D
var restraint:Node3D
var controls:Node3D
var samples:Array=[]
var output:String
func _initialize()->void:call_deferred("run")
func require(ok:bool,why:String)->bool:
	if not ok:push_error(why)
	return ok
func key(down:bool)->void:
	var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=down;Input.parse_input_event(event)
func finish(reason:String="source_setup_failed")->void:
	key(false)
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"reason":reason,"samples":samples,"fixture_only":true},"  "));f.close()
	print("BOARDING_DIAGNOSTIC ",reason)
	if is_instance_valid(host):host.free()
	quit(0)
func run()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--report="):output=arg.trim_prefix("--report=")
	if output.is_empty():quit(2);return
	host = Node.new()
	host.name = "AstraeaOriginalSourceCarryFixture_UNACCEPTED"
	root.add_child(host)
	var viewport := SubViewport.new()
	viewport.name = "World360"
	viewport.size = Vector2i(640,360)
	viewport.own_world_3d = true
	viewport.audio_listener_enable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	host.add_child(viewport)
	ship = Node3D.new()
	ship.name = "Astraea"
	viewport.add_child(ship)
	var space := Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts := Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors := Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var systems := Node.new();systems.name="ShipSystems";ship.add_child(systems)
	assembly = load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd").create(districts)
	if not require(assembly != null,"retained exact source section/vehicle/stations assembled once"):
		finish();return
	body = assembly.get_node("Group4OwnedTram_Source024")
	safety = assembly.get_node("Group4BoardingSafety")
	if not require(body.has_meta("initial_pose_before_tree") and body.transform.is_equal_approx(body.get_meta("initial_pose_before_tree")),"full source vehicle pose was assigned before initial tree admission"):
		finish();return
	# These are the only actor pose assignments: fresh instances are outside the
	# tree and have never entered physics. No existing actor or stock is moved.
	actor = load("res://scripts/player.gd").new()
	actor.position = Vector3(-4.5,56.15,-75.3)
	actor.spawn_position = actor.position
	actor.rotation.y = body.rotation.y
	actors.add_child(actor)
	cart = load("res://scripts/cleaning_cart.gd").new()
	cart.name = "CustodialCart"
	cart.position = Vector3(-5.6,56.125,-73.5)
	cart.contact_monitor = true
	cart.max_contacts_reported = 32
	actors.add_child(cart)
	motor = load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd").attach_original_cart(assembly,cart)
	restraint = assembly.get_node("Group4OriginalCartRestraint")
	var budget: Node = load("res://scripts/lighting_budget.gd").new()
	budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.configure(ship,actor)
	controls=load("res://scripts/group4_tram_operating_controls.gd").build(assembly,body,safety,restraint,motor,actor,budget)
	load("res://scripts/group4_station_information.gd").build(assembly,safety)
	for i in range(20):await physics_frame
	safety.set_meta("integration_boarding_admitted",true)
	if not controls.begin_boarding("CENTRAL"):finish("boarding_request_refused");return
	for i in range(1200):
		if safety.phase=="boarding":break
		await physics_frame
	if safety.phase!="boarding":finish("boarding_phase_timeout");return
	# Phase boarding begins when opening is requested, not when leaves finish.
	for i in range(240):
		if safety.station_gates["CENTRAL"].open_fraction>.999 and safety.car_gates[safety.door_side("CENTRAL")].open_fraction>.999:break
		await physics_frame
	if safety.station_gates["CENTRAL"].open_fraction<.999 or safety.car_gates[safety.door_side("CENTRAL")].open_fraction<.999:finish("gate_opening_held");return
	actor.gameplay_input_enabled=true
	var target:Vector3=body.to_global(Vector3(0,.02,0))
	key(true)
	for i in range(1200):
		var delta:=target-actor.global_position;actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
		if i%10==0 or actor.global_position.y<55.9:
			var hits:Array=[]
			for j in actor.get_slide_collision_count():
				var c:=actor.get_slide_collision(j);hits.append({"owner":str(c.get_collider().get_path()),"normal":str(c.get_normal()),"position":str(c.get_position())})
			samples.append({"frame":i,"position":str(actor.global_position),"velocity":str(actor.velocity),"on_floor":actor.is_on_floor(),"input_pressed":Input.is_physical_key_pressed(KEY_W),"input_enabled":actor.gameplay_input_enabled,"station_gate_open":safety.station_gates["CENTRAL"].open_fraction,"car_gate_open":safety.car_gates[safety.door_side("CENTRAL")].open_fraction,"target":str(target),"hits":hits})
		if actor.global_position.y<55.9:finish("fell_below_platform");return
		if Vector2(delta.x,delta.z).length()<.16:finish("crossed");return
	finish("crossing_frame_limit")
