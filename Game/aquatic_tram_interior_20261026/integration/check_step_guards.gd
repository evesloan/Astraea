extends SceneTree
const STEP=preload("res://aquatic_tram_interior_20261026/integration/step_motion.gd")
var results:Array=[]
func _initialize()->void:call_deferred("run")
func box(parent:Node3D,at:Vector3,size:Vector3)->void:
	var body:=StaticBody3D.new();parent.add_child(body);body.position=at
	var shape:=CollisionShape3D.new();var mesh:=BoxShape3D.new();mesh.size=size;shape.shape=mesh;body.add_child(shape)
func run()->void:
	for mode in ["ordinary_tread","too_high","low_ceiling","wall_no_landing","no_obstacle"]:
		var fixture:=Node3D.new();root.add_child(fixture)
		box(fixture,Vector3(0,-.1,0),Vector3(8,.2,4))
		if mode=="ordinary_tread" or mode=="low_ceiling":box(fixture,Vector3(1.25,.09,0),Vector3(1.5,.18,2))
		if mode=="too_high":box(fixture,Vector3(1.25,.2,0),Vector3(1.5,.4,2))
		if mode=="low_ceiling":box(fixture,Vector3(0,1.88,0),Vector3(4,.1,2))
		if mode=="wall_no_landing":box(fixture,Vector3(.51,1,0),Vector3(.02,2,2))
		var actor:=CharacterBody3D.new();fixture.add_child(actor);actor.position=Vector3(.222,.001,0)
		var shape:=CollisionShape3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;shape.shape=capsule;shape.position.y=.9;actor.add_child(shape)
		for i in range(3):await physics_frame
		var before:=actor.global_position
		var moved:bool=STEP.apply(actor,Vector3(.05,0,0))
		var expected:bool=mode=="ordinary_tread"
		results.append({"mode":mode,"moved":moved,"expected":expected,"before":str(before),"after":str(actor.global_position),"pass":moved==expected and (moved or actor.global_position==before)})
		fixture.queue_free();await physics_frame
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(results,"\t"));file.close()
	print(JSON.stringify(results));quit(0 if results.all(func(r):return r.pass) else 2)
