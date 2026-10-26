extends SceneTree
class Guard extends Node3D:
	var clear:=true
	var phase:="unlocked"
	func unloaded_clear_to_depart()->bool:return clear
	func loaded_clear_to_depart()->bool:return clear
var checks:=0
func verify(ok:bool,label:String)->void:
	assert(ok,label);checks+=1
func _initialize()->void:call_deferred("run")
func frames()->void:
	for i in 3:await physics_frame
func ray_blocked(world:Node3D)->bool:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(3,1,-432),Vector3(8.2,1,-432))
	return not world.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
func run()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	var world:=Node3D.new();root.add_child(world)
	var crossing:Node3D=load("res://grand_arrivals_tram_20261026/crossing_r002/controller.gd").new();world.add_child(crossing);crossing.set_physics_process(false)
	var actor:=CharacterBody3D.new();var col:=CollisionShape3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;col.shape=capsule;actor.add_child(col);world.add_child(actor);actor.position=Vector3(5.6,.9,-432)
	await frames()
	verify(not crossing.get_meta("production_admitted"),"Candidate cannot claim production admission")
	verify(crossing.fraction==1,"Public passage initially open")
	verify(not crossing.request_lock(),"Occupied crossing refuses train permit")
	crossing._physics_process(2);verify(crossing.fraction==1,"No barrier lowers onto character")
	actor.position.x=0;await frames();crossing._physics_process(2);await frames()
	verify(crossing.closed_and_clear(),"Empty crossing closes and verifies both physical panels")
	verify(ray_blocked(world),"Closed native panel has physical barrier contact")
	verify(not crossing.request_release(false),"Tram-clear evidence required before reopening")
	verify(crossing.request_release(true),"Clear tram permits release")
	crossing._physics_process(2);await frames();verify(not ray_blocked(world),"Raised panels preserve the original crossing")
	var cart:=RigidBody3D.new();cart.freeze=true;var box:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.8,1,.8);box.shape=shape;cart.add_child(box);world.add_child(cart);cart.position=Vector3(5.6,.5,-432);await frames()
	verify(not crossing.request_lock(),"Unrestrained rigid payload blocks train permit")
	crossing._physics_process(2);verify(crossing.fraction==1,"No barrier lowers onto rigid payload")
	cart.position.x=0;await frames()
	# Actual adapter and retained super guard chain, without _ready/ship assembly.
	var motor:Node3D=load("res://grand_arrivals_tram_20261026/crossing_r002/loaded_actuator.gd").new()
	var body:=AnimatableBody3D.new();body.sync_to_physics=false;world.add_child(body)
	var safety:=Guard.new();var restraint:=Guard.new();world.add_child(safety);world.add_child(restraint)
	motor.vehicle=body;motor.safety=safety;motor.restraint=restraint
	motor.plan=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/grade_r007/MOTOR_PLAN.json"));motor.poses=JSON.parse_string(FileAccess.get_file_as_string(motor.plan.pose_file))
	for i in 2:
		var truck:=AnimatableBody3D.new();truck.sync_to_physics=false;body.add_child(truck);motor.bogies.append(truck)
	motor.configure_crossing(crossing);motor.cursor=motor.crossing_interval.x-2;motor.target=motor.cursor;motor.apply_pose(motor.cursor);motor.last_vehicle_pose=body.global_transform;motor.set_meta("integration_motion_admitted",true)
	var destination:float=motor.crossing_interval.y+2
	verify(not motor.request_distance(destination),"Open panels prevent original actuator departure")
	verify(motor.needs_crossing(destination,motor.cursor),"Reverse route has same crossing protection")
	crossing._physics_process(2);await frames()
	restraint.clear=false;verify(not motor.request_distance(destination),"Original cart restraint rejection preserved")
	restraint.clear=true;safety.clear=false;verify(not motor.request_distance(destination),"Original portal rejection preserved")
	safety.clear=true;verify(motor.request_distance(destination),"Secured empty physical crossing permits guarded fixture request")
	actor.position.x=5.6;await frames();motor._physics_process(.016)
	verify(motor.motion_fault and not motor.moving and motor.speed==0,"New occupancy faults and stops existing motion owner")
	var result:={"passed":true,"checks":checks,"crossing_interval":str(motor.crossing_interval),"physical_native_panels":crossing.panels.size(),"production_admitted":false,"scope":"Real native gate contacts/occupancy and actual adapter guard chain in isolated fixture; no original loaded joint, rider, installed assembly or full-route acceptance"}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();print(JSON.stringify(result));motor.free();world.free();quit(0)
