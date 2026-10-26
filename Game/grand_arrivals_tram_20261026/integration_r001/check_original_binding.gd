extends SceneTree
const P:="res://grand_arrivals_tram_20261026/integration_r001/"
var checks:=0
var failures:Array=[]
var report:Dictionary={}
func require(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var ship:=Node3D.new();ship.name="FreshOriginalGradeBinding_NOT_INSTALLED";root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var factory=load(P+"assembly.gd")
	var assembly:Node3D=factory.create(districts,"FORWARD")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var original_pose:=body.global_transform
	var cart:RigidBody3D=load("res://scripts/cleaning_cart.gd").new()
	cart.name="CustodialCart";cart.transform=body.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.025,.14));actors.add_child(cart)
	cart.freeze=true
	for stock:RigidBody3D in cart.products:stock.freeze=true
	var cart_id:=cart.get_instance_id()
	var motor:Node3D=factory.attach_original_cart(assembly,cart)
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var restraint:Node3D=assembly.get_node("Group4OriginalCartRestraint")
	motor.set_physics_process(false)
	for i in 3:await physics_frame
	require(body.get_meta("exact_original_portal_contact_components",0)==18,"Original six portal frames converted exactly once to eighteen exact source solids")
	require(body.get_meta("group4_source_actuator")==motor.get_instance_id(),"Single original vehicle motor owner")
	require(restraint.cart.get_instance_id()==cart_id and cart.products.size()==4,"Original stocked cart identity retained")
	require(restraint.motor==motor and motor.restraint==restraint,"Single original restraint bound to grade motor")
	require(motor.bogies.size()==2 and motor.wheel_pivots.size()==4,"Actual original two trucks and four mesh wheels attached")
	require(body.global_transform.is_equal_approx(original_pose),"No post-entry initial vehicle relocation")
	require(not motor.request_stop("FORWARD") and not safety.request_boarding("FORWARD") and not restraint.request_lock(),"All installed admission gates remain held")
	var max_chord:=0.0;var max_gauge:=0.0;var max_wheel_center:=0.0
	# Source-mesh measurements, not placeholder trucks. No physics/rider runs
	# while sampling; persistent actors remain frozen in their initial positions.
	for row:Array in motor.poses:
		motor.apply_pose(row[0])
		max_chord=maxf(max_chord,absf(motor.bogies[0].global_position.distance_to(motor.bogies[1].global_position)-3.0))
		for truck:Node3D in motor.bogies:
			max_gauge=maxf(max_gauge,absf(truck.to_global(Vector3(-.86,0,0)).distance_to(truck.to_global(Vector3(.86,0,0)))-1.72))
	# Mesh vertex centroids relative to the authored wheel pivots are invariant
	# under this route's pitch/yaw/roll and are checked on the actual source.
	for wheel:Node3D in motor.wheel_pivots:
		var mesh:MeshInstance3D=wheel.get_child(0)
		var points:PackedVector3Array=mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
		var sum:=Vector3.ZERO
		for point:Vector3 in points:sum+=wheel.to_local(mesh.to_global(point))
		max_wheel_center=maxf(max_wheel_center,(sum/points.size()).length())
	require(max_chord<.0002,"Actual original truck chord over all authored poses")
	require(max_gauge<.0002,"Actual original truck wheel gauge over all authored poses")
	require(max_wheel_center<.0002,"Original mesh wheel centres coincide with original truck pivots")
	for stop:Dictionary in motor.plan.stops:
		motor.apply_pose(stop.distance_m)
		var dock:Transform3D=safety.expected_dock(stop.station)
		require(body.global_position.distance_to(dock.origin)<.0001 and body.global_basis.is_equal_approx(dock.basis),"Exact authored grade stop "+stop.station)
		require(safety.station_gates.has(stop.station) and safety.bridges.has(stop.station),"Original station identity "+stop.station)
		require(safety.door_side(stop.station) in ["PORT","STARBOARD"],"Real original portal side "+stop.station)
	motor.apply_pose(6);motor.cursor=6;motor.target=6;motor.last_vehicle_pose=body.global_transform
	report={"poses":motor.poses.size(),"max_chord_error_m":max_chord,"max_gauge_error_m":max_gauge,"max_original_wheel_center_error_m":max_wheel_center,"cart_physics_tested":false,"scope":"Fresh complete inherited five-station assembly with original vehicle, portals, trucks, wheels and original stocked cart; not installed full ship, rolling traction, boarding, rider carry or FPS acceptance"}
	ship.free();finish()
func finish()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	report.checks=checks;report.failures=failures
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print(JSON.stringify(report));quit(0 if failures.is_empty() else 1)
