extends "res://tests/validate_group5_large_venue_doors.gd"
var motion_samples:=0
func motion_contacts(ship:Node3D,doors:Array)->void:
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for door:Node3D in doors:
		for body:AnimatableBody3D in door.panels:
			for child in body.get_children():
				if not child is CollisionShape3D:continue
				var query:=PhysicsShapeQueryParameters3D.new();var shape:BoxShape3D=child.shape.duplicate();shape.size-=Vector3.ONE*.001;shape.margin=0;query.shape=shape;query.transform=child.global_transform;query.exclude=[body.get_rid()];query.margin=0
				var bad:Array=[]
				for hit in space.intersect_shape(query,64):
					if hit.collider is StaticBody3D or hit.collider is AnimatableBody3D:bad.append(str(hit.collider.get_path()))
				record("actual_living_motion_"+str(motion_samples),bad.is_empty());motion_samples+=1
				if not bad.is_empty():print("LIVING_MOTION_CONTACT ",str(door.name),body.name,door.fraction,bad)
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var owner:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false);var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LIVING_GIFTS_DOORS.json"))
	var originals:Dictionary={};var installed:Node3D=owner.get_node_or_null("Group5LivingDoors")
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if installed==null or not installed.is_ancestor_of(mesh):originals[mesh.get_instance_id()]=[mesh.mesh.get_instance_id(),mesh.global_transform]
	var builder=load("res://scripts/group5_living_gifts_doors.gd");var startup:bool=ship.get_meta("group5_living_doors_attached",false)
	var default_doors:Array=builder.build(ship);record("default_skips_service_interface_candidate",default_doors.size()==1)
	# Explicit scoped interface fixture,not default cross-group adoption.
	var doors:Array=builder.build(ship,true);record("two_existing_opening_candidates",doors.size()==2);record("repeat_source_build_same_nodes",builder.build(ship,true)==doors)
	var pub:Node3D=doors[0];var service:Node3D=doors[1];record("shared_interface_remains_unaccepted",not spec.source_shared_interfaces_accepted and service.get_meta("cross_group_adoption_required"))
	var kept:=0
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if originals.has(mesh.get_instance_id()):
			var before:Array=originals[mesh.get_instance_id()];record("preserved_original_living_"+str(mesh.get_instance_id()),mesh.mesh.get_instance_id()==before[0] and mesh.global_transform.is_equal_approx(before[1]));kept+=1
	record("all_original_living_meshes_preserved",kept==originals.size())
	actor.set_controls_enabled(true);actor.global_position=Vector3(52,52.53,216);actor.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	var ray:=PhysicsRayQueryParameters3D.create(Vector3(13,45.65,218),Vector3(46.88,56.45,236));record("protected_aquatic_upper_frame_sightline",space.intersect_ray(ray).is_empty())
	var optical:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for at in [Vector3(44.5,52.53,236),Vector3(50.8,52.53,235.7),Vector3(50.5,52.53,241)]:
		actor.global_position=at
		for i in range(3):await physics_frame
		budget.refresh();var active:=0;var reaches:=0
		for light:Light3D in budget.sources:
			if not is_instance_valid(light) or not light.is_inside_tree():continue
			if light.visible and light.shadow_enabled:active+=1
			if owner.is_ancestor_of(light) and light.visible and light.shadow_enabled and light.global_position.distance_to(at+Vector3.UP*1.5)<light.omni_range and budget._clear_sample(light.global_position,at+Vector3.UP*1.5):reaches+=1
		record("affected_living_optics_"+str(at),reaches>0 and active<=8 and budget.shadow_source_budget==8);optical.append({"at":str(at),"active_original_sources_reaching_viewer":reaches,"active_shadow_sources":active})
	# Source-motion fixtures precede the continuous original-controller walk.
	actor.global_position=Vector3(52,52.53,216);actor.velocity=Vector3.ZERO
	for i in range(15):await physics_frame
	for want in [true,false]:
		for door:Node3D in doors:door.interact(actor)
		for frame in range(85):
			await physics_frame
			if frame%5==0:motion_contacts(ship,doors)
		record("source_motion_end_"+str(want),pub.fraction==(1.0 if want else 0.0) and service.fraction==(1.0 if want else 0.0))
	var ok:=errors.is_empty()
	for at in [Vector3(52,52.53,225),Vector3(46.7,52.53,227.5),Vector3(44.5,52.53,232),Vector3(44.5,52.53,236),vec(spec.doors[0].public_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous original aquatic-facing public approach to retained nursery threshold"):ok=false
	if ok and not await operate(actor,pub,"PublicControl",true):ok=false
	for at in [Vector3(44.5,52.53,236),Vector3(48.2,52.53,236),Vector3(50.8,52.53,235.7),vec(spec.doors[0].interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous opened public threshold and original nursery turn"):ok=false
	if ok:await guarded_attempt(ship,actor,pub)
	if ok and not await operate(actor,pub,"InteriorControl",false):ok=false
	if ok and not await operate(actor,pub,"InteriorControl",true):ok=false
	for at in [Vector3(50.8,52.53,235.7),Vector3(52.4,52.53,237.8),vec(spec.doors[1].interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous retained service lane outside the original stock screen"):ok=false
	if ok and not await operate(actor,service,"InteriorControl",true):ok=false
	if ok:await guarded_attempt(ship,actor,service)
	if ok and not await operate(actor,service,"InteriorControl",false):ok=false
	if ok and not await operate(actor,service,"InteriorControl",true):ok=false
	for at in [Vector3(52.4,52.53,241),Vector3(52.4,52.53,244.5),Vector3(51.5,52.53,247),Vector3(52.4,52.53,244.5),vec(spec.doors[1].public_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous original service aperture and existing exterior column/turn receiving floor"):ok=false
	if ok and not await operate(actor,service,"PublicControl",false):ok=false
	if ok and not await operate(actor,service,"PublicControl",true):ok=false
	for at in [Vector3(52.4,52.53,244.5),Vector3(52.4,52.53,241),vec(spec.doors[1].interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous actual receiving floor back through service candidate"):ok=false
	if ok and not await operate(actor,service,"InteriorControl",false):ok=false
	for at in [Vector3(52.4,52.53,237.8),Vector3(50.5,52.53,238),Vector3(50.5,52.53,241),Vector3(48.9,52.53,241),Vector3(50.5,52.53,241),Vector3(50.5,52.53,238),Vector3(50.8,52.53,235.7),vec(spec.doors[0].interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous original stock-screen fore return and wrapping-workbench approach"):ok=false
	if ok and not await operate(actor,pub,"InteriorControl",false):ok=false
	if ok and not await operate(actor,pub,"InteriorControl",true):ok=false
	for at in [Vector3(50.8,52.53,235.7),Vector3(48.2,52.53,236),Vector3(44.5,52.53,236),vec(spec.doors[0].public_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous original public threshold egress"):ok=false
	if ok and not await operate(actor,pub,"PublicControl",false):ok=false
	for at in [Vector3(44.5,52.53,236),Vector3(44.5,52.53,232),Vector3(46.7,52.53,227.5),Vector3(52,52.53,225),Vector3(52,52.53,216)]:
		if not ok:break
		if not await leg(actor,at,"continuous original protected public return"):ok=false
	physical_key(false);record("full_living_normal_route",ok and legs.size()==37 and operations.size()==12 and guards==2)
	record("both_new_doors_end_closed",pub.fraction==0 and service.fraction==0 and not pub.desired_open and not service.desired_open)
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"startup_public_attached":startup,"service_is_explicit_test_interface_candidate":true,"cross_group_interface_accepted":false,"original_meshes_preserved":kept,"actual_moving_body_pose_samples":motion_samples,"affected_optical_samples":optical,"continuous_original_controller_legs":legs,"normal_RMB_E_operations":operations,"occupied_actual_character_guards":guards,"teleports_inside_walking_routes":0,"scope":"Actual original main,four new public/mounted controls,two physical doors,original flora/stock/wrapping/column/floor preserved;explicit aft service candidate only,Group6 adoption held;no original room/capacity/registry/hull edits,no cart/species,save/role/pressure,engineering,Game/CRT/hardware/final-art or whole-group acceptance"}
	FileAccess.open("res://artifacts/group5_living_gifts_doors.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print("GROUP5_LIVING_GIFTS_DOORS ",JSON.stringify({"status":out.status,"checks":checks.size(),"legs":legs.size(),"operations":operations.size(),"guards":guards,"poses":motion_samples,"errors":errors}));quit(0 if errors.is_empty() else 1)
func guarded_attempt(ship:Node3D,actor:CharacterBody3D,door:Node3D)->void:
	var witness:=CharacterBody3D.new();var col:=CollisionShape3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;col.shape=shape;col.position=Vector3.UP*.9;witness.add_child(col);ship.get_node("ShipSpace/PersistentActors").add_child(witness);witness.global_position=door.to_global(Vector3(0,.02,-.18))
	for i in range(3):await physics_frame
	await aim(actor,door.get_node("InteriorControl").to_global(Vector3(0,0,.055)));record("living_guard_target_"+str(guards),actor.interaction_target==door);await key_e()
	for i in range(5):await physics_frame
	record("living_actual_character_guard_"+str(guards),door.desired_open and door.fraction==1 and door.obstructed);guards+=1;witness.queue_free()
	for i in range(3):await physics_frame
