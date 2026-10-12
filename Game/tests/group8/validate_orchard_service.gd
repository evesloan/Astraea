extends "res://tests/validate_thread_shell.gd"
var g8_checks:=0
var g8_legs:=0
var g8_frames:=0
var g8_distance:=0.0
var g8_maximum_step:=0.0
var g8_ship:Node3D
var g8_additions:Node3D
func verify(value:bool,message:String)->void:
	g8_checks+=1;assert(value,message)
func go(actor:CharacterBody3D,target:Vector2)->void:
	var budget:=int(Vector2(actor.position.x,actor.position.z).distance_to(target)*60/3.1)+160
	var reached:=false
	for frame in range(budget):
		var offset:=Vector3(target.x-actor.position.x,0,target.y-actor.position.z)
		if offset.length()<.08:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z)
		actor.move_and_slide();await physics_frame
		var step:=before.distance_to(actor.position);g8_distance+=step;g8_maximum_step=maxf(g8_maximum_step,step);g8_frames+=1
		verify(absf(actor.position.y-61)<.13,"Orchard actor left retained floor")
		verify(step<.08,"Orchard walking step exceeds ordinary fixed60 movement")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Missing actual retained floor beneath step")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("ORCHARD G8 WALK BLOCK ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Orchard actual-player walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;g8_legs+=1
