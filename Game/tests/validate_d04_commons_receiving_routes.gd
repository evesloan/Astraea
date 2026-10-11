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
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var n:Node3D=ship.find_child("D04PortForwardNorthernReceiving",true,false)
	player.global_position=Vector3(-43.8,16.53,-334);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(15):await physics_frame
	var space:=ship.get_world_3d().direct_space_state
	for z in[-365.9,-354,-348,-342,-331,-324,-317,-303,-295.8]:
		var at:=Vector3(-43.8,16.5,z);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("retained_street_floor_"+str(z),not h.is_empty()and n.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("retained_street_capsule_"+str(z),capsule_clear(space,at));record("retained_street_cart_"+str(z),cart_clear(space,at,0))
	for at in[Vector3(-51.8,16.5,-351.9),Vector3(-51.8,16.5,-345)]:
		var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("retained_care_floor_"+str(at),not h.is_empty()and n.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("retained_care_capsule_"+str(at),capsule_clear(space,at));record("retained_care_cart_"+str(at),cart_clear(space,at,0))
	for z in[-364,-350,-332,-317,-295.5]:
		var at:=Vector3(-57,12,z);record("retained_north_staff_capsule_"+str(z),capsule_clear(space,at));record("retained_north_staff_cart_"+str(z),cart_clear(space,at,0))
	var walks:Array=[]
	for goal in[Vector3(-43.8,16.5,-331.7),Vector3(-43.8,16.5,-295.8)]:
		var w:Dictionary=await walk_to(player,goal);walks.append(w);record("northern_street_actual_walk_"+str(walks.size()),w.reached and w.floor_contact)
	player.global_position=Vector3(-57,12.03,-364);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(15):await physics_frame
	var staff:Dictionary=await walk_to(player,Vector3(-57,12,-295.5));record("full_northern_staff_actual_walk",staff.reached and staff.floor_contact)
	physical_key(false)
	var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"check_count":checks.size(),"errors":errors,"street_controller_walks":walks,"protected_north_staff_controller_walk":staff,"ray_excludes":0,"ordinary_graphics_CRT_hardware_accepted":false,"cart_safe_vertical_accepted":false}
	FileAccess.open("res://artifacts/d04_port_forward_commons_routes.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
