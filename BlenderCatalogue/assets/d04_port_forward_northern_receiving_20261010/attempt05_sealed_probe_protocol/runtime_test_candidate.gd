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
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_NORTHERN_RECEIVING.json"))
	var group:Node=ship.find_child("D04PortForwardNorthernReceiving",true,false);var hull:Node=ship.find_child("LowerHullBody_WIP",true,false);var old:Node=ship.find_child("D04PortForwardReceiving",true,false)
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-43.8,16.53,-367.5);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-44,12.02,-324.5))
	for i in range(2):await physics_frame
	paused=true
	var space:=ship.get_world_3d().direct_space_state
	record("model_pin",FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==p.model_sha256)
	for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
	var underside_samples:Array=[]
	for i in range(p.foundation_feet.size()):
		var foot:Dictionary=p.foundation_feet[i]
		for dx in[-.38,0,.38]:
			for dz in[-.38,0,.38]:
				var at:=Vector3(foot.x+dx,-3.5,foot.z+dz);var h:=ray(space,at+Vector3.UP*.015,at-Vector3.UP*.015)
				var ok:bool=not h.is_empty()and hull.is_ancestor_of(h.collider)and str(h.collider.get_parent().name)=="HUL_KeelPan"and absf(h.position.y+3.5)<.002
				record("retained_keel_underside_"+str(i)+"_"+str(dx)+"_"+str(dz),ok);underside_samples.append({"at":str(at),"original_keel_hit":ok,"hit":""if h.is_empty()else str(h.collider.get_path())})
	var approved_guards:Array=p.guard_preimages.map(func(g):return str(g.name))
	var volume_receipts:Array=[]
	for part in p.parts:
		if not part.runtime_collision:continue
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
		var shape:=BoxShape3D.new();shape.size=hi-lo-Vector3.ONE*.004;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2);var bad:Array=[]
		for h in space.intersect_shape(q,256):
			if not group.is_ancestor_of(h.collider)and not(not p.open_receiving_connection and str(h.collider.get_parent().name)in approved_guards):bad.append(str(h.collider.get_path()))
		record("foreign_volume_"+str(part.name),bad.is_empty());volume_receipts.append({"part":part.name,"foreign_contacts":bad,"query_inset_m":.002})
		if not bad.is_empty():print("NORTH_FOREIGN ",part.name," ",bad)
	for f in p.source_fitting_bounds:
		var lo:=vec(f.min);var hi:=vec(f.max);var shape:=BoxShape3D.new();shape.size=hi-lo-Vector3.ONE*.006;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2);var bad:Array=[]
		for h in space.intersect_shape(q,256):
			if not str(h.collider.get_parent().name).begins_with(str(f.prefix)+"__"):bad.append(str(h.collider.get_path()))
		record("rigid_fitting_foreign_containment_"+str(f.prefix),bad.is_empty())
		if not bad.is_empty():print("FITTING_FOREIGN ",f.prefix," ",bad)
	var floors:Array=[]
	for z in[-365.9,-364,-350,-332,-324.2,-317.1,-309.7,-302.3,-295.2]:
		var at:=Vector3(-43.8,16.5,z);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);var ok:bool=not h.is_empty()and group.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002;record("new_street_floor_"+str(z),ok);record("street_capsule_"+str(z),capsule_clear(space,at));record("street_cart_"+str(z),cart_clear(space,at,0));floors.append({"at":str(at),"new_floor":ok})
	for key in ["care_cart_station","quiet_bench_approach"]:
		var at:=vec(p[key]);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("care_pocket_floor_"+key,not h.is_empty()and group.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("care_pocket_capsule_"+key,capsule_clear(space,at));record("care_pocket_cart_"+key,cart_clear(space,at,0))
	var west_hit:=ray(space,vec(p.care_cart_station)+Vector3.UP*1.65,Vector3(-56,18.15,-351.9));record("opaque_care_service_edge",not west_hit.is_empty()and str(west_hit.collider.get_parent().name)=="D04NR_CareWestWall")
	for z in[-364,-350,-332,-317,-295.5]:
		var at:=Vector3(-57,12,z);record("original_north_staff_capsule_"+str(z),capsule_clear(space,at));record("original_north_staff_cart_"+str(z),cart_clear(space,at,0))
	var crew_contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CREW_HOME_APPROACH_RUNTIME.json"))
	for i in range(crew_contract.route_xz.size()):
		var at:=Vector3(crew_contract.route_xz[i][0],12,crew_contract.route_xz[i][1]);record("retained_crew_capsule_"+str(i),capsule_clear(space,at));record("retained_crew_cart_"+str(i),cart_clear(space,at,PI/2 if i<3 or i==4 else 0))
	for g in p.guard_preimages:record("original_end_guard_gate_"+str(g.name),(old.find_child(str(g.name),true,false)==null)==bool(p.open_receiving_connection))
	record("prior10_physical_proposals",ship.find_child("D04PortForwardHomeCandidates",true,false).get_child_count()==4 and ship.find_child("D04PortForwardSecondHomeCandidates",true,false).get_child_count()==4 and ship.find_child("D04PortForwardThirdHomeCandidates",true,false).get_child_count()==2)
	record("all20_capacity25_preserved",p.all20_allocations_unchanged.size()==20 and ship.find_child("D04PortForwardThirdHomeCandidates",true,false).get_meta("capacity_preserved",0)==25)
	record("no_northern_interiors_or_capacity_added",group.get_meta("new_interiors_built",-1)==0 and group.get_meta("new_guest_units",-1)==0 and group.get_meta("new_rest_places",-1)==0 and group.get_meta("remaining_interiors",-1)==10 and group.get_meta("remaining_reserved_rests",-1)==13)
	record("source_culling_preserved",ship.get_node("ShipSystems/ReceivedRoomResidency").enabled);record("engineering_and_vertical_held",not group.get_meta("primary_load_accepted",true)and not group.get_meta("cart_safe_vertical_accepted",true))
	paused=false
	var walks:Array=[];var staff_walks:Array=[];var arrivals:Array=[]
	if p.open_receiving_connection:
		player.global_position=Vector3(-43.8,16.53,-367.5);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(10):await physics_frame
		var goals:Array=[Vector3(-43.8,16.5,-354),Vector3(-43.8,16.5,-351.9),vec(p.care_cart_station),Vector3(p.quiet_bench_approach[0],16.5,-345),Vector3(-43.8,16.5,-345),Vector3(-43.8,16.5,-331),Vector3(-43.8,16.5,-317),Vector3(-43.8,16.5,-303),Vector3(-43.8,16.5,-295.6),Vector3(-43.8,16.5,-317),Vector3(-43.8,16.5,-347),Vector3(-43.8,16.5,-367.5)]
		for goal in goals:
			var w:Dictionary=await walk_to(player,goal);walks.append(w);record("actual_northern_player_walk_"+str(walks.size()),w.reached and w.floor_contact)
			if not w.reached:break
		player.global_position=Vector3(-57,12.03,-364);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(10):await physics_frame
		for z in[-350,-332,-317,-295.5]:
			var w:Dictionary=await walk_to(player,Vector3(-57,12,z));staff_walks.append(w);record("protected_north_staff_actual_walk_"+str(staff_walks.size()),w.reached and w.floor_contact)
			if not w.reached:break
		for route in[[Vector3(-1.5,16.53,-405.2),Vector3(-8.5,16.5,-405.2)],[Vector3(-60.05,16.53,-369.5),Vector3(-66.4,16.5,-369.5)]]:
			player.global_position=route[0];player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
			for i in range(10):await physics_frame
			var w:Dictionary=await walk_to(player,route[1]);arrivals.append(w);record("retained_public_staff_arrival_"+str(arrivals.size()),w.reached and w.floor_contact)
	physical_key(false)
	var result={"status":"PASS"if errors.is_empty()else"FAIL","stage":"connected"if p.open_receiving_connection else"sealed","model_sha256":p.model_sha256,"checks":checks,"check_count":checks.size(),"errors":errors,"source_pins":51,"original_keel_top_preimage_samples":306,"original_keel_underside_samples":underside_samples,"source_foreign_volumes":volume_receipts,"floors":floors,"existing_player_northern_walks":walks,"protected_north_staff_actual_walks":staff_walks,"retained_public_staff_arrivals":arrivals,"ray_excludes":0,"primary_load_accepted":false,"cart_safe_vertical_accepted":false,"ordinary_graphics_review":false,"new_interiors_built":0,"remaining_interiors":10,"remaining_reserved_rests":13}
	var name:String="d04_port_forward_northern_connected.json"if p.open_receiving_connection else"d04_port_forward_northern_sealed.json"
	FileAccess.open("res://artifacts/"+name,FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
