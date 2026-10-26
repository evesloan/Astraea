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
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/r003/PLAN.json"))
	var poses:Array=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/r003/POSE_KNOTS.json"))
	var state:=body.get_world_3d().direct_space_state
	for i in range(poses.size()-1):
		var a:Array=poses[i];var b:Array=poses[i+1]
		if a[0]<plan.orchard_interval_m[0] or b[0]>plan.orchard_interval_m[1]:continue
		var delta:=wrapf(float(b[3])-float(a[3]),-PI,PI)
		var half:=absf(delta)*.5
		# Mid-heading box encloses the full heading interval, without inflating Y.
		var box:=BoxShape3D.new()
		box.size=Vector3(2*(2*cos(half)+2.7*sin(half)),4.35,2*(2.7*cos(half)+2*sin(half)))
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.exclude=exclusions;q.margin=0
		q.transform=Transform3D(Basis(Vector3.UP,float(a[3])+delta*.5),Vector3(a[1],57.925,a[2]))
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
	report.status="PASS_INSTALLED_RESERVED_INTERVAL" if report.hits.is_empty() else "INSTALLED_CONTACT_HOLD"
	# A stationary overview of actual installed geometry, not a fabricated rider
	# or motion acceptance. The original player/residency focus remains untouched.
	var camera:=Camera3D.new();ship.add_child(camera)
	camera.global_position=Vector3(22.5,59.4,-247.5)
	camera.look_at(Vector3(12,56,-235),Vector3.UP);camera.fov=78;camera.current=true
	for i in range(5):await process_frame
	await RenderingServer.frame_post_draw
	var image:Image=presentation.world_view.get_texture().get_image()
	var path:=argument("--result").get_base_dir()+"/orchard_installed_station.png"
	if image!=null:report.image_error=image.save_png(path);report.image_path=path
	report.remaining=["Actual complete vehicle/door/cart continuous installed checks beyond reserved interval box","Boarding and circulation","Moving RID/resource correction","Real rider sightlines and performance","Selection and Windows export"]
	finish()
func finish()->void:
	var path:=argument("--result");assert(not FileAccess.file_exists(path))
	var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close()
	print(JSON.stringify(report));quit(0 if report.get("status","")=="PASS_INSTALLED_RESERVED_INTERVAL" else 2)
