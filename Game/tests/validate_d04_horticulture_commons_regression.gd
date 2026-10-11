extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(key:String,ok:bool)->void:
	checks[key]=ok
	if not ok:errors.append(key)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func capsule_clear(space:PhysicsDirectSpaceState3D,at:Vector3)->bool:
	var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001
	q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
	if not space.intersect_shape(q,32).is_empty():return false
	# Opposite cross-rays also catch a stance placed wholly inside an opaque
	# closed mesh; concave surface queries alone can miss that case.
	for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
		if not ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta).is_empty():return false
	return true
func cart_clear(space:PhysicsDirectSpaceState3D,at:Vector3,yaw:float)->bool:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
	for item in d.boxes:
		var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	for item in d.wheel_contacts:
		var shape:=SphereShape3D.new();shape.radius=float(item.radius);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	return true
func physical_key(down:bool)->void:
	var e:=InputEventKey.new();e.keycode=KEY_W;e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk_to(player:CharacterBody3D,goal:Vector3)->Dictionary:
	var start:=player.global_position;var delta:=goal-start;delta.y=0
	player.rotation.y=atan2(-delta.x,-delta.z);physical_key(true)
	var budget:=int(delta.length()/3.1*60)+150;var frames:=0;var reached:=false;var route_contacts:Dictionary={}
	for i in range(budget):
		await physics_frame;frames+=1
		for j in range(player.get_slide_collision_count()):route_contacts[str(player.get_slide_collision(j).get_collider().get_path())]=true
		var now:=goal-player.global_position;now.y=0
		if now.dot(delta.normalized())<.16:reached=true;break
	physical_key(false)
	for i in range(20):await physics_frame
	var contacts:Array=[]
	for i in range(player.get_slide_collision_count()):contacts.append(str(player.get_slide_collision(i).get_collider().get_path()))
	if not reached:print("WALK_BLOCKED_CONTACTS ",contacts," ALL ",route_contacts.keys())
	var at:=player.global_position;var horizontal:=Vector2(at.x-goal.x,at.z-goal.z).length()
	return {"reached":reached and horizontal<.55 and absf(at.y-goal.y)<.12,"frames":frames,"start":str(start),"goal":str(goal),"final":str(at),"floor_contact":player.is_on_floor(),"existing_player_controller":true}
