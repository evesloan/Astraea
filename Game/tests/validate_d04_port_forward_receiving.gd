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
	var budget:=int(delta.length()/3.1*60)+150;var frames:=0;var reached:=false
	for i in range(budget):
		await physics_frame;frames+=1
		var now:=goal-player.global_position;now.y=0
		if now.dot(delta.normalized())<.16:reached=true;break
	physical_key(false)
	for i in range(20):await physics_frame
	var contacts:Array=[]
	for i in range(player.get_slide_collision_count()):contacts.append(str(player.get_slide_collision(i).get_collider().get_path()))
	if not reached:print("WALK_BLOCKED_CONTACTS ",contacts)
	var at:=player.global_position;var horizontal:=Vector2(at.x-goal.x,at.z-goal.z).length()
	return {"reached":reached and horizontal<.55 and absf(at.y-goal.y)<.12,"frames":frames,"start":str(start),"goal":str(goal),"final":str(at),"floor_contact":player.is_on_floor(),"existing_player_controller":true}
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var receiving:Node3D=ship.find_child("D04PortForwardReceiving",true,false)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_RECEIVING.json"));var space:=ship.get_world_3d().direct_space_state
	var visual:Node3D=receiving.get_node("ReceivedSourceGeometry");var floor:Node3D=visual.find_child("D04PF_ReceivedFloor",true,false);var lower:Node3D=visual.find_child("D04PF_StaffLowerLanding",true,false)
	for fi in range(p.feet.size()):
		var f:Dictionary=p.feet[fi];var owner:Node=ship.find_child(str(f.owner),true,false)
		for dx in [-.14,0,.14]:
			for dz in [-.14,0,.14]:
				var at:=Vector3(f.x+dx,f.y-.24,f.z+dz);var h:=ray(space,at-Vector3.UP*.03,at+Vector3.UP*.03)
				record("retained_bearing_"+str(fi)+"_"+str(dx)+"_"+str(dz),owner!=null and not h.is_empty()and owner.is_ancestor_of(h.collider)and absf(h.position.y-(float(f.y)-.24))<.002)
	var route:Array=[Vector3(-3.98,16.5,-405.2),Vector3(-8.5,16.5,-405.2),Vector3(-20,16.5,-405.2),Vector3(-32,16.5,-405.2),Vector3(-44,16.5,-405.2),Vector3(-44,16.5,-435),Vector3(-44,16.5,-420),Vector3(-44,16.5,-390),Vector3(-44,16.5,-369.5),Vector3(-52,16.5,-369.5),Vector3(-60.05,16.5,-369.5),Vector3(-66.4,16.5,-369.5)]
	for i in range(route.size()):
		var at:Vector3=route[i];var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04)
		var expected:Node=ship.find_child("D04_fore_route",true,false)if i==0 else floor
		record("received_route_floor_"+str(i),not h.is_empty()and expected.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002)
		record("route_capsule_"+str(i),capsule_clear(space,at));record("real_cart_station_"+str(i),cart_clear(space,at,PI/2 if i<5 or i>8 else 0))
	var stair_points:Array=[Vector3(-63.55,12,-369.2),Vector3(-63.55,12.6,-372.8),Vector3(-63.55,13.5,-375.8),Vector3(-63.55,14.25,-379.8),Vector3(-60.05,14.25,-379.8),Vector3(-60.05,14.85,-376.3),Vector3(-60.05,15.9,-372.8),Vector3(-60.05,16.5,-369.5)]
	for i in range(stair_points.size()):
		var at:Vector3=stair_points[i];var h:=ray(space,at+Vector3.UP*.045,at-Vector3.UP*.045)
		record("stair_supported_"+str(i),not h.is_empty()and receiving.is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.002);record("stair_capsule_"+str(i),capsule_clear(space,at))
	var floor_points:Array=[Vector3(-68.3,16.5,-374.9),Vector3(-68.3,16.5,-365.1),Vector3(-68.3,16.5,-372.5)]
	for i in range(floor_points.size()):
		var at:Vector3=floor_points[i];var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("source_fitting_floor_"+str(i),not h.is_empty()and floor.is_ancestor_of(h.collider))
	# Probe each exact exported guard thickness plus5mm; the retained stair
	# side guard is92mm away and otherwise legitimately precedes the new guard.
	for i in range(p.guards.size()):
		var guard:MeshInstance3D=visual.find_child(str(p.guards[i]),true,false);var b:AABB=guard.global_transform*guard.get_aabb();var center:=b.get_center();var axis:=Vector3(b.size.x*.5+.005,0,0)if b.size.x<b.size.z else Vector3(0,0,b.size.z*.5+.005);var h:=ray(space,center-axis,center+axis)
		record("perimeter_guard_"+str(i),not h.is_empty()and guard.is_ancestor_of(h.collider))
		if not h.is_empty()and not guard.is_ancestor_of(h.collider):print("GUARD_CONTACT ",i," ",guard.name," ",h.collider.get_path()," ",h.position)
	var old:Node=ship.find_child("LowerStaffEnclosure",true,false);var door:Node3D=receiving.get_node("D03StaffReceivingDoor")
	var wall:=ray(space,Vector3(-58.3,13.2,-369),Vector3(-58.82,13.2,-369))
	if not p.open_staff_gateway:record("original_staff_wall_sealed",not wall.is_empty()and old.is_ancestor_of(wall.collider))
	else:
		for name in p.staff_wall_cut.meshes:record("bounded_old_batch_replaced_"+str(name),old.find_child(str(name),true,false)==null)
		for i in range(100):await physics_frame
		record("door_initial_closed",not door.desired_open and door.open_fraction<.001)
		door.interact(null)
		for frame in range(100):
			await physics_frame
			if frame in[0,20,40,60,80,99]:
				for leaf in door.leaves:
					var c:CollisionShape3D=leaf.get_node("LeafContact");var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;var hits:=space.intersect_shape(q,64);var foreign:Array=[]
					for h in hits:
						if not door.is_ancestor_of(h.collider):foreign.append(str(h.collider.get_path()))
					record("leaf_sweep_"+str(frame)+"_"+str(leaf.name),foreign.is_empty())
					if not foreign.is_empty():print("FOREIGN_LEAF_CONTACT ",frame," ",leaf.name," ",foreign)
		record("door_open",door.desired_open and door.open_fraction>.999)
		for y in[12.2,12.79,13.2,14.3]:record("full_staff_aperture_"+str(y),ray(space,Vector3(-59.2,y,-369),Vector3(-58.3,y,-369)).is_empty())
		var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-57,12.03,-369);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
		for i in range(10):await physics_frame
		var walking:Array=[]
		for goal in[Vector3(-59.6,12,-369),Vector3(-63.55,12,-369),Vector3(-63.55,14.25,-379.8),Vector3(-60.05,14.25,-379.8),Vector3(-60.05,16.5,-369.5),Vector3(-66.4,16.5,-369.5)]:
			var result:Dictionary=await walk_to(player,goal);walking.append(result);record("existing_controller_staff_walk_"+str(walking.size()),result.reached and result.floor_contact)
			if not result.reached:break
		physical_key(false)
		door.interact(null)
		for i in range(100):await physics_frame
		record("door_closed_roundtrip",not door.desired_open and door.open_fraction<.001)
		receiving.set_meta("bounded_staff_walk_evidence",walking)
	# Existing physical controller crosses the unchanged axial public arrival seam.
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-1.5,16.53,-405.2);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	for i in range(10):await physics_frame
	var walk:Dictionary=await walk_to(player,Vector3(-8.5,16.5,-405.2));record("existing_controller_public_arrival",walk.reached and walk.floor_contact);physical_key(false)
	var homes:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false);record("original85_homes",int(homes.get_meta("source_candidate_units",0))==85);record("original221_anchors",int(homes.get_meta("source_rest_slots",0))==221)
	record("D04_rooms_unadopted",int(receiving.get_meta("rooms_adopted",-1))==0);record("culling_preserved",ship.get_node("ShipSystems/ReceivedRoomResidency").enabled)
	var r={"status":"PASS"if errors.is_empty()else"FAIL","stage":"staff_connected"if p.open_staff_gateway else"staff_wall_sealed","model_sha256":p.model_sha256,"checks":checks,"check_count":checks.size(),"errors":errors,"bearing_samples":216,"ray_excludes":0,"real_cart_station_queries":route.size(),"existing_controller_public_arrival":walk,"existing_controller_staff_walk":receiving.get_meta("bounded_staff_walk_evidence",[]),"staff_cart_vertical_acceptance":false,"rooms_adopted":0,"primary_load_accepted":false,"whole_Group1_complete":false,"limits":p.limits}
	FileAccess.open("res://artifacts/d04_port_forward_connected.json"if p.open_staff_gateway else"res://artifacts/d04_port_forward_sealed.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  "));print(JSON.stringify({"status":r.status,"check_count":r.check_count,"errors":errors,"public_walk":walk,"staff_walk":r.existing_controller_staff_walk}));quit(0 if errors.is_empty()else 1)
