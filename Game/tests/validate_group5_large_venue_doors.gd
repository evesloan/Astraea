extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
var operations:Array=[]
var guards:=0
var completed:=0
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
	var result:Dictionary=await walk_to(actor,goal);result.scope=label;legs.append(result)
	record("foyer_leg_"+str(legs.size()),result.reached and result.floor_contact)
	return result.reached and result.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,side:String,want:bool)->bool:
	await aim(actor,door.get_node(side).to_global(Vector3(0,0,.055)))
	if actor.interaction_target!=door:
		var q:=PhysicsRayQueryParameters3D.create(actor.camera.global_position,actor.camera.global_position-actor.camera.global_basis.z*2.5)
		q.exclude=[actor.get_rid()]
		var hit:=actor.get_world_3d().direct_space_state.intersect_ray(q)
		print("GROUP5_FOYER_TARGET_DIAGNOSTIC ",JSON.stringify({"door":str(door.persistent_id),"side":side,"actor":str(actor.global_position),"camera":str(actor.camera.global_position),"control":str(door.get_node(side).global_position),"aim":str(door.get_node(side).to_global(Vector3(0,0,.055))),"hit":str(hit.collider.get_parent().get_path()) if not hit.is_empty() else "missing","hit_position":str(hit.position) if not hit.is_empty() else "missing","current_target":str(actor.interaction_target)}))
	record("normal_RMB_"+str(operations.size()),actor.interaction_target==door)
	await key_e()
	for i in range(85):await physics_frame
	var ok:bool=door.fraction==(1.0 if want else 0.0) and door.desired_open==want
	operations.append({"physical_id":str(door.persistent_id),"side":side,"open":want,"fraction":door.fraction,"normal_input":true,"passed":ok})
	record("normal_E_"+str(operations.size()),ok);return ok
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var builder=load("res://scripts/group5_large_venue_doors.gd")
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_DOORS.json"))
	var startup:bool=ship.get_meta("group5_large_venue_doors_attached",false)
	var doors:Array=builder.build(ship)
	record("five_source_foyer_doors",doors.size()==5)
	record("repeat_build_reuses_existing_doors",builder.build(ship)==doors)
	for row in definition.doors:
		var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,str(row.programme_key))
		actor.global_position=vec(row.public_approach_world_xyz);actor.velocity=Vector3.ZERO
		actor.set_controls_enabled(true);manager.prepare_position(actor.global_position)
		for i in range(15):await physics_frame
		record(str(row.programme_key)+" supported_original_main_fixture",actor.is_on_floor())
		var door:Node3D=owner.get_node(str(row.door_name))
		record(str(row.programme_key)+" default_closed",not door.desired_open and door.fraction==0)
		record(str(row.programme_key)+" exact_source_models",FileAccess.get_sha256(str(row.source_model))==str(row.source_sha256) and FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		if not await leg(actor,owner.position+vec(row.safe_foyer_public_local_xyz),"original main receiving floor into retained foyer before closed door"):break
		if not await leg(actor,owner.position+vec(row.public_stance_local_xyz),"continuous retained foyer to public original wall-end control"):break
		if not await operate(actor,door,"PublicControl",true):break
		if not await leg(actor,owner.position+vec(row.safe_foyer_public_local_xyz),"public control back to supported original foyer centre"):break
		if not await leg(actor,owner.position+vec(row.inside_local_xyz),"through actual opened wide threshold into original destination"):break
		if not await leg(actor,owner.position+vec(row.interior_stance_local_xyz),"destination-side original wall control outside moving pocket"):break
		# Explicit actual-character guard fixture. The original actor stays at its
		# supported control stance and attempts ordinary RMB/E close.
		var witness:=CharacterBody3D.new();witness.name="Group5FoyerGuardFixture"
		var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8
		var collision:=CollisionShape3D.new();collision.shape=shape;collision.position=Vector3(0,.9,0)
		witness.add_child(collision);ship.get_node("ShipSpace/PersistentActors").add_child(witness)
		witness.global_position=door.to_global(Vector3(0,.02,0))
		for i in range(3):await physics_frame
		await aim(actor,door.get_node("InteriorControl").to_global(Vector3(0,0,.055)))
		record(str(row.programme_key)+" normal_guard_target",actor.interaction_target==door)
		await key_e()
		for i in range(5):await physics_frame
		record(str(row.programme_key)+" actual_character_holds_close",door.desired_open and door.fraction==1 and door.obstructed)
		guards+=1;witness.queue_free()
		for i in range(3):await physics_frame
		if not await operate(actor,door,"InteriorControl",false):break
		var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
		var query:=PhysicsRayQueryParameters3D.create(door.to_global(Vector3(.3,1.35,.4)),door.to_global(Vector3(.3,1.35,-.4)));query.exclude=[actor.get_rid()]
		var hit:=state.intersect_ray(query)
		record(str(row.programme_key)+" actual_closed_moving_panel_contact",not hit.is_empty() and hit.collider is AnimatableBody3D and hit.collider.get_parent()==door)
		if not await operate(actor,door,"InteriorControl",true):break
		if not await leg(actor,owner.position+vec(row.inside_local_xyz),"destination control back to original supported interior foyer"):break
		if not await leg(actor,owner.position+vec(row.safe_foyer_public_local_xyz),"continuous opened-door egress to retained public foyer"):break
		if not await leg(actor,owner.position+vec(row.public_stance_local_xyz),"return to public control for ordinary closed default"):break
		if not await operate(actor,door,"PublicControl",false):break
		if not await leg(actor,owner.position+vec(row.safe_foyer_public_local_xyz),"closed door public stance back to retained receiving centre"):break
		if not await leg(actor,vec(row.public_approach_world_xyz),"original connected receiving floor back to shared main spine"):break
		record(str(row.programme_key)+" ends_closed",door.fraction==0 and not door.desired_open)
		completed+=1
		print("GROUP5_LARGE_FOYER_WALK ",row.programme_key," legs ",legs.size()," errors ",errors)
		if not errors.is_empty():break
	physical_key(false)
	record("all_five_normal_routes",completed==5 and legs.size()==50 and operations.size()==20 and guards==5)
	# Cache state is a separate explicit fixture after all walking routes.
	var cached:=0
	for row in definition.doors:
		if completed!=5:break
		var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,str(row.programme_key))
		var door:Node3D=owner.get_node(str(row.door_name));var id:int=door.get_instance_id()
		actor.global_position=owner.position+vec(row.public_stance_local_xyz);manager.prepare_position(actor.global_position)
		for i in range(3):await physics_frame
		door.interact(actor)
		for i in range(85):await physics_frame
		record(str(row.programme_key)+" cache_fixture_open",door.fraction==1 and door.desired_open)
		actor.global_position=Vector3(1000,1000,1000);manager.refresh(9.0)
		record(str(row.programme_key)+" actual_cached_detach",not owner.is_inside_tree())
		manager.prepare_position(owner.position+vec(row.public_stance_local_xyz))
		for i in range(3):await physics_frame
		record(str(row.programme_key)+" same_open_door_return",owner.is_inside_tree() and door.get_instance_id()==id and door.desired_open and door.fraction==1)
		cached+=1
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"completed_venues":completed,"legs":legs,"normal_RMB_E_operations":operations,"actual_character_guard_attempts":guards,"cached_open_returns":cached,"builder_attached_during_main_startup":startup,"source_opening_widths_m":[8,8,8,10,10],"teleports_inside_walking_routes":0,"scope":"Actual main/five original receiving floors,original controller and normal RMB/E;explicit between-venue initial fixtures;50 continuous public-foyer/interior/return legs,20 ordinary operations,five actual-character guard fixtures and separate cached-state fixtures. Not shipwide journeys,staff-riser joins,role/pressure,save,cart/species,engineering or Game/CRT/hardware/final-art acceptance.","whole_group_accepted":false}
	FileAccess.open("res://artifacts/group5_large_venue_doors_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_LARGE_VENUE_DOORS ",JSON.stringify({"status":out.status,"checks":checks.size(),"completed":completed,"legs":legs.size(),"operations":operations.size(),"guards":guards,"cached":cached,"errors":errors}))
	quit(0 if errors.is_empty() else 1)
