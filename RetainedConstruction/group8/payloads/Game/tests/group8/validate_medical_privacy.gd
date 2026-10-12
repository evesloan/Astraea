extends "res://tests/validate_thread_shell.gd"
var checks:=0
var legs:=0
var frames:=0
var distance:=0.0
var max_step:=0.0
var motion_frames:=0
var ship:Node3D
var arch:Node3D
var additions:Node3D
var plan:Dictionary
func verify(value:bool,message:String)->void:
	checks+=1
	assert(value,message)
func go(actor:CharacterBody3D,target:Vector3)->void:
	var budget:=int(actor.position.distance_to(target)*60/3.1)+160;var reached:=false
	for frame in range(budget):
		var offset:=target-actor.position;offset.y=0
		if offset.length()<.08:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z);actor.move_and_slide();await physics_frame
		var step:=actor.position.distance_to(before);distance+=step;max_step=maxf(max_step,step);frames+=1
		verify(absf(actor.position.y-21)<.12 and step<.08,"Continuous original-player clinical walk lost floor or exceeded a walking step")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Retained medical floor missing beneath actual walking step")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("MEDICAL WALK HOLD ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Medical walk stalled: %s to %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;legs+=1
func local_go(actor:CharacterBody3D,d:Node3D,x:float,z:float)->void:
	await go(actor,d.global_transform*Vector3(x,0,z))