func operate(door:Node3D,actor:CharacterBody3D,precise:bool=false)->void:
	if precise:await press_door(actor,door,door.leaves[0].get_node("PushContact"))
	else:door.interact(actor)
	for frame in range(100):
		await physics_frame
		for leaf in door.leaves:
			for shape in leaf.get_children():
				if not shape is CollisionShape3D:continue
				var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape.shape;query.transform=shape.global_transform;query.exclude=[leaf.get_rid(),actor.get_rid()]
				for hit in g8_ship.get_world_3d().direct_space_state.intersect_shape(query,64):verify(not g8_additions.is_ancestor_of(hit.collider),"New galley fitting obstructs actual moving original leaf")
	verify(door.open_fraction>.999 if door.desired_open else door.open_fraction<.001,"Original service door failed to reach requested state")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	g8_ship=main.get_node("World360/Astraea");var room:Node3D=g8_ship.get_node("ShipSpace/Districts/D10_OrchardFoodHall_WIP")
	var actor:CharacterBody3D=g8_ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/orchard_service.json"))
	var ids:Dictionary={};var seats:Dictionary={}
	for child:Node3D in room.find_children("OrchardChair_*","Node3D",false,false):seats[str(child.get_meta("persistent_id"))]=child.global_transform
	for key in ["staff_door","pavilion_door_0","pavilion_door_1"]:ids[key]=str(room.get_node("OrchardFood_"+key).persistent_id)
	g8_additions=g8_ship.get_node("ShipSpace/Districts/Group8OrchardService_WIP")
	for frame in range(10):await physics_frame
	verify(g8_additions.get_meta("new_capacity")==0 and g8_additions.get_meta("new_floor_owners")==0 and g8_additions.get_meta("new_controllers")==0,"Protected programme ownership changed")
	verify(seats.size()==240 and room.find_children("OrchardChair_*","Node3D",false,false).size()==240,"Protected240 seats changed")
	for child:Node3D in room.find_children("OrchardChair_*","Node3D",false,false):verify(seats[str(child.get_meta("persistent_id"))].is_equal_approx(child.global_transform),"Original dining chair pose changed")
	for key in ids:verify(str(room.get_node("OrchardFood_"+key).persistent_id)==ids[key],"Original service door identity changed")
	verify(g8_additions.find_children("*","MeshInstance3D",true,false).size()==p.runtime_batches.size(),"Missing actual galley runtime batches")
	for row in p.runtime_batches:
		var mesh:MeshInstance3D=g8_additions.find_child(str(row.name),true,false);verify(mesh!=null,"Missing exported batch")
		var faces:=mesh.mesh.get_faces();verify(faces.size()==int(row.triangles)*3,"Actual exported triangle count changed")
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var a:Array=row.world_aabb;verify(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002,"Actual runtime source pose changed")
		verify(mesh.has_node("StaticContact")==bool(row.collide),"Galley collision differs from actual source policy")
	for row in p.meshes:
		var a:Array=row.world_aabb;var shape:=BoxShape3D.new();shape.size=Vector3(maxf(.0001,a[1]-a[0]-.0004),maxf(.0001,a[3]-a[2]-.0004),maxf(.0001,a[5]-a[4]-.0004));shape.margin=0
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])*.5,(a[2]+a[3])*.5,(a[4]+a[5])*.5));query.exclude=[actor.get_rid()]
		for hit in g8_ship.get_world_3d().direct_space_state.intersect_shape(query,64):
			if not room.is_ancestor_of(hit.collider):continue
			var permitted:=false
			for prefix in row.permitted_retained_context:
				if str(hit.collider.get_parent().name).begins_with(str(prefix)):permitted=true
			verify(permitted,"New galley fitting intrudes into retained food hall: %s / %s"%[row.name,hit.collider.get_path()])
	var omitted:Array[RID]=[actor.get_rid()]
	for body in g8_additions.find_children("*","CollisionObject3D",true,false):omitted.append(body.get_rid())
	for row in p.supports:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);ray.exclude=omitted
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(ray)
		verify(not hit.is_empty() and absf(hit.position.y-at.y)<.003,"New fixture lacks actual retained floor/counter support")
	for row in p.retained_contacts:
		var at:=Vector3(row.at[0],row.at[1],row.at[2])
		var direction:=Vector3.RIGHT if str(row.kind)=="fixture_to_original_wall" else Vector3.UP
		var query:=PhysicsRayQueryParameters3D.create(at-direction*.06,at+direction*.035);query.exclude=omitted
		var hit:=g8_ship.get_world_3d().direct_space_state.intersect_ray(query)
		var contact:=not hit.is_empty()and str(hit.collider.get_parent().name).begins_with(str(row.expected_prefix))
		if not contact:print("G8 ORCHARD MOUNT HOLD ",row," / ",hit)
		verify(contact,"New hood/task fixture lacks its named actual retained surface contact")
	verify(g8_additions.find_children("*","SpotLight3D",true,false).size()==p.lights.size(),"Missing galley light sources")
	var budget:Node=g8_ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for row in p.lights:
		var light:SpotLight3D=g8_additions.get_node(str(row.name));verify(light.global_position.distance_to(Vector3(row.at[0],row.at[1],row.at[2]))<.0001,"Lamp detached from physical source marker")
		verify(budget.sources.has(light)and budget.requested_shadow.has(light.get_instance_id()),"Galley lamp failed to join existing shared budget")
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.07)
		verify(g8_ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Galley source exit obstructed")
		var target:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*float(row.range))
		verify(not g8_ship.get_world_3d().direct_space_state.intersect_ray(target).is_empty(),"Task source lacks a real source-range receiver")
	# One public entry fixture, then only ordinary original-player walking.
	actor.position=Vector3(6,61.06,-216);actor.velocity=Vector3.ZERO
	for frame in range(10):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	for target in [Vector2(23,-216),Vector2(26.5,-216),Vector2(26.5,-233.4),Vector2(47.6,-233.4),Vector2(47.2,-214)]:await go(actor,target)
	var staff:Node3D=room.get_node("OrchardFood_staff_door");verify(not staff.desired_open,"Original staff threshold starts closed");await operate(staff,actor,true)
	for target in [Vector2(51,-214),Vector2(51,-228),Vector2(51,-222),Vector2(51,-209),Vector2(51,-201.5),Vector2(40,-201.5)]:await go(actor,target)
	for index in [1,0]:
		var z:float=-208.5 if index==1 else-223.5;await go(actor,Vector2(40,z))
		var d:Node3D=room.get_node("OrchardFood_pavilion_door_"+str(index));await operate(d,actor)
		for target in [Vector2(33.5,z),Vector2(33.5,z-4),Vector2(33.5,z),Vector2(32.2,z),Vector2(32.2,z+4),Vector2(34.6,z+4),Vector2(34.6,z+2.4),Vector2(34.6,z+4),Vector2(32.2,z+4),Vector2(32.2,z),Vector2(31.2,z),Vector2(40,z)]:await go(actor,target)
		await operate(d,actor);verify(not d.desired_open and d.open_fraction<.001,"Original pavilion door closes after staff withdrawal")
	# Changed local delivery streets use the actual original cart, load and driver query.
	var cart:RigidBody3D=g8_ship.find_child("CustodialCart",true,false);var excluded:Array[RID]=[]
	for body in g8_ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for x in [40.0,51.0]:
		for i in range(25):
			var z:float=-229.0+i*.9 if x==51.0 else-230.0+i*.9
			for yaw in [0.0,PI]:driver_pose(g8_ship,cart,Vector3(x,61.03,z),yaw,excluded)
	for target in [Vector2(40,-201.5),Vector2(51,-201.5),Vector2(51,-214),Vector2(47.2,-214)]:await go(actor,target)
	await operate(staff,actor);verify(not staff.desired_open,"Original public/staff threshold returns closed")
	var report:={"status":"PASS","checks":g8_checks,"runtime_batches":p.runtime_batches.size(),"fixture_lights":p.lights.size(),"original_candidate_seats_preserved":seats.size(),"original_service_door_identities_preserved":ids.size(),"source_floor_counter_supports":p.supports.size(),"retained_fixture_mounts":p.retained_contacts.size(),"walking_legs":g8_legs,"ordinary_walk_frames":g8_frames,"walk_distance_m":g8_distance,"maximum_step_m":g8_maximum_step,"setup_placements":1,"subsequent_teleports":0,"original_cart_load_driver_static_query_poses":samples,"runtime_sha256":p.model_sha256,"native_sha256":p.native_sha256,"operational_hygiene_species_engineering_and_final_art_acceptance":false}
	FileAccess.open("res://artifacts/group8_orchard_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 ORCHARD PASS: ",JSON.stringify(report))
	main.queue_free();for frame in range(4):await process_frame
	quit(0)
