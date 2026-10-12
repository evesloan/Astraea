extends SceneTree
var checks:=0
func _initialize()->void:call_deferred("run")
func walk(actor: CharacterBody3D,target: Vector3)->void:
	var key:=InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached:=false
	for frame in range(600):
		var delta:=target-actor.global_position
		if Vector2(delta.x,delta.z).length()<.1:reached=true;break
		actor.rotation.y=atan2(-delta.x,-delta.z);await physics_frame
		assert(actor.global_position.y>101.95 and actor.global_position.y<102.1);checks+=1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached and actor.is_on_floor(),"Existing bounded care approach remains clear")
func floor_fixture(section: Node3D, row: Dictionary)->void:
	var faces:=PackedVector3Array()
	for t in row.triangles:
		var p:Array[Vector3]=[]
		for q in t:p.append(Vector3(q[0],row.floor_y,q[1]))
		if (p[1]-p[0]).cross(p[2]-p[0]).y>0:p.reverse()
		faces.append_array(PackedVector3Array(p))
	var body:=StaticBody3D.new();var collision:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new()
	shape.set_faces(faces);collision.shape=shape;body.add_child(collision);section.add_child(body)
func run()->void:
	var world:=Node3D.new();root.add_child(world)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_care_programmes/FITTINGS_r001.json"))
	var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/FLOOR_INTERFACE.json"))
	var results:Array=[]
	for row in data.rows:
		var section:Node3D=load("res://scripts/group2_completion/package.gd").build_section(world,row.key)
		for floor in floors.rows:
			if floor.source_owner==row.key:floor_fixture(section,floor)
		var original:=section.get_node("RetainedSource")
		var before:Dictionary={}
		for mesh in original.find_children("*","MeshInstance3D",true,false):before[mesh]=mesh.global_transform
		var kit:Node3D=load("res://scripts/group2_care_programmes/package.gd").build(section,row.key,true)
		for mesh in before:assert(mesh.global_transform.is_equal_approx(before[mesh]));checks+=1
		for shape in kit.find_children("*","CollisionShape3D",true,false):assert(shape.shape!=null)
		var actor:CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
		var start:Array=row.approach_walk[0];actor.position=Vector3(start[0],102.05,start[2]);actor.spawn_position=actor.position
		for frame in range(20):await physics_frame
		for p in row.approach_walk:await walk(actor,Vector3(p[0],102,p[2]))
		await walk(actor,Vector3(start[0],102,start[2]));actor.free()
		results.append({"key":row.key,"all_original_mesh_poses_unchanged":true,"bounded_original_player_approach":true,"receiving_and_fluid_acceptance":false})
		section.free();await physics_frame;print("CARE SOURCE "+row.key+" passed")
	var file:=FileAccess.open("res://artifacts/group2_care_programmes.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"rows":results,"new_capacity":0,"actual_external_connections_accepted":false},"\t")+"\n")
	print("GROUP2 CARE SOURCE PASS six unchanged-source counter approaches");quit()
