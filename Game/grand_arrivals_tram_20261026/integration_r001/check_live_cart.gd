extends SceneTree
const P:="res://grand_arrivals_tram_20261026/integration_r001/"
var report:Dictionary={"scope":"Fresh original assembly live stocked-cart restraint and short flat departure; no installed full ship, grade traction, rider or full-route acceptance"}
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
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var cart:RigidBody3D=load("res://scripts/cleaning_cart.gd").new();cart.name="CustodialCart"
	cart.transform=body.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.025,.14));actors.add_child(cart)
	var motor:Node3D=factory.attach_original_cart(assembly,cart)
	var safety:Node3D=motor.safety;var restraint:Node3D=motor.restraint
	for i in 180:await physics_frame
	report.settled_cart_local=str(body.global_transform.affine_inverse()*cart.global_transform)
	report.settled_cart_linear_speed=cart.linear_velocity.length()
	report.departure_clear=safety.unloaded_clear_to_depart()
	if not require(restraint.aligned(),"Unmodified cart physically settles in original lock tolerance"):ship.free();finish();return
	restraint.set_meta("integration_joint_admitted",true)
	if not require(restraint.request_lock(),"Original guard permits physical clamp/joint lock"):ship.free();finish();return
	for i in 150:await physics_frame
	if not require(restraint.phase=="locked" and is_instance_valid(restraint.joint) and restraint.loaded_clear_to_depart(),"Original stocked cart constrained by real original joint"):ship.free();finish();return
	var identities:Array=[]
	for stock:RigidBody3D in cart.products:identities.append(stock.get_instance_id())
	motor.set_meta("integration_motion_admitted",true)
	if not require(motor.request_distance(6.5),"Original guarded short departure accepted"):ship.free();finish();return
	var frames:=0
	while motor.moving and frames<420:
		await physics_frame;frames+=1
		if restraint.maximum_cart_frame_error_m>.025:failures.append("Original cart frame exceeded 25mm; stopped fixture");break
	report.frames=frames;report.cursor=motor.cursor;report.cart_frame_error_m=restraint.maximum_cart_frame_error_m
	report.motor_fault=motor.motion_fault;report.restraint_fault=restraint.motion_fault
	require(not motor.moving and not motor.motion_fault and not restraint.motion_fault and absf(motor.cursor-6.5)<.00001,"Original loaded cart carried to precise bounded destination")
	var after:Array=[]
	for stock:RigidBody3D in cart.products:after.append(stock.get_instance_id())
	require(after==identities,"Original four products preserved")
	require(not restraint.request_unlock(),"Original restraint refuses release away from station")
	ship.free();finish()
func finish()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	report.checks=checks;report.failures=failures
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print(JSON.stringify(report));quit(0 if failures.is_empty() else 1)
