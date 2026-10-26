extends SceneTree
const P:="res://aquatic_tram_interior_20261026/integration/"
var report:={"scope":"Actual installed stationary Aquatic: original lift, player, boarding controller and bridge. No cart relocation, tram travel or FPS claim.","selected":false,"checks":[],"failures":[],"queries":0,"hits":[]}
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
func walk(target:Vector3,min_y:float=55.9)->bool:
	var start:=Time.get_ticks_msec();actor.gameplay_input_enabled=true;key(true)
	while Vector2(actor.global_position.x-target.x,actor.global_position.z-target.z).length()>.16:
		if Time.get_ticks_msec()-start>12000 or actor.global_position.y<min_y:
			key(false);actor.set_controls_enabled(false);report.walk_stop=str(actor.global_position);return false
		var delta:=target-actor.global_position;actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
	key(false);actor.set_controls_enabled(false);return true
func gates_open()->bool:
	var start:=Time.get_ticks_msec()
	while safety.phase!="boarding" or safety.station_gates["AFT_MIDSHIP"].open_fraction<.999 or safety.car_gates["STARBOARD"].open_fraction<.999:
		if Time.get_ticks_msec()-start>20000:return false
		await physics_frame
	return true
func capture(label:String,yaw:float)->void:
	actor.rotation.y=yaw;actor.camera.rotation.x=-.12;actor.camera.current=true
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
	if not require(ship.arrive_at(Vector3(23.2,56.2,221),PI/2),"Original verified station arrival"):finish();return
	actor.set_controls_enabled(false)
	await capture("arrival_pre_clearance",-PI/2)
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var lift:Node3D=assembly.get_node("Group4Lift_AFT_MIDSHIP");safety=assembly.get_node("Group4BoardingSafety")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	if not require(await installed_sweep(assembly,body),"Actual installed reserved and original component sweeps"):finish();return
	var pose:=body.global_transform;var original_actor:=actor.get_instance_id();var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart");var cart_id:=cart.get_instance_id()
	for i in range(3):await physics_frame
	require(not safety.request_boarding("AFT_MIDSHIP"),"Production boarding hold retained")
	if not require(lift.request_floor(1),"Original lift accepts upper station request"):finish();return
	start=Time.get_ticks_msec()
	while lift.current_floor!=1 or lift.phase=="moving" or lift.phase=="closing":
		if Time.get_ticks_msec()-start>20000:require(false,"Lift upper arrival deadline");finish();return
		await physics_frame
	require(absf(lift.cabin.global_position.y-56.1)<.001,"Original cabin at boarding datum")
	await capture("occupied_arrival",-PI/2)
	# Permission applies only to this diagnostic instance after installed sweep029.
	# Source/default operation and motor admission stay held.
	safety.set_meta("integration_boarding_admitted",true)
	if not require(safety.request_boarding("AFT_MIDSHIP"),"Original stationary boarding request"):finish();return
	if not require(await gates_open(),"Original bridge and station/car gates fully open"):finish();return
	if not require(await walk(body.to_global(Vector3(0,.02,0))),"Original player physically crosses bridge into car"):finish();return
	await capture("rider_aquatic_interior",-PI/2)
	if not require(safety.request_secure(),"Original secure request accepted"):finish();return
	start=Time.get_ticks_msec()
	while safety.phase!="secured":
		if Time.get_ticks_msec()-start>20000:require(false,"Secure deadline");finish();return
		await physics_frame
	require(safety.unloaded_clear_to_depart(),"Original portals and bridge secured; no motion")
	if not require(safety.request_boarding("AFT_MIDSHIP"),"Original reboard request"):finish();return
	if not require(await gates_open(),"Original portals reopen for alighting"):finish();return
	if not require(await walk(Vector3(23.2,56.12,221)),"Original player returns physically to station"):finish();return
	require(actor.get_instance_id()==original_actor and cart.get_instance_id()==cart_id,"Persistent original player/cart retained")
	require(body.global_transform.is_equal_approx(pose),"Tram remained stationary throughout")
	await capture("station_lift_stair_context",.8)
	if not require(await walk(Vector3(23.3,56.12,186)),"Player enters original upper lift physically"):finish();return
	if not require(lift.request_floor(0),"Occupied original lift accepts lower request"):finish();return
	start=Time.get_ticks_msec()
	while lift.current_floor!=0 or lift.phase!="idle":
		if Time.get_ticks_msec()-start>20000:require(false,"Occupied lift lower arrival deadline");finish();return
		await physics_frame
	require(absf(actor.global_position.y-52.5)<.12,"Original cabin carries standing actor to lower gallery")
	for target in [Vector3(23.3,52.52,191.4),Vector3(33.3,52.52,191.4),Vector3(33.3,52.52,189.3)]:
		if not require(await walk(target,52.3),"Original lower gallery route "+str(target)):finish();return
	if not require(await walk(Vector3(25.5,56.12,189.3),52.3),"Actual installed stair ascent to station"):finish();return
	require(absf(actor.global_position.y-56.1)<.12,"Actual stair terminates at station datum")
	await capture("upper_relaxation_context",.6)
	report.remaining=["Loaded cart boarding and travel","Ordinary approach beyond diagnostic spawn","Grand-space architectural review","Resource stability and actual moving route performance","Final physical selection and matching Windows"]
	finish()
