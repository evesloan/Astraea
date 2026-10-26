extends SceneTree
const P:="res://aquatic_tram_interior_20261026/integration/"
var report:={"scope":"Local exact retained original lift/platform/stair access; not installed or FPS acceptance.","selected":false,"checks":[],"failures":[],"queries":0,"hits":[]}
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
	var start:=Time.get_ticks_msec();var first:=actor.global_position;var frames:=0;actor.gameplay_input_enabled=true;key(true)
	while Vector2(actor.global_position.x-target.x,actor.global_position.z-target.z).length()>.16:
		if Time.get_ticks_msec()-start>12000 or actor.global_position.y<min_y:
			key(false);actor.set_controls_enabled(false);report.walk_stop={"position":str(actor.global_position),"target":str(target),"elapsed_ms":Time.get_ticks_msec()-start,"physics_frames":frames,"velocity":str(actor.velocity),"contacts":contact_names()};return false
		var delta:=target-actor.global_position;actor.rotation.y=atan2(-delta.x,-delta.z);frames+=1
		await physics_frame
	key(false);actor.set_controls_enabled(false)
	if not report.has("walks"):report.walks=[]
	report.walks.append({"from":str(first),"to":str(actor.global_position),"elapsed_ms":Time.get_ticks_msec()-start,"physics_frames":frames,"contacts":contact_names()});return true
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
	ship=Node3D.new();ship.name="AquaticLocalCirculation_NOT_INSTALLED";root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PIT_AND_BINDING.json"))
	var material:=StandardMaterial3D.new()
	load("res://scripts/structural_floor_builder.gd").build_regions(space,material,material,[proof.before],{"guest_floor":material})
	if not require(load(P+"floor.gd").apply(ship),"Exact floor receiver"):finish();return
	var built:Node3D=load(P+"assembly.gd").create(districts,"AFT_MIDSHIP");built.name="Group4Completion"
	actor=load(P+"player.gd").new();actor.position=Vector3(23.2,56.2,221);actor.spawn_position=actor.position;space.add_child(actor)
	for i in range(3):await physics_frame
	var start:=Time.get_ticks_msec()
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var lift:Node3D=assembly.get_node("Group4Lift_AFT_MIDSHIP")
	if not require(lift.request_floor(1),"Original lift accepts upper request"):finish();return
	start=Time.get_ticks_msec()
	while lift.current_floor!=1 or lift.phase!="idle":
		if Time.get_ticks_msec()-start>20000:require(false,"Lift upper deadline");finish();return
		await physics_frame
	for target in [Vector3(23.3,56.12,213),Vector3(23.3,56.12,205),Vector3(23.3,56.12,197),Vector3(23.3,56.12,189),Vector3(23.3,56.12,186)]:
		if not require(await walk(target),"Continuous platform walk to "+str(target)):finish();return
	if not require(lift.request_floor(0),"Occupied original lift accepts lower request"):finish();return
	start=Time.get_ticks_msec()
	while lift.current_floor!=0 or lift.phase!="idle":
		if Time.get_ticks_msec()-start>20000:require(false,"Occupied lift lower arrival deadline");finish();return
		await physics_frame
	require(absf(actor.global_position.y-52.5)<.12,"Original cabin carries standing actor to lower gallery")
	for target in [Vector3(23.3,52.52,189),Vector3(26.5,52.52,189),Vector3(26.5,52.52,187.3),Vector3(33.3,52.52,187.3),Vector3(33.3,52.52,189.3)]:
		if not require(await walk(target,52.3),"Original lower gallery route "+str(target)):finish();return
	if not require(await walk(Vector3(25.5,56.12,189.3),52.3),"Actual installed stair ascent to station"):finish();return
	require(absf(actor.global_position.y-56.1)<.12,"Actual stair terminates at station datum")

	report.remaining=["Loaded cart boarding and travel","Ordinary approach beyond diagnostic spawn","Grand-space architectural review","Resource stability and actual moving route performance","Final physical selection and matching Windows"]
	finish()
func finish()->void:
	key(false)
	if is_instance_valid(actor):actor.set_controls_enabled(false)
	if is_instance_valid(safety):safety.set_meta("integration_boarding_admitted",false)
	var output:=argument("--result");assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close();print(JSON.stringify(report));quit(0 if report.failures.is_empty() else 2)

func contact_names()->Array:
	var out:Array=[]
	for i in range(actor.get_slide_collision_count()):
		var c:=actor.get_slide_collision(i);out.append({"owner":str(c.get_collider().get_path()),"normal":str(c.get_normal())})
	return out
