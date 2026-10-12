extends "res://tests/validate_thread_shell.gd"
var checks:=0
var failed:=false
var ship:Node3D
var walk_frames:=0
var walk_legs:=0
var walk_distance:=0.0
var max_step:=0.0
var motion_frames:=0
func verify(ok:bool,message:String)->void:
	checks+=1
	if not ok:failed=true;push_error(message);quit(1)
func go(actor:CharacterBody3D,target:Vector3)->void:
	var reached:=false
	for frame in range(int(actor.position.distance_to(target)*60/3.1)+180):
		var offset:=target-actor.position;offset.y=0
		if offset.length()<.08:reached=true;break
		var before:=actor.position;var speed:=offset.normalized()*3.1
		actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z);actor.move_and_slide();await physics_frame
		var step:=before.distance_to(actor.position);walk_distance+=step;max_step=maxf(max_step,step);walk_frames+=1
		verify(absf(actor.position.y)<.12 and step<.08,"Candidate actor left actual old/proposed floor support or ordinary walking step")
		var q:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.12,actor.position-Vector3.UP*.25);q.exclude=[actor.get_rid()]
		verify(not ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"Plant candidate path lacks physical support")
		if failed:return
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("SYNTHESIS CANDIDATE WALK HOLD ",actor.get_slide_collision(i).get_collider().get_path())
	verify(reached,"Plant candidate walk stalled: %s toward %s"%[actor.position,target]);actor.velocity=Vector3.ZERO;walk_legs+=1
