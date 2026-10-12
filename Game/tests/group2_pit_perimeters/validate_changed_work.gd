extends SceneTree
# New terraces/pose patches and the affected existing low routes only.
var checks := 0
func _initialize() -> void: call_deferred("run")
func floor_fixture(parent: Node3D,row: Dictionary) -> void:
	var faces := PackedVector3Array()
	for triangle in row.triangles:
		var p: Array[Vector3] = []
		for v in triangle: p.append(Vector3(v[0],row.floor_y,v[1]))
		if (p[1]-p[0]).cross(p[2]-p[0]).y > 0:p.reverse()
		faces.append_array(PackedVector3Array(p))
	var body := StaticBody3D.new();var shape := ConcavePolygonShape3D.new();shape.set_faces(faces)
	var contact := CollisionShape3D.new();contact.shape=shape;body.add_child(contact);parent.add_child(body)
func walk(actor: CharacterBody3D,target: Vector3) -> void:
	var key := InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached := false
	for frame in range(800):
		var delta := target-actor.global_position
		if Vector2(delta.x,delta.z).length()<.09:reached=true;break
		actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
		assert(actor.global_position.y>101.95 and actor.global_position.y<102.70,"Source receiver height remains bounded")
		checks += 1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached,"Changed-work route blocked: actor=%s target=%s" % [actor.global_position,target])
	assert(actor.is_on_floor() and abs(actor.global_position.y-target.y)<.09)
	checks += 2
func run() -> void:
	var world := Node3D.new();root.add_child(world)
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_pit_perimeters/PLAN_r003.json"))
	var floors: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/FLOOR_INTERFACE.json"))
	var routes: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_private_vertical/CONVERSATION_INTERFACE.json"))
	var results: Array=[]
	for row in plan.suites:
		var key := str(int(row.source_index));assert(key!="790")
		var section: Node3D=load("res://scripts/group2_completion/package.gd").build_section(world,key)
		for floor in floors.rows:
			if floor.source_owner==key:floor_fixture(section,floor)
		var old: Node3D=load("res://scripts/group2_private_vertical/package.gd").build_conversation_receiver(section,key,true)
		var visual := section.get_node("RetainedSource") as Node3D
		var before: Dictionary={}
		for mesh in visual.find_children("*","MeshInstance3D",true,false):before[mesh]=mesh.global_transform
		var receiver: Node3D=load("res://scripts/group2_pit_perimeters/package.gd").build(section,key,true)
		var selected: Array[String] = []
		for name in row.furniture_pose_patch.exact_mesh_names:selected.append(str(name).validate_node_name())
		for mesh in before:
			var expected: Transform3D=before[mesh]
			if str(mesh.name) in selected:
				var delta: Array=row.furniture_pose_patch.per_mesh_world_delta.get(str(mesh.name),[0,.45,0])
				expected.origin+=Vector3(delta[0],delta[1],delta[2])
			assert(mesh.global_transform.is_equal_approx(expected),"Only declared world elevation changes")
			checks += 1
		assert(old.find_child("G2R_"+key+"_ContinuousRearRamp",true,false)!=null)
		var contract: Dictionary=section.get_meta("source_contract")
		# Existing recorded routes are real original-player walks on unchanged low floors.
		for route in contract.source_routes_world:
			var actor: CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
			var start: Array=route[1][0];actor.global_position=Vector3(start[0],102.05,start[2]);actor.spawn_position=actor.global_position
			for frame in range(20):await physics_frame
			for p in route[1]:await walk(actor,Vector3(p[0],102,p[2]))
			actor.free();await physics_frame
		# Rear ramp is preserved; new raised dining/front/outer/rear terraces form one loop.
		var actor: CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
		var route_row: Dictionary={}
		for candidate in routes.suites:
			if int(candidate.source_index)==int(row.source_index):route_row=candidate
		var start: Array=route_row.walking_fixture[0];actor.global_position=Vector3(start[0],102.05,start[2]);actor.spawn_position=actor.global_position
		for frame in range(20):await physics_frame
		for p in route_row.walking_fixture:await walk(actor,Vector3(p[0],p[1],p[2]))
		for p in row.changed_walk_loop:await walk(actor,Vector3(p[0],p[1],p[2]))
		var back: Array=route_row.walking_fixture.duplicate();back.reverse()
		for p in back:await walk(actor,Vector3(p[0],p[1],p[2]))
		actor.free();results.append({"source_index":int(row.source_index),"original_world_geometry_and_basis_preserved":true,
			"declared_furniture_elevation_only":true,"low_source_routes":true,"preserved_rear_ramp":true,
			"full_raised_perimeter_walk_loop":true,"new_units":0})
		section.free();await physics_frame
		print("PIT PERIMETER suite "+key+" passed")
	var file:=FileAccess.open("res://artifacts/group2_pit_perimeters.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"suites":results,"790_excluded":true,
		"production_adoption":false,"cart_species_engineering_final_game_accepted":false,
		"scope":"Changed private terraces/furniture pose deltas and affected source routes only; lift suite not repeated"},"\t")+"\n")
	print("GROUP2 PIT PERIMETERS PASS five changed-work source/player loops and exact declared pose changes")
	quit()
