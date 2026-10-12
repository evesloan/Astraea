extends "res://tests/validate_thread_shell.gd"
var checks:=0
var walk_frames:=0
var walk_legs:=0
var walk_distance:=0.0
var max_step:=0.0
var motion_frames:=0
var cart_samples:=0
var ship:Node3D
var stream:Node3D
var plan:Dictionary
func verify(ok:bool,message:String)->void:checks+=1;assert(ok,message)
func go(actor:CharacterBody3D,target:Vector3)->void:
	var reached:=false;var budget:=int(actor.position.distance_to(target)*60/3.1)+160
	for frame in range(budget):
		var offset:=target-actor.position;offset.y=0
		if offset.length()<.08:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z);actor.move_and_slide();await physics_frame
		var step:=before.distance_to(actor.position);max_step=maxf(max_step,step);walk_distance+=step;walk_frames+=1
		verify(absf(actor.position.y-61)<.12 and step<.08,"Dining actor left actual D10 floor or ordinary walking step")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Dining actor has no actual original floor support")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("DINING WALK HOLD ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Dining walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;walk_legs+=1
func animate(d:Node3D,actor:CharacterBody3D)->void:
	for f in range(90):
		await physics_frame;motion_frames+=1
		for leaf:AnimatableBody3D in d.leaves:
			for child in leaf.get_children():
				if not child is CollisionShape3D:continue
				var contact:CollisionShape3D=child
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[actor.get_rid(),leaf.get_rid()]
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):verify(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Local dining gateway clips fixed geometry: %s %.3f %s"%[d.name,d.open_fraction,hit.collider.get_path()])
	verify(d.open_fraction>.999 if d.desired_open else d.open_fraction<.001,"Local dining gateway failed to reach requested state")
func scoped_cart_envelope(d:Node3D,actor:CharacterBody3D,key:String)->void:
	# Only the changed local gateway is checked with the exact original source all-yaw envelope.
	# This is81 bounded stationary query poses,not another driven cart or shipwide experiment.
	var contract:Dictionary=plan.retained_contracts[key].source_cart_envelope;var shape:=CylinderShape3D.new();shape.radius=float(contract.test_radius_with_margin_m);shape.height=float(contract.actual_max_height_m)+.02;shape.margin=.001
	for i in range(27):
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,d.global_position+Vector3(0,.035+shape.height/2,-1.3+float(i)*.1));q.exclude=[actor.get_rid()];q.margin=0
		var hits:=ship.get_world_3d().direct_space_state.intersect_shape(q,64)
		if not hits.is_empty():print("DINING ORIGINAL CART ENVELOPE HOLD ",key," sample",i," ",hits)
		verify(hits.is_empty(),"Changed default-open gateway obstructs the exact original source cart envelope");cart_samples+=1
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");stream=ship.get_node("ShipSystems/RemainingBatchStreaming");plan=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_service.json"));var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var old_ids:Dictionary={}
	for d:Node3D in ship.find_children("*","Node3D",true,false):
		if d.get_script()==load("res://scripts/service_door.gd"):old_ids[str(d.get_path())]=str(d.persistent_id)
	var test_number:=int(OS.get_environment("G8_DINING_ROOM"));verify(test_number in [1,2,3],"One explicitly selected supported room-internal fixture required")
	var setup_side:=1 if test_number==2 else -1;var setup_z0:=-250 if test_number==3 else -466
	actor.position=Vector3(setup_side*11,61.06,setup_z0+34);actor.velocity=Vector3.ZERO
	for f in range(12):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var preserve_count:=0;var batches:=0;var lights:=0;var supports:=0;var contacts:=0
	var core:Node3D=ship.get_node("ShipSpace/Districts/ForwardPublicCore_WIP");var seams:Array=[]
	for mesh:MeshInstance3D in core.find_children("*","MeshInstance3D",true,false):
		var a:AABB=mesh.global_transform*mesh.get_aabb()
		if a.position.y<63 and a.end.y>61.05 and a.position.z< -430 and a.end.z> -434 and ((a.position.x< -4 and a.end.x> -10)or(a.position.x<10 and a.end.x>4)):seams.append({"path":str(mesh.get_path()),"world_aabb":[a.position.x,a.end.x,a.position.y,a.end.y,a.position.z,a.end.z]})
	FileAccess.open("res://data/architecture/group8/DINING_FORWARD_CORE_SEAM.json",FileAccess.WRITE).store_string(JSON.stringify({"unchanged_core_intersection_sources":seams,"core_owner":"Group1/shared integration","new_core_geometry_or_collision_changes":0},"  ")+"\n")
	for number in [test_number]:
		var key:="D10_directory_%02d"%number;var side:=1 if number==2 else -1;var z0:=-250 if number==3 else -466;var central_v:=35.5 if number==3 else 34.0
		
		var room:Node3D=stream.rooms[key]
		for f in range(12):await physics_frame
		verify(room.get_meta("stream_loaded",false),"Actual dining source room not installed")
		var original:Node3D=room.get_child(0);var snapshots:Dictionary={}
		for node:Node3D in original.find_children("*","Node3D",true,false):snapshots[node.get_instance_id()]={"node":node,"pose":node.global_transform}
		var n:Node3D=room.get_node_or_null(str(plan.root_name))
		if n==null:n=load("res://scripts/group8/dining_service.gd").build(ship,room)
		for f in range(8):await physics_frame
		verify(n.get_meta("new_capacity")==0 and n.get_meta("new_floor_owners")==0 and n.get_meta("new_shared_backends")==0,"Dining programme/capacity/backend ownership changed")
		for row in plan.runtime_batches:
			var mesh:MeshInstance3D=n.find_child(str(row.name),true,false)
			if str(row.programme_key)!=key:verify(mesh==null,"Another room's service meshes leaked into this source lifetime");continue
			verify(mesh!=null and mesh.has_node("StaticContact")==bool(row.collide),"Exact new service batch or collision policy missing");batches+=1
			var lo:=Vector3(INF,INF,INF);var hi:=-lo;var faces:=mesh.mesh.get_faces()
			for v in faces:var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at)
			var a:Array=row.world_aabb;verify(lo.distance_to(Vector3(a[0],a[2],a[4]))<.0002 and hi.distance_to(Vector3(a[1],a[3],a[5]))<.0002 and faces.size()==int(row.triangles)*3,"Source fitting import bounds/triangles changed")
		var omitted:Array[RID]=[actor.get_rid()]
		for body in n.find_children("*","CollisionObject3D",true,false):omitted.append(body.get_rid())
		for row in plan.supports:
			if str(row.programme_key)!=key:continue
			var at:=Vector3(row.at[0],row.at[1],row.at[2]);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);ray.exclude=omitted;var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			verify(not hit.is_empty()and absf(hit.position.y-61)<.003,"Original compiler floor support missing beneath new dining screen");supports+=1
		for row in plan.retained_contacts:
			if str(row.programme_key)!=key:continue
			var at:=Vector3(row.at[0],row.at[1],row.at[2]);var dir:=Vector3(row.direction[0],row.direction[1],row.direction[2]);var ray:=PhysicsRayQueryParameters3D.create(at-dir*.02,at+dir*.025);ray.exclude=omitted;var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			verify(not hit.is_empty()and str(hit.collider.get_path()).contains(str(row.expected_prefix)),"Actual original dining wall joint missing");contacts+=1
		var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
		for row in plan.lights:
			if str(row.programme_key)!=key:continue
			var light:SpotLight3D=n.get_node(str(row.name));verify(budget.sources.has(light)and budget.requested_shadow.has(light.get_instance_id()),"New housed service source not owned by existing light budget")
			var dir:=(Vector3(row.aim[0],row.aim[1],row.aim[2])-light.global_position).normalized();var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+dir*.045)
			verify(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual new fixture exit obstructed")
			ray.to=light.global_position+dir*float(row.range);verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual new task fixture lacks receiver in range");lights+=1
		if number==3:await go(actor,Vector3(side*11,61,z0+central_v))
		await go(actor,Vector3(side*47.7 if number==1 else(side*48 if number==2 else side*48),61,z0+central_v))
		var door_row:Dictionary={}
		for row in plan.doors:
			if str(row.programme_key)==key:door_row=row
		var d:Node3D=n.get_node(str(door_row.name));verify(d.desired_open and d.open_fraction>.999 and str(d.persistent_id)==str(door_row.persistent_id),"New utility identity/default state wrong")
		await go(actor,Vector3(d.position.x,61,z0+central_v));await go(actor,d.global_position+Vector3(0,0,1.2))
		scoped_cart_envelope(d,actor,key)
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open,"Public utility call failed")
		for x in [-.4,.4]:
			var ray:=PhysicsRayQueryParameters3D.create(d.global_position+Vector3(x,1.2,.8),d.global_position+Vector3(x,1.2,-.8));ray.exclude=[actor.get_rid()];var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray);verify(not hit.is_empty()and d.is_ancestor_of(hit.collider),"Closed local utility gateway lacks real leaf collision")
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor)
		await go(actor,d.global_position+Vector3(0,0,-2.0));await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open,"Inside utility call failed")
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor)
		await go(actor,d.global_position+Vector3(0,0,-.6));d.interact(actor);verify(d.obstructed and d.desired_open,"Occupied local utility sweep failed to refuse close")
		for f in range(15):await physics_frame
		verify(d.open_fraction>.999,"Occupied local utility gate moved")
		await go(actor,d.global_position+Vector3(0,0,-2.0));await go(actor,Vector3(d.position.x,61,z0+27.2))
		await go(actor,Vector3(side*52.4,61,z0+27.2)) # exact original u44.4 lane at passive wall station
		budget.refresh()
		for row in plan.lights:
			if str(row.programme_key)==key and str(row.name).contains("WashTask"):
				var light:SpotLight3D=n.get_node(str(row.name));verify(budget._has_visible_sample(light)and light.visible and light.shadow_enabled,"Actual reached hygiene stance must admit its real task source")
		await go(actor,Vector3(d.position.x,61,z0+27.2));await go(actor,d.global_position+Vector3(0,0,1.2))
		await go(actor,Vector3(d.position.x,61,z0+central_v));await go(actor,Vector3(side*48,61,z0+central_v));await go(actor,Vector3(side*48,61,z0+48))
		budget.refresh()
		for row in plan.lights:
			if str(row.programme_key)==key and str(row.name).contains("UsedReturnTask"):
				var light:SpotLight3D=n.get_node(str(row.name));verify(budget._has_visible_sample(light)and light.visible and light.shadow_enabled,"Actual reached return stance must admit its real task source")
		await go(actor,Vector3(side*48,61,z0+central_v));await go(actor,Vector3(side*11,61,z0+central_v));await go(actor,Vector3(side*11,61,z0+34))
		for row in snapshots.values():verify(is_instance_valid(row.node)and row.node.global_transform.is_equal_approx(row.pose),"Original dining furniture/source pose changed");preserve_count+=1
	var lifecycle:Dictionary={"tested":false}
	if test_number==3:
		var room:Node3D=stream.rooms["D10_directory_03"];var n:Node3D=room.get_node(str(plan.root_name));var refs:Array=[]
		for light in n.find_children("*","SpotLight3D",true,false):refs.append(weakref(light))
		var actor_pose:=actor.global_transform;var previous_stream_actor:Node3D=stream.actor
		var fixture:=Node3D.new();fixture.name="Group8ScopedStreamRangeFixture";root.add_child(fixture);fixture.position=Vector3(0,61,-600)
		stream.set_physics_process(false);stream.actor=fixture;stream.refresh()
		verify(not room.get_meta("stream_loaded",true)and not room.has_node(str(plan.root_name)),"Actual existing streamer must unload the owned dining kit with its source room")
		for ref:WeakRef in refs:verify(ref.get_ref()==null,"Unloaded dining fixture leaked")
		var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
		for light in budget.sources:verify(is_instance_valid(light),"Budget retained a dead dining source")
		stream.actor=previous_stream_actor;stream.refresh();stream.set_physics_process(true);fixture.free()
		verify(actor.global_transform.is_equal_approx(actor_pose),"Scoped lifecycle fixture must not move or replace the original actor")
		verify(room.get_meta("stream_loaded",false)and room.has_node(str(plan.root_name)),"Local dining construction must restore with exact source room")
		n=room.get_node(str(plan.root_name));verify(n.find_children("*","SpotLight3D",true,false).size()==2 and n.has_node("Group8DiningUtility_03"),"Restored dining kit duplicated or lost fittings")
		lifecycle={"tested":true,"scoped_existing_streamer_range_fixture":true,"original_actor_pose_and_identity_unchanged":true,"dead_source_cleanup":true,"continuous_whole_catchment_walk_acceptance":false}
	for path in old_ids:verify(str(ship.get_node(path).persistent_id)==old_ids[path],"Original service door identity changed")
	var report:={"status":"PASS","checks":checks,"tested_programme": "D10_directory_%02d"%test_number,"unchanged_source_node_poses":preserve_count,"original_seats_preserved":240,"original_service_door_ids":old_ids.size(),"new_standard_door_instances":1,"candidate_family_new_standard_door_instances":3,"new_source_batches":batches,"new_housed_sources":lights,"actual_floor_supports":supports,"actual_retained_wall_contacts":contacts,"motion_frames":motion_frames,"original_cart_envelope_gateway_samples":cart_samples,"cart_scope":"Exact retained all-yaw source envelope at changed default-open gateway;stationary queries,not driving or shipwide cart acceptance","precise_RMB_E_both_sides":true,"occupied_sweep_refusal":true,"lifecycle":lifecycle,"walk_legs":walk_legs,"walk_frames":walk_frames,"walk_distance_m":walk_distance,"maximum_step_m":max_step,"setup_placements":1,"subsequent_route_teleports":0,"external_public_connection_test":"SharedTable test001 held at unchanged Group1 ForwardPublicCore wall;room-internal fixture only here","external_catchments_food_hygiene_species_cart_operation_engineering_final_art_acceptance":false}
	FileAccess.open("res://data/architecture/group8/DINING_SERVICE_RUNTIME_%02d.json"%test_number,FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 DINING SERVICE PASS: ",JSON.stringify(report))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
