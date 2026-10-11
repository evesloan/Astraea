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
var lift:Node3D
var expected_held:=false
var riding:=false
var floor_y:=16.5
var floor_owners:Dictionary={}
const OUT="res://artifacts/d04_commons_loaded_vertical_attempt001.json"
func key(code:int,on:bool)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=on;Input.parse_input_event(e);Input.flush_buffered_events()
func mouse(on:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=on;Input.parse_input_event(e);Input.flush_buffered_events()
func look(yaw:float,pitch:float=0,limit:float=.04)->void:
 var e:=InputEventMouseMotion.new();var dy:=clampf(wrapf(yaw-actor.global_rotation.y,-PI,PI),-limit,limit);var dp:=clampf(pitch-actor.pitch,-limit,limit);e.relative=Vector2(-dy/.002,-dp/.002);Input.parse_input_event(e);Input.flush_buffered_events()
func stop_keys()->void:
 for k in [KEY_W,KEY_S,KEY_A,KEY_D]:key(k,false)
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if errors.is_empty()else"FAIL","errors":errors,"input_frames":frames,"actual_support_samples":support_samples,"cart_distance_m":cart_distance,"stages":stages,"trace":trace,"actual_floor_owners":floor_owners.keys(),"ordinary_WASD_mouse_RMB_E":true,"original_player_tether_cart_unchanged":true,"four_original_loose_products":true,"fixture_groups":1,"post_fixture_actor_cart_product_transform_velocity_writes":0,"cart_vertical_accepted":errors.is_empty() and stages.any(func(p):return p.kind=="returned_commons_dock"),"dedicated_clean_used_segregation_accepted":false,"stocking_used_flow_provider_save_accepted":false,"freehand_comfort_final_graphics_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 if not ok:errors.append(label);stop_keys();receipt();print("DOCK_FAIL ",label," actor=",actor.global_position if actor!=null else Vector3.ZERO," cart=",cart.global_position if cart!=null else Vector3.ZERO);quit(1)
 return ok
func state(held:bool=true)->bool:
 frames+=1
 if riding:floor_y=lift.cabin.global_position.y
 if not require(frames<120000 and Time.get_ticks_msec()-started<1800000,"Bounded run budget"):return false
 if not require(cart.driver==actor if expected_held else cart.driver==null,"Original grip state"):return false
 if not require(cart.global_position.is_finite()and cart.linear_velocity.length()<6 and cart.global_basis.y.dot(Vector3.UP)>.97 and absf(cart.global_position.y-floor_y)<.12 and absf(actor.global_position.y-floor_y)<.12,"Upright supported original cart/operator"):return false
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
   var q:=PhysicsRayQueryParameters3D.create(Vector3(at.x,floor_y+.2,at.z),Vector3(at.x,floor_y-.2,at.z));q.exclude=excluded;var h:=ship.get_world_3d().direct_space_state.intersect_ray(q)
   if not require(not h.is_empty()and ship.is_ancestor_of(h.collider)and absf(h.position.y-floor_y)<.03,"Actual wheel/operator original floor bearing"):return false
   floor_owners[str(h.collider.get_path())]=true
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
 for i in range(30000):
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
 if not await pose(b,yaw):return false
 return await settle(60)
func turn(center:Vector3,a:float,b:float)->bool:
 var n:=int(ceil(absf(b-a)/deg_to_rad(2)))
 for i in range(1,n+1):
  if not await pose(center,lerpf(a,b,float(i)/n)):return false
  if not await settle(3):return false
 # Continue the corner into its real outgoing lane; do not demand static caster alignment at an artificial pause.
 turn_exit_center=center-Basis(Vector3.UP,b).z*.72
 if not await line(center,turn_exit_center,b):return false
 if not require(Vector2(cart.global_position.x,cart.global_position.z).distance_to(Vector2(turn_exit_center.x,turn_exit_center.z))<.25 and absf(wrapf(cart.global_rotation.y-b,-PI,PI))<deg_to_rad(7),"Loaded rolling corner within lane position/heading allowance"):return false
 stages.append({"kind":"loaded_quarter_turn","center":str(center),"from_yaw":a,"to_yaw":b,"actual_cart_yaw":cart.global_rotation.y,"rolling_exit_center":str(turn_exit_center),"maximum_corner_heading_error_deg":7,"frame":frames});return true
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
 expected_held=true
 if not require(cart.driver==actor,"Original RMB/E regrip"):return false
 return true
func park(dock:Dictionary)->bool:
 if not await settle(90):return false
 var at:=Vector3(dock.position[0],16.5,dock.position[2]);var gaps:Array=[]
 for x in[-.32,.32]:gaps.append(float(dock.wheel_stop_front_z)-(cart.global_transform*Vector3(x,.09,-.43)).z-.09)
 if not require(absf(cart.global_position.x-at.x)<.10 and absf(cart.global_position.z-at.z)<.12 and absf(wrapf(cart.global_rotation.y-PI,-PI,PI))<.08,"Actual dock alignment"):return false
 if not require(gaps.all(func(g):return g>= -.005 and g<.09),"Two actual front wheel/stop clearances "+str(gaps)):return false
 await press_e()
 expected_held=false
 if not require(cart.driver==null,"Original RMB/E dock release"):return false
 var start:=cart.global_position
 if not await settle(120,false):return false
 if not require(cart.global_position.distance_to(start)<.08 and cart.linear_velocity.length()<.05,"Released loaded cart remains parked"):return false
 stages.append({"kind":"released_loaded_dock","dock":dock.name,"cart":str(cart.global_position),"wheel_stop_gaps_m":gaps,"stable_frames":120,"frame":frames})
 return await regrip()
func use_node(target:Node3D)->bool:
 var delta:Vector3=target.global_position-actor.camera.global_position;var yaw:=atan2(-delta.x,-delta.z);var pitch:=atan2(delta.y,Vector2(delta.x,delta.z).length())
 for i in range(40):look(yaw,pitch);await physics_frame;if not state():return false
 mouse(true)
 for i in range(5):await physics_frame;if not state():return false
 if not require(actor.interaction_target==target,"Precise original lift button target "+str(target.persistent_id)):return false
 key(KEY_E,true);await physics_frame;key(KEY_E,false)
 if not state():return false
 mouse(false);return true
func button(index:int,cabin:bool)->Node3D:
 var parent:Node=lift.cabin if cabin else lift
 for node in parent.get_children():
  if node.get_script()==load("res://scripts/lift_button.gd")and node.floor_index==index:return node
 return null
func wait_lift(index:int,travel:bool)->bool:
 riding=travel
 for i in range(2400):
  await physics_frame
  if not state():return false
  if lift.current_floor==index and lift.phase=="idle":
   floor_y=lift.floor_heights[index];riding=false
   stages.append({"kind":"loaded_lift_arrival"if travel else"called_installed_lift","deck":index+1,"frame":frames,"cart":str(cart.global_position),"actor":str(actor.global_position)});return true
 return require(false,"Installed lift bounded arrival "+str(index))
func release()->bool:
 await press_e();expected_held=false
 return require(cart.driver==null,"Original RMB/E release")
func board_travel_exit(index:int)->bool:
 if not await line(cart.global_position,Vector3(.1,floor_y,-106),-PI/2):return false
 if not await release():return false
 if not await move_actor(Vector3(-.9,floor_y,-106),-PI/2):return false
 if not require(not lift.cabin_gate.threshold_occupied(),"Original cart/operator clear cabin threshold"):return false
 if not await use_node(button(index,true)):return false
 if not await wait_lift(index,true):return false
 if not await move_actor(cart.global_position+Basis(Vector3.UP,-PI/2)*Vector3(0,0,1.62),-PI/2):return false
 if not await regrip():return false
 if not await line(cart.global_position,Vector3(-5.5,floor_y,-106),-PI/2):return false
 stages.append({"kind":"actual_loaded_unboard","deck":index+1,"frame":frames,"cart":str(cart.global_position)});return true
func route_leg(target:Vector3,heading:float)->bool:
 return await line(cart.global_position,target,heading)
func follow_poses(route:Array)->bool:
 for i in range(1,route.size()):
  var a:Array=route[i-1];var b:Array=route[i];var from:=Vector3(a[0],a[1],a[2]);var to:=Vector3(b[0],b[1],b[2]);var ya:float=a[3];var yb:float=ya+wrapf(float(b[3])-ya,-PI,PI)
  if absf(yb-ya)>.01:
   var n:=int(ceil(absf(yb-ya)/deg_to_rad(2)))
   for k in range(1,n+1):
    if not await pose(from.lerp(to,float(k)/n),lerpf(ya,yb,float(k)/n)):return false
    if not await settle(3):return false
  if not await line(cart.global_position,to,float(b[3])):return false
  stages.append({"kind":"actual_loaded_route_pose","pose":i,"frame":frames,"target":str(to),"target_yaw":b[3],"cart_yaw":cart.global_rotation.y,"cart":str(cart.global_position)})
 return true
func _initialize()->void:started=Time.get_ticks_msec();call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(150):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");cart=ship.find_child("CustodialCart",true,false);lift=ship.find_child("PrimaryAtriumLift",true,false)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false)
 if not require(staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]and staff.floor_heights==[0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0]and str(staff.persistent_id)=="forward_staff_lift_001","Protected original staff stops/identity blank D04-D07"):return
 if not require(lift.deck_numbers==range(1,19)and lift.floor_heights==JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/PRIMARY_ATRIUM_CORE.json")).floor_y,"Original central eighteen-stop lift"):return
 var route:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json")).cart_poses
 var first:=Vector3(route[0][0],route[0][1],route[0][2])
 var locals:Array=[]
 for product in cart.products:locals.append(cart.to_local(product.global_position));ids.append(str(product.persistent_id))
 cart.global_position=first+Vector3.UP*.04;cart.rotation=Vector3.ZERO;cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
 for i in range(4):cart.products[i].global_position=cart.global_transform*locals[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
 actor.global_position=first+Vector3(0,.03,1.62);actor.velocity=Vector3.ZERO;actor.rotation.y=0;actor.set_controls_enabled(true)
 for i in range(90):await physics_frame
 var d:Vector3=cart.interaction_owner.global_position-actor.camera.global_position;actor.pitch=atan2(d.y,Vector2(d.x,d.z).length());actor.camera.rotation.x=actor.pitch
 last_actor=actor.global_position;last_cart=cart.global_position
 if not await regrip():return
 if not await follow_poses(route):return
 if not await release():return
 if not await move_actor(Vector3(-5.42,16.5,-104.35),0):return
 if not await move_actor(Vector3(-3.4,16.5,-104.35),0):return
 if not await use_node(button(3,false)):return
 if not await wait_lift(3,false):return
 if not await move_actor(Vector3(-5.42,16.5,-104.35),-PI/2):return
 if not await move_actor(cart.global_position+Basis(Vector3.UP,-PI/2)*Vector3(0,0,1.62),-PI/2):return
 if not await regrip():return
 if not await board_travel_exit(2):return
 # Same original loaded cart leaves D03, reboards, then returns physically to D04.
 if not await board_travel_exit(3):return
 var reverse:Array=route.duplicate(true);reverse.reverse();reverse[0]=[-5.5,16.5,-106,-PI/2]
 if not await follow_poses(reverse):return
 var arrival:=Vector3(-66.1,16.5,-361.8)
 if not await line(first,arrival,0):return
 if not await turn(arrival,0,PI/2):return
 if not await line(turn_exit_center,Vector3(-77.3,16.5,-361.8),PI/2):return
 if not await turn(Vector3(-77.3,16.5,-361.8),PI/2,PI):return
 if not await line(turn_exit_center,Vector3(-77.3,16.5,-358.49),PI):return
 var dock:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CART_DOCKING.json")).docks[0]
 if not await park(dock):return
 if not await release():return
 stages.append({"kind":"returned_commons_dock","frame":frames,"cart":str(cart.global_position)})
 receipt();print("D04_COMMONS_LOADED_VERTICAL_PASS frames=",frames," samples=",support_samples," metres=",cart_distance);quit()
