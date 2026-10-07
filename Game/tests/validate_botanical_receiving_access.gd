extends "res://tests/medical_test_scene.gd"
# Reuse existing input/ray/support helpers; only this bounded D06 exercise is new.
const BOTANICAL_CONTRACT := "res://tests/fixtures/botanical_moss_receiving_acceptance011.json"
const BOTANICAL_CONTRACT_SHA := "81c9f0364f49ec765dddcacf1e9eade05892d6f1be8f5777dfc68d3d743fe714"
var walked_frames: int=0
var travelled_m: float=0.0
var guard_rays: int=0
var axial_clearance_queries: int=0
var loaded_proof: Dictionary={}
var completed_bumps: Array=[]
var crossed_seams: Dictionary={}
var track_motion: bool=false
var guard_probe_exclusions: Array[RID]=[]
var footprint_support_queries: int=0
var moss_portal_crossings: int=0
var moss_route_completed: bool=false

func _initialize() -> void:
	test_name="botanical_receiving_access"
	call_deferred("run")

func vec(value: Vector3) -> Array: return [value.x,value.y,value.z]

func write_receipt(status: String,detail: String="") -> void:
	if receipt_path.is_empty(): return
	var out: Dictionary={"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"support_samples":support_samples,"auxiliary_underlying_floor_footprint_queries":footprint_support_queries,"ordinary_walk_frames":walked_frames,"walked_metres":travelled_m,"guard_rays":guard_rays,"axial_clearance_queries":axial_clearance_queries,"completed_actual_player_bumps":completed_bumps,"seams_crossed_by_player":crossed_seams,"initial_verified_arrivals":1 if track_motion else 0,"later_teleports":0,"fixture_sha256":FileAccess.get_sha256(BOTANICAL_CONTRACT),"metrics":metrics,"moss_portal_crossings":moss_portal_crossings,"moss_route_completed":moss_route_completed,"scope":"Bounded actual unchanged-player Botanical receiving and Moss interior/return; cart/species, visuals and full ship acceptance remain separate."}
	var file:=FileAccess.open(receipt_path,FileAccess.WRITE)
	if file!=null: file.store_string(JSON.stringify(out,"  ")+"\n")

func advance(count: int,check_d06_support: bool=false) -> bool:
	for frame in range(count):
		var before: Vector3=actor.global_position if is_instance_valid(actor) else Vector3.ZERO
		if not await super.advance(1,false): return false
		if not track_motion: continue
		if not require(actor.global_position.distance_to(before)<.25,"Unexpected player displacement; no post-start teleport/recovery allowed"): return false
		if (before.x>-8 and actor.global_position.x<=-8) or (before.x<-8 and actor.global_position.x>=-8): moss_portal_crossings+=1
		var was_x: float=before.x
		var now_x: float=actor.global_position.x
		if (was_x>-4 and now_x<=-4) or (was_x<-4 and now_x>=-4): crossed_seams["port"]=int(crossed_seams.get("port",0))+1
		if (was_x<4 and now_x>=4) or (was_x>4 and now_x<=4): crossed_seams["starboard"]=int(crossed_seams.get("starboard",0))+1
		if check_d06_support:
			if not require(absf(actor.global_position.y-27)<.08,"Original player left D06 floor datum"): return false
			if not support_at(Vector3(actor.global_position.x,27,actor.global_position.z)): return false
			# At deliberate barrier contact, a low plinth can lie over a footprint probe.
			# This auxiliary floor-owner query excludes only the guard meshes; actual
			# player movement/collisions remain completely unchanged, as in pool probes.
			for offset in [Vector2(.28,0),Vector2(-.28,0),Vector2(0,.28),Vector2(0,-.28)]:
				var point:=Vector3(actor.global_position.x+offset.x,27,actor.global_position.z+offset.y)
				var excluded: Array[RID]=exclusions();excluded.append_array(guard_probe_exclusions)
				var hit: Dictionary=ray(point+Vector3.UP*.14,point-Vector3.UP*.16,excluded)
				if not require(not hit.is_empty() and floors.is_ancestor_of(hit.collider) and absf(float(hit.position.y)-27)<.015 and float(hit.normal.y)>.95,"Missing underlying compiler footprint support"): return false
				footprint_support_queries+=1
	return true

func walk(point: Vector2) -> bool:
	release_inputs()
	var start:=Vector2(actor.global_position.x,actor.global_position.z)
	var allowance: int=ceili(start.distance_to(point)/3.1*60.0)+240
	for frame in range(allowance):
		var delta: Vector2=point-Vector2(actor.global_position.x,actor.global_position.z)
		var speed: float=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.16 and speed<.08:
			key(KEY_W,false);return support_at(Vector3(point.x,27,point.y))
		if delta.length()>.025: actor.rotation.y=atan2(-delta.x,-delta.y)
		actor.set("pitch",0.0);actor.camera.rotation.x=0.0
		key(KEY_W,delta.length()>maxf(.11,speed*speed/32.0+.035))
		var previous: Vector3=actor.global_position
		if not await advance(1,true): return false
		travelled_m+=Vector2(actor.global_position.x-previous.x,actor.global_position.z-previous.z).length()
		walked_frames+=1
	return require(false,"Ordinary W-input botanical route blocked at "+str(actor.global_position)+" toward "+str(point))

func route(points: Array) -> bool:
	for point in points:
		if not await walk(Vector2(float(point[0]),float(point[1]))): return false
	return true

func guard_contact(a: Vector3,b: Vector3,label: String) -> bool:
	var hit: Dictionary=ray(a,b,exclusions())
	if not require(not hit.is_empty() and built.is_ancestor_of(hit.collider),"Actual receiving guard contact missing: "+label): return false
	guard_rays+=1
	return true

func static_interfaces() -> bool:
	for side in [-1,1]:
		var owner: String=str(data.floor_owners["port" if side<0 else "starboard"])
		for z in [-236.5,-234.0,-228.0,-222.0,-216.0,-210.0,-209.5]:
			if not support_at(Vector3(float(side)*6,27,float(z)),owner): return false
			# Verify both sides of each actual seam; exact boundary hit owner may be either.
			if not support_at(Vector3(float(side)*3.98,27,float(z)),"D06_fore_route"): return false
			if not support_at(Vector3(float(side)*4.02,27,float(z)),owner): return false
		for index in range(59):
			var z: float=-237.5+float(index)*.5
			for y in [27.4,28.0]:
				if side==-1 and z> -218.1 and z< -213.9:
					if not require(ray(Vector3(-7.4,float(y),z),Vector3(-8.2,float(y),z),exclusions()).is_empty(),"Moss portal must now be clear"): return false
				else:
					if not guard_contact(Vector3(float(side)*7.4,float(y),z),Vector3(float(side)*8.2,float(y),z),"closed outer edge"): return false
		for z_and_sign in [[-238.0,1.0],[-208.0,-1.0]]:
			var z: float=float(z_and_sign[0]);var inward: float=float(z_and_sign[1])
			for y in [27.4,28.0]:
				if not guard_contact(Vector3(float(side)*6,float(y),z+inward*.7),Vector3(float(side)*6,float(y),z-inward*.2),"band end"): return false
	for portal in data.future_portals:
		if portal.programme_id=="D06_directory_03":
			if not require(portal.state=="OPEN" and portal.floor_y==27 and portal.center_z==-216 and portal.edge_x==-8 and portal.clear_width_m==4.2,"Exact Moss portal identity/datum required"): return false
			for x in [-7.98,-8.02,-8.5,-9.0,-10.0]:
				if not support_at(Vector3(float(x),27,-216)): return false
			continue
		if not require(portal.state=="CLOSED" and portal.floor_y==27 and portal.center_z==-216,"Future portal identity/datum changed"): return false
		var side: float=-1.0 if float(portal.edge_x)<0 else 1.0
		for z in [float(portal.center_z)-float(portal.clear_width_m)/2+.25,float(portal.center_z),float(portal.center_z)+float(portal.clear_width_m)/2-.25]:
			if not guard_contact(Vector3(side*7.4,27.6,z),Vector3(side*8.2,27.6,z),str(portal.programme_id)+" deliberately closed"): return false
	# An almost full-width continuous axial box; query margins do not alter production collision.
	var shape:=BoxShape3D.new();shape.size=Vector3(7.98,3.58,2.8);shape.margin=.001
	for z in [-237.0,-234.0,-231.0,-228.0,-225.0,-222.0,-219.0,-216.0,-213.0,-210.0]:
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.collision_mask=1;query.exclude=exclusions();query.transform.origin=Vector3(0,28.8,float(z))
		if not require(space.intersect_shape(query,8).is_empty(),"Eight-metre reserved axial street has an obstruction"): return false
		axial_clearance_queries+=1
	return true

func bump_guard(label: String,direction: Vector2) -> bool:
	release_inputs()
	actor.rotation.y=atan2(-direction.x,-direction.y)
	actor.set("pitch",0.0);actor.camera.rotation.x=0.0
	var start: Vector3=actor.global_position
	var touched: bool=false
	key(KEY_W,true)
	for frame in range(45):
		if not await advance(1,true): return false
		if not require(absf(actor.global_position.x)<7.7 and actor.global_position.z>-237.7 and actor.global_position.z< -208.3,"Original capsule escaped the bounded receiving floor"): return false
		for index in range(actor.get_slide_collision_count()):
			var collision: KinematicCollision3D=actor.get_slide_collision(index)
			var body: Object=collision.get_collider()
			if body is Node and built.is_ancestor_of(body as Node) and absf(collision.get_normal().y)<.7: touched=true
	key(KEY_W,false)
	if not await advance(15,true): return false
	if not require(touched,"Player did not actually contact closed guard: "+label): return false
	completed_bumps.append({"name":label,"from":vec(start),"to":vec(actor.global_position),"actual_slide_collision_with_guard":true})
	return true

func exercise() -> bool:
	if not static_interfaces(): return false
	if not await route([[0,-234]]): return false
	for side in [-1,1]:
		var x: float=float(side)*6
		var label: String="port" if side<0 else "starboard"
		if not await route([[x,-234],[x,-236.5]]): return false
		if not await bump_guard(label+" fore end",Vector2(0,-1)): return false
		if not await route([[x,-236.5],[x,-228],[x,-216],[x,-209.5]]): return false
		if not await bump_guard(label+" aft end",Vector2(0,1)): return false
		if not await route([[x,-209.5],[x,-216]]): return false
		if side==-1:
			if not await moss_interior(): return false
		else:
			if not await bump_guard(label+" closed future portal",Vector2(float(side),0)): return false
		if not await route([[x,-216],[x,-234],[0,-234]]): return false
	if not await route([[0,-209.5],[0,-234],[0,-250]]): return false
	if not require(completed_bumps.size()==5 and moss_portal_crossings>=2 and moss_route_completed and int(crossed_seams.get("port",0))>=2 and int(crossed_seams.get("starboard",0))>=2,"Both seams and Moss doorway must be crossed out/back and all five retained actual barriers contacted"): return false
	metrics["future_portals"]=data.future_portals
	metrics["axial_strip_preserved_x_m"]=[-4,4]
	metrics["capsule_radius_m"]=.3;metrics["capsule_height_m"]=1.8
	return true

func run() -> void:
	started=Time.get_ticks_msec()
	receipt_path="res://artifacts/"+test_name+"_attempt_"+str(Time.get_unix_time_from_system()).replace(".","_")+"_"+str(started)+".json"
	if not require(FileAccess.get_sha256(BOTANICAL_CONTRACT)==BOTANICAL_CONTRACT_SHA,"Exact botanical acceptance fixture required"): return
	data=JSON.parse_string(FileAccess.get_file_as_string(BOTANICAL_CONTRACT))
	for path in data.unchanged_input_sha256:
		if not require(FileAccess.get_sha256("res://"+str(path))==str(data.unchanged_input_sha256[path]),"Changed retained movement/support input: "+str(path)): return
	main=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
	for frame in range(150): await physics_frame
	ship=main.get_node("World360/Astraea") as Node3D
	actor=ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart=ship.find_child("CustodialCart",true,false) as RigidBody3D
	floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	built=ship.get_node(NodePath(str(data.guard_root))) as Node3D
	space=ship.get_world_3d().direct_space_state
	for body in built.find_children("*","StaticBody3D",true,false): guard_probe_exclusions.append(body.get_rid())
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual main-scene player/floors/closed guards required"): return
	if not pin_imports(): return
	loaded_proof=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(loaded_proof.get("validation_completed",false)),"Complete installed botanical/medical source and contact proof failed"): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled,"Unchanged active production player required"): return
	var shapes: Array=actor.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CapsuleShape3D and absf(shapes[0].shape.radius-.3)<.000001 and absf(shapes[0].shape.height-1.8)<.000001 and absf(actor.camera.position.y-1.65)<.000001,"Original capsule and ordinary eye height required"): return
	if not require(ship.arrive_at(Vector3(0,27.1,-250),0.0),"Initial existing axial-floor arrival refused"): return
	if not await advance(45,false): return
	if not require(absf(actor.global_position.y-27)<.08,"Initial verified arrival failed to settle"): return
	if not support_at(Vector3(0,27,-250),"D06_fore_route"): return
	track_motion=true
	if not await exercise(): return
	if failed: return
	release_inputs();write_receipt("PASS")
	print(test_name.to_upper()," PASS: ordinary unchanged-player receiving check; ",walked_frames," walk frames, ",support_samples," support rays, ",guard_rays," guard rays, ",completed_bumps.size()," real retained barrier contacts plus Moss interior/return. No cart/species acceptance.")
	main.queue_free();await process_frame;quit(0)