func finish()->void:
	key(false)
	if is_instance_valid(actor):actor.set_controls_enabled(false)
	if is_instance_valid(safety):safety.set_meta("integration_boarding_admitted",false)
	var output:=argument("--result");assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close();print(JSON.stringify(report));quit(0 if report.failures.is_empty() else 2)

func installed_sweep(assembly:Node3D,body:AnimatableBody3D)->bool:
	var exclusions:Array[RID]=[body.get_rid()]
	for item:CollisionObject3D in body.find_children("*","CollisionObject3D",true,false):exclusions.append(item.get_rid())
	for path:String in ["NamedSectionReceiving20261024/RollingGuidewayContacts","OrchardInteriorReceiving/RollingGuidewayContacts","AquaticInteriorReceiving/RollingGuidewayContacts"]:
		for item:CollisionObject3D in assembly.get_node(path).find_children("*","CollisionObject3D",true,false):exclusions.append(item.get_rid())
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r009/PLAN.json"))
	var poses:Array=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r009/POSE_KNOTS.json"))
	var state:=body.get_world_3d().direct_space_state
	for i in range(poses.size()-1):
		var a:Array=poses[i];var b:Array=poses[i+1]
		if a[0]<plan.aquatic_interval_m[0] or b[0]>plan.aquatic_interval_m[1]:continue
		var delta:=wrapf(float(b[3])-float(a[3]),-PI,PI)
		var half:=absf(delta)*.5
		# Mid-heading box encloses the full heading interval, without inflating Y.
		var box:=BoxShape3D.new()
		box.size=Vector3(2*(2*cos(half)+2.7*sin(half)),float(plan.guideway.running_clearance_top_y)-float(plan.guideway.boarding_y),2*(2.7*cos(half)+2*sin(half)))
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.exclude=exclusions;q.margin=0
		q.transform=Transform3D(Basis(Vector3.UP,float(a[3])+delta*.5),Vector3(a[1],(float(plan.guideway.running_clearance_top_y)+float(plan.guideway.boarding_y))*.5,a[2]))
		var initial:=state.intersect_shape(q,32)
		q.motion=Vector3(float(b[1])-float(a[1]),0,float(b[2])-float(a[2]))
		var sweep:=state.cast_motion(q)
		report.queries+=1
		if not initial.is_empty() or sweep[0]<1:
			var owners:Array[String]=[]
			for hit:Dictionary in initial:owners.append(str(hit.collider.get_path()))
			if owners.is_empty():
				q.transform.origin+=q.motion*minf(1.,sweep[1]+.0001);q.motion=Vector3.ZERO
				for hit:Dictionary in state.intersect_shape(q,32):owners.append(str(hit.collider.get_path()))
			report.hits.append({"cursor":a[0],"safe_fraction":sweep[0],"owners":owners})
	report.reserved_vertical_interval=[plan.guideway.boarding_y,plan.guideway.running_clearance_top_y]
	if report.hits.is_empty():
		report.component_sweep=load("res://orchard_tram_interior_20261025/integration/component_sweep.gd").audit(ship,assembly,poses,plan.aquatic_interval_m,exclusions)
	report.status="PASS_INSTALLED_RESERVED_INTERVAL" if report.hits.is_empty() and report.get("component_sweep",{}).get("hits",["not_run"]).is_empty() else "INSTALLED_CONTACT_HOLD"
	return report.status=="PASS_INSTALLED_RESERVED_INTERVAL"
