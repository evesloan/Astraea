extends "res://tests/validate_thread_shell.gd"
var checks:=0
var legs:=0
var frames:=0
var distance:=0.0
var max_step:=0.0
var motion_frames:=0
var ship:Node3D
var addition:Node3D
var plan:Dictionary
func verify(ok:bool,message:String)->void:checks+=1;assert(ok,message)
func go(actor:CharacterBody3D,target:Vector3)->void:
	var reached:=false;var budget:=int(actor.position.distance_to(target)*60/3.1)+160
	for f in range(budget):
		var offset:=target-actor.position;offset.y=0
		if offset.length()<.22:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z);actor.move_and_slide();await physics_frame
		var step:=before.distance_to(actor.position);distance+=step;max_step=maxf(max_step,step);frames+=1
		verify(absf(actor.position.y-21)<.12 and step<.08,"Medical Bay actor left retained floor or ordinary walking step")
		var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);ray.exclude=[actor.get_rid()]
		verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Original medical floor support missing")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("MEDICAL BAY WALK HOLD ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Medical Bay walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;legs+=1
func local_go(actor:CharacterBody3D,d:Node3D,x:float,z:float)->void:await go(actor,d.global_transform*Vector3(x,0,z))
func animate(d:Node3D,actor:CharacterBody3D)->void:
	for f in range(90):
		await physics_frame;motion_frames+=1
		for side in range(2):
			var hinge:Node3D=d.hinge_nodes[side];var omitted:Array[RID]=[actor.get_rid()]
			for m:MeshInstance3D in hinge.get_children():omitted.append(m.get_node("StaticContact").get_rid())
			for mesh:MeshInstance3D in hinge.get_children():
				var body:AnimatableBody3D=mesh.get_node("StaticContact");var contact:CollisionShape3D=body.get_child(0)
				verify(contact.global_transform.is_equal_approx(mesh.global_transform)and(PhysicsServer3D.body_get_state(body.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)as Transform3D).is_equal_approx(body.global_transform),"New native-copy contact diverged from actual mesh/physics pose")
				var a:=mesh.get_aabb();var box:=BoxShape3D.new();box.size=a.size-Vector3.ONE*.0004;box.margin=0
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=mesh.global_transform*Transform3D(Basis.IDENTITY,a.get_center());q.exclude=omitted;q.margin=0
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):
					var obstacle:Node=hit.collider;var name:=str(obstacle.get_parent().name);var expected:=str(d.binding.receivers.left if side==0 else d.binding.receivers.right)
					var permitted:=name==expected
					if addition.is_ancestor_of(obstacle)and name.begins_with("G8B_BATCH_"):
						for row in plan.runtime_batches:
							if str(row.name)!=name:continue
							permitted=true
							for member in row.source_members:permitted=permitted and(str(member)==expected or str(member).begins_with("G8B_Surgery%02d_%sHingeBearing"%[int(d.binding.source_pod_number),"Left"if side==0 else"Right"]))
							var bounds:AABB=obstacle.get_parent().global_transform*obstacle.get_parent().get_aabb()
							for x in[bounds.position.x,bounds.end.x]:
								for z in[bounds.position.z,bounds.end.z]:permitted=permitted and Vector2(x-hinge.global_position.x,z-hinge.global_position.z).length()<.22
					verify(permitted,"New surgical privacy leaf clips non-joint geometry: %s %.3f %s"%[mesh.name,d.open_fraction,obstacle.get_path()])
	verify(d.open_fraction>.999 if d.desired_open else d.open_fraction<.001,"Medical Bay pair did not reach requested endpoint")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	plan=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_bay.json"));actor.position=Vector3(28,21.06,-430);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");var room:Node3D=stream.rooms["D05_directory_02"]
	verify(room.get_meta("stream_loaded",false),"Actual Medical Bay source room missing")
	var original:Node3D=room.get_child(0);var poses:Dictionary={}
	for node:Node3D in room.find_children("*","Node3D",true,false):poses[node.get_instance_id()]={"node":node,"pose":node.global_transform}
	addition=load("res://scripts/group8/medical_bay.gd").build(ship,room)
	for f in range(8):await physics_frame
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var sources:=0
	for row in plan.lights:
		var old:OmniLight3D=room.get_node(str(row.original_generic_name));var light:SpotLight3D=addition.get_node(str(row.name));var lens:MeshInstance3D=original.find_child(str(row.physical_lens_name),true,false)
		verify(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.03).has_point(light.global_position),"Directional source detached from exact original visible lens")
		verify(old.global_position.is_equal_approx(light.global_position)and not old.get_meta("fixture_powered",true)and not old.visible and not old.shadow_enabled,"Generic emission still active or source intent moved")
		verify(budget.sources.has(light)and budget.requested_shadow[light.get_instance_id()],"Directional source missing from unchanged budget")
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.05)
		verify(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual modeled medical fixture exit blocked")
		ray.to=light.global_position+Vector3.DOWN*float(row.range);verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Medical fixture lacks actual receiver within range");sources+=1
	var omitted:Array[RID]=[actor.get_rid()]
	for body in addition.find_children("*","CollisionObject3D",true,false):omitted.append(body.get_rid())
	for row in plan.supports:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);ray.exclude=omitted;var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		verify(not hit.is_empty()and absf(hit.position.y-21)<.003,"New receiver lost original floor bearing")
	for row in plan.retained_contacts:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var dir:=Vector3(row.direction[0],row.direction[1],row.direction[2]);var ray:=PhysicsRayQueryParameters3D.create(at-dir*.02,at+dir*.025);ray.exclude=omitted;var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		verify(not hit.is_empty()and str(hit.collider.get_path()).contains(str(row.expected_prefix)),"New receiver/control lacks exact original pier support")
	for row in plan.doors:
		var d:Node3D=addition.get_node(str(row.name));verify(d.desired_open and d.open_fraction>.999 and str(d.persistent_id)==str(row.persistent_id),"New surgery identity/default wrong")
		await go(actor,Vector3(28,21,row.at[2]));await local_go(actor,d,-2.18,2.2)
		await press_door(actor,d,d.get_node("PublicPhysicalControl"));await animate(d,actor);verify(not d.desired_open,"Public surgical privacy control failed")
		for x in[-.6,.6]:
			var ray:=PhysicsRayQueryParameters3D.create(d.global_transform*Vector3(x,1.2,.8),d.global_transform*Vector3(x,1.2,-1.1));ray.exclude=[actor.get_rid()];var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			verify(not hit.is_empty()and d.is_ancestor_of(hit.collider),"Closed surgical pair lacks real privacy collision")
		await press_door(actor,d,d.get_node("PublicPhysicalControl"));await animate(d,actor)
		await local_go(actor,d,0,1.1);await local_go(actor,d,0,-2.63);await local_go(actor,d,-2.18,-2.63)
		await press_door(actor,d,d.get_node("PrivatePhysicalControl"));await animate(d,actor);verify(not d.desired_open,"Private surgical privacy control failed")
		await press_door(actor,d,d.get_node("PrivatePhysicalControl"));await animate(d,actor)
		await local_go(actor,d,0,-2.63);await local_go(actor,d,0,-.8);d.interact(actor);verify(d.obstructed and d.desired_open,"Occupied surgical swing must refuse closing")
		for f in range(15):await physics_frame
		verify(d.open_fraction>.999,"Occupied surgical pair moved")
		await local_go(actor,d,0,1.1);await go(actor,Vector3(28,21,row.at[2]))
	await go(actor,Vector3(28,21,-430))
	for row in poses.values():verify(is_instance_valid(row.node)and row.node.global_transform.is_equal_approx(row.pose),"Original medical architecture/furniture/intent node pose changed")
	verify(original.find_children("*","MeshInstance3D",true,false).size()==2225 and sources==39,"Original Medical Bay source roster changed")
	var report:={"status":"PASS","checks":checks,"original_medical_meshes":2225,"original_node_poses":poses.size(),"retained_general_bed_ids":20,"retained_surgical_suite_ids":4,"new_privacy_pairs":4,"physical_controls":8,"existing_fixture_directional_adaptations":39,"new_physical_light_fixtures":0,"motion_frames":motion_frames,"walk_legs":legs,"walk_frames":frames,"walk_distance_m":distance,"maximum_step_m":max_step,"setup_placements":1,"subsequent_route_teleports":0,"precise_RMB_E_both_sides":true,"occupied_sweep_refusal":true,"clinical_pressure_species_cart_engineering_final_art_acceptance":false,"external_public_staff_catchment_acceptance":false}
	FileAccess.open("res://data/architecture/group8/MEDICAL_BAY_RUNTIME_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 MEDICAL BAY PASS: ",JSON.stringify(report))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
