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
		verify(absf(actor.position.y)<.13,"Arrivals actor left retained D01 floor");verify(step<.08,"Ordinary walking step exceeded")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual retained support missing beneath step")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("G8 ARRIVALS WALK BLOCK ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Arrivals walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;g8_legs+=1
func animate(d:Node3D,actor:CharacterBody3D)->void:
	for frame in range(100):
		await physics_frame
		for leaf in d.leaves:
			for shape in leaf.get_children():
				if not shape is CollisionShape3D:continue
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape.shape;q.transform=shape.global_transform;q.exclude=[leaf.get_rid(),actor.get_rid()]
				for hit in g8_ship.get_world_3d().direct_space_state.intersect_shape(q,64):verify(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"New standard door leaf clips fixed geometry")
	verify(d.open_fraction>.999 if d.desired_open else d.open_fraction<.001,"Actual local service door did not reach requested state")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	g8_ship=main.get_node("World360/Astraea");var old:Node3D=g8_ship.get_node("ShipSpace/Districts/D01_D02_ArrivalsFusion_Integrated_WIP")
	var actor:CharacterBody3D=g8_ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/arrivals_service.json"));var original_poses:Dictionary={};var original_ids:Dictionary={}
	for node:Node3D in old.find_children("*","Node3D",true,false):
		if old.get_node("ArrivalsVisitorLift").is_ancestor_of(node):continue
		original_poses[str(node.get_path())]=node.global_transform
	for d:Node3D in g8_ship.find_children("*","Node3D",true,false):
		if d.get_script()==load("res://scripts/service_door.gd"):original_ids[str(d.get_path())]=str(d.persistent_id)
	var lift:Node3D=old.get_node("ArrivalsVisitorLift");var lift_id:=str(lift.persistent_id);var lift_stops:Array=lift.floor_heights.duplicate()
	additions=g8_ship.get_node("ShipSpace/Districts/Group8ArrivalsService_WIP")
	for frame in range(10):await physics_frame
	for path in original_poses:verify(original_poses[path].is_equal_approx(old.get_node(path).global_transform),"Original arrivals/reception/exhibit pose changed")
	for path in original_ids:verify(str(g8_ship.get_node(path).persistent_id)==original_ids[path],"Original service-door identity changed")
	verify(str(lift.persistent_id)==lift_id and lift.floor_heights==lift_stops and lift_stops==[0.0,6.0],"Original visitor lift/stops changed")
	verify(additions.get_meta("new_floor_owners")==0 and additions.get_meta("new_capacity")==0 and additions.get_meta("new_controllers")==0,"Programme/floor/capacity/controller ownership changed")
	verify(additions.find_children("G8A_BATCH_*","MeshInstance3D",true,false).size()==p.runtime_batches.size(),"Missing actual runtime source batches")
	for row in p.runtime_batches:
		var mesh:MeshInstance3D=additions.find_child(str(row.name),true,false);verify(mesh!=null,"Missing source batch")
		var faces:=mesh.mesh.get_faces();verify(faces.size()==int(row.triangles)*3,"Runtime source triangles changed")
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb;verify(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002,"Runtime native source pose changed")
		verify(mesh.has_node("StaticContact")==bool(row.collide),"Native collision policy changed")
	for row in p.meshes:
		var a:Array=row.world_aabb;var shape:=BoxShape3D.new();shape.size=Vector3(maxf(.0001,a[1]-a[0]-.0004),maxf(.0001,a[3]-a[2]-.0004),maxf(.0001,a[5]-a[4]-.0004));shape.margin=0
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=Vector3((a[0]+a[1])*.5,(a[2]+a[3])*.5,(a[4]+a[5])*.5);q.exclude=[actor.get_rid()]
		for hit in g8_ship.get_world_3d().direct_space_state.intersect_shape(q,64):
			if not old.is_ancestor_of(hit.collider):continue
			var permitted:=false
			for prefix in row.permitted_retained_context:
				if str(hit.collider.get_parent().name).begins_with(str(prefix).replace(".","_")):permitted=true
			verify(permitted,"New baggage fitting intrudes into retained architecture: %s / %s"%[row.name,hit.collider.get_path()])
	var omitted:Array[RID]=[actor.get_rid()]
	for body in additions.find_children("*","CollisionObject3D",true,false):omitted.append(body.get_rid())
	for row in p.supports:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);ray.exclude=omitted
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(ray);verify(not hit.is_empty()and absf(hit.position.y-at.y)<.003,"Actual original floor support missing")
	for row in p.retained_contacts:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var direction:=Vector3.UP
		if row.has("direction"):direction=Vector3(row.direction[0],row.direction[1],row.direction[2])
		var ray:=PhysicsRayQueryParameters3D.create(at-direction*.06,at+direction*.035);ray.exclude=omitted
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(ray)
		var expected:=str(row.expected_prefix).replace(".","_")
		var contact:=not hit.is_empty()and (str(hit.collider.get_parent().name).begins_with(expected)or str(hit.collider.get_path()).contains(expected))
		if not contact:print("G8 ARRIVALS CONTACT HOLD ",row," / ",hit)
		verify(contact,"Actual named original shell/upper slab support missing")
	var budget:Node=g8_ship.get_node("ShipSystems/LocalShadowSourceBudget");verify(additions.find_children("*","SpotLight3D",true,false).size()==p.lights.size(),"Physical task sources missing")
	for row in p.lights:
		var light:SpotLight3D=additions.get_node(str(row.name));verify(light.global_position.distance_to(Vector3(row.at[0],row.at[1],row.at[2]))<.0001,"Light detached from actual physical exit")
		verify(budget.sources.has(light)and budget.requested_shadow.has(light.get_instance_id()),"New source missing from shared budget")
		verify(g8_ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.07)).is_empty(),"Fixture source exit obstructed")
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*float(row.range))).is_empty(),"Fixture lacks actual receiver within source range")
	var d:Node3D=additions.get_node(str(p.door.name));verify(str(d.persistent_id)==str(p.door.persistent_id)and not d.desired_open and d.open_fraction<.001,"New proposed door identity/default incorrect")
	verify(d.global_position.distance_to(Vector3(p.door.at[0],p.door.at[1],p.door.at[2]))<.0001,"Door detached from exported source marker")
	# One ordinary public-arrival fixture, then only continuous physical walking.
	actor.position=Vector3(-5,.06,-432);actor.velocity=Vector3.ZERO
	for frame in range(10):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	for target in [Vector2(-24,-432),Vector2(-24,-447),Vector2(-37.9,-447),Vector2(-37.9,-458),Vector2(-37.9,-452)]:await go(actor,target)
	var closed:=PhysicsRayQueryParameters3D.create(Vector3(-37.9,1.2,-452),Vector3(-43,1.2,-452));closed.exclude=[actor.get_rid()];var closed_hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(closed)
	verify(not closed_hit.is_empty()and d.is_ancestor_of(closed_hit.collider),"Closed standard door lacks real leaf collision")
	await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(d.desired_open and d.open_fraction>.999,"Precise public-side RMB/E failed")
	for target in [Vector2(-43.5,-452),Vector2(-49.5,-452),Vector2(-49.5,-459),Vector2(-49.5,-463.8),Vector2(-47,-463.8),Vector2(-47,-461.0),Vector2(-47,-457.9),Vector2(-42.2,-457.9),Vector2(-42.2,-452),Vector2(-48.4,-452),Vector2(-48.4,-450.5),Vector2(-48.4,-452),Vector2(-43.5,-452),Vector2(-42.1,-452)]:await go(actor,target)
	await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open and d.open_fraction<.001,"Precise staff-side RMB/E closing failed")
	await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor)
	await go(actor,Vector2(-40.65,-452));d.interact(actor);verify(d.obstructed and d.desired_open,"Occupied actual sweep must reject closing")
	for frame in range(30):await physics_frame
	verify(d.open_fraction>.999,"Occupied local door did not remain open")
	await go(actor,Vector2(-37.9,-452));await go(actor,Vector2(-39.3,-452));await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open,"Local service threshold returns closed after withdrawal")
	await go(actor,Vector2(-37.9,-452))
	for target in [Vector2(-37.9,-447),Vector2(-24,-447),Vector2(-24,-432)]:await go(actor,target)
	var report:={"status":"PASS","checks":g8_checks,"runtime_batches":p.runtime_batches.size(),"physical_fixture_lights":p.lights.size(),"original_arrivals_nodes_and_poses_preserved":original_poses.size(),"original_service_door_identities_preserved":original_ids.size(),"original_visitor_lift_identity_and_stops_preserved":true,"new_authored_standard_door":1,"new_door_precise_RMB_E_both_sides":true,"new_door_occupied_sweep_interlock":true,"floor_supports":p.supports.size(),"named_retained_structure_contacts":p.retained_contacts.size(),"walk_legs":g8_legs,"ordinary_walk_frames":g8_frames,"walk_distance_m":g8_distance,"maximum_walk_step_m":g8_max_step,"setup_placements":1,"subsequent_route_teleports":0,"runtime_sha256":p.model_sha256,"native_sha256":p.native_sha256,"whole_operational_species_cart_engineering_final_art_acceptance":false}
	FileAccess.open("res://artifacts/group8_arrivals_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 ARRIVALS PASS: ",JSON.stringify(report))
	main.queue_free();for frame in range(4):await process_frame
	quit(0)