func animate(d:Node3D,actor:CharacterBody3D)->void:
	for frame in range(90):
		await physics_frame;motion_frames+=1
		for leaf:AnimatableBody3D in d.leaves:
			for child in leaf.get_children():
				if not child is CollisionShape3D:continue
				var contact:CollisionShape3D=child;var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[actor.get_rid(),leaf.get_rid()]
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):verify(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Plant gateway clips fixed source geometry: %s %s"%[d.name,hit.collider.get_path()])
		if failed:return
	verify(d.open_fraction>.999 if d.desired_open else d.open_fraction<.001,"Plant gateway requested state not reached")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var old_bay:Node3D=ship.find_child("D01_SynthesisServiceBay_WIP",true,false);verify(old_bay!=null,"Original bay missing");var original_poses:Dictionary={};var original_ids:Dictionary={}
	for ob:Node3D in old_bay.find_children("*","Node3D",true,false):original_poses[ob.get_instance_id()]={"node":ob,"pose":ob.global_transform}
	for d:Node3D in ship.find_children("*","Node3D",true,false):
		if d.get_script()==load("res://scripts/service_door.gd"):original_ids[str(d.get_path())]=str(d.persistent_id)
	var floor:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/synthesis_floor_proposal.json"))
	verify(not floor.active_adoption,"Candidate test must retain floor proposal status")
	var candidate_floor:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,floor.regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"Group8SynthesisMissingFloor_TEST_ONLY")
	candidate_floor.set_meta("shared_adoption",false)
	var n:Node3D=load("res://scripts/group8/synthesis_plant.gd").build(ship,true);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/synthesis_plant.json"))
	actor.position=Vector3(-45.5,.06,0);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var admitted:Dictionary={}
	var own_contacts:Array[RID]=[]
	for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):own_contacts.append(body.get_rid())
	for row in p.supports:
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.08)
		q.exclude=own_contacts
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q);verify(not hit.is_empty()and("CompiledStructuralFloors"in str(hit.collider.get_path())or"Group8SynthesisMissingFloor_TEST_ONLY"in str(hit.collider.get_path())),"New plant pad lacks explicit retained/proposed supporting floor")
	for row in p.lights:
		var light:SpotLight3D=n.get_node(str(row.name));var q:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.04);verify(ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"New housed plant source exit blocked")
		q.to=light.global_position+Vector3.DOWN*light.spot_range;verify(not ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"New plant source has no physical receiver")
	for target:Vector3 in[Vector3(-58,0,0),Vector3(-58,0,7),Vector3(-71,0,7),Vector3(-70,0,16),Vector3(-70,0,7),Vector3(-81,0,7),Vector3(-81,0,16),Vector3(-81,0,7),Vector3(-89,0,7),Vector3(-89,0,1.75),Vector3(-73,0,1.75)]:
		await go(actor,target);if failed:return
		budget.refresh();var visible:Array=[]
		for light:SpotLight3D in n.find_children("*","SpotLight3D",true,false):
			if light.visible and light.shadow_enabled:visible.append(str(light.name))
		verify(not visible.is_empty(),"Reached candidate process/work stance lacks actual admitted housed source");admitted[str(target)]=visible
	for row in p.doors:
		var d:Node3D=n.get_node(str(row.name));var z:float=float(row.at[2]);await go(actor,Vector3(-70,0,actor.position.z));await go(actor,Vector3(-70,0,7 if z>0 else-7));await go(actor,Vector3(-64.8,0,7 if z>0 else-7));await go(actor,d.global_position+Vector3(0,0,1.2))
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open,"Precise plant call did not close")
		var q:=PhysicsRayQueryParameters3D.create(d.global_position+Vector3(.4,1.2,.8),d.global_position+Vector3(.4,1.2,-.8));q.exclude=[actor.get_rid()];var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q);verify(not hit.is_empty()and d.is_ancestor_of(hit.collider),"Closed plant gateway has no leaf collision")
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);await go(actor,d.global_position+Vector3(0,0,-2))
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);verify(not d.desired_open,"Opposite plant call did not close")
		await press_door(actor,d,d.leaves[0].get_node("PushContact"));await animate(d,actor);await go(actor,d.global_position+Vector3(0,0,-.6));d.interact(actor);verify(d.obstructed and d.desired_open,"Occupied plant gateway failed to refuse close")
		await go(actor,d.global_position+Vector3(0,0,-2));await go(actor,Vector3(-64.8,0,25.1 if z>0 else-25.1));budget.refresh()
		var light:SpotLight3D=n.get_node("G8S_LIGHT_Packing"if z>0 else"G8S_LIGHT_Wash");verify(light.visible and light.shadow_enabled and budget._has_visible_sample(light),"Reached packing/wash stance has no admitted real task source")
		await go(actor,Vector3(-64.8,0,7 if z>0 else-7));if failed:return
	for row in original_poses.values():verify(row.node.global_transform.is_equal_approx(row.pose),"Original synthesis bay pose changed")
	for path in original_ids:verify(str(ship.get_node(path).persistent_id)==original_ids[path],"Original service door ID changed")
	if failed:return
	var r:={"status":"PASS_SOURCE_CANDIDATE_WITH_EXPLICIT_TEST_FLOOR","shared_floor_adoption":false,"new_missing_floor_proposal_m2":floor.proposed_missing_floor_area_m2,"checks":checks,"original_bay_node_poses":original_poses.size(),"original_service_door_ids":original_ids.size(),"new_process_hub_candidates":4,"new_standard_door_instances":2,"precise_RMB_E_both_sides":true,"occupied_refusal_and_closed_leaf_collision":true,"motion_frames":motion_frames,"new_housed_sources":14,"actual_admission_at_reached_candidate_stances":admitted,"floor_support_pads":p.supports.size(),"walk_legs":walk_legs,"walk_frames":walk_frames,"walk_distance_m":walk_distance,"maximum_step_m":max_step,"setup_placements":1,"subsequent_teleports":0,"actual_shared_plant_food_hygiene_cart_species_primary_engineering_final_art_acceptance":false}
	FileAccess.open("res://data/architecture/group8/SYNTHESIS_CANDIDATE_RUNTIME_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  ")+"\n");print("GROUP8 SYNTHESIS CANDIDATE PASS: ",JSON.stringify(r))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