func check_motion(d:Node3D,actor:CharacterBody3D)->void:
	for frame in range(90):
		await physics_frame;motion_frames+=1
		for index in range(2):
			var hinge:Node3D=d.hinge_nodes[index];var omitted:Array[RID]=[actor.get_rid()]
			for mesh:MeshInstance3D in hinge.get_children():omitted.append(mesh.get_node("StaticContact").get_rid())
			for mesh:MeshInstance3D in hinge.get_children():
				var body:AnimatableBody3D=mesh.get_node("StaticContact");var contact:CollisionShape3D=body.get_child(0)
				verify(not contact.disabled and body.collision_layer==1 and contact.shape is ConcavePolygonShape3D,"Moving original leaf contact disabled or replaced")
				verify(contact.global_transform.is_equal_approx(mesh.global_transform),"Moving contact departed exact retained mesh pose")
				verify((PhysicsServer3D.body_get_state(body.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)as Transform3D).is_equal_approx(body.global_transform),"Physics-server contact pose differs from moving retained leaf")
				var a:=mesh.get_aabb();var box:=BoxShape3D.new();box.size=a.size-Vector3.ONE*.0004;box.margin=0
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=mesh.global_transform*Transform3D(Basis.IDENTITY,a.get_center());q.exclude=omitted;q.margin=0
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):
					var obstacle:Node=hit.collider;var name:=str(obstacle.get_parent().name);var allowed:=false
					var tag:="TRIAGE_%02d"%int(d.binding.source_pod_number);var side:="left"if index==0 else "right"
					if name==tag+"_portal_"+side+"_receiver":
						# The only retained contact exemption is this exact source hinge receiver.
						var bounds:AABB=obstacle.get_parent().global_transform*obstacle.get_parent().get_aabb();var leaf_bounds:AABB=mesh.global_transform*a;var overlap:=bounds.intersection(leaf_bounds)
						allowed=not overlap.has_volume()or Vector2(overlap.get_center().x-hinge.global_position.x,overlap.get_center().z-hinge.global_position.z).length()<.20
					elif additions.is_ancestor_of(obstacle):
						for batch in plan.runtime_batches:
							if str(batch.name)!=name:continue
							allowed=true
							for member in batch.source_members:allowed=allowed and str(member).begins_with("G8M_Pod%02d_%sHingeBearing"%[int(d.binding.source_pod_number),"Left"if index==0 else "Right"])
							var aa:AABB=obstacle.get_parent().global_transform*obstacle.get_parent().get_aabb()
							for x in [aa.position.x,aa.end.x]:
								for z in [aa.position.z,aa.end.z]:allowed=allowed and Vector2(x-hinge.global_position.x,z-hinge.global_position.z).length()<.08
					verify(allowed,"Medical leaf motion clips non-joint geometry: %s %.3f %s"%[mesh.name,d.open_fraction,obstacle.get_path()])
	verify(d.open_fraction>.999 if d.desired_open else d.open_fraction<.001,"Medical privacy pair failed to reach requested endpoint")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");arch=ship.get_node("ShipSpace/Districts/D05MedicalWelcome_WIP/AuthoredMedicalWelcome")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	plan=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"));var old_meshes:Dictionary={};var old_ids:Dictionary={};var moving_names:Dictionary={}
	for row in plan.doors:
		for side in ["left","right"]:
			for name in row.members[side]:moving_names[str(name)]=true
	for mesh:MeshInstance3D in arch.find_children("*","MeshInstance3D",true,false):old_meshes[mesh.get_instance_id()]={"node":mesh,"pose":mesh.global_transform,"resource":mesh.mesh.get_instance_id(),"moving":moving_names.has(str(mesh.name))}
	for node:Node3D in ship.find_children("*","Node3D",true,false):
		if node.get_script()==load("res://scripts/service_door.gd"):old_ids[node.get_instance_id()]={"node":node,"id":str(node.persistent_id)}
	additions=load("res://scripts/group8/medical_privacy.gd").build(ship)
	for frame in range(8):await physics_frame
	var unique:Dictionary={}
	for row in old_ids.values():unique[row.id]=true
	for row in plan.doors:verify(not unique.has(str(row.persistent_id)),"New clinical driver ID conflicts");unique[str(row.persistent_id)]=true
	for row in old_meshes.values():verify(row.node.global_transform.is_equal_approx(row.pose)and row.node.mesh.get_instance_id()==row.resource,"Initial retained medical source changed")
	var omitted:Array[RID]=[actor.get_rid()]
	for body in additions.find_children("*","CollisionObject3D",true,false):omitted.append(body.get_rid())
	for row in plan.retained_contacts:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var direction:=Vector3(row.direction[0],row.direction[1],row.direction[2]);var ray:=PhysicsRayQueryParameters3D.create(at-direction*.015,at+direction*.02);ray.exclude=omitted
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		verify(not hit.is_empty()and str(hit.collider.get_path()).contains(str(row.expected_prefix).replace(".","_")),"Exact medical fitted wall/receiver support missing: %s / %s"%[row,hit])
	# One setup in the actual retained connected medical cross-street; all pod visits walk.
	actor.position=Vector3(-12.2,21.06,-458);actor.velocity=Vector3.ZERO
	for frame in range(10):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	for row in plan.doors:
		var d:Node3D=arch.get_node(str(row.name))
		await go(actor,Vector3(d.global_position.x,21,-458));await local_go(actor,d,-1.5,1.0)
		await press_door(actor,d,d.get_node("PublicPhysicalControl"));await check_motion(d,actor);verify(not d.desired_open,"Public physical control failed to close original leaves")
		for x in [-.6,.6]:
			var ray:=PhysicsRayQueryParameters3D.create(d.global_transform*Vector3(x,1.2,.8),d.global_transform*Vector3(x,1.2,-1.1));ray.exclude=[actor.get_rid()]
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			if hit.is_empty()or not d.is_ancestor_of(hit.collider):
				print("CLOSED RAY HOLD ",d.name," x=",x," hit=",hit)
				for m in d.bound_meshes:print("NATIVE LEAF POSE ",m.name," ",m.global_transform," body=",m.get_node("StaticContact").global_transform)
			verify(not hit.is_empty()and d.is_ancestor_of(hit.collider),"Closed original medical leaves lack real privacy collision")
		await press_door(actor,d,d.get_node("PublicPhysicalControl"));await check_motion(d,actor)
		await local_go(actor,d,0,1);await local_go(actor,d,0,-3.5);await local_go(actor,d,1.1,-3.5)
		await press_door(actor,d,d.get_node("PrivatePhysicalControl"));await check_motion(d,actor);verify(not d.desired_open,"Private physical control failed to close original leaves")
		await press_door(actor,d,d.get_node("PrivatePhysicalControl"));await check_motion(d,actor)
		await local_go(actor,d,0,-3.5);await local_go(actor,d,0,-.8);d.interact(actor);verify(d.obstructed and d.desired_open,"Occupied medical swing must refuse closing")
		for frame in range(15):await physics_frame
		verify(d.open_fraction>.999,"Occupied original pair moved")
		await local_go(actor,d,0,1);await go(actor,Vector3(d.global_position.x,21,-458))
	await go(actor,Vector3(-12.2,21,-458))
	for row in old_meshes.values():verify(row.node.global_transform.is_equal_approx(row.pose)and row.node.mesh.get_instance_id()==row.resource,"Medical source did not return to exact original pose/resource")
	for row in old_ids.values():verify(str(row.node.persistent_id)==row.id,"Original shared-door identity changed")
	verify(arch.find_children("*","MeshInstance3D",true,false).size()==old_meshes.size()and additions.get_meta("new_capacity")==0 and additions.get_meta("new_floor_owners")==0,"Medical programme/capacity/mesh ownership changed")
	var report:={"status":"PASS","checks":checks,"retained_meshes":old_meshes.size(),"original_door_ids":old_ids.size(),"pods":8,"exact_source_leaf_pairs":8,"physical_controls":16,"new_fitted_controller_instances":8,"new_shared_backends":0,"motion_frames":motion_frames,"walk_legs":legs,"walk_frames":frames,"walk_distance_m":distance,"maximum_step_m":max_step,"setup_placements":1,"subsequent_teleports":0,"source_native_sha256":plan.original_native_sha256,"source_runtime_sha256":plan.original_runtime_sha256,"model_sha256":plan.model_sha256,"precise_RMB_E_both_sides":true,"occupied_refusal":true,"clinical_pressure_species_cart_engineering_final_art_acceptance":false,"shared_static_guard_successor_adopted":false}
	FileAccess.open("res://data/architecture/group8/MEDICAL_PRIVACY_RUNTIME_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 MEDICAL PRIVACY PASS: ",JSON.stringify(report))
	main.queue_free();for frame in range(4):await process_frame
	quit(0)
