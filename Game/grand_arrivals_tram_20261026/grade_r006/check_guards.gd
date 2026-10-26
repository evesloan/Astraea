extends SceneTree
const MOTOR=preload("res://grand_arrivals_tram_20261026/grade_r006/loaded_actuator.gd")
class Guard extends Node3D:
	var clear:=true
	func unloaded_clear_to_depart()->bool:return clear
	func loaded_clear_to_depart()->bool:return clear
var checks:=0
var failures:Array=[]
func require(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label);push_error(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	var host:=Node3D.new();root.add_child(host)
	var vehicle:=AnimatableBody3D.new();vehicle.sync_to_physics=false;host.add_child(vehicle)
	var gates:=Guard.new();var load_guard:=Guard.new();host.add_child(gates);host.add_child(load_guard)
	# Deliberately do not call _ready: no production assembly or admission here.
	# Exercise the actual successor's unchanged request and physics guard chain.
	var motor:=MOTOR.new();motor.vehicle=vehicle;motor.safety=gates;motor.restraint=load_guard
	motor.plan=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/grade_r006/MOTOR_PLAN.json"))
	motor.poses=JSON.parse_string(FileAccess.get_file_as_string(motor.plan.pose_file))
	for i in 2:
		var truck:=AnimatableBody3D.new();truck.sync_to_physics=false;vehicle.add_child(truck);motor.bogies.append(truck)
	var max_chord:=0.0;var max_gauge:=0.0
	for row:Array in motor.poses:
		motor.apply_pose(float(row[0]))
		var rear:Vector3=motor.bogies[0].global_position;var front:Vector3=motor.bogies[1].global_position
		max_chord=maxf(max_chord,absf(rear.distance_to(front)-3.0))
		for truck:Node3D in motor.bogies:
			max_gauge=maxf(max_gauge,absf(truck.to_global(Vector3(.86,0,0)).distance_to(truck.to_global(Vector3(-.86,0,0)))-1.72))
	require(max_chord<.0002,"Original kingpin chord preserved in actual Godot transforms")
	require(max_gauge<.0002,"Original wheel gauge preserved in actual Godot transforms")
	motor.cursor=400.0;motor.target=400.0;motor.apply_pose(motor.cursor);motor.last_vehicle_pose=vehicle.global_transform
	motor.set_meta("integration_motion_admitted",false)
	require(not motor.request_distance(401),"Production admission hold rejects movement")
	motor.set_meta("integration_motion_admitted",true);load_guard.clear=false
	require(not motor.request_distance(401),"Original loaded-cart guard rejects departure")
	load_guard.clear=true;gates.clear=false
	require(not motor.request_distance(401),"Original portal and bridge guard rejects departure")
	gates.clear=true
	require(not motor.request_distance(-1),"Out-of-range departure rejected")
	require(motor.request_distance(401),"Secured fixture accepts bounded graded movement")
	var start:=vehicle.global_position
	for i in 600:motor._physics_process(1.0/60.0)
	require(not motor.moving and absf(motor.cursor-401)<.00001,"Graded movement stops at exact target")
	require(vehicle.global_position.y>start.y,"Motion actually changes elevation")
	require(motor.request_distance(402),"Next bounded request accepted")
	load_guard.clear=false;motor._physics_process(1.0/60.0)
	require(motor.motion_fault and not motor.moving and motor.speed==0,"Loss of loaded restraint faults and stops movement")
	motor.motion_fault=false;load_guard.clear=true;motor.last_vehicle_pose=vehicle.global_transform
	require(motor.request_distance(402),"Fixture reset permits independent unexpected-pose test")
	vehicle.position.x+=.01;motor._physics_process(1.0/60.0)
	require(motor.motion_fault and not motor.moving,"Unexpected external vehicle pose still faults")
	motor.free();host.free()
	var result:Dictionary={"checks":checks,"failures":failures,"poses":7962,"max_chord_error_m":max_chord,"max_gauge_error_m":max_gauge,"scope":"Actual successor guard chain and Godot transforms in an isolated fixture; no hardware collision, installed boarding, rider carry, traction, full ship or FPS acceptance"}
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));quit(0 if failures.is_empty() else 1)
