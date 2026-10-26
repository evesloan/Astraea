extends SceneTree
const P:="res://orchard_tram_interior_20261025/integration/"
var presentation:Node
var ship:Node3D
var report:={"selected":false,"ready":false,"scope":"Complete inherited ship with unselected Orchard integration; stationary installed geometry validation, no travel performance claim","queries":0,"hits":[]}
func _initialize()->void:call_deferred("run")
func argument(key:String)->String:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with(key+"="):return arg.substr(key.length()+1)
	return ""
func run()->void:
	presentation=load(P+"main.tscn").instantiate();root.add_child(presentation)
	presentation.set_world_resolution(2)
	ship=presentation.world_view.get_node("Astraea")
	var started:=Time.get_ticks_msec()
	while not ship.get_meta("runtime_ready",false):
		if Time.get_ticks_msec()-started>180000:
			report.status="STARTUP_DEADLINE";finish();return
		await process_frame
	report.ready=true;report.startup_seconds=(Time.get_ticks_msec()-started)/1000.0
	for i in range(3):await physics_frame
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var exclusions:Array[RID]=[body.get_rid()]
	for item:CollisionObject3D in body.find_children("*","CollisionObject3D",true,false):exclusions.append(item.get_rid())
	for path:String in ["NamedSectionReceiving20261024/RollingGuidewayContacts","OrchardInteriorReceiving/RollingGuidewayContacts"]:
		for item:CollisionObject3D in assembly.get_node(path).find_children("*","CollisionObject3D",true,false):exclusions.append(item.get_rid())
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/r006/PLAN.json"))
	var poses:Array=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/r006/POSE_KNOTS.json"))
	var state:=body.get_world_3d().direct_space_state
	for i in range(poses.size()-1):
		var a:Array=poses[i];var b:Array=poses[i+1]
		if a[0]<plan.orchard_interval_m[0] or b[0]>plan.orchard_interval_m[1]:continue
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
			if report.hits.size()>=12:break
	report.reserved_vertical_interval=[plan.guideway.boarding_y,plan.guideway.running_clearance_top_y]
	if report.hits.is_empty():
		report.component_sweep=load(P+"component_sweep.gd").audit(ship,assembly,poses,plan.orchard_interval_m,exclusions)
	report.status="PASS_INSTALLED_RESERVED_INTERVAL" if report.hits.is_empty() and report.get("component_sweep",{}).get("hits",["not_run"]).is_empty() else "INSTALLED_CONTACT_HOLD"
	if "--orchard-review-spawn" in OS.get_cmdline_user_args():
		report.verified_station_arrival=ship.arrive_at(Vector3(13.5,56.2,-236.1),0.)
		if not report.verified_station_arrival:report.status="ARRIVAL_HOLD";finish();return
		var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
		actor.set_controls_enabled(false)
		actor.camera.current=true
		for i in range(20):await process_frame
		var lamps:Array=[]
		for light:Light3D in ship.find_children("*","Light3D",true,false):
			if light.global_position.distance_to(actor.global_position)<18:
				lamps.append({"path":str(light.get_path()),"visible":light.visible,"shadow":light.shadow_enabled,"energy":light.light_energy})
		report.nearby_fixture_state=lamps
		report.review_scope="Diagnostic station startup and original verified arrival, actual player camera and existing light budget; not travel or final art acceptance"
		report.camera_position=[actor.camera.global_position.x,actor.camera.global_position.y,actor.camera.global_position.z]
		await RenderingServer.frame_post_draw
		var image:Image=presentation.world_view.get_texture().get_image()
		var folder:=argument("--result").get_base_dir()
		report.image_error=image.save_png(folder+"/orchard_actual_player_1080.png")
		presentation.set_world_resolution(0)
		for i in range(5):await process_frame
		await RenderingServer.frame_post_draw
		report.retro_image_error=presentation.post_view.get_texture().get_image().save_png(folder+"/orchard_actual_player_retro360.png")
	report.remaining=["Loaded-cart boarding and ordinary arrival beyond diagnostic spawn","Boarding and circulation","Moving RID/resource correction","Real rider sightlines and performance","Selection and Windows export"]
	finish()
func finish()->void:
	var path:=argument("--result");assert(not FileAccess.file_exists(path))
	var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close()
	print(JSON.stringify(report));quit(0 if report.get("status","")=="PASS_INSTALLED_RESERVED_INTERVAL" else 2)
