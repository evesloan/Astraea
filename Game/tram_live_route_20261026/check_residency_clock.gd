extends SceneTree
class ClockResidency:
	extends "res://scripts/received_homes_20261015/residency.gd"
	var now_ms:int=100000
	func _clock_msec()->int:return now_ms
var checks:=0
var failures:Array=[]
func require(ok:bool,message:String)->void:
	checks+=1
	if not ok:failures.append(message);push_error(message)
func _initialize()->void:call_deferred("run")
func run()->void:
	var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var actor:=Node3D.new();actors.add_child(actor)
	var body:=RigidBody3D.new();body.freeze=true;actors.add_child(body)
	var room:=Node3D.new();room.name="Retained_788";host.add_child(room)
	var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,"788")
	room.set_meta("retained_group2_home",true);room.set_meta("resident_visual",source)
	var contacts:Array=[]
	for shape:CollisionShape3D in source.find_children("*","CollisionShape3D",true,false):contacts.append([shape.get_instance_id(),shape.shape.get_instance_id(),shape.transform])
	var controls:Array=[]
	for node:Node in source.get_children():
		if str(node.name).begins_with("Fitting_"):
			node.open_fraction=.37;node.desired_open=true;node._apply_pose();controls.append([node,node.persistent_id])
	var manager:=ClockResidency.new();host.add_child(manager);manager.set_process(false);manager.set_physics_process(false);manager.host=host;manager.actor=actor
	var witness:=VisibleOnScreenNotifier3D.new();host.add_child(witness)
	var entry:Dictionary={"room":room,"parent":host,"bounds":AABB(Vector3(1000,0,0),Vector3.ONE),"witness":witness,"attached":true,"hidden_seconds":0.0,"meshes":1324}
	manager.entries.append(entry)
	manager.refresh(.2);require(entry.attached,"Hidden distant room retained initially")
	manager.now_ms+=7999;manager.refresh(.2);require(entry.attached,"Full 8 seconds grace preserved")
	manager.now_ms+=1;manager.refresh(.2);require(not entry.attached and room.get_parent()==null,"Release at 8 real seconds despite only .6 simulated seconds")
	var lease:Dictionary=source.get_meta("group2_mesh_lease")
	for row:Dictionary in lease.rows:require(row.suspended,"Actual original source mesh lease suspended")
	actor.position=Vector3(1000,0,0);manager.refresh(.2);require(entry.attached and room.get_parent()==host,"Near collision preparation remains synchronous")
	for row:Dictionary in lease.rows:require(not row.suspended,"Actual source restored")
	manager.now_ms+=60000;manager.refresh(.2);require(entry.attached,"Near player never expires")
	actor.position=Vector3(940,0,0);manager.refresh(.2);require(entry.attached and entry.demand.keep_band_only,"Original 65m hysteresis safety band retained")
	actor.position=Vector3.ZERO;body.position=Vector3(1000,0,0);manager.refresh(.2);manager.now_ms+=60000;manager.refresh(.2);require(entry.attached and entry.demand.body_near,"Loose-body supporting room retained")
	body.position=Vector3.ZERO;manager.refresh(.2);manager.now_ms+=8000;manager.refresh(.2);require(not entry.attached,"Repeated release after all demand removed")
	actor.position=Vector3(1000,0,0);manager.prepare_position(actor.position);require(entry.attached,"Explicit arrival still restores synchronously")
	var after:Array=[]
	for shape:CollisionShape3D in source.find_children("*","CollisionShape3D",true,false):after.append([shape.get_instance_id(),shape.shape.get_instance_id(),shape.transform])
	require(contacts==after,"Collision node/shape identities and poses preserved")
	for control:Array in controls:require(control[0].persistent_id==control[1] and control[0].open_fraction==.37 and control[0].desired_open,"Persistent door state preserved")
	var result:Dictionary={"checks":checks,"failures":failures,"physics_seconds_before_release":.6,"real_seconds_before_release":8,"contact_count":contacts.size(),"door_count":controls.size()}
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):
			var f:=FileAccess.open(arg.substr(9),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	host.queue_free();await process_frame;await process_frame
	print(JSON.stringify(result));quit(0 if failures.is_empty() else 1)
