extends "res://tests/validate_thread_shell.gd"
var g8_checks:=0
var g8_legs:=0
var g8_frames:=0
var g8_distance:=0.0
var g8_max_step:=0.0
var g8_ship:Node3D
var additions:Node3D
func verify(value:bool,message:String)->void:g8_checks+=1;assert(value,message)
func go(actor:CharacterBody3D,target:Vector2)->void:
	var budget:=int(Vector2(actor.position.x,actor.position.z).distance_to(target)*60/3.1)+160;var reached:=false
	for frame in range(budget):
		var offset:=Vector3(target.x-actor.position.x,0,target.y-actor.position.z)
		if offset.length()<.08:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z);actor.move_and_slide();await physics_frame
		var step:=before.distance_to(actor.position);g8_distance+=step;g8_max_step=maxf(g8_max_step,step);g8_frames+=1
		verify(absf(actor.position.y-78.0)<.13,"Library actor left retained D01 floor");verify(step<.08,"Ordinary walking step exceeded")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual retained support missing beneath step")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("G8 LIBRARY WALK BLOCK ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Library walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;g8_legs+=1
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	g8_ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=g8_ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/library_service.json"));var room:Node3D=g8_ship.get_node("ShipSpace/Districts/LongLibraryReceiving_WIP")
	verify(str(room.get_meta("programme_key"))=="D12_directory_02"and room.global_position.distance_to(Vector3(8,78,-466))<.0001,"Original library programme/pose changed")
	# One supported fore-route seed; normal source streaming installs the candidate hook.
	actor.position=Vector3(2,78.06,-456);actor.velocity=Vector3.ZERO
	for frame in range(45):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	verify(bool(room.get_meta("stream_loaded")),"Original library did not stream at normal approach")
	additions=room.get_node(str(p.root_name));var original:Node3D=room.get_child(0)
	verify(original.find_children("*","MeshInstance3D",true,false).size()==3150,"Original installed source3150shapes required")
	var poses:Dictionary={}
	for node:Node3D in original.find_children("*","Node3D",true,false):poses[str(node.get_path())]=node.global_transform
	var composite:Node3D=g8_ship.find_child("LongLibraryCompositeReceivingCore",true,false);verify(composite!=null and composite.get_child_count()==143,"Original QuietGrove composite must survive")
	var composite_poses:Dictionary={}
	for node:Node3D in composite.get_children():composite_poses[str(node.get_path())]=node.global_transform
	verify(additions.get_meta("new_floor_owners")==0 and additions.get_meta("new_capacity")==0 and additions.get_meta("new_controllers")==0,"Group8 scope changed original floor/capacity/controller ownership")
	verify(additions.find_children("G8L_BATCH_*","MeshInstance3D",true,false).size()==p.runtime_batches.size(),"Missing source batches")
	for row in p.runtime_batches:
		var mesh:MeshInstance3D=additions.find_child(str(row.name),true,false);verify(mesh!=null,"Missing source batch")
		var faces:=mesh.mesh.get_faces();verify(faces.size()==int(row.triangles)*3,"Runtime source triangles changed")
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb;verify(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002,"Actual new source pose changed")
		verify(mesh.has_node("StaticContact")==bool(row.collide),"Source collision policy changed")
	for row in p.meshes:
		var a:Array=row.world_aabb;var shape:=BoxShape3D.new();shape.size=Vector3(maxf(.0001,a[1]-a[0]-.0004),maxf(.0001,a[3]-a[2]-.0004),maxf(.0001,a[5]-a[4]-.0004));shape.margin=0
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=Vector3((a[0]+a[1])*.5,(a[2]+a[3])*.5,(a[4]+a[5])*.5);q.exclude=[actor.get_rid()]
		for hit in g8_ship.get_world_3d().direct_space_state.intersect_shape(q,64):
			if not original.is_ancestor_of(hit.collider)and not composite.is_ancestor_of(hit.collider):continue
			var allowed:=false
			for prefix in row.permitted_retained_context:
				if str(hit.collider.get_parent().name).begins_with(str(prefix).replace(".","_")):allowed=true
			verify(allowed,"New fitting intrudes into retained library/QuietGrove: %s/%s"%[row.name,hit.collider.get_path()])
	var exclude:Array[RID]=[actor.get_rid()]
	for body in additions.find_children("*","CollisionObject3D",true,false):exclude.append(body.get_rid())
	for row in p.supports:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);ray.exclude=exclude
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(ray);verify(not hit.is_empty()and absf(hit.position.y-at.y)<.003 and str(hit.collider.get_path()).contains("D12_directory_02_recovered_floor"),"Original sole library-floor support missing")
	for row in p.retained_contacts:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var direction:=Vector3(row.direction[0],row.direction[1],row.direction[2]);var ray:=PhysicsRayQueryParameters3D.create(at-direction*.06,at+direction*.035);ray.exclude=exclude
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(ray);verify(not hit.is_empty()and str(hit.collider.get_parent().name).begins_with(str(row.expected_prefix)),"Named original ceiling/roof tie support missing")
	var budget:Node=g8_ship.get_node("ShipSystems/LocalShadowSourceBudget");verify(additions.find_children("*","SpotLight3D",true,false).size()==p.lights.size(),"Visible physical fixture sources missing")
	for row in p.lights:
		var light:SpotLight3D=additions.get_node(str(row.name));verify(light.global_position.distance_to(Vector3(row.at[0],row.at[1],row.at[2]))<.0001,"Light detached from physical source")
		verify(budget.sources.has(light)and budget.requested_shadow.has(light.get_instance_id()),"New source missing from shared budget")
		verify(g8_ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.07)).is_empty(),"Source exit obstructed")
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*float(row.range))).is_empty(),"Source has no physical receiver")
	var route:Array[Vector2]=[Vector2(10,-456),Vector2(22,-456),Vector2(22,-451),Vector2(22,-452.2),Vector2(38,-452.2),Vector2(41.8,-451.9),Vector2(41.8,-453.2),Vector2(46.6,-453.2),Vector2(46.6,-459.05),Vector2(48.15,-459.05),Vector2(46.6,-459.05),Vector2(43.3,-458.5),Vector2(43.8,-458.5),Vector2(46.6,-458.5),Vector2(46.6,-462.7),Vector2(41.55,-462.7),Vector2(46.6,-462.7),Vector2(46.6,-458.5),Vector2(43.8,-458.5),Vector2(43.8,-456.6),Vector2(46.6,-456.6),Vector2(46.6,-453.2),Vector2(41.8,-453.2),Vector2(41.8,-451.9),Vector2(41.8,-449.2),Vector2(44,-449.2),Vector2(47.6,-448.75),Vector2(44,-449.2),Vector2(41.8,-451.9),Vector2(38,-452.2),Vector2(22,-452.2),Vector2(22,-451),Vector2(10,-451),Vector2(10,-456),Vector2(2,-456)]
	var light_observations:Dictionary={}
	for target in route:
		await go(actor,target)
		if target==Vector2(48.15,-459.05)or target==Vector2(43.3,-458.5)or target==Vector2(47.6,-448.75):
			for frame in range(20):await physics_frame
			budget.refresh();var state:Dictionary={}
			for row in p.lights:state[str(row.name)]=bool(additions.get_node(str(row.name)).visible)
			light_observations[str(target)]=state;print("G8 LIBRARY SOURCE ADMISSION ",target," ",state)
	for path in poses:verify(poses[path].is_equal_approx(original.get_node(path).global_transform),"Original library source pose changed")
	for path in composite_poses:verify(composite_poses[path].is_equal_approx(composite.get_node(path).global_transform),"Original QuietGrove receiving pose changed")
	var old_light_refs:Array=[]
	for light in additions.find_children("*","SpotLight3D",true,false):old_light_refs.append(weakref(light))
	await go(actor,Vector2(2,-524));for frame in range(20):await physics_frame
	verify(not bool(room.get_meta("stream_loaded"))and not room.has_node(str(p.root_name)),"New furnishings must unload with original room")
	for ref:WeakRef in old_light_refs:verify(ref.get_ref()==null,"Unloaded new light leaked into scene")
	for light in budget.sources:verify(is_instance_valid(light),"Shared budget retained a dead source")
	await go(actor,Vector2(2,-456));for frame in range(30):await physics_frame
	verify(bool(room.get_meta("stream_loaded"))and room.has_node(str(p.root_name)),"New furnishings must restore with original room")
	additions=room.get_node(str(p.root_name));verify(additions.find_children("*","SpotLight3D",true,false).size()==4 and room.get_child(0).find_children("*","MeshInstance3D",true,false).size()==3150,"Restore duplicated or lost original/new source")
	var report:={"status":"PASS","checks":g8_checks,"runtime_batches":p.runtime_batches.size(),"physical_fixture_lights":4,"original_library_meshes_preserved":3150,"original_library_node_poses_checked":poses.size(),"original_QuietGrove_parts_preserved":143,"floor_supports":p.supports.size(),"named_retained_ceiling_roof_contacts":p.retained_contacts.size(),"walk_legs":g8_legs,"ordinary_walk_frames":g8_frames,"walk_distance_m":g8_distance,"maximum_walk_step_m":g8_max_step,"setup_placements":1,"subsequent_route_teleports":0,"actual_source_stream_unload_restore_pass":true,"new_light_budget_lifetime_pass":true,"actual_new_fixture_admission_observations":light_observations,"runtime_sha256":p.model_sha256,"native_sha256":p.native_sha256,"whole_operational_species_cart_engineering_final_art_acceptance":false}
	FileAccess.open("res://artifacts/group8_library_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 LIBRARY PASS: ",JSON.stringify(report))
	main.queue_free();for frame in range(4):await process_frame
	quit(0)
