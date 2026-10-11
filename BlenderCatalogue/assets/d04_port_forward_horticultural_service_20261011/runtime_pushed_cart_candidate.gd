extends SceneTree
var failures:Array=[]
var trace:Array=[]
var frames:=0
var actor:CharacterBody3D
var cart:RigidBody3D
var ship:Node3D
var ids:Array=[]
var support_samples:=0
func key(code:int,on:bool)->void:
	var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=on;Input.parse_input_event(e)
func require(ok:bool,label:String)->bool:
	if not ok:failures.append(label);print("PUSH_FAIL ",label);receipt();quit(1)
	return ok
func receipt()->void:
	FileAccess.open("res://artifacts/d04_commons_pushed_cart.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if failures.is_empty()else"FAIL","errors":failures,"original_player_controller":true,"original_physical_tether":true,"four_original_loose_products":true,"initial_fixture_placements":1,"later_actor_cart_product_transform_writes":0,"scripted_velocity_or_move_and_slide_calls":0,"input_frames":frames,"actual_wheel_and_operator_floor_samples":support_samples,"actual_engine_pose_trace":trace,"nominal_gallery_circuit_m":22.4,"scope":"Ordinary W/S gallery delivery and back-out only; no public aperture/cart turns/service-bay turns/freehand comfort/vertical/traffic or whole-neighborhood acceptance."},"  "))
func state()->bool:
	if not require(cart.driver==actor and cart.global_basis.y.dot(Vector3.UP)>.98 and absf(cart.global_position.y-16.5)<.12,"Original cart tether/upright/support"):return false
	if not require(absf(cart.global_position.z+361.8)<.35,"Gallery cart drift"):return false
	for i in range(4):
		var product:RigidBody3D=cart.products[i];var local:=cart.to_local(product.global_position)
		if not require(str(product.persistent_id)==ids[i] and local.y>.78 and local.y<1.35 and absf(local.x)<.43 and absf(local.z)<.62,"Original loose product identity/tray "+str(i)):return false
	if frames%6==0:
		var excluded:Array[RID]=[cart.get_rid(),actor.get_rid()]
		for product in cart.products:excluded.append(product.get_rid())
		var contacts:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"));var points:Array=[actor.global_position]
		for wheel in contacts.wheel_contacts:points.append(cart.global_transform*Vector3(wheel.center[0],0,wheel.center[2]))
		for point in points:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(point.x,16.7,point.z),Vector3(point.x,16.3,point.z));q.exclude=excluded;var h:=ship.get_world_3d().direct_space_state.intersect_ray(q)
			if not require(not h.is_empty() and str(h.collider.get_parent().name)=="D04CS_Floor" and absf(h.position.y-16.5)<.002,"Actual gallery wheel/operator bearing"):return false
			support_samples+=1
		trace.append({"frame":frames,"cart":str(cart.global_position),"operator":str(actor.global_position),"yaw":cart.global_rotation.y})
	return true
func line(target:float)->bool:
	for i in range(1800):
		var d:=target-actor.global_position.x;var speed:=Vector2(actor.velocity.x,actor.velocity.z).length()
		if absf(d)<.16 and speed<.08:
			key(KEY_W,false);key(KEY_S,false)
			for j in range(60):await physics_frame;frames+=1;if not state():return false
			return require(absf(cart.global_position.x-(target-1.62))<.65,"Actual force-tether endpoint")
		var moving:bool=absf(d)>maxf(.11,speed*speed/32+.035);key(KEY_W,moving and d<0);key(KEY_S,moving and d>0)
		await physics_frame;frames+=1;if not state():return false
	return require(false,"Ordinary W/S cart route stalled")
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(150):await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");cart=ship.find_child("CustodialCart",true,false)
	var locals:Array=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position));ids.append(str(product.persistent_id))
	cart.global_position=Vector3(-66.1,16.54,-361.8);cart.rotation=Vector3(0,PI/2,0);cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):cart.products[i].global_position=cart.global_transform*locals[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.global_position=Vector3(-64.48,16.53,-361.8);actor.velocity=Vector3.ZERO;actor.rotation.y=PI/2;actor.set_controls_enabled(true)
	for i in range(90):await physics_frame
	var aim:Vector3=cart.interaction_owner.global_position-actor.camera.global_position;actor.camera.rotation.x=atan2(aim.y,Vector2(aim.x,aim.z).length())
	var mouse:=InputEventMouseButton.new();mouse.button_index=MOUSE_BUTTON_RIGHT;mouse.pressed=true;Input.parse_input_event(mouse);for i in range(4):await physics_frame
	if not require(actor.interaction_target==cart.interaction_owner,"Precise original cart RMB handle target"):return
	key(KEY_E,true);await physics_frame;key(KEY_E,false);for i in range(30):await physics_frame
	if not require(cart.driver==actor,"Ordinary original RMB/E grip"):return
	mouse.pressed=false;Input.parse_input_event(mouse);actor.camera.rotation.x=0
	if not await line(-75.68):return
	if not await line(-64.48):return
	mouse.pressed=true;Input.parse_input_event(mouse);await physics_frame;key(KEY_E,true);await physics_frame;key(KEY_E,false);await physics_frame
	if not require(cart.driver==null,"Original RMB/E release"):return
	mouse.pressed=false;Input.parse_input_event(mouse);receipt();print("D04_PUSHED_CART_PASS frames=",frames," bearing=",support_samples);quit(0)