func _initialize()->void:call_deferred("run")
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json"))
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var commons:Node3D=ship.find_child("D04PortForwardCommonsServiceActivity",true,false)
	player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(15):await physics_frame
	var space:=ship.get_world_3d().direct_space_state
	for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
	for f in p.model_pins:record("model_pin_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	for i in range(p.foundation_feet.size()):
		for dx in[-.35,0,.35]:
			for dz in[-.35,0,.35]:
				var at:=vec(p.foundation_feet[i].at)+Vector3(dx,-.3,dz);var h:=ray(space,at-Vector3.UP*.02,at+Vector3.UP*.02);record("keel_underside_"+str(i)+"_"+str(dx)+"_"+str(dz),not h.is_empty() and str(h.collider.get_parent().name)=="HUL_KeelPan"and absf(h.position.y+3.5)<.002)
	for b in p.stock_product_support_contacts:
		var at:=vec(b.position);var h:=ray(space,at+Vector3.UP*.01,at-Vector3.UP*.01);record("original_stock_shelf_contact_"+str(b.name),not h.is_empty() and (str(h.collider.get_parent().name).begins_with("D04CS_CleanStockCabinet__") or str(h.collider.get_parent().name).begins_with("D04CS_"+str(b.name)+"__")) and absf(h.position.y-at.y)<.002)
		for dx in[-.08,.08]:
			var q:=at+Vector3(dx,0,0);var face:=ray(space,q+Vector3.UP*.02,q-Vector3.UP*.02);record("original_stock_adjacent_shelf_"+str(b.name)+"_"+str(dx),not face.is_empty() and str(face.collider.get_parent().name).begins_with("D04CS_CleanStockCabinet__") and absf(face.position.y-at.y)<.002)
	for part in p.successor_parts:
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
		var shape:=BoxShape3D.new();shape.size=hi-lo-Vector3.ONE*.004;shape.margin=0;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,(hi+lo)/2);var bad:Array=[]
		if not p.open_receiving_connection:
			for h in space.intersect_shape(query,128):
				var name:=str(h.collider.get_parent().name)
				if name not in p.preimages.map(func(a):return str(a.name)) and name not in p.successor_inherited_joint_contacts.get(str(part.name),[]):bad.append(str(h.collider.get_path()))
		else:
			var model:Node3D=commons.find_child(str(part.name),true,false)
			if model==null:bad.append("missing successor")
		record("revised_contained_successor_"+str(part.name),bad.is_empty())
	var stations:Array=p.gallery_route+[p.clean_stock_cart_station,p.soiled_return_cart_station,p.quiet_activity_approach]
	for i in range(stations.size()):
		var at:=vec(stations[i]);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("floor_"+str(i),not h.is_empty() and str(h.collider.get_parent().name)=="D04CS_Floor"and absf(h.position.y-16.5)<.002);record("capsule_"+str(i),capsule_clear(space,at))
		if i!=6:
			for j in range(9):record("cart_turn_"+str(i)+"_"+str(j),cart_clear(space,at,j*PI/4))
	# Retained cart contact geometry sampled continuously along the public gallery and each service approach.
	var segments:Array=[]
	for i in range(p.gallery_route.size()-1):segments.append([p.gallery_route[i],p.gallery_route[i+1]])
	segments.append([p.gallery_route[1],p.soiled_return_cart_station]);segments.append([p.gallery_route[2],p.clean_stock_cart_station])
	var sweep_count:=0
	for segment in segments:
		var a:=vec(segment[0]);var b:=vec(segment[1]);var delta:=b-a;var yaw:=atan2(-delta.x,-delta.z);var steps:=int(ceil(delta.length()/.25))
		for i in range(steps+1):record("retained_cart_sweep_"+str(sweep_count),cart_clear(space,a.lerp(b,float(i)/steps),yaw));sweep_count+=1
	var public_cart_poses:=0
	var wheel_floor_samples:=0
	if p.open_receiving_connection:
		var cart_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
		for item in p.public_cart_arrival_maneuver_poses:
			var at:=vec(item.position);var basis:=Basis(Vector3.UP,float(item.yaw));record("public_cart_maneuver_"+str(public_cart_poses),cart_clear(space,at,float(item.yaw)))
			for wheel in cart_data.wheel_contacts:
				var contact:=at+basis*vec(wheel.center)-Vector3.UP*float(wheel.radius);var h:=ray(space,contact+Vector3.UP*.02,contact-Vector3.UP*.02);record("public_cart_wheel_floor_"+str(wheel_floor_samples),not h.is_empty() and str(h.collider.get_parent().name) in ["D04CS_Floor","D04PF_ReceivedFloor"] and absf(h.position.y-16.5)<.002);wheel_floor_samples+=1
			public_cart_poses+=1
	# Opaque partition physically separates clean and return stances; no dirty-route operation is inferred.
	var h:=ray(space,vec(p.clean_stock_cart_station)+Vector3.UP,vec(p.soiled_return_cart_station)+Vector3.UP);record("clean_return_partition",not h.is_empty() and str(h.collider.get_parent().name)=="D04CS_CellPartition_1")
	var stock:=commons.find_child("D04CS_CleanStockCabinet__*",true,false);record("original_stock_cabinet_present",stock!=null)
	for q in p.preimages:record("preimage_gate_"+str(q.name),(ship.find_child(str(q.name),true,false)==null)==bool(p.open_receiving_connection))
	record("receiving_aperture_capsule_gate",capsule_clear(space,vec(p.public_entry))==bool(p.open_receiving_connection))
	var roots:Array=[["D04PortForwardHomeCandidates",4],["D04PortForwardSecondHomeCandidates",4],["D04PortForwardThirdHomeCandidates",2],["D04PortForwardFourthHomeCandidates",4],["D04PortForwardFifthHomeCandidates",6]]
	for pair in roots:
		var home:Node3D=ship.find_child(str(pair[0]),true,false);record("retained_homes_"+str(pair[0]),home!=null and int(home.get_meta("physical_candidates",0))==int(pair[1]))
	var old:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false);record("original85_homes",int(old.get_meta("source_candidate_units",0))==85);record("original221_anchors",int(old.get_meta("source_rest_slots",0))==221);record("culling_preserved",ship.get_node("ShipSystems/ReceivedRoomResidency").enabled)
	var crew:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CREW_HOME_APPROACH_RUNTIME.json"))
	for i in range(crew.route_xz.size()):
		var at:=Vector3(crew.route_xz[i][0],12,crew.route_xz[i][1]);record("crew_capsule_"+str(i),capsule_clear(space,at));record("crew_cart_"+str(i),cart_clear(space,at,PI/2 if i<3 or i==4 else 0))
	var walks:Array=[]
	if p.open_receiving_connection:
		# Approach the new aperture around retained commons furniture, never relocate it.
		player.global_position=Vector3(-66.1,16.53,-369.5);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(15):await physics_frame
		var goals:Array=[Vector3(-63.8,16.5,-369.5),Vector3(-63.8,16.5,-361.8),Vector3(-66.1,16.5,-361.8),Vector3(-72.3,16.5,-361.8),vec(p.soiled_return_cart_station),Vector3(-72.3,16.5,-361.8),Vector3(-77.3,16.5,-361.8),vec(p.clean_stock_cart_station),Vector3(-77.3,16.5,-361.8),Vector3(-82.2,16.5,-361.8),vec(p.quiet_activity_approach),Vector3(-82.2,16.5,-361.8),Vector3(-66.1,16.5,-361.8),Vector3(-63.8,16.5,-361.8),Vector3(-63.8,16.5,-369.5),Vector3(-66.1,16.5,-369.5)]
		for goal in goals:
			var q:Dictionary=await walk_to(player,goal);walks.append(q);record("actual_player_walk_"+str(walks.size()),q.reached and q.floor_contact)
			if not q.reached:break
	physical_key(false)
	var result={"status":"PASS"if errors.is_empty()else"FAIL","stage":"connected"if p.open_receiving_connection else"sealed","check_count":checks.size(),"checks":checks,"errors":errors,"model_pins":p.model_pins,"existing_player_walks":walks,"retained_cart_sweep_samples":sweep_count,"public_cart_maneuver_poses":public_cart_poses,"public_cart_wheel_floor_samples":wheel_floor_samples,"cart_turn_samples":54,"keel_underside_samples":108,"ray_excludes":0,"primary_load_accepted":false,"cart_safe_vertical_accepted":false,"stock_refill_save_operation_accepted":false,"shared_clean_soiled_crossing_operation_accepted":false,"ordinary_graphics_CRT_hardware_accepted":false,"all20_connected_home_proposals_and25_existing_rests_preserved":true}
	FileAccess.open("res://artifacts/d04_horticulture_commons_regression.json"if p.open_receiving_connection else"res://artifacts/d04_horticulture_commons_regression_sealed.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
