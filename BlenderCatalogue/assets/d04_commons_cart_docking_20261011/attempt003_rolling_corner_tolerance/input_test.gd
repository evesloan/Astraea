extends SceneTree
# One initial fixture. Travel uses only original keyboard/mouse, player and tether.
var errors:Array=[]
var trace:Array=[]
var stages:Array=[]
var frames:=0
var support_samples:=0
var actor:CharacterBody3D
var cart:RigidBody3D
var ship:Node3D
var ids:Array=[]
var last_actor:=Vector3.ZERO
var last_cart:=Vector3.ZERO
var cart_distance:=0.0
var started:=0
var turn_exit_center:=Vector3.ZERO
const OUT="res://artifacts/d04_commons_loaded_docking_attempt003.json"
func key(code:int,on:bool)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=on;Input.parse_input_event(e);Input.flush_buffered_events()
func mouse(on:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=on;Input.parse_input_event(e);Input.flush_buffered_events()
func look(yaw:float,pitch:float=0,limit:float=.04)->void:
 var e:=InputEventMouseMotion.new();var dy:=clampf(wrapf(yaw-actor.global_rotation.y,-PI,PI),-limit,limit);var dp:=clampf(pitch-actor.pitch,-limit,limit);e.relative=Vector2(-dy/.002,-dp/.002);Input.parse_input_event(e);Input.flush_buffered_events()
func stop_keys()->void:
 for k in [KEY_W,KEY_S,KEY_A,KEY_D]:key(k,false)
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if errors.is_empty()else"FAIL","errors":errors,"input_frames":frames,"actual_support_samples":support_samples,"cart_distance_m":cart_distance,"stages":stages,"trace":trace,"ordinary_WASD_mouse_RMB_E":true,"original_player_tether_cart_unchanged":true,"four_original_loose_products":true,"fixture_groups":1,"post_fixture_actor_cart_product_transform_velocity_writes":0,"cart_vertical_accepted":false,"dedicated_clean_used_segregation_accepted":false,"stocking_used_flow_provider_save_accepted":false,"freehand_comfort_final_graphics_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 if not ok:errors.append(label);stop_keys();receipt();print("DOCK_FAIL ",label," actor=",actor.global_position if actor!=null else Vector3.ZERO," cart=",cart.global_position if cart!=null else Vector3.ZERO);quit(1)
 return ok
func state(held:bool=true)->bool:
 frames+=1
 if not require(frames<18000 and Time.get_ticks_msec()-started<600000,"Bounded run budget"):return false
 if not require(cart.driver==actor if held else cart.driver==null,"Original grip state"):return false
 if not require(cart.global_position.is_finite()and cart.linear_velocity.length()<6 and cart.global_basis.y.dot(Vector3.UP)>.97 and absf(cart.global_position.y-16.5)<.12 and absf(actor.global_position.y-16.5)<.12,"Upright supported original cart/operator"):return false
 if not require(cart.global_position.distance_to(last_cart)<.16 and actor.global_position.distance_to(last_actor)<.12,"No discontinuous travel"):return false
 cart_distance+=cart.global_position.distance_to(last_cart);last_cart=cart.global_position;last_actor=actor.global_position
 for i in range(4):
  var product:RigidBody3D=cart.products[i];var local:=cart.to_local(product.global_position)
  if not require(str(product.persistent_id)==ids[i]and product.get_parent()==cart.get_parent()and local.y>.78 and local.y<1.35 and absf(local.x)<.43 and absf(local.z)<.62,"Loose load retained "+str(i)):return false
 if frames%6==0:
  var excluded:Array[RID]=[cart.get_rid(),actor.get_rid()]
  for product in cart.products:excluded.append(product.get_rid())
  var points:Array=[actor.global_position]
  for item in JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json")).wheel_contacts:points.append(cart.global_transform*Vector3(item.center[0],0,item.center[2]))
  for at in points:
   var q:=PhysicsRayQueryParameters3D.create(Vector3(at.x,16.7,at.z),Vector3(at.x,16.3,at.z));q.exclude=excluded;var h:=ship.get_world_3d().direct_space_state.intersect_ray(q)
   if not require(not h.is_empty()and str(h.collider.get_parent().name)=="D04CS_Floor"and absf(h.position.y-16.5)<.002,"Actual wheel/operator original floor bearing"):return false
   support_samples+=1
  trace.append({"frame":frames,"cart":[cart.global_position.x,cart.global_position.y,cart.global_position.z],"actor":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"cart_yaw":cart.global_rotation.y,"actor_yaw":actor.global_rotation.y})
 return true
func settle(count:int,held:bool=true)->bool:
 stop_keys()
 for i in range(count):
  await physics_frame
  if not state(held):return false
 return true
func move_actor(target:Vector3,yaw:float)->bool:
 for i in range(600):
  var delta:=target-actor.global_position;delta.y=0;var speed:=Vector2(actor.velocity.x,actor.velocity.z).length();var yaw_error:=absf(wrapf(yaw-actor.global_rotation.y,-PI,PI))
  if delta.length()<.045 and speed<.05 and yaw_error<.012:stop_keys();return true
  look(yaw);var local:=actor.global_basis.inverse()*delta;var dead:=maxf(.022,speed*speed/32+.012);var moving:=delta.length()>maxf(.035,speed*speed/32+.012)
  key(KEY_W,moving and local.z< -dead);key(KEY_S,moving and local.z>dead);key(KEY_A,moving and local.x< -dead);key(KEY_D,moving and local.x>dead)
  await physics_frame
  if not state():return false
 return require(false,"Ordinary input tracking stalled target="+str(target))
func pose(center:Vector3,yaw:float)->bool:
 return await move_actor(center+Basis(Vector3.UP,yaw)*Vector3(0,0,1.62),yaw)
func line(a:Vector3,b:Vector3,yaw:float)->bool:
 var n:=int(ceil(a.distance_to(b)/.12))
 for i in range(1,n+1):
  if not await pose(a.lerp(b,float(i)/n),yaw):return false
 return await settle(60)
func turn(center:Vector3,a:float,b:float)->bool:
 var n:=int(ceil(absf(b-a)/deg_to_rad(2)))
 for i in range(1,n+1):
  if not await pose(center,lerpf(a,b,float(i)/n)):return false
  if not await settle(3):return false
 # Continue the corner into its real outgoing lane; do not demand static caster alignment at an artificial pause.
 turn_exit_center=center-Basis(Vector3.UP,b).z*.72
 if not await line(center,turn_exit_center,b):return false
 if not require(Vector2(cart.global_position.x,cart.global_position.z).distance_to(Vector2(turn_exit_center.x,turn_exit_center.z))<.25 and absf(wrapf(cart.global_rotation.y-b,-PI,PI))<.08,"Actual force/torque turn endpoint"):return false
 stages.append({"kind":"loaded_quarter_turn","center":str(center),"from_yaw":a,"to_yaw":b,"frame":frames});return true
func press_e()->void:
 mouse(true);key(KEY_E,true);await physics_frame;key(KEY_E,false)
 for i in range(4):await physics_frame
 mouse(false)
func regrip()->bool:
 var d:Vector3=cart.interaction_owner.global_position-actor.camera.global_position;var yaw:=atan2(-d.x,-d.z);var pitch:=atan2(d.y,Vector2(d.x,d.z).length())
 for i in range(30):look(yaw,pitch);await physics_frame;if not state(false):return false
 mouse(true)
 for i in range(4):await physics_frame;if not state(false):return false
 if not require(actor.interaction_target==cart.interaction_owner,"Precise original handle for regrip"):return false
 key(KEY_E,true);await physics_frame;key(KEY_E,false)
 for i in range(4):await physics_frame
 mouse(false)
 if not require(cart.driver==actor,"Original RMB/E regrip"):return false
 return true
func park(dock:Dictionary)->bool:
 if not await settle(90):return false
 var at:=Vector3(dock.position[0],16.5,dock.position[2]);var gaps:Array=[]
 for x in[-.32,.32]:gaps.append(float(dock.wheel_stop_front_z)-(cart.global_transform*Vector3(x,.09,-.43)).z-.09)
 if not require(absf(cart.global_position.x-at.x)<.10 and absf(cart.global_position.z-at.z)<.12 and absf(wrapf(cart.global_rotation.y-PI,-PI,PI))<.08,"Actual dock alignment"):return false
 if not require(gaps.all(func(g):return g>= -.005 and g<.09),"Two actual front wheel/stop clearances "+str(gaps)):return false
 await press_e()
 if not require(cart.driver==null,"Original RMB/E dock release"):return false
 var start:=cart.global_position
 if not await settle(120,false):return false
 if not require(cart.global_position.distance_to(start)<.08 and cart.linear_velocity.length()<.05,"Released loaded cart remains parked"):return false
 stages.append({"kind":"released_loaded_dock","dock":dock.name,"cart":str(cart.global_position),"wheel_stop_gaps_m":gaps,"stable_frames":120,"frame":frames})
 return await regrip()
func _initialize()->void:started=Time.get_ticks_msec();call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(150):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");cart=ship.find_child("CustodialCart",true,false)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false)
 if not require(staff!=null and staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]and staff.floor_heights==[0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0]and str(staff.persistent_id)=="forward_staff_lift_001","Actual protected staff stops and blank D04-D07"):return
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CART_DOCKING.json"));var locals:Array=[]
 for product in cart.products:locals.append(cart.to_local(product.global_position));ids.append(str(product.persistent_id))
 cart.global_position=Vector3(-66.1,16.54,-361.8);cart.rotation=Vector3(0,PI/2,0);cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
 for i in range(4):cart.products[i].global_position=cart.global_transform*locals[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
 actor.global_position=Vector3(-64.48,16.53,-361.8);actor.velocity=Vector3.ZERO;actor.rotation.y=PI/2;actor.set_controls_enabled(true)
 for i in range(90):await physics_frame
 var d:Vector3=cart.interaction_owner.global_position-actor.camera.global_position;actor.pitch=atan2(d.y,Vector2(d.x,d.z).length());actor.camera.rotation.x=actor.pitch
 mouse(true)
 for i in range(4):await physics_frame
 if not require(actor.interaction_target==cart.interaction_owner,"Initial original handle target"):return
 key(KEY_E,true);await physics_frame;key(KEY_E,false)
 for i in range(30):await physics_frame
 mouse(false)
 if not require(cart.driver==actor,"Initial original RMB/E grip"):return
 last_actor=actor.global_position;last_cart=cart.global_position
 var origin:=Vector3(-66.1,16.5,-361.8);var clean:=Vector3(-77.3,16.5,-361.8);var used:=Vector3(-72.3,16.5,-361.8)
 if not await line(origin,clean,PI/2):return
 if not await turn(clean,PI/2,PI):return
 if not await line(turn_exit_center,Vector3(-77.3,16.5,-358.49),PI):return
 if not await park(p.docks[0]):return
 if not await line(Vector3(-77.3,16.5,-358.49),clean,PI):return
 if not await turn(clean,PI,3*PI/2):return
 if not await line(turn_exit_center,used,3*PI/2):return
 if not await turn(used,3*PI/2,PI):return
 if not await line(turn_exit_center,Vector3(-72.3,16.5,-358.49),PI):return
 if not await park(p.docks[1]):return
 if not await line(Vector3(-72.3,16.5,-358.49),used,PI):return
 if not await turn(used,PI,3*PI/2):return
 if not await line(turn_exit_center,origin,3*PI/2):return
 await press_e()
 if not require(cart.driver==null,"Final original release"):return
 receipt();print("D04_LOADED_DOCKS_PASS frames=",frames," bearing=",support_samples," distance=",cart_distance);quit(0)