# MOSS_ACCESS_EXACT_SECTION_BEGIN
func moss_interior() -> bool:
	# Source public route centre-lines, explicit original entry datum and dry garden loop.
	if not await route([[-6,-216],[-10,-216],[-18,-216],[-18,-238],[-44,-238],[-44,-216],[-44,-188],[-18,-188],[-18,-216]]): return false
	# The care route is source-authored, reached through its existing cross-path.
	if not await route([[-44,-216],[-51,-216],[-51,-245],[-42.2,-245],[-42.2,-246.6]]): return false
	if not await read_moss_information("WP10_info_care_01"): return false
	if not await route([[-42.2,-245],[-51,-245],[-51,-216],[-44,-216],[-18,-216],[-18,-222.2],[-19.8,-222.2]]): return false
	if not await read_moss_information("WP10_info_stream_01"): return false
	if not await route([[-18,-222.2],[-18,-216],[-10,-216],[-6,-216]]): return false
	moss_route_completed=true
	return true

func read_moss_information(identity: String) -> bool:
	var target: Node3D=ship.get_node("ShipSpace/D06_MossSanctuary_Receiving_WIP/"+identity)
	var delta: Vector3=target.global_position-actor.camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	var pitch: float=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.set("pitch",pitch);actor.camera.rotation.x=pitch
	focus(true)
	if not await advance(10,true): return false
	if not require(not target.expanded,"Information starts closed"): return false
	key(KEY_E,true)
	if not await advance(1,true): return false
	key(KEY_E,false)
	if not await advance(5,true): return false
	if not require(target.expanded,"Original RMB/E did not open "+identity): return false
	key(KEY_E,true)
	if not await advance(1,true): return false
	key(KEY_E,false)
	if not await advance(5,true): return false
	if not require(not target.expanded,"Original RMB/E did not close "+identity): return false
	focus(false)
	return true
# MOSS_ACCESS_EXACT_SECTION_END
